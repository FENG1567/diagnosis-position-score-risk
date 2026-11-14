#!/usr/bin/env python3
"""Summarize issued per-level CIs and compare rounded with full-precision coverage."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import run_per_level_validation as frozen_runner


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parents[2]
OUTPUT_DIR = WORK_ROOT / "outputs" / "v2" / "level_validation"
CONFIG_PATH = frozen_runner.DEFAULT_CONFIG.resolve()
PRIMARY_ROWS_PATH = OUTPUT_DIR / "per_level_replicate_results.csv"
SUMMARY_PATH = OUTPUT_DIR / "per_level_summary.csv"
METHOD_SUMMARY_PATH = OUTPUT_DIR / "per_level_design_method_summary.csv"
BY_LEVEL_PATH = OUTPUT_DIR / "per_level_fullprecision_sensitivity_by_level.csv"
DISCORDANCE_PATH = OUTPUT_DIR / "per_level_rounding_coverage_discordances.csv"
MANIFEST_PATH = OUTPUT_DIR / "per_level_rounding_sensitivity_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _risk_bounds(df: pd.DataFrame, level: float, group: int, min_patients: int,
                 audit_module) -> tuple[str, tuple[float, float] | None]:
    cell = df[df.score == level]
    arm = cell[cell.grp == group]
    n = len(arm)
    events = float(arm.outcome.sum())
    patients = int(arm.pid.nunique())
    risk = events / n if n else math.nan
    if n == 0:
        return "no records", None
    if patients < min_patients:
        return "too few distinct patients", None
    if events <= 0 or events >= n:
        return "degenerate outcome: point estimate only", None

    contributions = (arm.outcome.to_numpy(float) - risk) / n
    se = float(np.sqrt(audit_module._cluster_variance(
        contributions, arm.pid.to_numpy(), total_clusters=df.pid.nunique()
    )))
    if not np.isfinite(se) or se <= 0:
        return "zero or invalid cluster variance", None
    logit = np.log(risk / (1 - risk))
    se_logit = se / (risk * (1 - risk))
    lower, upper = audit_module.sigmoid(np.array([
        logit - 1.96 * se_logit, logit + 1.96 * se_logit
    ]))
    return "computed", (100 * float(lower), 100 * float(upper))


def _delta_bounds(df: pd.DataFrame, level: float, min_patients: int,
                  min_records_per_arm: int, min_records_per_level: int,
                  audit_module) -> tuple[str, tuple[float, float] | None]:
    cell = df[df.score == level]
    never = cell[cell.grp == 1]
    principal = cell[cell.grp == 0]
    n1, n0 = len(never), len(principal)
    e1, e0 = float(never.outcome.sum()), float(principal.outcome.sum())
    patients1, patients0 = int(never.pid.nunique()), int(principal.pid.nunique())
    if not n1 or not n0:
        return "no shared support", None
    if patients1 < min_patients or patients0 < min_patients:
        return "too few distinct patients in a definition", None
    if (n1 < min_records_per_arm or n0 < min_records_per_arm or
            n1 + n0 < min_records_per_level):
        return "below record-count threshold", None
    if e1 <= 0 or e1 >= n1 or e0 <= 0 or e0 >= n0:
        return "degenerate outcome: point estimate only", None

    p1, p0 = e1 / n1, e0 / n0
    contributions = np.concatenate((
        (never.outcome.to_numpy(float) - p1) / n1,
        -(principal.outcome.to_numpy(float) - p0) / n0,
    ))
    ids = np.concatenate((never.pid.to_numpy(), principal.pid.to_numpy()))
    se = float(np.sqrt(audit_module._cluster_variance(
        contributions, ids, total_clusters=df.pid.nunique()
    )))
    if not np.isfinite(se) or se <= 0:
        return "zero or invalid cluster variance", None
    delta = p1 - p0
    return "computed", (100 * (delta - 1.96 * se), 100 * (delta + 1.96 * se))


def _mcse_ratio(covered: np.ndarray, emitted: np.ndarray, coverage: float | None):
    if coverage is None or len(emitted) < 2 or float(np.mean(emitted)) <= 0:
        return None
    influence = covered - coverage * emitted
    return float(np.std(influence, ddof=1) / math.sqrt(len(emitted)) / np.mean(emitted))


def _summary_record(design: str, method: str, target_count: int, emitted: np.ndarray,
                    rounded_covered: np.ndarray, raw_covered: np.ndarray,
                    discordant_count: int, endpoint_mismatch_count: int) -> dict:
    reps = len(emitted)
    eligible = reps * target_count
    n_emitted = int(emitted.sum())
    n_withheld = eligible - n_emitted
    output_rate = n_emitted / eligible if eligible else None
    output_mcse = (
        float(np.std(emitted, ddof=1) / math.sqrt(reps) / target_count)
        if eligible and reps > 1 else None
    )
    rounded_n_covered = int(rounded_covered.sum())
    raw_n_covered = int(raw_covered.sum())
    rounded_coverage = rounded_n_covered / n_emitted if n_emitted else None
    raw_coverage = raw_n_covered / n_emitted if n_emitted else None
    return {
        "design": design,
        "method": method,
        "truth_defined": bool(target_count),
        "n_defined_score_arm_intervals_per_dataset": int(target_count),
        "n_design_replicates": reps,
        "n_eligible_intervals": eligible,
        "n_ci_emitted": n_emitted,
        "n_withheld": n_withheld,
        "output_rate": output_rate,
        "output_rate_mcse_clustered_by_dataset": output_mcse,
        "n_covered_issued_rounded_ci": rounded_n_covered,
        "conditional_coverage_issued_rounded_ci": rounded_coverage,
        "conditional_coverage_mcse_issued_clustered_by_dataset": _mcse_ratio(
            rounded_covered, emitted, rounded_coverage
        ),
        "n_covered_fullprecision_ci": raw_n_covered,
        "conditional_coverage_fullprecision_ci": raw_coverage,
        "conditional_coverage_mcse_fullprecision_clustered_by_dataset": _mcse_ratio(
            raw_covered, emitted, raw_coverage
        ),
        "coverage_difference_fullprecision_minus_issued": (
            raw_coverage - rounded_coverage
            if raw_coverage is not None and rounded_coverage is not None else None
        ),
        "n_coverage_discordant_due_to_rounding": int(discordant_count),
        "n_emitted_endpoint_rounding_mismatches": int(endpoint_mismatch_count),
        "interpretation": (
            "Undefined: no population-defined target intervals in this design."
            if not target_count else
            "Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets."
        ),
    }


def main() -> None:
    started = time.monotonic()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    frozen_runner.validate_config(config)
    freeze = json.loads((OUTPUT_DIR / "pre_run_freeze.json").read_text(encoding="utf-8"))
    paths = {
        "config_sha256": CONFIG_PATH,
        "runner_sha256": Path(frozen_runner.__file__).resolve(),
        "shared_inference_tool_sha256": frozen_runner.AUDIT_DIR / "cohort_definition_audit.py",
        "dgp_generator_sha256": frozen_runner.AUDIT_DIR / "benchmark.py",
    }
    actual_hashes = {key: sha256(path) for key, path in paths.items()}
    for key, value in actual_hashes.items():
        if freeze.get(key) != value:
            raise RuntimeError(f"frozen input hash mismatch for {key}: {value}")

    primary = pd.read_csv(PRIMARY_ROWS_PATH)
    expected_rows = sum(
        int(config["outer_replicates_per_design"]) * len(design["scores"]) * 3
        for design in config["designs"]
    )
    if len(primary) != expected_rows:
        raise RuntimeError(f"primary replicate output has {len(primary)} rows; expected {expected_rows}")
    if set(primary["design"].astype(str).unique()) != {
            design["name"] for design in config["designs"]}:
        raise RuntimeError("primary replicate output design set does not match frozen config")

    simulate_dataset, _ = frozen_runner.load_sources()
    # The full-precision calculation below mirrors the frozen inference equations.
    import cohort_definition_audit as audit_module

    thresholds = config["inference_validation"]
    min_patients = int(thresholds["min_patients"])
    min_records_per_arm = int(thresholds["min_records_per_arm"])
    min_records_per_level = int(thresholds["min_records_per_level"])
    reps = int(config["outer_replicates_per_design"])

    design_method_summaries = []
    by_level_summaries = []
    discordances = []
    regenerated = 0

    for design_index, design in enumerate(config["designs"]):
        name = design["name"]
        scores = list(map(float, design["scores"]))
        joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
        risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
        group_defined = {
            (score, group): bool(joint[group, j] > 0)
            for j, score in enumerate(scores) for group in (0, 1)
        }
        delta_defined = {
            score: bool(joint[0, j] > 0 and joint[1, j] > 0)
            for j, score in enumerate(scores)
        }
        group_target_count = sum(group_defined.values())
        delta_target_count = sum(delta_defined.values())
        target_counts = {"group_risk": group_target_count, "delta_s": delta_target_count}
        method_arrays = {
            method: {
                "emitted": np.zeros(reps, dtype=int),
                "rounded_covered": np.zeros(reps, dtype=int),
                "raw_covered": np.zeros(reps, dtype=int),
                "discordances": 0,
                "endpoint_mismatches": 0,
            }
            for method in ("group_risk", "delta_s")
        }
        level_arrays = {
            (score, method, arm): {
                "eligible": bool(
                    group_defined[(score, 0 if arm == "principal" else 1)]
                    if method == "group_risk" else delta_defined[score]
                ),
                "emitted": np.zeros(reps, dtype=int),
                "rounded_covered": np.zeros(reps, dtype=int),
                "raw_covered": np.zeros(reps, dtype=int),
                "discordances": 0,
                "endpoint_mismatches": 0,
            }
            for score in scores
            for method, arms in (("group_risk", ("principal", "never")),
                                 ("delta_s", ("never_minus_principal",)))
            for arm in arms
        }

        primary_design = primary[primary["design"] == name].set_index(
            ["replicate", "level", "estimand", "arm"], verify_integrity=True
        )
        base_seed = int(config["seed"]) + design_index * 1_000_003
        for rep in range(reps):
            rng = np.random.default_rng(base_seed + rep * 10_007)
            frame = simulate_dataset(design, rng).rename(columns={"y": "outcome"})
            regenerated += 1
            total_clusters = int(frame.pid.nunique())
            for j, score in enumerate(scores):
                raw_results = []
                for group, arm in ((0, "principal"), (1, "never")):
                    status, bounds = _risk_bounds(frame, score, group, min_patients, audit_module)
                    truth_defined = group_defined[(score, group)]
                    truth = 100 * float(risks[group, j]) if truth_defined else None
                    raw_results.append(("group_risk", arm, status, bounds, truth_defined, truth))
                status, bounds = _delta_bounds(
                    frame, score, min_patients, min_records_per_arm,
                    min_records_per_level, audit_module
                )
                truth_defined = delta_defined[score]
                truth = (
                    100 * (float(risks[1, j]) - float(risks[0, j]))
                    if truth_defined else None
                )
                raw_results.append(("delta_s", "never_minus_principal", status,
                                    bounds, truth_defined, truth))

                for method, arm, raw_status, raw_bounds, defined, truth in raw_results:
                    emitted_row = primary_design.loc[(rep, score, method, arm)]
                    issued_status = str(emitted_row["ci_status"])
                    if raw_status != issued_status:
                        raise RuntimeError(
                            f"status mismatch {name} rep {rep} score {score} {method}/{arm}: "
                            f"reconstructed={raw_status}, issued={issued_status}"
                        )
                    is_emitted = issued_status == "computed"
                    if is_emitted:
                        if raw_bounds is None:
                            raise RuntimeError(f"missing full-precision CI for emitted {name}/{rep}/{score}/{method}/{arm}")
                        issued_bounds = (
                            float(emitted_row["ci_lower_pp"]), float(emitted_row["ci_upper_pp"])
                        )
                        rounded_raw = (round(raw_bounds[0], 2), round(raw_bounds[1], 2))
                        if (abs(rounded_raw[0] - issued_bounds[0]) > 1e-10 or
                                abs(rounded_raw[1] - issued_bounds[1]) > 1e-10):
                            method_arrays[method]["endpoint_mismatches"] += 1
                            level_arrays[(score, method, arm)]["endpoint_mismatches"] += 1
                            raise RuntimeError(
                                f"rounded endpoint mismatch {name} rep {rep} score {score} {method}/{arm}: "
                                f"reconstructed={rounded_raw}, issued={issued_bounds}"
                            )
                    if not defined:
                        continue

                    state = method_arrays[method]
                    level_state = level_arrays[(score, method, arm)]
                    rounded_covered = bool(emitted_row["covered"]) if is_emitted else False
                    if is_emitted:
                        if truth is None:
                            raise RuntimeError("truth undefined for an eligible emitted interval")
                        raw_covered = bool(raw_bounds[0] <= truth <= raw_bounds[1])
                        # Confirm the primary runner's stored coverage is its issued rounded-interval result.
                        if rounded_covered != bool(issued_bounds[0] <= truth <= issued_bounds[1]):
                            raise RuntimeError("stored primary coverage does not match issued rounded endpoints")
                        state["emitted"][rep] += 1
                        level_state["emitted"][rep] += 1
                        state["rounded_covered"][rep] += int(rounded_covered)
                        level_state["rounded_covered"][rep] += int(rounded_covered)
                        state["raw_covered"][rep] += int(raw_covered)
                        level_state["raw_covered"][rep] += int(raw_covered)
                        if rounded_covered != raw_covered:
                            state["discordances"] += 1
                            level_state["discordances"] += 1
                            discordances.append({
                                "design": name,
                                "replicate": rep,
                                "level": score,
                                "method": method,
                                "arm": arm,
                                "truth_pp": truth,
                                "issued_lower_pp": issued_bounds[0],
                                "issued_upper_pp": issued_bounds[1],
                                "fullprecision_lower_pp": raw_bounds[0],
                                "fullprecision_upper_pp": raw_bounds[1],
                                "issued_rounded_covered": rounded_covered,
                                "fullprecision_covered": raw_covered,
                            })

        for method, target_count in target_counts.items():
            state = method_arrays[method]
            design_method_summaries.append(_summary_record(
                name, method, target_count, state["emitted"], state["rounded_covered"],
                state["raw_covered"], state["discordances"], state["endpoint_mismatches"]
            ))
        for (score, method, arm), state in level_arrays.items():
            target_count = int(state["eligible"])
            by_level_summaries.append(_summary_record(
                name, method, target_count, state["emitted"], state["rounded_covered"],
                state["raw_covered"], state["discordances"], state["endpoint_mismatches"]
            ) | {"level": score, "arm": arm})
        print(f"[per-level-rounding] completed {design_index + 1}/11: {name}", flush=True)

    method_df = pd.DataFrame(design_method_summaries)
    by_level_df = pd.DataFrame(by_level_summaries)
    discordance_columns = [
        "design", "replicate", "level", "method", "arm", "truth_pp",
        "issued_lower_pp", "issued_upper_pp", "fullprecision_lower_pp",
        "fullprecision_upper_pp", "issued_rounded_covered", "fullprecision_covered",
    ]
    pd.DataFrame.from_records(discordances, columns=discordance_columns).to_csv(
        DISCORDANCE_PATH, index=False, encoding="utf-8"
    )
    method_df.to_csv(METHOD_SUMMARY_PATH, index=False, encoding="utf-8")
    by_level_df.to_csv(BY_LEVEL_PATH, index=False, encoding="utf-8")

    # Verify that the reconstructed issued-CI counts reproduce the frozen runner's summary.
    primary_summary = pd.read_csv(SUMMARY_PATH).set_index(
        ["design", "level", "estimand", "arm"], verify_integrity=True
    )
    for row in by_level_summaries:
        key = (row["design"], row["level"], row["method"], row["arm"])
        frozen = primary_summary.loc[key]
        if (int(frozen["n_eligible_replicates"]) != int(row["n_eligible_intervals"]) or
                int(frozen["n_ci_emitted"]) != int(row["n_ci_emitted"]) or
                int(frozen["n_covered"]) != int(row["n_covered_issued_rounded_ci"])):
            raise RuntimeError(f"sensitivity table does not reproduce frozen summary for {key}")

    output_paths = [METHOD_SUMMARY_PATH, BY_LEVEL_PATH, DISCORDANCE_PATH]
    manifest = {
        "record_type": "per_level_issued_vs_fullprecision_ci_sensitivity",
        "status": "complete",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "config_sha256": actual_hashes["config_sha256"],
        "runner_sha256": actual_hashes["runner_sha256"],
        "shared_inference_tool_sha256": actual_hashes["shared_inference_tool_sha256"],
        "dgp_generator_sha256": actual_hashes["dgp_generator_sha256"],
        "primary_replicate_results_sha256": sha256(PRIMARY_ROWS_PATH),
        "sensitivity_script_sha256": sha256(Path(__file__).resolve()),
        "seed": int(config["seed"]),
        "replicates_per_design": reps,
        "design_count": len(config["designs"]),
        "regenerated_dataset_count": regenerated,
        "calculation": (
            "Reconstructs full-precision group-risk logit-Wald endpoints and delta_s Wald endpoints "
            "from the same deterministic simulated records, using the frozen tool's cluster variance "
            "and sigmoid helpers and identical CI gates. Rounds reconstructed endpoints to 2 decimals "
            "and asserts exact agreement with every emitted checkpoint endpoint. The primary coverage "
            "remains coverage of the issued rounded endpoints; full-precision coverage is reported only "
            "as a sensitivity."
        ),
        "mcse": "Dataset-clustered MCSE computed over the independent outer replicates; all score/arm cells within a dataset stay together.",
        "endpoint_rounding_mismatches": int(method_df["n_emitted_endpoint_rounding_mismatches"].sum()),
        "coverage_discordances": int(method_df["n_coverage_discordant_due_to_rounding"].sum()),
        "outputs": [
            {"path": path.name, "sha256": sha256(path), "rows": int(len(pd.read_csv(path)))}
            for path in output_paths
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[per-level-rounding] wrote sensitivity outputs to {OUTPUT_DIR}", flush=True)


if __name__ == "__main__":
    main()

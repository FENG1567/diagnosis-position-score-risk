#!/usr/bin/env python3
"""Confirmatory per-level validation using the frozen shared inference function."""
from __future__ import annotations

import hashlib
import argparse
import json
import math
import os
import platform
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parents[2]
AUDIT_DIR = HERE.parent / "audit"
DEFAULT_CONFIG = HERE / "per_level_validation_config.json"
DEFAULT_OUTPUT = WORK_ROOT / "outputs" / "v2" / "level_validation"
FROZEN_TOOL_SHA256 = "8b074a3b3adf808311cc42e7f3fdf7d24427e31aab421569ea3460b07c184994"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_sources():
    sys.path.insert(0, str(AUDIT_DIR))
    from benchmark import simulate_dataset  # frozen DGP generator; no benchmark driver is run
    from cohort_definition_audit import per_level_inference
    return simulate_dataset, per_level_inference


def validate_config(cfg: dict) -> None:
    if cfg.get("config_status") != "frozen_before_confirmatory_outcomes":
        raise ValueError("per-level config is not marked frozen before confirmatory outcomes")
    if int(cfg["outer_replicates_per_design"]) != 1000:
        raise ValueError("confirmatory run requires exactly 1,000 replicates per design")
    if int(cfg["seed"]) != 27112027:
        raise ValueError("unexpected per-level confirmatory seed")
    if len(cfg["designs"]) != 11:
        raise ValueError("confirmatory per-level config must contain all 11 frozen designs")
    for design in cfg["designs"]:
        joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
        scores = np.asarray(design["scores"], dtype=float)
        if joint.shape != (2, len(scores)) or not np.isclose(joint.sum(), 1.0):
            raise ValueError(f"invalid group-score probabilities in {design['name']}")
        expected = [float(scores[j]) for j in range(len(scores))
                    if joint[0, j] > 0 and joint[1, j] > 0]
        supplied = list(map(float, design["expected_support"]))
        if expected != supplied:
            raise ValueError(f"expected_support mismatch in {design['name']}: {supplied} != {expected}")


def _ci_bounds(record: dict, field: str):
    value = record[field]
    if value is None:
        return None, None
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"unexpected CI format in {field}: {value!r}")
    return float(value[0]), float(value[1])


def _safe_mean(values):
    values = [float(v) for v in values if v is not None and np.isfinite(v)]
    return float(np.mean(values)) if values else None


def _summary_metric(items: list[dict], truth: float, name: str, status_field: str,
                    ci_field: str, point_field: str, records_for_groupcounts: bool):
    n_all = len(items)
    emitted = [row for row in items if row[status_field] == "computed"]
    n_output = len(emitted)
    covered = []
    for row in emitted:
        lo, hi = _ci_bounds(row, ci_field)
        covered.append(bool(lo <= truth <= hi))
    point_rows = [row for row in items
                  if row[point_field] is not None and np.isfinite(row[point_field])]
    bias_point = _safe_mean([row[point_field] - truth for row in point_rows])
    bias_emitted = _safe_mean([row[point_field] - truth for row in emitted])
    coverage = (float(sum(covered) / n_output) if n_output else None)
    output_rate = (n_output / n_all) if n_all else None
    output_mcse = (math.sqrt(output_rate * (1 - output_rate) / n_all)
                   if n_all and output_rate is not None else None)
    coverage_mcse = (math.sqrt(coverage * (1 - coverage) / n_output)
                     if n_output and coverage is not None else None)
    summary = {
        "n_eligible_replicates": n_all,
        "n_point_available": len(point_rows),
        "point_available_rate": len(point_rows) / n_all if n_all else None,
        "n_ci_emitted": n_output,
        "output_rate": output_rate,
        "output_rate_mcse": output_mcse,
        "n_covered": int(sum(covered)),
        "conditional_coverage": coverage,
        "conditional_coverage_mcse": coverage_mcse,
        "bias_pp_point_available": bias_point,
        "bias_pp_ci_emitted": bias_emitted,
        "refusal_counts_json": json.dumps(dict(sorted(
            (key, count) for key, count in Counter(row[status_field] for row in items).items()
            if key != "computed")), sort_keys=True),
    }
    if records_for_groupcounts:
        for field, prefix in (("n0", "principal_records"), ("n1", "never_records"),
                              ("patients0", "principal_patients"),
                              ("patients1", "never_patients"),
                              ("events0", "principal_events"),
                              ("events1", "never_events")):
            vals = [int(row[field]) for row in items]
            summary[f"{prefix}_mean"] = _safe_mean(vals)
            summary[f"{prefix}_median"] = float(np.median(vals)) if vals else None
            summary[f"{prefix}_min"] = min(vals) if vals else None
            summary[f"{prefix}_max"] = max(vals) if vals else None
    return summary


def analyze(config_path: Path, output_dir: Path, pilot: bool = False,
            aggregate_only: bool = False) -> dict:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    validate_config(cfg)
    output_dir.mkdir(parents=True, exist_ok=True)
    locked_seed = int(cfg["seed"])
    locked_replicates = int(cfg["outer_replicates_per_design"])
    run_mode = "aggregate_only_recovery" if aggregate_only else "confirmatory"
    if pilot:
        cfg = json.loads(json.dumps(cfg))
        cfg["seed"] = 27112028
        cfg["outer_replicates_per_design"] = 2
        cfg["benchmark_id"] = f"{cfg['benchmark_id']}_pipeline_pilot"
        run_mode = "pipeline_pilot_aggregate_only" if aggregate_only else "pipeline_pilot"

    audit_path = AUDIT_DIR / "cohort_definition_audit.py"
    benchmark_path = AUDIT_DIR / "benchmark.py"
    config_hash = sha256(config_path)
    audit_hash = sha256(audit_path)
    benchmark_hash = sha256(benchmark_path)
    if audit_hash != FROZEN_TOOL_SHA256:
        raise RuntimeError(f"frozen inference tool hash mismatch: {audit_hash}")

    simulate_dataset, per_level_inference = load_sources()
    thresholds = cfg["inference_validation"]
    min_patients = int(thresholds["min_patients"])
    min_records_per_arm = int(thresholds["min_records_per_arm"])
    min_records_per_level = int(thresholds["min_records_per_level"])
    replicate_rows: list[dict] = []
    checkpoint_dir = output_dir / "replicate_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_paths: list[Path] = []
    start = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()

    for design_index, design in enumerate(cfg["designs"]):
        if aggregate_only:
            break
        design_row_start = len(replicate_rows)
        design_name = design["name"]
        scores = list(map(float, design["scores"]))
        joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
        risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
        common_levels = set(map(float, design["expected_support"]))
        group_truth_defined = {
            (float(score), int(group)): bool(joint[group, j] > 0)
            for j, score in enumerate(scores) for group in (0, 1)
        }
        delta_truth_defined = {float(score): bool(joint[0, j] > 0 and joint[1, j] > 0)
                               for j, score in enumerate(scores)}
        base_seed = int(cfg["seed"]) + design_index * 1_000_003

        for rep in range(int(cfg["outer_replicates_per_design"])):
            rng = np.random.default_rng(base_seed + rep * 10_007)
            frame = simulate_dataset(design, rng)
            input_df = frame.rename(columns={"y": "outcome"})
            results = per_level_inference(
                input_df, scores, min_patients=min_patients,
                min_records_per_arm=min_records_per_arm,
                min_records_per_level=min_records_per_level,
            )
            if len(results) != len(scores):
                raise RuntimeError(f"unexpected per-level output length in {design_name} rep {rep}")

            for j, result in enumerate(results):
                score = float(result["level"])
                if score != scores[j]:
                    raise RuntimeError(f"level order changed in {design_name} rep {rep}")
                n0, n1 = int(result["n_primary"]), int(result["n_never"])
                patients0, patients1 = int(result["patients_primary"]), int(result["patients_never"])
                events0, events1 = int(result["events_primary"]), int(result["events_never"])
                is_common = score in common_levels
                support_type = ("common_support" if is_common else
                                "one_definition_support" if (joint[0, j] > 0 or joint[1, j] > 0)
                                else "structurally_absent")
                shared_counts = {
                    "design": design_name,
                    "replicate": rep,
                    "level": score,
                    "support_type": support_type,
                    "n_principal": n0,
                    "n_never": n1,
                    "patients_principal": patients0,
                    "patients_never": patients1,
                    "events_principal": events0,
                    "events_never": events1,
                }

                for group, arm, risk_field, ci_field, status_field, n, patients, events in (
                    (0, "principal", "risk_primary", "risk_primary_ci_pp",
                     "risk_primary_ci_status", n0, patients0, events0),
                    (1, "never", "risk_never", "risk_never_ci_pp",
                     "risk_never_ci_status", n1, patients1, events1),
                ):
                    truth_defined = group_truth_defined[(score, group)]
                    point = result[risk_field]
                    lo, hi = _ci_bounds(result, ci_field)
                    status = result[status_field]
                    truth = 100 * float(risks[group, j]) if truth_defined else None
                    covered = (bool(lo <= truth <= hi)
                               if truth_defined and status == "computed" else None)
                    replicate_rows.append({
                        **shared_counts,
                        "estimand": "group_risk",
                        "arm": arm,
                        "truth_defined": truth_defined,
                        "target_common_support": is_common,
                        "truth_pp": truth,
                        "point_pp": point,
                        "ci_lower_pp": lo,
                        "ci_upper_pp": hi,
                        "ci_status": status,
                        "observed_cell_present": n > 0,
                        "covered": covered,
                    })

                truth_defined = delta_truth_defined[score]
                delta_point = result["diff_pp"]
                lo, hi = _ci_bounds(result, "delta_ci_pp")
                status = result["delta_ci_status"]
                truth = (100 * (float(risks[1, j]) - float(risks[0, j]))
                         if truth_defined else None)
                replicate_rows.append({
                    **shared_counts,
                    "estimand": "delta_s",
                    "arm": "never_minus_principal",
                    "truth_defined": truth_defined,
                    "target_common_support": is_common,
                    "truth_pp": truth,
                    "point_pp": delta_point,
                    "ci_lower_pp": lo,
                    "ci_upper_pp": hi,
                    "ci_status": status,
                    "observed_cell_present": bool(n0 > 0 and n1 > 0),
                    "covered": (bool(lo <= truth <= hi)
                                if truth_defined and status == "computed" else None),
                })

        checkpoint_path = checkpoint_dir / f"replicates_{design_index + 1:02d}_{design_name}.csv"
        pd.DataFrame.from_records(replicate_rows[design_row_start:]).to_csv(
            checkpoint_path, index=False, encoding="utf-8")
        checkpoint_paths.append(checkpoint_path)
        print(f"[per-level] completed {design_index + 1}/{len(cfg['designs'])}: {design_name}; "
              f"checkpoint={checkpoint_path.name}", flush=True)

    reps = int(cfg["outer_replicates_per_design"])
    expected_checkpoint_paths = [
        checkpoint_dir / f"replicates_{design_index + 1:02d}_{design['name']}.csv"
        for design_index, design in enumerate(cfg["designs"])
    ]
    if aggregate_only:
        missing = [path.name for path in expected_checkpoint_paths if not path.exists()]
        if missing:
            raise FileNotFoundError(f"aggregate-only mode needs all design checkpoints; missing: {missing}")
        checkpoint_paths = expected_checkpoint_paths
    if len(checkpoint_paths) != len(cfg["designs"]):
        raise RuntimeError("one per-design checkpoint is required before final aggregation")
    replicate_df = pd.concat(
        [pd.read_csv(path) for path in checkpoint_paths], ignore_index=True)
    for design in cfg["designs"]:
        design_rows = replicate_df[replicate_df["design"] == design["name"]]
        expected_rows = reps * len(design["scores"]) * 3
        observed_replicates = sorted(map(int, design_rows["replicate"].unique()))
        if len(design_rows) != expected_rows or observed_replicates != list(range(reps)):
            raise ValueError(
                f"checkpoint mismatch for {design['name']}: {len(design_rows)} rows, "
                f"replicates={observed_replicates}; expected {expected_rows} rows and 0..{reps - 1}"
            )
    summaries: list[dict] = []
    refusal_rows: list[dict] = []
    for (design_name, score, estimand, arm), group in replicate_df.groupby(
            ["design", "level", "estimand", "arm"], sort=False, dropna=False):
        eligible = group[group["truth_defined"]]
        support_type = str(group["support_type"].iloc[0])
        truth = (float(eligible["truth_pp"].iloc[0]) if len(eligible) else None)
        if len(eligible):
            # Adapt the long replicate schema to the summary helper's count and CI fields.
            metric_items = []
            for row in eligible.to_dict("records"):
                metric_items.append({
                    **row,
                    "ci_bounds": ([row["ci_lower_pp"], row["ci_upper_pp"]]
                                  if row["ci_lower_pp"] is not None else None),
                    "n0": row["n_principal"],
                    "n1": row["n_never"],
                    "patients0": row["patients_principal"],
                    "patients1": row["patients_never"],
                    "events0": row["events_principal"],
                    "events1": row["events_never"],
                })
            info = _summary_metric(metric_items, truth, estimand,
                                   "ci_status", "ci_bounds", "point_pp", True)
        else:
            info = {
                "n_eligible_replicates": 0, "n_point_available": 0,
                "point_available_rate": None, "n_ci_emitted": 0, "output_rate": None,
                "output_rate_mcse": None, "n_covered": 0, "conditional_coverage": None,
                "conditional_coverage_mcse": None, "bias_pp_point_available": None,
                "bias_pp_ci_emitted": None, "refusal_counts_json": "{}",
            }
            for prefix in ("principal_records", "never_records", "principal_patients",
                           "never_patients", "principal_events", "never_events"):
                for suffix in ("mean", "median", "min", "max"):
                    info[f"{prefix}_{suffix}"] = None
        summaries.append({
            "design": design_name, "level": float(score), "estimand": estimand,
            "arm": arm, "support_type": support_type,
            "truth_defined": bool(len(eligible)), "truth_pp": truth,
            "n_design_replicates": reps, **info,
        })
        counts = Counter(group["ci_status"].astype(str))
        for status, count in sorted(counts.items()):
            refusal_rows.append({
                "design": design_name, "level": float(score), "estimand": estimand,
                "arm": arm, "truth_defined": bool(len(eligible)), "support_type": support_type,
                "ci_status": status, "replicate_count": int(count),
                "eligible_replicate_count": len(eligible),
            })

    family_rows: list[dict] = []
    for design in cfg["designs"]:
        name = design["name"]
        rows = replicate_df[replicate_df["design"] == name]
        valid = rows[rows["truth_defined"]]
        common = set(map(float, design["expected_support"]))
        family_defined = bool(common)
        complete_n = covered_n = 0
        if family_defined:
            for rep in range(reps):
                per_rep = valid[valid["replicate"] == rep]
                complete = len(per_rep) > 0 and bool((per_rep["ci_status"] == "computed").all())
                if complete:
                    complete_n += 1
                    covered_n += int(bool(per_rep["covered"].all()))
            output_rate = complete_n / reps
            coverage = covered_n / complete_n if complete_n else None
            output_mcse = math.sqrt(output_rate * (1 - output_rate) / reps)
            coverage_mcse = (math.sqrt(coverage * (1 - coverage) / complete_n)
                             if complete_n else None)
        else:
            output_rate = coverage = output_mcse = coverage_mcse = None
        n_group_risk = int(valid[valid["estimand"] == "group_risk"].drop_duplicates(
            ["level", "arm"]).shape[0])
        n_delta = int(valid[valid["estimand"] == "delta_s"]["level"].nunique())
        family_rows.append({
            "design": name,
            "family": "all_defined_group_risk_and_common_support_delta_s_pointwise_intervals",
            "family_defined": family_defined,
            "n_defined_group_risk_intervals": n_group_risk,
            "n_defined_delta_s_intervals": n_delta,
            "n_eligible_datasets": reps if family_defined else 0,
            "n_complete_output_families": complete_n,
            "complete_family_output_rate": output_rate,
            "complete_family_output_rate_mcse": output_mcse,
            "n_complete_families_covering_all_truths": covered_n,
            "conditional_simultaneous_containment": coverage,
            "conditional_simultaneous_containment_mcse": coverage_mcse,
            "interpretation": (
                "Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim."
                if family_defined else
                "Undefined: design has no population common-support delta_s estimand."
            ),
        })

    summary_df = pd.DataFrame(summaries)
    refusal_df = pd.DataFrame(refusal_rows)
    family_df = pd.DataFrame(family_rows)
    replicate_path = output_dir / "per_level_replicate_results.csv"
    summary_path = output_dir / "per_level_summary.csv"
    refusal_path = output_dir / "per_level_refusals.csv"
    family_path = output_dir / "complete_family_summary.csv"
    replicate_df.to_csv(replicate_path, index=False, encoding="utf-8")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8")
    refusal_df.to_csv(refusal_path, index=False, encoding="utf-8")
    family_df.to_csv(family_path, index=False, encoding="utf-8")

    manifest = {
        "benchmark_id": cfg["benchmark_id"],
        "run_mode": run_mode,
        "status": "complete",
        "start_timestamp_utc": started_utc,
        "finish_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "replicates_per_design": reps,
        "locked_replicates_per_design": locked_replicates,
        "design_count": len(cfg["designs"]),
        "dataset_count": reps * len(cfg["designs"]),
        "seed": int(cfg["seed"]),
        "locked_config_seed": locked_seed,
        "config_path": str(config_path.resolve()),
        "config_sha256": config_hash,
        "shared_tool_path": str(audit_path.resolve()),
        "shared_tool_sha256": audit_hash,
        "dgp_generator_path": str(benchmark_path.resolve()),
        "dgp_generator_sha256": benchmark_hash,
        "runner_path": str(Path(__file__).resolve()),
        "runner_sha256": sha256(Path(__file__)),
        "test_path": str(HERE / "test_per_level_validation.py"),
        "test_sha256": sha256(HERE / "test_per_level_validation.py"),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "tool_call": "cohort_definition_audit.per_level_inference directly; no bootstrap or logistic path called",
        "support_eligibility": cfg["inference_validation"]["support_eligibility"],
        "family_interval_note": cfg["inference_validation"]["family_diagnostic"],
        "outputs": [path.name for path in (replicate_path, summary_path, refusal_path, family_path)],
        "per_design_checkpoints": [str(path.relative_to(output_dir)) for path in checkpoint_paths],
        "raw_patient_records_written": False,
    }
    manifest_path = output_dir / "per_level_run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[per-level] wrote outputs to {output_dir.resolve()}", flush=True)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot", action="store_true",
                        help="run two pipeline-check replicates per design on seed 27112028")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="rebuild summaries from persisted per-design checkpoints")
    args = parser.parse_args()
    analyze(args.config.resolve(), args.output_dir.resolve(), pilot=args.pilot,
            aggregate_only=args.aggregate_only)

#!/usr/bin/env python3
"""Run the frozen conditional-design interval validation and write per-design checkpoints."""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.special import ndtri


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUDIT_DIR = HERE.parent / "audit"
sys.path.insert(0, str(AUDIT_DIR))
sys.path.insert(0, str(HERE.parent))

import benchmark  # noqa: E402
from conditional_interval import conditional_design_interval  # noqa: E402


CONFIG_PATH = HERE / "conditional_validation_config.json"
OUTPUT_DIR = ROOT / "outputs" / "v2" / "conditional_validation"
FREEZE_PATH = OUTPUT_DIR / "pre_run_freeze.json"
CHECKPOINT_DIR = OUTPUT_DIR / "replicate_checkpoints"
RUN_MANIFEST_PATH = OUTPUT_DIR / "conditional_run_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_point_and_range(frame: pd.DataFrame) -> tuple[float | None, float | None]:
    """Independently reconstruct the fixed-design linear form and patient range sum."""
    group0 = frame.loc[frame.grp == 0, "score"].unique()
    group1 = frame.loc[frame.grp == 1, "score"].unique()
    levels = np.intersect1d(group0, group1)
    if not len(levels):
        return None, None
    supported = frame.loc[frame.score.isin(levels)]
    scores = supported.score.to_numpy(float)
    groups = supported.grp.to_numpy(int)
    outcomes = supported.y.to_numpy(float)
    pids = supported.pid.to_numpy()
    cell_counts = {
        (float(level), int(group)): int(((scores == level) & (groups == group)).sum())
        for level in levels for group in (0, 1)
    }
    level_counts = {float(level): int((scores == level).sum()) for level in levels}
    denominator = len(supported)
    coefficients = np.asarray([
        (level_counts[float(score)] / denominator) /
        cell_counts[(float(score), int(group))] * (1.0 if group == 1 else -1.0)
        for score, group in zip(scores, groups)
    ], dtype=float)
    point = float(coefficients @ outcomes)
    _, cluster_code = np.unique(pids, return_inverse=True)
    ranges = np.bincount(cluster_code, weights=np.abs(coefficients))
    sum_squared_ranges = float(ranges @ ranges)
    return point, sum_squared_ranges


def observed_common_support(frame: pd.DataFrame) -> list[float]:
    return list(map(float, np.intersect1d(
        frame.loc[frame.grp == 0, "score"].unique(),
        frame.loc[frame.grp == 1, "score"].unique(),
    )))


def conditional_truth_on_observed_support(frame: pd.DataFrame, design: dict):
    """Evaluate theta_D using actual observed support and pooled-record weights."""
    support = observed_common_support(frame)
    if not support:
        return None
    true_delta = {
        float(score): float(design["risks_never"][j] - design["risks_principal"][j])
        for j, score in enumerate(design["scores"])
    }
    supported = frame.loc[frame.score.isin(support)]
    level_weights = supported.groupby("score").size() / len(supported)
    return float(sum(float(level_weights.loc[score]) * true_delta[float(score)]
                     for score in support))


def simulate_fixed_design(design: dict, rng: np.random.Generator) -> pd.DataFrame:
    """Generate outcomes conditional on a fixed paired/singleton patient design."""
    counts = design["fixed_cell_record_counts"]
    cell_counts = {
        (0.0, 0): int(counts["primary_score_0"]),
        (1.0, 0): int(counts["primary_score_1"]),
        (0.0, 1): int(counts["never_score_0"]),
        (1.0, 1): int(counts["never_score_1"]),
    }
    pid_rows: list[int] = []
    score_rows: list[int] = []
    group_rows: list[int] = []
    patient_count = 0
    for level in (0, 1):
        n0 = cell_counts[(float(level), 0)]
        n1 = cell_counts[(float(level), 1)]
        paired = min(n0, n1)
        for _ in range(paired):
            pid_rows.extend((patient_count, patient_count))
            score_rows.extend((level, level))
            group_rows.extend((0, 1))
            patient_count += 1
        if n0 > paired:
            for _ in range(n0 - paired):
                pid_rows.append(patient_count)
                score_rows.append(level)
                group_rows.append(0)
                patient_count += 1
        if n1 > paired:
            for _ in range(n1 - paired):
                pid_rows.append(patient_count)
                score_rows.append(level)
                group_rows.append(1)
                patient_count += 1

    pid = np.asarray(pid_rows, dtype=np.int64)
    score = np.asarray(score_rows, dtype=np.int64)
    group = np.asarray(group_rows, dtype=np.int64)
    patient_latent = rng.normal(size=patient_count)
    residual = rng.normal(size=len(pid))
    rho = float(design["outcome_icc"])
    latent = math.sqrt(rho) * patient_latent[pid] + math.sqrt(1 - rho) * residual
    risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
    outcome = (latent < ndtri(risks[group, score])).astype(float)
    frame = pd.DataFrame({"pid": pid, "score": score, "grp": group, "y": outcome})
    if len(frame) != int(design["n_records"]) or frame.pid.nunique() != patient_count:
        raise RuntimeError(f"fixed-design size mismatch in {design['name']}")
    if not frame.groupby(["score", "grp"]).size().to_dict() == {
            (0, 0): cell_counts[(0.0, 0)],
            (0, 1): cell_counts[(0.0, 1)],
            (1, 0): cell_counts[(1.0, 0)],
            (1, 1): cell_counts[(1.0, 1)],
    }:
        raise RuntimeError(f"fixed cell counts changed in {design['name']}")
    return frame


def simulate_dataset(design: dict, rng: np.random.Generator) -> pd.DataFrame:
    if design.get("dgp_type") == "fixed_design_paired_patients":
        return simulate_fixed_design(design, rng)
    return benchmark.simulate_dataset(design, rng)


def population_truth(design: dict):
    truth, weights = benchmark.truth_and_weights(design)
    return (float(truth) if truth is not None else None), weights


def result_record(design: dict, design_index: int, replicate: int, seed: int,
                  frame: pd.DataFrame, interval: dict, conditional_truth,
                  pop_truth, pop_weights: dict, independent_point, independent_ranges,
                  alpha: float) -> dict:
    support = observed_common_support(frame)
    expected = list(map(float, design["expected_support"]))
    pop_defined = pop_truth is not None
    support_match = bool(support == expected) if pop_defined else None
    support_lost = bool(pop_defined and not support_match)
    conditional_defined = conditional_truth is not None
    emitted = interval["state"] == "conditional interval computed"
    if conditional_defined != bool(support):
        raise RuntimeError("conditional truth/support inconsistency")

    if conditional_defined:
        if independent_point is None or independent_ranges is None:
            raise RuntimeError("independent point/range reconstruction missing on supported design")
        point_error = abs(float(interval["point"]) - independent_point)
        range_error = abs(float(interval["sum_squared_cluster_ranges"]) - independent_ranges)
        if point_error > 1e-12 or range_error > 1e-12:
            raise RuntimeError(
                f"helper point/range mismatch: point={point_error}, range={range_error}"
            )
        expected_halfwidth = math.sqrt(math.log(2 / alpha) * independent_ranges / 2)
        if abs(float(interval["halfwidth"]) - expected_halfwidth) > 1e-12:
            raise RuntimeError("helper Hoeffding half-width disagrees with reconstructed cluster ranges")
        expected_lower = max(-1.0, independent_point - expected_halfwidth)
        expected_upper = min(1.0, independent_point + expected_halfwidth)
        if (abs(float(interval["lower"]) - expected_lower) > 1e-12 or
                abs(float(interval["upper"]) - expected_upper) > 1e-12):
            raise RuntimeError("helper clipped endpoints disagree with fixed-design Hoeffding formula")
    else:
        point_error = range_error = 0.0

    conditional_covered = (
        bool(interval["lower"] <= conditional_truth <= interval["upper"])
        if emitted and conditional_defined else None
    )
    population_covered_diagnostic = (
        bool(interval["lower"] <= pop_truth <= interval["upper"])
        if emitted and pop_defined else None
    )
    conditional_population_difference_pp = (
        100 * (conditional_truth - pop_truth)
        if conditional_defined and pop_defined else None
    )
    return {
        "design_index": int(design_index),
        "design": design["name"],
        "family": design["family"],
        "contrast_pattern": design.get("contrast_pattern"),
        "requested_bad_score_record_mass": design.get("requested_bad_score_record_mass"),
        "actual_bad_score_record_mass": design.get("actual_bad_score_record_mass"),
        "replicate": int(replicate),
        "dataset_seed": int(seed),
        "n_records": int(len(frame)),
        "n_patients": int(frame.pid.nunique()),
        "n_observed_common_levels": len(support),
        "observed_common_support": "|".join(map(str, support)),
        "expected_population_support": "|".join(map(str, expected)),
        "conditional_truth_defined": bool(conditional_defined),
        "conditional_truth_status": "computed_on_observed_common_support" if conditional_defined else "no_observed_common_support",
        "conditional_truth_pp": 100 * conditional_truth if conditional_defined else None,
        "population_truth_defined": bool(pop_defined),
        "population_truth_pp": 100 * pop_truth if pop_defined else None,
        "population_truth_expected_weights_json": json.dumps(pop_weights, sort_keys=True),
        "population_target_support_match": support_match,
        "population_target_support_lost": support_lost if pop_defined else None,
        "conditional_minus_population_truth_pp": conditional_population_difference_pp,
        "interval_state": interval["state"],
        "conditional_interval_emitted": bool(emitted),
        "point_pp": 100 * float(interval["point"]) if emitted else None,
        "lower_pp": 100 * float(interval["lower"]) if emitted else None,
        "upper_pp": 100 * float(interval["upper"]) if emitted else None,
        "halfwidth_pp": 100 * float(interval["halfwidth"]) if emitted else None,
        "width_pp": 100 * float(interval["width"]) if emitted else None,
        "full_range_interval": bool(interval["full_range"]) if emitted else None,
        "halfwidth_ge_one": bool(interval["halfwidth_ge_one"]) if emitted else None,
        "sum_squared_cluster_ranges": float(interval["sum_squared_cluster_ranges"])
            if emitted else None,
        "n_supported_records": int(interval["n_supported_records"]),
        "n_supported_patients": int(interval["n_supported_patients"]),
        "conditional_covered": conditional_covered,
        "population_truth_covered_diagnostic": population_covered_diagnostic,
        "independent_point_abs_difference": float(point_error),
        "independent_sum_squared_ranges_abs_difference": float(range_error),
    }


def checkpoint_path(index: int, design: dict) -> Path:
    return CHECKPOINT_DIR / f"replicates_{index + 1:02d}_{design['name']}.csv"


def validate_checkpoint(path: Path, index: int, design: dict, reps: int) -> dict:
    data = pd.read_csv(path, low_memory=False)
    observed_replicates = sorted(map(int, data["replicate"].unique()))
    if len(data) != reps or observed_replicates != list(range(reps)):
        raise ValueError(
            f"{path.name} has {len(data)} rows and replicates {observed_replicates[:3]}.."
            f"{observed_replicates[-3:]}; expected {reps} rows and 0..{reps - 1}"
        )
    if set(data["design"].astype(str).unique()) != {design["name"]}:
        raise ValueError(f"{path.name} has unexpected design labels")
    return {
        "design_index": int(index),
        "design": design["name"],
        "path": str(path.relative_to(OUTPUT_DIR)),
        "rows": int(len(data)),
        "replicates": len(observed_replicates),
        "sha256": sha256(path),
    }


def _binomial_mcse(rate, n):
    if rate is None or not n:
        return None
    return float(math.sqrt(rate * (1 - rate) / n))


def summarize_design(data: pd.DataFrame, design: dict, reps: int) -> dict:
    conditional_defined = data["conditional_truth_defined"].fillna(False).astype(bool)
    emitted = data["conditional_interval_emitted"].fillna(False).astype(bool)
    cond_rows = data.loc[emitted]
    n_defined = int(conditional_defined.sum())
    n_emitted = int(emitted.sum())
    coverage = float(cond_rows["conditional_covered"].astype(bool).mean()) if n_emitted else None
    output_rate_all = n_emitted / reps
    output_rate_defined = n_emitted / n_defined if n_defined else None
    n_pop = int(data["population_truth_defined"].fillna(False).astype(bool).sum())
    pop_defined = data["population_truth_defined"].fillna(False).astype(bool)
    pop_emitted = emitted & pop_defined
    n_pop_emitted = int(pop_emitted.sum())
    pop_diag_coverage = (
        float(data.loc[pop_emitted, "population_truth_covered_diagnostic"].astype(bool).mean())
        if n_pop_emitted else None
    )
    support_match = data.loc[pop_defined, "population_target_support_match"].astype(bool)
    support_match_rate = float(support_match.mean()) if n_pop else None
    support_loss_count = int((~support_match).sum()) if n_pop else 0
    widths = cond_rows["width_pp"].dropna().to_numpy(float)
    full = cond_rows["full_range_interval"].astype(bool).to_numpy() if n_emitted else np.asarray([], dtype=bool)
    hge1 = cond_rows["halfwidth_ge_one"].astype(bool).to_numpy() if n_emitted else np.asarray([], dtype=bool)
    mismatch = data.loc[emitted & pop_defined, "conditional_minus_population_truth_pp"].dropna().to_numpy(float)
    row = {
        "design": design["name"],
        "family": design["family"],
        "contrast_pattern": design.get("contrast_pattern"),
        "requested_bad_score_record_mass": design.get("requested_bad_score_record_mass"),
        "actual_bad_score_record_mass": design.get("actual_bad_score_record_mass"),
        "n_replicates": int(reps),
        "n_conditional_truth_defined_datasets": n_defined,
        "conditional_estimand_defined_rate": n_defined / reps,
        "conditional_estimand_defined_rate_mcse": _binomial_mcse(n_defined / reps, reps),
        "n_intervals_emitted": n_emitted,
        "n_supported_datasets_withheld": n_defined - n_emitted,
        "interval_output_rate_all_datasets": output_rate_all,
        "interval_output_rate_all_datasets_mcse": _binomial_mcse(output_rate_all, reps),
        "interval_output_rate_given_conditional_estimand": output_rate_defined,
        "interval_output_rate_given_conditional_estimand_mcse": (
            _binomial_mcse(output_rate_defined, n_defined) if n_defined else None
        ),
        "n_conditional_covered": int(cond_rows["conditional_covered"].astype(bool).sum()) if n_emitted else 0,
        "conditional_coverage": coverage,
        "conditional_coverage_mcse": _binomial_mcse(coverage, n_emitted),
        "median_width_pp": float(np.median(widths)) if len(widths) else None,
        "mean_width_pp": float(np.mean(widths)) if len(widths) else None,
        "width_p05_pp": float(np.quantile(widths, 0.05)) if len(widths) else None,
        "width_p95_pp": float(np.quantile(widths, 0.95)) if len(widths) else None,
        "n_full_range_intervals": int(full.sum()),
        "full_range_rate_among_emitted": float(full.mean()) if len(full) else None,
        "full_range_rate_mcse": _binomial_mcse(float(full.mean()), len(full)) if len(full) else None,
        "n_halfwidth_ge_one": int(hge1.sum()),
        "halfwidth_ge_one_rate_among_emitted": float(hge1.mean()) if len(hge1) else None,
        "halfwidth_ge_one_rate_mcse": _binomial_mcse(float(hge1.mean()), len(hge1)) if len(hge1) else None,
        "n_population_truth_defined_datasets": n_pop,
        "population_target_support_match_rate": support_match_rate,
        "n_population_target_support_lost": support_loss_count,
        "population_target_support_loss_rate": (support_loss_count / n_pop) if n_pop else None,
        "population_target_support_loss_rate_mcse": (
            _binomial_mcse(support_loss_count / n_pop, n_pop) if n_pop else None
        ),
        "n_population_truth_interval_diagnostics": n_pop_emitted,
        "population_truth_covered_diagnostic_count": (
            int(data.loc[pop_emitted, "population_truth_covered_diagnostic"].astype(bool).sum())
            if n_pop_emitted else 0
        ),
        "population_truth_coverage_diagnostic_not_conditional_coverage": pop_diag_coverage,
        "population_truth_coverage_diagnostic_mcse": _binomial_mcse(pop_diag_coverage, n_pop_emitted),
        "mean_conditional_minus_population_truth_pp_among_emitted": (
            float(np.mean(mismatch)) if len(mismatch) else None
        ),
        "interpretation": (
            "Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval."
        ),
    }
    return row


def check_frozen_inputs(config: dict, freeze: dict) -> dict:
    expected_paths = {
        "config_builder_path": HERE / "freeze_conditional_validation.py",
        "runner_path": Path(__file__).resolve(),
        "conditional_interval_helper_path": HERE.parent / "conditional_interval.py",
        "dgp_generator_path": AUDIT_DIR / "benchmark.py",
        "source_benchmark_config_path": AUDIT_DIR / "benchmark_config.json",
    }
    hashes = {key: sha256(path.resolve()) for key, path in expected_paths.items()}
    for key, actual in hashes.items():
        frozen = freeze["code_hashes"][key]["sha256"]
        if actual != frozen:
            raise RuntimeError(f"frozen file changed after pre-outcome freeze: {key}")
    config_hash = sha256(CONFIG_PATH)
    if config_hash != freeze["config_sha256"]:
        raise RuntimeError("conditional config hash changed after freeze")
    if config.get("config_status") != "frozen_before_validation_outcomes":
        raise RuntimeError("config is not marked frozen before validation outcomes")
    if len(config["designs"]) != int(config["design_count"]):
        raise RuntimeError("config design count mismatch")
    return {**hashes, "config_sha256": config_hash}


def write_manifest(manifest: dict) -> None:
    manifest["updated_utc"] = datetime.now(timezone.utc).isoformat()
    RUN_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    frozen_hashes = check_frozen_inputs(config, freeze)
    reps = int(config["outer_replicates_per_design"])
    alpha = float(config["alpha"])
    original_dgp_path = AUDIT_DIR / "benchmark_config.json"
    original_hash = sha256(original_dgp_path)
    if original_hash != config["original_frozen_dgp"]["source_config_sha256"]:
        raise RuntimeError("original DGP config changed since conditional plan freeze")

    manifest = {
        "record_type": "conditional_design_validation_run",
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "benchmark_id": config["benchmark_id"],
        "config_path": str(CONFIG_PATH.resolve()),
        "config_sha256": frozen_hashes["config_sha256"],
        "seed": int(config["seed"]),
        "replicates_per_design": reps,
        "design_count": len(config["designs"]),
        "original_dgp_count": int(config["original_dgp_count"]),
        "fixed_design_count": int(config["fixed_design_count"]),
        "frozen_hashes": frozen_hashes,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "thread_limits": {
            name: os.environ.get(name)
            for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "checkpoints_complete": [],
        "raw_patient_records_written": False,
        "population_truth_interpretation": "Mismatch diagnostic only; conditional interval guarantee targets theta_D.",
    }
    write_manifest(manifest)
    started = time.monotonic()
    try:
        for design_index, design in enumerate(config["designs"]):
            path = checkpoint_path(design_index, design)
            if path.exists():
                info = validate_checkpoint(path, design_index, design, reps)
                manifest["checkpoints_complete"] = [
                    item for item in manifest["checkpoints_complete"]
                    if item["design"] != design["name"]
                ] + [info]
                manifest["elapsed_seconds"] = round(time.monotonic() - started, 3)
                write_manifest(manifest)
                print(f"[conditional-validation] reused {design_index + 1}/{len(config['designs'])}: {design['name']}", flush=True)
                continue

            pop_truth, pop_weights = population_truth(design)
            base_seed = int(config["seed"]) + design_index * 1_000_003
            records = []
            for replicate in range(reps):
                dataset_seed = base_seed + replicate * 10_007
                rng = np.random.default_rng(dataset_seed)
                frame = simulate_dataset(design, rng)
                conditional_truth = conditional_truth_on_observed_support(frame, design)
                interval = conditional_design_interval(frame, alpha=alpha)
                independent_point, independent_ranges = independent_point_and_range(frame)
                records.append(result_record(
                    design, design_index, replicate, dataset_seed, frame, interval,
                    conditional_truth, pop_truth, pop_weights, independent_point,
                    independent_ranges, alpha,
                ))

            data = pd.DataFrame.from_records(records)
            if len(data) != reps or sorted(map(int, data["replicate"])) != list(range(reps)):
                raise RuntimeError(f"replicate count mismatch for {design['name']}")
            fd, temporary_name = tempfile.mkstemp(
                prefix=f".{path.stem}.", suffix=".tmp", dir=CHECKPOINT_DIR
            )
            os.close(fd)
            temporary = Path(temporary_name)
            try:
                data.to_csv(temporary, index=False, encoding="utf-8")
                validate_checkpoint(temporary, design_index, design, reps)
                temporary.replace(path)
            finally:
                if temporary.exists():
                    temporary.unlink()
            info = validate_checkpoint(path, design_index, design, reps)
            manifest["checkpoints_complete"].append(info)
            manifest["elapsed_seconds"] = round(time.monotonic() - started, 3)
            write_manifest(manifest)
            print(f"[conditional-validation] completed {design_index + 1}/{len(config['designs'])}: {design['name']}; checkpoint={path.name}", flush=True)

        expected_paths = [checkpoint_path(i, design) for i, design in enumerate(config["designs"])]
        all_details = pd.concat([pd.read_csv(path, low_memory=False) for path in expected_paths],
                                ignore_index=True)
        if len(all_details) != reps * len(config["designs"]):
            raise RuntimeError("combined conditional replicate count mismatch")
        summaries = []
        for design in config["designs"]:
            data = all_details.loc[all_details.design == design["name"]]
            if len(data) != reps:
                raise RuntimeError(f"aggregate dataset count mismatch for {design['name']}")
            summaries.append(summarize_design(data, design, reps))
        replicate_path = OUTPUT_DIR / "conditional_replicate_results.csv"
        summary_path = OUTPUT_DIR / "conditional_design_summary.csv"
        all_details.to_csv(replicate_path, index=False, encoding="utf-8")
        pd.DataFrame(summaries).to_csv(summary_path, index=False, encoding="utf-8")
        manifest.update({
            "status": "complete",
            "finish_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "dataset_count": len(all_details),
            "output_files": [
                {"path": replicate_path.name, "sha256": sha256(replicate_path), "rows": len(all_details)},
                {"path": summary_path.name, "sha256": sha256(summary_path), "rows": len(summaries)},
            ],
            "point_range_validation": {
                "independent_reconstruction": "All simulated datasets; point and sum of squared patient cluster ranges independently rebuilt by NumPy.",
                "maximum_point_abs_difference": float(all_details["independent_point_abs_difference"].max()),
                "maximum_sum_squared_ranges_abs_difference": float(all_details["independent_sum_squared_ranges_abs_difference"].max()),
            },
        })
        write_manifest(manifest)
        print(f"[conditional-validation] wrote {len(summaries)} design summaries from {len(all_details)} datasets", flush=True)
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["failure"] = f"{type(exc).__name__}: {exc}"
        manifest["elapsed_seconds"] = round(time.monotonic() - started, 3)
        write_manifest(manifest)
        raise


if __name__ == "__main__":
    main()

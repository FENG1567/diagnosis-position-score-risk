#!/usr/bin/env python3
"""Create and hash the prespecified conditional-interval validation plan."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUDIT_DIR = HERE.parent / "audit"
SOURCE_CONFIG = AUDIT_DIR / "benchmark_config.json"
CONFIG_PATH = HERE / "conditional_validation_config.json"
OUTPUT_DIR = ROOT / "outputs" / "v2" / "conditional_validation"
FREEZE_PATH = OUTPUT_DIR / "pre_run_freeze.json"
SEED = 27112029
REPLICATES = 1000
PAIRED_PATIENTS_PER_GROUP = 1000
BAD_MASSES = [0.001, 0.005, 0.02, 0.10, 0.50]
CONTRASTS = ["null", "positive", "cancelling"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fixed_design(bad_mass: float, contrast: str) -> dict:
    n_per_group = PAIRED_PATIENTS_PER_GROUP
    n_bad_pooled = int(round(2 * n_per_group * bad_mass))
    n_primary_bad = 1
    n_never_bad = n_bad_pooled - n_primary_bad
    n_primary_good = n_per_group - n_primary_bad
    n_never_good = n_per_group - n_never_bad
    if min(n_primary_bad, n_never_bad, n_primary_good, n_never_good) < 1:
        raise ValueError(f"bad-mass design has an empty common-support cell: {bad_mass}")

    if contrast == "null":
        risks_primary, risks_never = [0.25, 0.25], [0.25, 0.25]
    elif contrast == "positive":
        risks_primary, risks_never = [0.25, 0.25], [0.40, 0.40]
    elif contrast == "cancelling":
        risks_primary, risks_never = [0.25, 0.40], [0.40, 0.25]
    else:
        raise ValueError(f"unknown contrast {contrast}")

    observed_mass = (n_primary_bad + n_never_bad) / (2 * n_per_group)
    name = f"fixed_badmass_{bad_mass:g}_{contrast}"
    return {
        "name": name,
        "family": "fixed_small_bad_mass",
        "dgp_type": "fixed_design_paired_patients",
        "role": "prespecified_supplement",
        "scores": [0, 1],
        "expected_support": [0, 1],
        "joint_probabilities_group_score": [
            [n_primary_good / (2 * n_per_group), n_primary_bad / (2 * n_per_group)],
            [n_never_good / (2 * n_per_group), n_never_bad / (2 * n_per_group)],
        ],
        "risks_principal": risks_primary,
        "risks_never": risks_never,
        "contrast_pattern": contrast,
        "requested_bad_score_record_mass": bad_mass,
        "actual_bad_score_record_mass": observed_mass,
        "fixed_cell_record_counts": {
            "primary_score_0": n_primary_good,
            "primary_score_1": n_primary_bad,
            "never_score_0": n_never_good,
            "never_score_1": n_never_bad,
        },
        "n_records": 2 * n_per_group,
        "n_patients": max(n_primary_good, n_never_good) + max(n_primary_bad, n_never_bad),
        "outcome_icc": 0.35,
        "cluster_structure": (
            "Within each score, pair min(n_primary, n_never) records into cross-group patient clusters; "
            "remaining records are single-record patient clusters. A patient random intercept plus "
            "record residual induces marginally calibrated Bernoulli risks."
        ),
    }


def build_config() -> dict:
    source = json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))
    original_designs = source.get("designs", [])
    if len(original_designs) != 11:
        raise ValueError(f"expected 11 frozen benchmark designs, found {len(original_designs)}")
    if int(source.get("outer_replicates_per_design", 0)) < REPLICATES:
        raise ValueError("source benchmark does not declare at least 1,000 replicates per design")
    for design in original_designs:
        joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
        if joint.shape != (2, len(design["scores"])) or not np.isclose(joint.sum(), 1.0):
            raise ValueError(f"invalid frozen DGP design: {design['name']}")

    designs = []
    for index, original in enumerate(original_designs):
        designs.append({**original, "family": "original_frozen_dgp", "design_index": index})
    for mass in BAD_MASSES:
        for contrast in CONTRASTS:
            design = _fixed_design(mass, contrast)
            design["design_index"] = len(designs)
            designs.append(design)

    return {
        "config_status": "frozen_before_validation_outcomes",
        "benchmark_id": "conditional_design_hoeffding_supplement_v1_2026-11-13",
        "amendment_timing": (
            "Exploratory amendment after eICU results had been disclosed; not part of the original frozen plan."
        ),
        "interpretation_limits": [
            "The conditional target is theta_D = E(sum_i a_i Y_i | observed complete-case design D).",
            "It is distinct from the population-weight Delta_w target when observed weights or support differ.",
            "Population-target comparisons are mismatch diagnostics, not conditional-interval coverage claims.",
            "This interval does not replace the primary C rule or any existing population-target interval.",
            "Report every prespecified design, including wide/full-range and adverse results; do not tune thresholds.",
            "Finite-sample validity requires mutually independent patient clusters conditional on D.",
        ],
        "seed": SEED,
        "outer_replicates_per_design": REPLICATES,
        "alpha": 0.05,
        "confidence_level": 0.95,
        "seed_rule": "default_rng(seed + design_index*1000003 + replicate_index*10007), indices start at zero",
        "original_frozen_dgp": {
            "source_config_path": str(SOURCE_CONFIG.resolve()),
            "source_config_sha256": sha256(SOURCE_CONFIG),
            "generator_path": str((AUDIT_DIR / "benchmark.py").resolve()),
            "design_count": 11,
            "replicates_per_design": REPLICATES,
            "generator": "benchmark.simulate_dataset, unchanged",
        },
        "fixed_design_supplement": {
            "replicates_per_design": REPLICATES,
            "n_primary_records": PAIRED_PATIENTS_PER_GROUP,
            "n_never_records": PAIRED_PATIENTS_PER_GROUP,
            "bad_score_record_masses": BAD_MASSES,
            "contrast_patterns": CONTRASTS,
            "cross_group_pairing": "Pair min(cell counts) within each score; unmatched records remain singleton clusters.",
            "outcome_icc": 0.35,
            "outcome_probability_calibration": "Gaussian random-intercept copula with exact marginal cell risks from the frozen config.",
        },
        "design_count": len(designs),
        "original_dgp_count": len(original_designs),
        "fixed_design_count": len(designs) - len(original_designs),
        "designs": designs,
        "estimands": {
            "conditional_target": (
                "For each replicate, E(sum_i a_i Y_i | D) using the actual observed common-support levels "
                "and the actual pooled-record weights on that observed support, whether or not expected support is lost."
            ),
            "population_target": (
                "Frozen DGP expected-support Delta_w; reported separately as a target-mismatch diagnostic."
            ),
        },
        "metrics": {
            "conditional_coverage": "Among emitted conditional-design intervals when observed common support is nonempty.",
            "population_truth_diagnostic": "Compare the conditional interval with population truth separately; not a coverage claim.",
            "width": "Report actual clipped interval width in percentage points, plus median/mean and quantiles.",
            "full_range": "Count intervals whose actual clipped endpoints are exactly [-1, 1].",
            "halfwidth_ge_one": "Separately count unclipped Hoeffding half-width >= 1, regardless of whether clipped endpoints are full range.",
            "support": "Report observed common-support rate, expected-support match, and target-support-loss rate.",
            "mcse": "Binomial Monte Carlo SE over independent outer replicates; coverage MCSE uses emitted intervals as denominator.",
        },
        "runtime": {
            "python": "C:\\Users\\aaa12\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
            "thread_limits": {"OPENBLAS_NUM_THREADS": 1, "OMP_NUM_THREADS": 1, "MKL_NUM_THREADS": 1},
        },
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists() or FREEZE_PATH.exists():
        raise FileExistsError("A conditional validation freeze already exists; preserve it and use a new run ID.")
    config = build_config()
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    code_paths = {
        "config_builder_path": Path(__file__).resolve(),
        "runner_path": (HERE / "run_conditional_validation.py").resolve(),
        "conditional_interval_helper_path": (HERE.parent / "conditional_interval.py").resolve(),
        "dgp_generator_path": (AUDIT_DIR / "benchmark.py").resolve(),
        "source_benchmark_config_path": SOURCE_CONFIG.resolve(),
    }
    freeze = {
        "record_type": "conditional_validation_pre_run_freeze",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config_status": config["config_status"],
        "benchmark_id": config["benchmark_id"],
        "seed": SEED,
        "replicates_per_design": REPLICATES,
        "design_count": config["design_count"],
        "original_dgp_count": config["original_dgp_count"],
        "fixed_design_count": config["fixed_design_count"],
        "config_path": str(CONFIG_PATH.resolve()),
        "config_sha256": sha256(CONFIG_PATH),
        "code_hashes": {
            key: {"path": str(path), "sha256": sha256(path)}
            for key, path in code_paths.items()
        },
        "runtime": config["runtime"],
        "outcome_generation_started": False,
        "statement": "The full 26-design configuration and all analysis choices were frozen before generating any validation outcomes.",
    }
    FREEZE_PATH.write_text(json.dumps(freeze, indent=2), encoding="utf-8")
    print(json.dumps({
        "config": str(CONFIG_PATH.resolve()),
        "freeze": str(FREEZE_PATH.resolve()),
        "config_sha256": freeze["config_sha256"],
        "design_count": freeze["design_count"],
        "original_dgp_count": freeze["original_dgp_count"],
        "fixed_design_count": freeze["fixed_design_count"],
        "seed": freeze["seed"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()

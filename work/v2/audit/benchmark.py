#!/usr/bin/env python3
"""Confirmatory paired simulation of refusal rules A/B/C plus a matched-threshold ablation D."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtri

from cohort_definition_audit import stratified_rd, stratified_rd_se, audit_v2


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "benchmark_config.json"
DEFAULT_OUTPUT = HERE.parents[2] / "outputs" / "v2" / "audit"


def load_config(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    reps = int(cfg["outer_replicates_per_design"])
    if reps < 1000:
        raise ValueError("confirmatory outer_replicates_per_design must be at least 1000")
    for design in cfg["designs"]:
        joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
        risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
        if joint.shape != risks.shape or not np.isclose(joint.sum(), 1.0):
            raise ValueError(f"invalid group-score probabilities or risks in {design['name']}")
        if np.any(joint < 0) or not np.all((risks >= 0) & (risks <= 1)):
            raise ValueError(f"invalid probabilities in {design['name']}")
        cluster_sizes = np.asarray(design["cluster_sizes"], dtype=float)
        if not np.isclose(cluster_sizes[:, 1].sum(), 1.0):
            raise ValueError(f"cluster size probabilities must sum to 1 in {design['name']}")
    return cfg


def truth_and_weights(design: dict):
    scores = np.asarray(design["scores"], dtype=float)
    levels = np.asarray(design["expected_support"], dtype=float)
    if not len(levels):
        return None, {}
    joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
    risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
    score_idx = {float(score): j for j, score in enumerate(scores)}
    js = np.asarray([joint[:, score_idx[float(level)]].sum() for level in levels], dtype=float)
    weights = js / js.sum()
    delta = np.asarray([risks[1, score_idx[float(level)]] -
                        risks[0, score_idx[float(level)]] for level in levels])
    return float(weights @ delta), {float(level): float(weight)
                                    for level, weight in zip(levels, weights)}


def conditional_observed_weight_truth(frame: pd.DataFrame, design: dict):
    """Truth conditional on this replicate's pooled record weights, only at full S* support."""
    truth, _ = truth_and_weights(design)
    if truth is None:
        return None, "no_population_estimand"
    observed = observed_support(frame)
    expected = np.asarray(design["expected_support"], dtype=float)
    if not len(observed):
        return None, "no_common_support"
    if not np.array_equal(observed, np.sort(expected)):
        return None, "target_support_lost"
    sub = frame[frame.score.isin(observed)]
    counts = sub.groupby("score").size()
    weights = counts / counts.sum()
    risk_delta = {float(score): float(design["risks_never"][j] -
                                     design["risks_principal"][j])
                  for j, score in enumerate(design["scores"])}
    conditional_truth = sum(float(weights.loc[score]) * risk_delta[float(score)]
                            for score in observed)
    return float(conditional_truth), "complete"


def simulate_dataset(design: dict, rng: np.random.Generator) -> pd.DataFrame:
    """Gaussian-copula Bernoulli outcomes with exact specified marginal risks."""
    n_patients = int(design["n_patients"])
    size_options = np.asarray([row[0] for row in design["cluster_sizes"]], dtype=int)
    size_probs = np.asarray([row[1] for row in design["cluster_sizes"]], dtype=float)
    cluster_sizes = rng.choice(size_options, size=n_patients, p=size_probs)
    patient_latent = rng.normal(size=n_patients)
    scores = np.asarray(design["scores"], dtype=float)
    joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
    risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
    cutpoints = ndtri(risks)
    rho = float(design["outcome_icc"])
    sqrt_rho = math.sqrt(rho)
    sqrt_resid = math.sqrt(1 - rho)
    pids, score_rows, groups, outcomes = [], [], [], []
    category_probs = joint.ravel()
    n_categories = len(category_probs)
    for pid, size in enumerate(cluster_sizes):
        cat = rng.choice(n_categories, size=int(size), p=category_probs)
        group = cat // len(scores)
        score_index = cat % len(scores)
        latent = sqrt_rho * patient_latent[pid] + sqrt_resid * rng.normal(size=int(size))
        y = (latent < cutpoints[group, score_index]).astype(float)
        pids.extend([pid] * int(size))
        score_rows.extend(scores[score_index].tolist())
        groups.extend(group.tolist())
        outcomes.extend(y.tolist())
    return pd.DataFrame({"pid": pids, "score": score_rows, "grp": groups, "y": outcomes})


def observed_support(frame: pd.DataFrame) -> np.ndarray:
    return np.intersect1d(frame.loc[frame.grp == 0, "score"].unique(),
                          frame.loc[frame.grp == 1, "score"].unique()).astype(float)


def interval_record(design_name: str, rep: int, policy: str, weight_mode: str,
                    rd, se, emitted: bool, reasons: list[str], frame: pd.DataFrame,
                    support_target: list[float], truth,
                    conditional_truth=None, conditional_truth_status="not computed"):
    observed = observed_support(frame)
    target = np.asarray(support_target, dtype=float)
    target_match = bool(truth is not None and np.array_equal(observed, np.sort(target)))
    point = float(rd) if rd is not None and np.isfinite(rd) else None
    se = float(se) if se is not None and np.isfinite(se) else None
    emitted = bool(emitted and point is not None and se is not None)
    lower = point - 1.96 * se if emitted else None
    upper = point + 1.96 * se if emitted else None
    contains_truth = bool(emitted and target_match and lower <= truth <= upper)
    wrong_support = bool(emitted and truth is not None and not target_match)
    missed = bool(emitted and truth is not None and (wrong_support or not contains_truth))
    coverage_eligible = bool(emitted and truth is not None and target_match)
    conditional_coverage_eligible = bool(emitted and conditional_truth is not None)
    conditional_covered = bool(conditional_coverage_eligible and
                               lower <= conditional_truth <= upper)
    return dict(
        design=design_name, replicate=int(rep), policy=policy, weight_mode=weight_mode,
        point_available=point is not None, point=point, se=se, interval_emitted=emitted,
        target_support_match=target_match, coverage_eligible=coverage_eligible,
        covered=contains_truth, unconditional_missed=missed,
        conditional_observed_weight_truth=conditional_truth,
        conditional_truth_support_status=conditional_truth_status,
        conditional_coverage_eligible=conditional_coverage_eligible,
        conditional_covered=conditional_covered,
        off_target_interval=wrong_support,
        interval_width=(upper - lower) if emitted else None,
        refusal_reasons="|".join(sorted(set(reasons))), truth=truth,
        observed_support="|".join(str(float(x)) for x in observed),
        expected_support="|".join(str(float(x)) for x in target),
    )


def fixed_weight_se(frame: pd.DataFrame, support, weights):
    return stratified_rd_se(frame.score.to_numpy(float), frame.y.to_numpy(float),
                            frame.grp.to_numpy(int), frame.pid.to_numpy(),
                            support_levels=support, fixed_weights=weights)[0]


def strategy_b(frame: pd.DataFrame, levels, minimum=10):
    for level in levels:
        for group in (0, 1):
            if int(((frame.score == level) & (frame.grp == group)).sum()) < minimum:
                return False
    return True


def strategy_d(frame: pd.DataFrame, levels, min_patients=20):
    if not len(levels):
        return False, ["no_common_support"]
    reasons = []
    for level in levels:
        for group in (0, 1):
            cell = frame[(frame.score == level) & (frame.grp == group)]
            if cell.pid.nunique() < min_patients:
                reasons.append("too_few_distinct_patients_per_score_definition_cell")
            events = float(cell.y.sum())
            if len(cell) == 0 or events <= 0 or events >= len(cell):
                reasons.append("degenerate_outcome_cell")
    return not reasons, sorted(set(reasons))


def evaluate_design(design: dict, design_index: int, cfg: dict, bootstrap_reps: int,
                    start_rep: int = 0, saved_rows: list[dict] | None = None,
                    checkpoint=None):
    truth, true_weights = truth_and_weights(design)
    support = list(map(float, design["expected_support"]))
    base_seed = int(cfg["seed"]) + design_index * 1_000_003
    rows = list(saved_rows or [])
    reps = int(cfg["outer_replicates_per_design"])
    min_record = 10
    min_patient = 20
    for rep in range(start_rep, reps):
        rng = np.random.default_rng(base_seed + rep * 10_007)
        d = simulate_dataset(design, rng)
        scores = d.score.to_numpy(float)
        outcomes = d.y.to_numpy(float)
        groups = d.grp.to_numpy(int)
        pids = d.pid.to_numpy()
        observed = observed_support(d)
        conditional_truth, conditional_status = conditional_observed_weight_truth(d, design)

        # A: no refusal rule, using the observed common-support target.
        rd_a, _, _, details_a = stratified_rd(scores, outcomes, groups)
        se_a, _ = stratified_rd_se(scores, outcomes, groups, pids)
        a_reasons = [] if np.isfinite(rd_a) and np.isfinite(se_a) else ["no_common_support"]
        rows.append(interval_record(design["name"], rep, "A", "estimated_pooled_record",
                                    rd_a, se_a, np.isfinite(rd_a) and np.isfinite(se_a),
                                    a_reasons, d, support, truth,
                                    conditional_truth, conditional_status))

        # B: the fixed >=10 records per observed score-definition cell rule.
        b_cells = support if truth is not None else observed
        b_pass = strategy_b(d, b_cells, min_record) if len(b_cells) else False
        b_reasons = [] if b_pass else (["no_common_support"] if not len(observed)
                                      else ["below_10_records_per_score_definition_cell"])
        rows.append(interval_record(design["name"], rep, "B", "estimated_pooled_record",
                                    rd_a, se_a, b_pass and np.isfinite(rd_a) and np.isfinite(se_a),
                                    b_reasons, d, support, truth,
                                    conditional_truth, conditional_status))

        # C: full audit_v2 policy, with the design's known population support fixed externally.
        c_cfg = dict(reps=bootstrap_reps, seed=base_seed + rep + 7919, min_events=10,
                     min_level_n=20, min_arm_n=10, min_clusters=20,
                     min_usable_bootstrap=20, model_check=False)
        c = audit_v2(d, expected_levels=support, config=c_cfg,
                     metadata={"semantics": "simulated principal vs non-principal record",
                               "row_unit": "admission", "cluster_unit": "patient",
                               "missingness_assumption": "none; complete simulated data"})
        # C owns only the refusal decision here. For a matched-support dataset, every
        # policy must use the same full-precision estimator and SE; audit_v2's public
        # reporting fields are rounded for display and must not drive coverage at a CI boundary.
        c_point = rd_a if np.isfinite(rd_a) else None
        c_se = se_a if np.isfinite(se_a) else None
        c_ci = c["delta_ci_pp"]
        rows.append(interval_record(design["name"], rep, "C", "estimated_pooled_record",
                                    c_point, c_se, c_ci is not None,
                                    c.get("refusal_reasons", []), d, support, truth,
                                    conditional_truth, conditional_status))

        # D: supplementary matched-threshold ablation. It uses the same 20-patient cell
        # threshold and exact nondegeneracy screen, but has no bootstrap or support-stability gate.
        d_pass, d_reasons = strategy_d(d, observed, min_patient)
        rows.append(interval_record(design["name"], rep, "D", "estimated_pooled_record",
                                    rd_a, se_a, d_pass and np.isfinite(rd_a) and np.isfinite(se_a),
                                    d_reasons, d, support, truth,
                                    conditional_truth, conditional_status))

        # Legacy comparator: same estimated-weight point estimate, fixed-observed-weight IF only.
        observed_weights = {float(row["level"]): float(row["weight"]) for row in details_a}
        se_legacy = (fixed_weight_se(d, observed, observed_weights) if len(observed) else np.nan)
        rows.append(interval_record(design["name"], rep, "A_legacy_fixed_weight_IF",
                                    "legacy_fixed_weight_variance", rd_a, se_legacy,
                                    np.isfinite(rd_a) and np.isfinite(se_legacy),
                                    a_reasons, d, support, truth,
                                    conditional_truth, conditional_status))

        # Oracle fixed-weight sensitivity: same population truth weights, estimated cell risks.
        if truth is not None:
            rd_fixed, _, _, _ = stratified_rd(scores, outcomes, groups,
                                               support_levels=support, fixed_weights=true_weights)
            se_fixed = stratified_rd_se(scores, outcomes, groups, pids,
                                        support_levels=support, fixed_weights=true_weights)[0]
            fixed_reason = [] if np.isfinite(rd_fixed) and np.isfinite(se_fixed) else ["target_support_lost"]
        else:
            rd_fixed, se_fixed, fixed_reason = np.nan, np.nan, ["no_estimand"]
        rows.append(interval_record(design["name"], rep, "A_fixed_true_weights",
                                    "fixed_population_weight_sensitivity", rd_fixed, se_fixed,
                                    np.isfinite(rd_fixed) and np.isfinite(se_fixed),
                                    fixed_reason, d, support, truth,
                                    conditional_truth=None,
                                    conditional_truth_status="not applicable to fixed-weight estimator"))
        if checkpoint and (rep + 1) % 100 == 0:
            checkpoint(rows, rep + 1)
    return rows


def _mcse_binary(rate, n):
    return math.sqrt(rate * (1 - rate) / n) if n and np.isfinite(rate) else None


def runtime_metadata():
    from importlib.metadata import PackageNotFoundError, version
    packages = {}
    for package in ("numpy", "pandas", "scipy", "statsmodels"):
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            packages[package] = None
    threads = {name: os.environ.get(name) for name in
               ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}
    return dict(executable=sys.executable, python_version=sys.version,
                python_version_short=platform.python_version(), packages=packages,
                thread_limits=threads)


def summarize_rows(rows: list[dict], n_reps: int) -> list[dict]:
    df = pd.DataFrame(rows)
    summaries = []
    for (design, policy, mode), group in df.groupby(["design", "policy", "weight_mode"], sort=False):
        emitted = group.interval_emitted.to_numpy(bool)
        on_target = group.coverage_eligible.to_numpy(bool)
        covered = group.covered.to_numpy(bool)
        conditional_eligible = group.conditional_coverage_eligible.to_numpy(bool)
        conditional_covered = group.conditional_covered.to_numpy(bool)
        misses = group.unconditional_missed.to_numpy(bool)
        emission_rate = float(emitted.mean())
        miss_rate = float(misses.mean()) if group.truth.notna().any() else np.nan
        n_eligible = int(on_target.sum())
        conditional_coverage = (float(covered[on_target].mean()) if n_eligible else np.nan)
        n_conditional = int(conditional_eligible.sum())
        conditional_observed_coverage = (float(conditional_covered[conditional_eligible].mean())
                                         if n_conditional else np.nan)
        on_target_widths = group.loc[group.coverage_eligible, "interval_width"].dropna().to_numpy(float)
        all_widths = group.loc[group.interval_emitted, "interval_width"].dropna().to_numpy(float)
        points_on_target = group.loc[group.target_support_match & group.point_available & group.truth.notna()]
        reasons = {}
        for value in group.refusal_reasons.dropna():
            for reason in str(value).split("|"):
                if reason:
                    reasons[reason] = reasons.get(reason, 0) + 1
        summaries.append(dict(
            design=design, policy=policy, weight_mode=mode, replicates=n_reps,
            point_estimate_pct=round(100 * group.point_available.mean(), 2),
            interval_emission_pct=round(100 * emission_rate, 2),
            interval_emission_mcse_pct=round(100 * _mcse_binary(emission_rate, n_reps), 3),
            target_support_match_pct=round(100 * group.target_support_match.mean(), 2),
            off_target_interval_pct=round(100 * group.off_target_interval.mean(), 2),
            conditional_coverage_pct=(round(100 * conditional_coverage, 2)
                                      if np.isfinite(conditional_coverage) else None),
            conditional_coverage_n=n_eligible,
            conditional_coverage_mcse_pct=(round(100 * _mcse_binary(conditional_coverage, n_eligible), 3)
                                           if n_eligible else None),
            conditional_observed_weight_coverage_pct=(
                round(100 * conditional_observed_coverage, 2)
                if np.isfinite(conditional_observed_coverage) else None),
            conditional_observed_weight_coverage_n=n_conditional,
            conditional_observed_weight_coverage_mcse_pct=(
                round(100 * _mcse_binary(conditional_observed_coverage, n_conditional), 3)
                if n_conditional else None),
            conditional_truth_complete_n=int(group.conditional_observed_weight_truth.notna().sum()),
            unconditional_missed_intervals=int(misses.sum()),
            unconditional_missed_pct=(round(100 * miss_rate, 2) if np.isfinite(miss_rate) else None),
            unconditional_missed_mcse_pct=(round(100 * _mcse_binary(miss_rate, n_reps), 3)
                                           if np.isfinite(miss_rate) else None),
            median_width_on_target=(round(float(np.median(on_target_widths)), 5)
                                    if len(on_target_widths) else None),
            mean_width_on_target=(round(float(np.mean(on_target_widths)), 5)
                                  if len(on_target_widths) else None),
            median_width_all_emitted=(round(float(np.median(all_widths)), 5)
                                      if len(all_widths) else None),
            mean_point_bias_on_target=(round(float((points_on_target.point -
                                                    points_on_target.truth).mean()), 6)
                                       if len(points_on_target) else None),
            refusal_counts=json.dumps(reasons, sort_keys=True),
        ))
    return summaries


def _paired_conditional_coverage(a: pd.DataFrame, b: pd.DataFrame,
                                 observed_weight_truth: bool = False):
    if observed_weight_truth:
        eligible_column = "conditional_coverage_eligible"
        covered_column = "conditional_covered"
        truth_column = "conditional_observed_weight_truth"
    else:
        eligible_column = "coverage_eligible"
        covered_column = "covered"
        truth_column = "truth"
    if not a[truth_column].notna().any() or not b[truth_column].notna().any():
        return None, None, 0
    ea = a[eligible_column].to_numpy(float)
    eb = b[eligible_column].to_numpy(float)
    ca = a[covered_column].to_numpy(float)
    cb = b[covered_column].to_numpy(float)
    na, nb = ea.sum(), eb.sum()
    if not na or not nb:
        return None, None, 0
    ta, tb = ca.sum() / na, cb.sum() / nb
    qa, qb = na / len(ea), nb / len(eb)
    influence_difference = (ca - ta * ea) / qa - (cb - tb * eb) / qb
    se = float(np.std(influence_difference, ddof=1) / math.sqrt(len(ea)))
    return float(ta - tb), se, int(min(na, nb))


def paired_comparisons(rows: list[dict]):
    df = pd.DataFrame(rows)
    pairs = [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("A", "D"),
             ("A", "A_legacy_fixed_weight_IF")]
    output = []
    for design, block in df.groupby("design", sort=False):
        by_policy = {policy: sub.sort_values("replicate")
                     for (policy, mode), sub in block.groupby(["policy", "weight_mode"], sort=False)
                     if policy in {p for pair in pairs for p in pair}}
        for policy_a, policy_b in pairs:
            if policy_a not in by_policy or policy_b not in by_policy:
                continue
            a, b = by_policy[policy_a].reset_index(drop=True), by_policy[policy_b].reset_index(drop=True)
            if len(a) != len(b) or not np.array_equal(a.replicate, b.replicate):
                raise ValueError(f"paired replicate mismatch for {design}: {policy_a} vs {policy_b}")
            emit_difference = a.interval_emitted.to_numpy(float) - b.interval_emitted.to_numpy(float)
            emission_diff = float(emit_difference.mean())
            emission_se = float(np.std(emit_difference, ddof=1) / math.sqrt(len(a)))
            if a.truth.notna().any():
                miss_difference = (a.unconditional_missed.to_numpy(float) -
                                   b.unconditional_missed.to_numpy(float))
                miss_diff = float(miss_difference.mean())
                miss_se = float(np.std(miss_difference, ddof=1) / math.sqrt(len(a)))
            else:
                miss_diff = miss_se = None
            cov_diff, cov_se, cov_n = _paired_conditional_coverage(a, b)
            observed_weight_cov_diff, observed_weight_cov_se, observed_weight_cov_n = (
                _paired_conditional_coverage(a, b, observed_weight_truth=True))
            both_width = a.coverage_eligible.to_numpy(bool) & b.coverage_eligible.to_numpy(bool)
            width_difference = (a.loc[both_width, "interval_width"].to_numpy(float) -
                                b.loc[both_width, "interval_width"].to_numpy(float))
            output.append(dict(
                design=design, first_policy=policy_a, second_policy=policy_b,
                contrast="first minus second", paired_replicates=len(a),
                emission_difference=emission_diff, emission_difference_mcse=emission_se,
                unconditional_miss_difference=miss_diff,
                unconditional_miss_difference_mcse=miss_se,
                conditional_coverage_difference=cov_diff,
                conditional_coverage_difference_mcse=cov_se,
                paired_coverage_n_min=cov_n,
                conditional_observed_weight_coverage_difference=observed_weight_cov_diff,
                conditional_observed_weight_coverage_difference_mcse=observed_weight_cov_se,
                paired_conditional_observed_weight_n_min=observed_weight_cov_n,
                mean_width_difference_on_jointly_emitted=(float(width_difference.mean())
                                                          if len(width_difference) else None),
                mean_width_difference_mcse=(float(np.std(width_difference, ddof=1) /
                                                  math.sqrt(len(width_difference)))
                                            if len(width_difference) > 1 else None),
                width_joint_n=int(len(width_difference)),
            ))
    return output


def run(config_path: Path, output_dir: Path, bootstrap_reps: int | None = None):
    config_path = config_path.resolve()
    raw = config_path.read_bytes()
    cfg = load_config(config_path)
    bootstrap_reps = int(bootstrap_reps or cfg["bootstrap_gate"]["replicates_per_eligible_C_dataset"])
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes = {
        "config_sha256": hashlib.sha256(raw).hexdigest(),
        "benchmark_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "audit_tool_sha256": hashlib.sha256((HERE / "cohort_definition_audit.py").read_bytes()).hexdigest(),
    }
    state_path = output_dir / "benchmark_run_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("hashes") != hashes:
            raise RuntimeError("existing benchmark state has different config or source hashes; refusing to resume")
        if int(state.get("bootstrap_replicates_per_eligible_C_dataset", -1)) != bootstrap_reps:
            raise RuntimeError("existing benchmark state has a different C bootstrap count; refusing to resume")
        if state.get("status") == "complete":
            raise RuntimeError("this frozen benchmark is already complete; choose a new output directory to rerun")
    else:
        state = dict(benchmark_id=cfg["benchmark_id"], status="running", hashes=hashes,
                     start_timestamp_utc=datetime.now(timezone.utc).isoformat(),
                     runtime=runtime_metadata(),
                     seed=cfg["seed"], outer_replicates_per_design=cfg["outer_replicates_per_design"],
                     bootstrap_replicates_per_eligible_C_dataset=bootstrap_reps,
                     completed_designs=[], segment_hashes={}, current_design=None,
                     last_completed_replicate=None)
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    rows = []
    completed = set(state.get("completed_designs", []))
    current_design = state.get("current_design")
    for index, design in enumerate(cfg["designs"]):
        name = design["name"]
        final_segment = output_dir / f"benchmark_replicates_{name}.csv"
        partial_segment = output_dir / f"benchmark_partial_{name}.csv"
        if name in completed:
            if not final_segment.exists():
                raise RuntimeError(f"missing completed segment for {name}")
            segment = pd.read_csv(final_segment).to_dict(orient="records")
            actual_hash = hashlib.sha256(final_segment.read_bytes()).hexdigest()
            if state["segment_hashes"].get(name) != actual_hash:
                raise RuntimeError(f"completed segment hash mismatch for {name}")
            rows.extend(segment)
            continue

        saved_rows = []
        start_rep = 0
        if current_design == name and partial_segment.exists():
            partial_hash = hashlib.sha256(partial_segment.read_bytes()).hexdigest()
            if state.get("partial_sha256") != partial_hash:
                raise RuntimeError(f"partial segment hash mismatch for {name}")
            saved_rows = pd.read_csv(partial_segment).to_dict(orient="records")
            start_rep = int(state.get("last_completed_replicate", 0))
        state["current_design"] = name
        state["last_completed_replicate"] = start_rep
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

        def checkpoint(segment_rows, next_rep):
            temp_path = output_dir / f"benchmark_partial_{name}.tmp"
            pd.DataFrame(segment_rows).to_csv(temp_path, index=False)
            os.replace(temp_path, partial_segment)
            state["current_design"] = name
            state["last_completed_replicate"] = next_rep
            state["partial_sha256"] = hashlib.sha256(partial_segment.read_bytes()).hexdigest()
            state["updated_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            print(f"[benchmark] {name}: saved through replicate {next_rep}/{cfg['outer_replicates_per_design']}",
                  flush=True)

        segment_rows = evaluate_design(design, index, cfg, bootstrap_reps,
                                       start_rep=start_rep, saved_rows=saved_rows,
                                       checkpoint=checkpoint)
        temp_final = output_dir / f"benchmark_replicates_{name}.tmp"
        pd.DataFrame(segment_rows).to_csv(temp_final, index=False)
        os.replace(temp_final, final_segment)
        if partial_segment.exists():
            partial_segment.unlink()
        state["completed_designs"] = list(state.get("completed_designs", [])) + [name]
        state["segment_hashes"][name] = hashlib.sha256(final_segment.read_bytes()).hexdigest()
        state.pop("partial_sha256", None)
        state["current_design"] = None
        state["last_completed_replicate"] = None
        state["updated_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        rows.extend(segment_rows)
        print(f"[benchmark] completed {name} ({index + 1}/{len(cfg['designs'])})", flush=True)

    summary = summarize_rows(rows, int(cfg["outer_replicates_per_design"]))
    paired = paired_comparisons(rows)
    summary_path = output_dir / "benchmark_summary.csv"
    paired_path = output_dir / "benchmark_paired_comparisons.csv"
    replicate_path = output_dir / "benchmark_replicate_metrics.csv"
    pd.DataFrame(summary).to_csv(summary_path, index=False)
    pd.DataFrame(paired).to_csv(paired_path, index=False)
    pd.DataFrame(rows).to_csv(replicate_path, index=False)
    manifest = dict(
        benchmark_id=cfg["benchmark_id"],
        output_schema_version=cfg.get("output_schema_version", 1),
        hashes=hashes,
        runtime=state["runtime"],
        config_path=str(config_path), output_directory=str(output_dir.resolve()),
        outer_replicates_per_design=cfg["outer_replicates_per_design"],
        bootstrap_replicates_per_eligible_C_dataset=bootstrap_reps,
        seed=cfg["seed"], designs=[d["name"] for d in cfg["designs"]],
        start_timestamp_utc=state["start_timestamp_utc"],
        finish_timestamp_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=round(time.time() - datetime.fromisoformat(state["start_timestamp_utc"]).timestamp(), 3),
        outputs=[summary_path.name, paired_path.name, replicate_path.name],
        raw_patient_records_written=False,
    )
    (output_dir / "benchmark_run_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    state["status"] = "complete"
    state["finish_timestamp_utc"] = manifest["finish_timestamp_utc"]
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(pd.DataFrame(summary).to_string(index=False), flush=True)
    print(f"[benchmark] wrote outputs to {output_dir.resolve()}", flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-reps", type=int, default=None,
                        help="override only for smoke/runtime checks; confirmatory default is frozen config")
    parser.add_argument("--dry-run", action="store_true", help="validate the frozen config without generating outcomes")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.dry_run:
        print(json.dumps({"benchmark_id": cfg["benchmark_id"],
                          "designs": len(cfg["designs"]),
                          "outer_replicates_per_design": cfg["outer_replicates_per_design"],
                          "total_outer_datasets": len(cfg["designs"]) * cfg["outer_replicates_per_design"],
                          "seed": cfg["seed"]}, indent=2))
        return 0
    run(args.config, args.output_dir, args.bootstrap_reps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fit the approved v3 score maps and run aggregate-only clustered validation.

Patient/admission identifiers are held in memory only. Every persisted artifact
contains aggregate counts, model coefficients, score-level risks, or metrics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

for _thread_var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_var] = "1"

import numpy as np
import scipy
import statsmodels
import statsmodels.api as sm

import count_eligibility as eligibility


BOOTSTRAP_REPS = 2000
MIN_TRAIN_EVENTS = 50
MIN_TRAIN_NONEVENTS = 50
MIN_ROLE_PATIENTS = 200
MIN_ROLE_EVENTS = 100
MIN_ROLE_NONEVENTS = 100
MIN_SUBGROUP_EVENTS = 20
MIN_SUBGROUP_NONEVENTS = 20
MIN_SUBGROUP_PATIENTS = 200
MIN_BOOTSTRAP_FRACTION = 0.95
MIN_HOSPITALS_FOR_SENSITIVITY = 20
MAP_NAMES = (
    "primary_only_fixed",
    "broad_fixed",
    "primary_only_recalibrated",
    "broad_recalibrated",
)
LOSS_NAMES = ("brier", "log_loss")
GROUPS = ("all", "primary", "never_primary")
CONTRASTS = (
    ("primary_fixed_minus_broad_fixed", "primary_only_fixed", "broad_fixed"),
    ("primary_recalibrated_minus_broad_recalibrated", "primary_only_recalibrated", "broad_recalibrated"),
    ("primary_recalibrated_minus_fixed", "primary_only_recalibrated", "primary_only_fixed"),
    ("broad_recalibrated_minus_fixed", "broad_recalibrated", "broad_fixed"),
)
DEFAULT_EICU = eligibility.DEFAULT_EICU
DEFAULT_MIMIC = eligibility.DEFAULT_MIMIC
DEFAULT_OUT = eligibility.DEFAULT_OUT


class FitFailure(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_seed(*parts: str) -> int:
    payload = "|".join((eligibility.SEED, "bootstrap", *parts)).encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest()[:16], 16)


def expit(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def log1pexp(value: float) -> float:
    if value > 0:
        return value + math.log1p(math.exp(-value))
    return math.log1p(math.exp(value))


def quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    fraction = position - lo
    return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction


def cohort_counts(records: list[dict[str, object]]) -> dict[str, int]:
    return {
        "records": len(records),
        "events": sum(int(row["outcome"]) for row in records),
        "nonevents": sum(1 - int(row["outcome"]) for row in records),
        "patients": len({str(row["pid"]) for row in records}),
        "event_patients": len({str(row["pid"]) for row in records if row["outcome"] == 1}),
        "nonevent_patients": len({str(row["pid"]) for row in records if row["outcome"] == 0}),
        "admissions": len({str(row["admission_id"]) for row in records}),
        "hospitals": len({str(row["hospital"]) for row in records if row["hospital"] is not None}),
    }


def required_role_gate(counts: dict[str, int], events: int, nonevents: int) -> tuple[bool, str]:
    failures = []
    if counts["events"] < events:
        failures.append(f"events<{events}")
    if counts["nonevents"] < nonevents:
        failures.append(f"nonevents<{nonevents}")
    if counts["patients"] < MIN_ROLE_PATIENTS:
        failures.append(f"patients<{MIN_ROLE_PATIENTS}")
    return (not failures, "pass" if not failures else ";".join(failures))


def subgroup_gate(counts: dict[str, int]) -> tuple[bool, str]:
    failures = []
    if counts["events"] < MIN_SUBGROUP_EVENTS:
        failures.append(f"events<{MIN_SUBGROUP_EVENTS}")
    if counts["nonevents"] < MIN_SUBGROUP_NONEVENTS:
        failures.append(f"nonevents<{MIN_SUBGROUP_NONEVENTS}")
    if counts["patients"] < MIN_SUBGROUP_PATIENTS:
        failures.append(f"patients<{MIN_SUBGROUP_PATIENTS}")
    return (not failures, "pass" if not failures else ";".join(failures))


def grouped_stats(records: list[dict[str, object]], x_getter) -> dict[float, tuple[int, int]]:
    counts: dict[float, list[int]] = defaultdict(lambda: [0, 0])
    for row in records:
        x_value = float(x_getter(row))
        y_value = int(row["outcome"])
        counts[x_value][0] += 1
        counts[x_value][1] += y_value
    return {x: (values[0], values[1]) for x, values in counts.items()}


def separated(stats: dict[float, tuple[int, int]]) -> bool:
    event_x = [x for x, (n, events) in stats.items() if events > 0]
    nonevent_x = [x for x, (n, events) in stats.items() if events < n]
    if not event_x or not nonevent_x:
        return True
    # Equality at the shared boundary is quasi-complete separation: the MLE can
    # diverge while leaving boundary observations at an interior fitted risk.
    return max(nonevent_x) <= min(event_x) or max(event_x) <= min(nonevent_x)


def fit_logistic(records: list[dict[str, object]], x_getter, label: str) -> dict[str, object]:
    stats = grouped_stats(records, x_getter)
    if len(stats) < 2:
        raise FitFailure(f"{label}: nonconstant predictor unavailable")
    n = sum(v[0] for v in stats.values())
    events = sum(v[1] for v in stats.values())
    if events == 0 or events == n:
        raise FitFailure(f"{label}: single outcome class")
    if separated(stats):
        raise FitFailure(f"{label}: complete separation")
    x_values = np.asarray([float(x_getter(row)) for row in records], dtype=float)
    y_values = np.asarray([int(row["outcome"]) for row in records], dtype=float)
    design = np.column_stack((np.ones(len(records), dtype=float), x_values))
    try:
        result = sm.GLM(y_values, design, family=sm.families.Binomial()).fit(maxiter=100, tol=1e-9, disp=0)
    except Exception as exc:
        raise FitFailure(f"{label}: statsmodels GLM failed ({type(exc).__name__})") from exc
    params = np.asarray(result.params, dtype=float)
    if not bool(result.converged):
        raise FitFailure(f"{label}: statsmodels GLM did not converge")
    if params.size != 2 or not np.isfinite(params).all() or not math.isfinite(float(result.llf)):
        raise FitFailure(f"{label}: nonfinite MLE")
    return {
        "beta0": float(params[0]),
        "beta1": float(params[1]),
        "log_likelihood": float(result.llf),
        "iterations": result.fit_history.get("iteration"),
    }


def fit_offset_intercept(records: list[dict[str, object]], eta_getter, label: str) -> dict[str, object]:
    events = sum(int(row["outcome"]) for row in records)
    nonevents = len(records) - events
    if events == 0 or nonevents == 0:
        raise FitFailure(f"{label}: one outcome class")
    y_values = np.asarray([int(row["outcome"]) for row in records], dtype=float)
    offset = np.asarray([float(eta_getter(row)) for row in records], dtype=float)
    if not np.isfinite(offset).all():
        raise FitFailure(f"{label}: nonfinite offset")
    try:
        result = sm.GLM(
            y_values,
            np.ones((len(records), 1), dtype=float),
            family=sm.families.Binomial(),
            offset=offset,
        ).fit(maxiter=100, tol=1e-9, disp=0)
    except Exception as exc:
        raise FitFailure(f"{label}: offset GLM failed ({type(exc).__name__})") from exc
    estimate = float(np.asarray(result.params, dtype=float)[0])
    if not bool(result.converged) or not math.isfinite(estimate):
        raise FitFailure(f"{label}: offset GLM did not converge to a finite estimate")
    return {"delta": estimate, "iterations": result.fit_history.get("iteration")}


def auc_from_eta(records: list[dict[str, object]], eta_getter) -> float | None:
    grouped: dict[float, list[int]] = defaultdict(lambda: [0, 0])
    for row in records:
        grouped[float(eta_getter(row))][int(row["outcome"])] += 1
    total_events = sum(counts[1] for counts in grouped.values())
    total_nonevents = sum(counts[0] for counts in grouped.values())
    if total_events == 0 or total_nonevents == 0:
        return None
    concordant = cumulative_nonevents = 0.0
    for _, (nonevents, events) in sorted(grouped.items()):
        concordant += events * (cumulative_nonevents + 0.5 * nonevents)
        cumulative_nonevents += nonevents
    return concordant / (total_events * total_nonevents)


def point_losses(records: list[dict[str, object]], eta_getter) -> dict[str, float]:
    n = len(records)
    if n == 0:
        return {"brier": math.nan, "log_loss": math.nan}
    brier_sum = log_loss_sum = 0.0
    for row in records:
        eta = float(eta_getter(row))
        outcome = int(row["outcome"])
        probability = expit(eta)
        brier_sum += (probability - outcome) ** 2
        log_loss_sum += log1pexp(eta) - outcome * eta
    return {"brier": brier_sum / n, "log_loss": log_loss_sum / n}


def check_role_disjointness(rows: list[dict[str, object]], database: str) -> dict[str, int]:
    patient_roles: dict[str, set[str]] = defaultdict(set)
    patient_hospitals: dict[str, set[str]] = defaultdict(set)
    hospital_roles: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        role = row["role"]
        if role not in eligibility.ROLES:
            continue
        if row["pid"] is not None:
            patient_roles[str(row["pid"])].add(str(role))
        if database == "eICU" and row["hospital"] is not None:
            hospital_roles[str(row["hospital"])].add(str(role))
            if row["pid"] is not None:
                patient_hospitals[str(row["pid"])].add(str(row["hospital"]))
    patient_overlap = sum(len(roles) > 1 for roles in patient_roles.values())
    hospital_overlap = sum(len(roles) > 1 for roles in hospital_roles.values())
    multihospital_overlap = sum(len(hospitals) > 1 for hospitals in patient_hospitals.values())
    if patient_overlap or hospital_overlap or multihospital_overlap:
        raise RuntimeError(
            f"{database} aggregate split assertion failed: patient_role_overlap={patient_overlap}, "
            f"hospital_role_overlap={hospital_overlap}, multihospital_patient_overlap={multihospital_overlap}"
        )
    return {
        "patient_role_overlap": patient_overlap,
        "hospital_role_overlap": hospital_overlap,
        "multihospital_patient_overlap": multihospital_overlap,
    }


def test_groups(records: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    return {
        "all": records,
        "primary": [row for row in records if row["group"] == 0],
        "never_primary": [row for row in records if row["group"] == 1],
    }


def map_eta(model: dict[str, object], score: int, delta: float = 0.0) -> float:
    return float(model["beta0"]) + float(model["beta1"]) * score + delta


def patient_bootstrap(test_records: list[dict[str, object]], database: str, disease: str):
    patient_data: dict[str, dict[str, object]] = defaultdict(lambda: {
        group: {"n": 0, "sums": {name: {loss: 0.0 for loss in LOSS_NAMES} for name in MAP_NAMES}}
        for group in GROUPS
    })
    for row in test_records:
        pid = str(row["pid"])
        y = int(row["outcome"])
        memberships = ["all"] + (["primary"] if row["group"] == 0 else ["never_primary"])
        for group in memberships:
            target = patient_data[pid][group]
            target["n"] += 1
            for map_name in MAP_NAMES:
                eta = float(row["etas"][map_name])
                probability = expit(eta)
                target["sums"][map_name]["brier"] += (probability - y) ** 2
                target["sums"][map_name]["log_loss"] += log1pexp(eta) - y * eta

    patients = sorted(patient_data)
    if not patients:
        empty_metric = {group: {name: {loss: [] for loss in LOSS_NAMES} for name in MAP_NAMES} for group in GROUPS}
        empty_contrast = {group: {name: {loss: [] for loss in LOSS_NAMES} for name, _, _ in CONTRASTS} for group in GROUPS}
        return {"metric_draws": empty_metric, "contrast_draws": empty_contrast,
                "usable": {group: 0 for group in GROUPS}, "failures": {group: BOOTSTRAP_REPS for group in GROUPS},
                "rng_seed": stable_seed(database, disease, "patient")}
    rng_seed = stable_seed(database, disease, "patient")
    rng = np.random.default_rng(rng_seed)
    probabilities = np.full(len(patients), 1.0 / len(patients), dtype=float)
    probabilities /= probabilities.sum()
    # Multinomial counts are exactly the multiplicities from drawing n patients
    # with replacement; the same matrix is reused for every map and test group.
    draw_matrix = rng.multinomial(len(patients), probabilities, size=BOOTSTRAP_REPS)
    draws = {
        group: {map_name: {loss: [] for loss in LOSS_NAMES} for map_name in MAP_NAMES}
        for group in GROUPS
    }
    contrast_draws = {
        group: {name: {loss: [] for loss in LOSS_NAMES} for name, _, _ in CONTRASTS}
        for group in GROUPS
    }
    failures: dict[str, int] = {}
    usable: dict[str, int] = {}
    for group in GROUPS:
        denominators_by_patient = np.asarray([patient_data[pid][group]["n"] for pid in patients], dtype=float)
        denominator = draw_matrix @ denominators_by_patient
        valid = denominator > 0
        usable[group] = int(valid.sum())
        failures[group] = BOOTSTRAP_REPS - usable[group]
        if not valid.any():
            continue
        map_means: dict[str, dict[str, np.ndarray]] = {name: {} for name in MAP_NAMES}
        for map_name in MAP_NAMES:
            for loss in LOSS_NAMES:
                patient_sums = np.asarray(
                    [patient_data[pid][group]["sums"][map_name][loss] for pid in patients], dtype=float
                )
                means = (draw_matrix[valid] @ patient_sums) / denominator[valid]
                map_means[map_name][loss] = means
                draws[group][map_name][loss] = means.tolist()
        for contrast, left, right in CONTRASTS:
            for loss in LOSS_NAMES:
                contrast_draws[group][contrast][loss] = (
                    map_means[left][loss] - map_means[right][loss]
                ).tolist()
    return {
        "metric_draws": draws,
        "contrast_draws": contrast_draws,
        "usable": usable,
        "failures": failures,
        "rng_seed": rng_seed,
    }


def hospital_bootstrap(test_records: list[dict[str, object]], disease: str):
    hospitals: dict[str, dict[str, object]] = defaultdict(lambda: {
        "n": 0, "sums": {name: {loss: 0.0 for loss in LOSS_NAMES} for name in MAP_NAMES}
    })
    for row in test_records:
        hospital = row["hospital"]
        if hospital is None:
            continue
        aggregate = hospitals[str(hospital)]
        aggregate["n"] += 1
        y = int(row["outcome"])
        for map_name in MAP_NAMES:
            eta = float(row["etas"][map_name])
            probability = expit(eta)
            aggregate["sums"][map_name]["brier"] += (probability - y) ** 2
            aggregate["sums"][map_name]["log_loss"] += log1pexp(eta) - y * eta
    hospital_ids = sorted(hospitals)
    if len(hospital_ids) < MIN_HOSPITALS_FOR_SENSITIVITY:
        return {"state": "unavailable_fewer_than_20_test_hospitals", "hospitals": len(hospital_ids)}

    rng_seed = stable_seed("eICU", disease, "hospital")
    rng = np.random.default_rng(rng_seed)
    probabilities = np.full(len(hospital_ids), 1.0 / len(hospital_ids), dtype=float)
    probabilities /= probabilities.sum()
    draw_matrix = rng.multinomial(len(hospital_ids), probabilities, size=BOOTSTRAP_REPS)
    draws = {name: {loss: [] for loss in LOSS_NAMES} for name, _, _ in CONTRASTS}
    denominator_by_hospital = np.asarray([hospitals[hospital]["n"] for hospital in hospital_ids], dtype=float)
    denominator = draw_matrix @ denominator_by_hospital
    valid = denominator > 0
    map_means: dict[str, dict[str, np.ndarray]] = {name: {} for name in MAP_NAMES}
    for map_name in MAP_NAMES:
        for loss in LOSS_NAMES:
            hospital_sums = np.asarray(
                [hospitals[hospital]["sums"][map_name][loss] for hospital in hospital_ids], dtype=float
            )
            means = (draw_matrix[valid] @ hospital_sums) / denominator[valid]
            map_means[map_name][loss] = means
    for contrast, left, right in CONTRASTS:
        for loss in LOSS_NAMES:
            draws[contrast][loss] = (map_means[left][loss] - map_means[right][loss]).tolist()
    failures = BOOTSTRAP_REPS - int(valid.sum())
    return {
        "state": "computed" if BOOTSTRAP_REPS - failures >= MIN_BOOTSTRAP_FRACTION * BOOTSTRAP_REPS else "withheld_lt_95pct_usable",
        "hospitals": len(hospital_ids),
        "usable": BOOTSTRAP_REPS - failures,
        "failures": failures,
        "rng_seed": rng_seed,
        "draws": draws,
    }


def build_metric_rows(database: str, disease: str, records: list[dict[str, object]],
                      models: dict[str, dict[str, object]], deltas: dict[str, float],
                      bootstrap: dict[str, object]):
    rows = []
    for group, group_rows in test_groups(records).items():
        counts = cohort_counts(group_rows)
        gate_ok, gate_reason = (required_role_gate(counts, MIN_ROLE_EVENTS, MIN_ROLE_NONEVENTS)
                                if group == "all" else subgroup_gate(counts))
        for map_name in MAP_NAMES:
            if map_name == "primary_only_fixed":
                model_key, delta = "primary_only", 0.0
            elif map_name == "broad_fixed":
                model_key, delta = "broad", 0.0
            elif map_name == "primary_only_recalibrated":
                model_key, delta = "primary_only", deltas.get("primary_only", math.nan)
            else:
                model_key, delta = "broad", deltas.get("broad", math.nan)
            if not math.isfinite(delta):
                continue
            eta_getter = lambda row, m=models[model_key], d=delta: map_eta(m, int(row["score"]), d)
            losses = point_losses(group_rows, eta_getter)
            observed = counts["events"] / counts["records"] if counts["records"] else math.nan
            mean_predicted = (
                sum(expit(eta_getter(row)) for row in group_rows) / len(group_rows)
                if group_rows else math.nan
            )
            citl = calibration_slope = calibration_model_intercept = None
            diagnostic_state = "below_gate_point_only" if not gate_ok else "not_estimable"
            if group_rows and gate_ok:
                etas = [eta_getter(row) for row in group_rows]
                if all(math.isfinite(value) for value in etas) and len(set(etas)) > 1:
                    try:
                        offset = fit_offset_intercept(group_rows, eta_getter, f"{database}/{disease}/{group}/{map_name}/citl")
                        slope = fit_logistic(
                            group_rows,
                            lambda row, get=eta_getter: get(row),
                            f"{database}/{disease}/{group}/{map_name}/calibration_slope",
                        )
                        citl = offset["delta"]
                        calibration_slope = slope["beta1"]
                        calibration_model_intercept = slope["beta0"]
                        diagnostic_state = "point_estimates_only"
                    except FitFailure as exc:
                        diagnostic_state = f"not_estimable:{exc}"
                else:
                    diagnostic_state = "not_estimable:constant_or_nonfinite_linear_predictor"
            auc = auc_from_eta(group_rows, eta_getter) if group_rows else None
            metric_draws = bootstrap.get("metric_draws", {}).get(group, {}).get(map_name, {})
            usable = bootstrap.get("usable", {}).get(group, 0)
            ci_ok = gate_ok and usable >= MIN_BOOTSTRAP_FRACTION * BOOTSTRAP_REPS
            row = {
                "database": database,
                "disease": disease,
                "test_group": group,
                "prediction": map_name,
                **counts,
                "observed_risk": observed,
                "mean_predicted_risk": mean_predicted,
                "brier": losses["brier"],
                "brier_ci_low": quantile(metric_draws.get("brier", []), 0.025) if ci_ok else None,
                "brier_ci_high": quantile(metric_draws.get("brier", []), 0.975) if ci_ok else None,
                "log_loss": losses["log_loss"],
                "log_loss_ci_low": quantile(metric_draws.get("log_loss", []), 0.025) if ci_ok else None,
                "log_loss_ci_high": quantile(metric_draws.get("log_loss", []), 0.975) if ci_ok else None,
                "auc_descriptive": auc,
                "calibration_in_large": citl,
                "calibration_slope": calibration_slope,
                "calibration_model_intercept": calibration_model_intercept,
                "calibration_state": diagnostic_state,
                "test_gate": gate_reason,
                "bootstrap_usable": usable,
                "bootstrap_failed": bootstrap.get("failures", {}).get(group, 0),
                "bootstrap_ci_state": "pointwise_95pct" if ci_ok else ("below_gate" if not gate_ok else "withheld_lt_95pct_usable"),
                "recalibration_delta": deltas.get(model_key) if "recalibrated" in map_name else 0.0,
            }
            rows.append(row)
    return rows


def build_contrast_rows(database: str, disease: str, records: list[dict[str, object]],
                        metric_rows: list[dict[str, object]], bootstrap: dict[str, object],
                        hospital: dict[str, object] | None = None):
    rows = []
    by_key = {(row["test_group"], row["prediction"]): row for row in metric_rows}
    for group in GROUPS:
        for contrast, left, right in CONTRASTS:
            left_row, right_row = by_key.get((group, left)), by_key.get((group, right))
            for loss in LOSS_NAMES:
                if left_row and right_row:
                    point = float(left_row[loss]) - float(right_row[loss])
                else:
                    point = None
                gate_ok = bool(left_row and right_row and left_row["test_gate"] == "pass")
                draws = bootstrap.get("contrast_draws", {}).get(group, {}).get(contrast, {}).get(loss, [])
                usable = len(draws)
                state = "point_only_below_gate" if not gate_ok else (
                    "pointwise_95pct" if usable >= MIN_BOOTSTRAP_FRACTION * BOOTSTRAP_REPS else "withheld_lt_95pct_usable"
                )
                rows.append({
                    "database": database,
                    "disease": disease,
                    "test_group": group,
                    "contrast": contrast,
                    "loss": loss,
                    "difference": point,
                    "ci_low": quantile(draws, 0.025) if state == "pointwise_95pct" else None,
                    "ci_high": quantile(draws, 0.975) if state == "pointwise_95pct" else None,
                    "bootstrap_usable": usable,
                    "bootstrap_failed": BOOTSTRAP_REPS - usable if gate_ok else 0,
                    "interval_state": state,
                    "direction_note": "primary-only minus broad: positive favors broad; recalibrated minus fixed: negative means lower loss",
                })
    if hospital is not None:
        for contrast, left, right in CONTRASTS:
            for loss in LOSS_NAMES:
                draws = hospital.get("draws", {}).get(contrast, {}).get(loss, [])
                point_rows = {(row["test_group"], row["prediction"]): row for row in metric_rows}
                left_row, right_row = point_rows.get(("all", left)), point_rows.get(("all", right))
                point = float(left_row[loss]) - float(right_row[loss]) if left_row and right_row else None
                interval_state = hospital.get("state", "unavailable")
                can_report = interval_state == "computed" and len(draws) >= MIN_BOOTSTRAP_FRACTION * BOOTSTRAP_REPS
                rows.append({
                    "database": database,
                    "disease": disease,
                    "test_group": "all",
                    "contrast": contrast,
                    "loss": loss,
                    "difference": point,
                    "ci_low": quantile(draws, 0.025) if can_report else None,
                    "ci_high": quantile(draws, 0.975) if can_report else None,
                    "bootstrap_usable": hospital.get("usable", 0),
                    "bootstrap_failed": hospital.get("failures", 0),
                    "interval_state": "hospital_cluster_pointwise_95pct" if can_report else interval_state,
                    "cluster_count": hospital.get("hospitals", 0),
                    "direction_note": "hospital-cluster sensitivity; record-weighted; primary-only minus broad positive favors broad",
                })
    return rows


def score_table(database: str, disease: str, records: list[dict[str, object]], models: dict[str, dict[str, object]], deltas: dict[str, float]):
    rows = []
    scores = sorted({int(row["score"]) for row in records})
    for group in GROUPS:
        for score in scores:
            selected = [row for row in records if int(row["score"]) == score and
                        (group == "all" or (group == "primary" and row["group"] == 0) or
                         (group == "never_primary" and row["group"] == 1))]
            if not selected:
                continue
            events = sum(int(row["outcome"]) for row in selected)
            output = {
                "database": database,
                "disease": disease,
                "test_group": group,
                "score": score,
                "records": len(selected),
                "patients": len({str(row["pid"]) for row in selected}),
                "events": events,
                "nonevents": len(selected) - events,
                "event_patients": len({str(row["pid"]) for row in selected if row["outcome"] == 1}),
                "nonevent_patients": len({str(row["pid"]) for row in selected if row["outcome"] == 0}),
                "observed_risk": events / len(selected),
            }
            for map_name in MAP_NAMES:
                model_key = "primary_only" if map_name.startswith("primary_only") else "broad"
                delta = deltas.get(model_key, 0.0) if "recalibrated" in map_name else 0.0
                output[map_name + "_predicted_risk"] = expit(map_eta(models[model_key], score, delta))
            rows.append(output)
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def verify_freeze_manifest(path: Path, script_path: Path) -> dict[str, object]:
    if not path.exists():
        raise RuntimeError(f"Frozen manifest missing: {path}")
    freeze = json.loads(path.read_text(encoding="utf-8"))
    expected = freeze.get("sha256", {})
    targets = {
        "protocol": script_path.parent / "design.md",
        "eligibility_code": script_path.parent / "count_eligibility.py",
        "fit_code": script_path,
    }
    for name, target in targets.items():
        actual = sha256_file(target)
        if expected.get(name) != actual:
            raise RuntimeError(f"Frozen hash mismatch for {name}")
    return freeze


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eicu-panel", type=Path, default=DEFAULT_EICU)
    parser.add_argument("--mimic-panel", type=Path, default=DEFAULT_MIMIC)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    args = parser.parse_args()
    if args.bootstrap_reps != BOOTSTRAP_REPS:
        raise ValueError(f"Protocol fixes bootstrap repetitions at {BOOTSTRAP_REPS}")

    script_path = Path(__file__).resolve()
    freeze = verify_freeze_manifest(args.outdir / "freeze_manifest.json", script_path)
    model_rows: list[dict[str, object]] = []
    metric_rows: list[dict[str, object]] = []
    contrast_rows: list[dict[str, object]] = []
    score_rows: list[dict[str, object]] = []
    gate_rows: list[dict[str, object]] = []
    branch_summaries: list[dict[str, str]] = []
    panel_meta: dict[str, object] = {}

    for database, panel_path in (("eICU", args.eicu_panel), ("MIMIC-IV", args.mimic_panel)):
        rows, panel_assertions = eligibility.read_panel(panel_path, database)
        split_meta = eligibility.assign_eicu(rows) if database == "eICU" else eligibility.assign_mimic(rows)
        disjointness = check_role_disjointness(rows, database)
        panel_meta[database] = {
            "panel_assertions": panel_assertions,
            "split": {key: value for key, value in split_meta.items() if not key.endswith("_internal")},
            "disjointness_assertions": disjointness,
        }
        for disease in eligibility.DISEASES:
            disease_rows = [r for r in rows if r["disease"] == disease]

            def analysis_rows(role: str, groups: set[int] | None = None) -> list[dict[str, object]]:
                return [
                    row for row in disease_rows
                    if row["role"] == role
                    and row["pid"] is not None
                    and row["admission_id"] is not None
                    and row["group"] in (0, 1)
                    and row["outcome"] in (0, 1)
                    and row["score"] is not None
                    and (groups is None or row["group"] in groups)
                ]

            train_primary = analysis_rows("train", {0})
            train_broad = analysis_rows("train", {0, 1})
            recal_broad = analysis_rows("recalibration", {0, 1})
            test_broad = analysis_rows("test", {0, 1})
            eligibility_sets = (
                ("train_primary_only", train_primary, MIN_TRAIN_EVENTS, MIN_TRAIN_NONEVENTS),
                ("train_broad", train_broad, MIN_TRAIN_EVENTS, MIN_TRAIN_NONEVENTS),
                ("recalibration_broad", recal_broad, MIN_ROLE_EVENTS, MIN_ROLE_NONEVENTS),
                ("test_broad", test_broad, MIN_ROLE_EVENTS, MIN_ROLE_NONEVENTS),
            )
            gates_ok = True
            for label, cohort, min_events, min_nonevents in eligibility_sets:
                counts = cohort_counts(cohort)
                ok, reason = required_role_gate(counts, min_events, min_nonevents)
                gate_rows.append({"database": database, "disease": disease, "cohort": label,
                                  **counts, "gate": "pass" if ok else "fail", "gate_reason": reason})
                gates_ok = gates_ok and ok
            for group, cohort in test_groups(test_broad).items():
                if group == "all":
                    continue
                counts = cohort_counts(cohort)
                ok, reason = subgroup_gate(counts)
                gate_rows.append({"database": database, "disease": disease, "cohort": "test_" + group,
                                  **counts, "gate": "pass" if ok else "point_only", "gate_reason": reason})

            status = "eligible" if gates_ok else "stopped_ineligible_gate"
            branch = {"database": database, "disease": disease, "branch_state": status}
            if not gates_ok:
                model_rows.append({**branch, "model_training_arm": "comparison", "fit_state": status})
                branch_summaries.append({"database": database, "disease": disease, "state": status})
                continue

            fit_specs = {
                "primary_only": train_primary,
                "broad": train_broad,
            }
            models: dict[str, dict[str, object]] = {}
            model_fit_failed = False
            for arm, train in fit_specs.items():
                train_counts = cohort_counts(train)
                support = sorted({int(row["score"]) for row in train})
                try:
                    fit = fit_logistic(train, lambda row: float(row["score"]), f"{database}/{disease}/{arm}")
                    models[arm] = fit
                    fit_state, error = "converged", None
                except FitFailure as exc:
                    fit_state, error, model_fit_failed = "failed", str(exc), True
                    models[arm] = {}
                model_rows.append({
                    **branch,
                    "model_training_arm": arm,
                    "train_records": train_counts["records"],
                    "train_patients": train_counts["patients"],
                    "train_events": train_counts["events"],
                    "train_nonevents": train_counts["nonevents"],
                    "train_event_patients": train_counts["event_patients"],
                    "train_nonevent_patients": train_counts["nonevent_patients"],
                    "train_score_support": ";".join(map(str, support)),
                    "beta0": models[arm].get("beta0"),
                    "beta1": models[arm].get("beta1"),
                    "log_likelihood": models[arm].get("log_likelihood"),
                    "iterations": models[arm].get("iterations"),
                    "fit_state": fit_state,
                    "fit_error": error,
                })
            if model_fit_failed:
                branch_summaries.append({"database": database, "disease": disease,
                                         "state": "stopped_map_fit_failure"})
                continue

            deltas: dict[str, float] = {}
            recal_failed = False
            for arm in ("primary_only", "broad"):
                try:
                    fit = fit_offset_intercept(
                        recal_broad,
                        lambda row, m=models[arm]: map_eta(m, int(row["score"])),
                        f"{database}/{disease}/{arm}/recalibration",
                    )
                    deltas[arm] = float(fit["delta"])
                    model_rows.append({
                        **branch,
                        "model_training_arm": arm,
                        "fit_state": "intercept_recalibrated",
                        "recalibration_delta": deltas[arm],
                        "recalibration_iterations": fit["iterations"],
                        "recalibration_records": len(recal_broad),
                        "recalibration_patients": cohort_counts(recal_broad)["patients"],
                    })
                except FitFailure as exc:
                    recal_failed = True
                    model_rows.append({**branch, "model_training_arm": arm,
                                       "fit_state": "recalibration_failed", "fit_error": str(exc)})
            if recal_failed:
                branch_summaries.append({"database": database, "disease": disease,
                                         "state": "stopped_recalibration_failure"})
                continue

            for row in test_broad:
                row["etas"] = {
                    "primary_only_fixed": map_eta(models["primary_only"], int(row["score"])),
                    "broad_fixed": map_eta(models["broad"], int(row["score"])),
                    "primary_only_recalibrated": map_eta(models["primary_only"], int(row["score"]), deltas.get("primary_only", 0.0)),
                    "broad_recalibrated": map_eta(models["broad"], int(row["score"]), deltas.get("broad", 0.0)),
                }
            bootstrap = patient_bootstrap(test_broad, database, disease)
            local_metrics = build_metric_rows(database, disease, test_broad, models, deltas, bootstrap)
            local_hospital = None
            if database == "eICU":
                local_hospital = hospital_bootstrap(test_broad, disease)
            metric_rows.extend(local_metrics)
            contrast_rows.extend(build_contrast_rows(database, disease, test_broad, local_metrics, bootstrap, local_hospital))
            score_rows.extend(score_table(database, disease, test_broad, models, deltas))
            branch_summaries.append({"database": database, "disease": disease, "state": "completed"})

    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "model_fits.csv", model_rows)
    write_csv(args.outdir / "eligibility_gate_results.csv", gate_rows)
    write_csv(args.outdir / "validation_metrics.csv", metric_rows)
    write_csv(args.outdir / "paired_loss_contrasts.csv", contrast_rows)
    write_csv(args.outdir / "score_level_risks.csv", score_rows)
    run_manifest = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_seed": eligibility.SEED,
        "freeze_manifest": str(args.outdir / "freeze_manifest.json"),
        "freeze_manifest_sha256": sha256_file(args.outdir / "freeze_manifest.json"),
        "python_version": sys.version,
        "library_versions": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "statsmodels": statsmodels.__version__,
        },
        "bootstrap_repetitions": BOOTSTRAP_REPS,
        "bootstrap_minimum_usable": int(MIN_BOOTSTRAP_FRACTION * BOOTSTRAP_REPS),
        "patient_bootstrap_metrics": "record-weighted Brier and stable log loss; pointwise percentile intervals; conditional on fixed maps",
        "test_calibration_diagnostics": "point estimates only; never alter predictions",
        "model_fitting_performed": True,
        "identifier_policy": "patient/admission identifiers used only in memory for assignment and cluster resampling; no identifiers are written",
        "panel_assertions_and_splits": panel_meta,
        "branches": branch_summaries,
    }
    (args.outdir / "model_run_manifest.json").write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Completed aggregate-only model evaluation: {args.outdir.resolve()}")
    print(f"Branches: {run_manifest['branches']}")
    print("Patient/admission identifiers were not written; all reported results are aggregate summaries.")


if __name__ == "__main__":
    main()

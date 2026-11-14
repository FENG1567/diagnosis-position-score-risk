#!/usr/bin/env python3
"""cohort_definition_audit.py -- a small, runnable audit for cohort-definition sensitivity.

The point of this tool is not to produce a number. It is to make explicit, for any dataset and any
instrument, four things that the published literature almost never states:

  1. who enters the analysis under each definition, and how the groups overlap
  2. whether the two definitions share a score range at all, and how much of each group lies in it
  3. whether the risk attached to the same score differs between definitions — with an estimator that
     fits nothing, and a model-based one as a cross-check
  4. when the question cannot be answered: no common support, too few events, a mapping that cannot be
     made monotone, or a bootstrap that loses the estimand

Usage
-----
    python cohort_definition_audit.py \
        --input panel.csv --id-col pid --score-col qsofa --outcome-col died \
        --definition-col pos --primary 1 --never ">1" --database MIMIC-IV --disease sepsis \
        --out report.md --outdir results/

    python cohort_definition_audit.py --selftest

Input contract (all required unless noted)
------------------------------------------
    id        one value per patient; repeat admissions must share it
    score     integer-valued instrument score
    outcome   binary
    definition  a column whose values identify the definition; the tool is told which value means
              "principal diagnosis" and which values mean "not principal"

Everything else (diagnosis semantics, score window, outcome window, missing-value handling) is carried
as free-text metadata into the report, because the tool cannot check it and pretending otherwise would be
worse than leaving it to the analyst.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap

import numpy as np
import pandas as pd

VERSION = "0.3.0-v2"


# ----------------------------------------------------------------------------- input and validation
def load_input(path: str, args) -> pd.DataFrame:
    # Keep diagnosis labels as nullable strings so missing values remain NA and category
    # matching can distinguish literal labels from numeric values such as 1 versus 1.0.
    df = pd.read_csv(path, dtype={args.definition_col: "string"})
    need = [args.id_col, args.score_col, args.outcome_col, args.definition_col]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(f"[input] missing required columns: {missing}")
    out = pd.DataFrame({
        "_pid_missing": df[args.id_col].isna(),
        "pid": df[args.id_col].astype(str),
        "score": pd.to_numeric(df[args.score_col], errors="coerce"),
        "outcome": pd.to_numeric(df[args.outcome_col], errors="coerce"),
        "definition": df[args.definition_col].str.strip(),
        "_definition_missing": df[args.definition_col].isna(),
    })
    return out


def assign_groups(df: pd.DataFrame, args) -> pd.DataFrame:
    """Map the definition column onto two groups.

    ``--never`` accepts literal categories (``"2,3"``) and numeric comparisons (``">1"``, ``"!=1"``),
    because the README documents the comparison form and an earlier version silently treated ``">1"`` as a
    literal category, which produced an empty group instead of an error.
    """
    spec = [v.strip() for v in str(args.never).split(",") if v.strip()]
    primary = str(args.primary).strip()

    def label(v):
        if pd.isna(v):
            return None
        return str(v).strip()

    def numeric_value(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def label_match(v, candidate: str) -> bool:
        value = label(v)
        if value is None:
            return False
        if value == candidate:
            return True
        x, y = numeric_value(value), numeric_value(candidate)
        return x is not None and y is not None and x == y

    def literal_match(v, cats: list[str]) -> bool:
        return any(label_match(v, candidate) for candidate in cats)

    def numeric_match(v) -> bool:
        x = numeric_value(v)
        if x is None:
            return False
        hit = False
        for s in spec:
            if s.startswith(">="):
                hit |= x >= float(s[2:])
            elif s.startswith("<="):
                hit |= x <= float(s[2:])
            elif s.startswith(">"):
                hit |= x > float(s[1:])
            elif s.startswith("<"):
                hit |= x < float(s[1:])
            elif s.startswith("!="):
                hit |= x != float(s[2:])
        return hit

    numeric_spec = any(s[0] in "<>!" for s in spec if s)
    cats = [s for s in spec if not (s and s[0] in "<>!")]

    def group(v):
        value = label(v)
        if value is None:
            return np.nan
        if label_match(value, primary):
            return 0
        # literal match first: a panel may legitimately carry the string ">1" as its category label,
        # which a purely numeric reading would drop. Numeric comparison then covers columns of numbers.
        if any(label_match(value, candidate) for candidate in spec):
            return 1
        if numeric_spec and numeric_match(value):
            return 1
        if cats and literal_match(v, cats):
            return 1
        return np.nan

    df = df.copy()
    df["grp"] = df.definition.map(group)
    return df


def validate(df: pd.DataFrame) -> list[str]:
    problems = []
    if "_pid_missing" in df.columns and bool(df._pid_missing.any()):
        return [f"patient identifier missing in {int(df._pid_missing.sum())} of {len(df)} rows; "
                f"without it the split and the cluster bootstrap cannot be defined, so the audit "
                f"refuses rather than treating the missing values as one patient"]
    # the outcome must be binary before anything else runs: a panel coded 0.2/0.8 is not a proportion
    # and must not be interpreted as one. An earlier version accepted it and returned a 60 pp estimate.
    bad = df.outcome.dropna()
    offenders = bad[(bad != 0) & (bad != 1)]
    if len(offenders):
        return [f"outcome is not binary: {len(offenders)} of {len(bad)} values are neither 0 nor 1 "
                f"(examples: {sorted(offenders.unique())[:4]}); the audit refuses this input "
                f"rather than interpreting it as a risk"]
    if df.score.isna().any():
        problems.append(f"score missing in {int(df.score.isna().sum())} rows; they are dropped")
    if df.outcome.isna().any():
        problems.append(f"outcome missing in {int(df.outcome.isna().sum())} rows; they are dropped")
    non_int = (df.score.dropna() % 1 != 0).sum()
    if non_int:
        problems.append(f"{int(non_int)} score values are not integers; the stratified estimator "
                        f"assumes discrete scores and will treat each distinct value as a level")
    if (df.definition.isna().any() or
            ("_definition_missing" in df.columns and bool(df._definition_missing.any()))):
        problems.append("definition column has missing values")
    return problems


# ----------------------------------------------------------------------------- estimators
def _levels_for_estimator(score: np.ndarray, g: np.ndarray, support_levels=None) -> np.ndarray:
    """Return observed or predeclared support levels in deterministic ascending order."""
    if support_levels is None:
        return np.intersect1d(np.unique(score[g == 0]), np.unique(score[g == 1]))
    levels = np.asarray(list(support_levels), dtype=float)
    if levels.ndim != 1 or not np.isfinite(levels).all():
        raise ValueError("support_levels must be a finite one-dimensional sequence")
    if len(np.unique(levels)) != len(levels):
        raise ValueError("support_levels must not contain duplicates")
    return np.sort(levels)


def stratified_rd(score: np.ndarray, y: np.ndarray, g: np.ndarray,
                  support_levels=None, fixed_weights=None):
    """Estimate a score-standardised risk difference using admission/record weights.

    Group 1 is the non-principal definition and group 0 is the principal definition.
    With no supplied support, the target is the observed common support. Supplying
    ``support_levels`` fixes the target support; every requested cell must be observed
    in both groups. By default weights are estimated from the pooled record counts.
    ``fixed_weights`` instead supplies reference weights for a separate fixed-weight
    estimand.
    """
    levels = _levels_for_estimator(score, g, support_levels)
    if not len(levels):
        return np.nan, 0.0, 0, []
    idx = np.searchsorted(levels, score)
    inside = (idx < len(levels)) & (levels[np.clip(idx, 0, len(levels) - 1)] == score)
    s, yy, gg = score[inside], y[inside], g[inside]
    if not len(s):
        return np.nan, 0.0, 0, []
    li = np.searchsorted(levels, s)
    k = len(levels)
    n1 = np.bincount(li[gg == 1], minlength=k).astype(float)
    y1 = np.bincount(li[gg == 1], weights=yy[gg == 1], minlength=k)
    n0 = np.bincount(li[gg == 0], minlength=k).astype(float)
    y0 = np.bincount(li[gg == 0], weights=yy[gg == 0], minlength=k)
    if not np.all((n1 > 0) & (n0 > 0)):
        return np.nan, 0.0, 0, []
    ns = n1 + n0
    p1, p0 = y1 / n1, y0 / n0
    if fixed_weights is None:
        w = ns / ns.sum()
    elif isinstance(fixed_weights, dict):
        try:
            w = np.asarray([fixed_weights[float(lv)] for lv in levels], dtype=float)
        except KeyError as exc:
            raise ValueError(f"fixed_weights has no entry for support level {exc.args[0]}") from exc
    else:
        w = np.asarray(fixed_weights, dtype=float)
    if w.shape != levels.shape or not np.isfinite(w).all() or (w < 0).any() or w.sum() <= 0:
        raise ValueError("fixed_weights must be finite, nonnegative, match support_levels, and sum positive")
    w = w / w.sum()
    rd = float(np.sum(w * (p1 - p0)))
    n_supported = int(ns.sum())
    detail = [dict(level=float(lv), n=int(ns[i]), n_never=int(n1[i]),
                   n_primary=int(n0[i]), events_never=float(y1[i]), events_primary=float(y0[i]),
                   risk_never=round(100 * p1[i], 2), risk_primary=round(100 * p0[i], 2),
                   diff_pp=round(100 * (p1[i] - p0[i]), 2), weight=float(w[i]))
              for i, lv in enumerate(levels)]
    return rd, float(n_supported / len(score)), int(k), detail


def stratified_rd_var(score: np.ndarray, y: np.ndarray, g: np.ndarray, pid: np.ndarray = None,
                      support_levels=None, fixed_weights=None):
    """Patient-cluster sandwich variance for a record-standardised risk difference.

    Cell-risk contributions are summed across every record from each patient before
    squaring. For estimated pooled-record weights the influence function also includes
    ``(d_s - RD) / N_support`` on each supported record. When ``fixed_weights`` are
    supplied, the weights are treated as fixed and that term is absent. The cluster
    sandwich receives the finite-sample correction M/(M-1), where M is the number of
    contributing patients.
    """
    levels = _levels_for_estimator(score, g, support_levels)
    if not len(levels):
        return np.nan, 0
    m_clusters_total = len(np.unique(pid)) if pid is not None else len(score)
    idx = np.searchsorted(levels, score)
    inside = (idx < len(levels)) & (levels[np.clip(idx, 0, len(levels) - 1)] == score)
    s, yy, gg = score[inside], y[inside], g[inside]
    pp = pid[inside] if pid is not None else np.arange(len(s))
    if not len(s):
        return np.nan, 0
    li = np.searchsorted(levels, s)
    k = len(levels)
    n1 = np.bincount(li[gg == 1], minlength=k).astype(float)
    y1 = np.bincount(li[gg == 1], weights=yy[gg == 1], minlength=k)
    n0 = np.bincount(li[gg == 0], minlength=k).astype(float)
    y0 = np.bincount(li[gg == 0], weights=yy[gg == 0], minlength=k)
    if not np.all((n1 > 0) & (n0 > 0)):
        return np.nan, 0
    ns = n1 + n0
    n_supported = ns.sum()
    if fixed_weights is None:
        w = ns / n_supported
    elif isinstance(fixed_weights, dict):
        try:
            w = np.asarray([fixed_weights[float(lv)] for lv in levels], dtype=float)
        except KeyError as exc:
            raise ValueError(f"fixed_weights has no entry for support level {exc.args[0]}") from exc
    else:
        w = np.asarray(fixed_weights, dtype=float)
    if w.shape != levels.shape or not np.isfinite(w).all() or (w < 0).any() or w.sum() <= 0:
        raise ValueError("fixed_weights must be finite, nonnegative, match support_levels, and sum positive")
    w = w / w.sum()
    p1, p0 = y1 / n1, y0 / n0
    d_s = p1 - p0
    rd = float(np.sum(w * d_s))
    a = np.zeros(len(s))
    for j in range(k):
        for grp, n_g, p_g, sign in ((1, n1[j], p1[j], 1.0), (0, n0[j], p0[j], -1.0)):
            m = (li == j) & (gg == grp)
            a[m] += sign * w[j] * (yy[m] - p_g) / n_g
    if fixed_weights is None:
        a += (d_s[li] - rd) / n_supported
    _, cluster_code = np.unique(pp, return_inverse=True)
    per_cluster = np.bincount(cluster_code, weights=a)
    m_clusters = len(per_cluster)
    correction = (m_clusters_total / (m_clusters_total - 1)
                  if m_clusters_total > 1 else 1.0)
    var = float(correction * np.sum(per_cluster ** 2))
    return var, int(n_supported)


def stratified_rd_se(score: np.ndarray, y: np.ndarray, g: np.ndarray, pid: np.ndarray = None,
                     support_levels=None, fixed_weights=None):
    """Square root of the cluster-robust direct-standardisation variance."""
    var, n = stratified_rd_var(score, y, g, pid, support_levels, fixed_weights)
    if not np.isfinite(var) or var < 0:
        return np.nan, n
    return float(np.sqrt(var)), n


def _cluster_variance(contribution: np.ndarray, pid: np.ndarray,
                      total_clusters: int | None = None) -> float:
    """Finite-sample corrected variance from row influence contributions."""
    _, cluster_code = np.unique(pid, return_inverse=True)
    cluster_sum = np.bincount(cluster_code, weights=contribution)
    m = int(total_clusters) if total_clusters is not None else len(cluster_sum)
    return float((m / (m - 1) if m > 1 else 1.0) * np.sum(cluster_sum ** 2))


def per_level_inference(df: pd.DataFrame, levels, min_patients: int = 20,
                        min_records_per_arm: int = 10, min_records_per_level: int = 20):
    """Attach independent group-risk and score-specific RD intervals to supported levels.

    Each interval is gated at its own score level. A sparse level suppresses that level's
    interval but does not remove otherwise valid intervals for other levels.
    """
    rows = []
    for lv in levels:
        cell = df[df.score == lv]
        g1 = cell[cell.grp == 1]
        g0 = cell[cell.grp == 0]
        n1, n0 = len(g1), len(g0)
        e1, e0 = float(g1.outcome.sum()), float(g0.outcome.sum())
        p1 = e1 / n1 if n1 else np.nan
        p0 = e0 / n0 if n0 else np.nan
        patients1, patients0 = int(g1.pid.nunique()), int(g0.pid.nunique())
        row = dict(level=float(lv), n=int(n1 + n0), n_never=int(n1), n_primary=int(n0),
                   patients_never=patients1, patients_primary=patients0,
                   events_never=e1, events_primary=e0,
                   risk_never=round(100 * p1, 2) if np.isfinite(p1) else None,
                   risk_primary=round(100 * p0, 2) if np.isfinite(p0) else None,
                   diff_pp=round(100 * (p1 - p0), 2) if n1 and n0 else None,
                   risk_never_ci_pp=None, risk_primary_ci_pp=None, delta_ci_pp=None,
                   risk_never_ci_status="not computed", risk_primary_ci_status="not computed",
                   delta_ci_status="not computed")
        for group_name, grp_df, n, events, risk, patients, ci_key, status_key in (
            ("never", g1, n1, e1, p1, patients1, "risk_never_ci_pp", "risk_never_ci_status"),
            ("primary", g0, n0, e0, p0, patients0, "risk_primary_ci_pp", "risk_primary_ci_status"),
        ):
            if n == 0:
                row[status_key] = "no records"
            elif patients < min_patients:
                row[status_key] = "too few distinct patients"
            elif events <= 0 or events >= n:
                row[status_key] = "degenerate outcome: point estimate only"
            else:
                contrib = (grp_df.outcome.to_numpy(float) - risk) / n
                se = float(np.sqrt(_cluster_variance(contrib, grp_df.pid.to_numpy(),
                                                     total_clusters=df.pid.nunique())))
                if not np.isfinite(se) or se <= 0:
                    row[status_key] = "zero or invalid cluster variance"
                else:
                    logit = np.log(risk / (1 - risk))
                    se_logit = se / (risk * (1 - risk))
                    lower, upper = sigmoid(np.array([logit - 1.96 * se_logit,
                                                      logit + 1.96 * se_logit]))
                    row[ci_key] = [round(100 * float(lower), 2), round(100 * float(upper), 2)]
                    row[status_key] = "computed"
        if not n1 or not n0:
            row["delta_ci_status"] = "no shared support"
        elif patients1 < min_patients or patients0 < min_patients:
            row["delta_ci_status"] = "too few distinct patients in a definition"
        elif n1 < min_records_per_arm or n0 < min_records_per_arm or n1 + n0 < min_records_per_level:
            row["delta_ci_status"] = "below record-count threshold"
        elif e1 <= 0 or e1 >= n1 or e0 <= 0 or e0 >= n0:
            row["delta_ci_status"] = "degenerate outcome: point estimate only"
        else:
            contrib = np.concatenate(((g1.outcome.to_numpy(float) - p1) / n1,
                                      -(g0.outcome.to_numpy(float) - p0) / n0))
            ids = np.concatenate((g1.pid.to_numpy(), g0.pid.to_numpy()))
            se = float(np.sqrt(_cluster_variance(contrib, ids,
                                                 total_clusters=df.pid.nunique())))
            if not np.isfinite(se) or se <= 0:
                row["delta_ci_status"] = "zero or invalid cluster variance"
            else:
                delta = p1 - p0
                row["delta_ci_pp"] = [round(100 * (delta - 1.96 * se), 2),
                                       round(100 * (delta + 1.96 * se), 2)]
                row["delta_ci_status"] = "computed"
        rows.append(row)
    return rows


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def fit_logit(X: np.ndarray, y: np.ndarray, iters: int = 30):
    b = np.zeros(X.shape[1])
    converged = False
    for _ in range(iters):
        p = sigmoid(X @ b)
        W = p * (1 - p) + 1e-9
        g = X.T @ (y - p)
        H = X.T @ (X * W[:, None])
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        b += step
        if np.max(np.abs(step)) < 1e-8:
            converged = True
            break
    return b, converged


def model_rd(df: pd.DataFrame, support_levels=None):
    """Model-based cross-check: logistic with group-by-score interaction, standardised."""
    levels = _levels_for_estimator(df.score.to_numpy(float), df.grp.to_numpy(int), support_levels)
    if not len(levels):
        return np.nan, "no common support"
    sub = df[df.score.isin(levels)]
    X = np.column_stack([np.ones(len(sub)), sub.score.to_numpy(float), sub.grp.to_numpy(float),
                         sub.score.to_numpy(float) * sub.grp.to_numpy(float)])
    b, conv = fit_logit(X, sub.outcome.to_numpy(float))
    if not conv:
        return np.nan, "did not converge"
    w = np.array([(sub.score == v).mean() for v in levels])
    w = w / w.sum()
    r1 = float(np.average(sigmoid(b[0] + b[1] * levels + b[2] + b[3] * levels), weights=w))
    r0 = float(np.average(sigmoid(b[0] + b[1] * levels), weights=w))
    return float(r1 - r0), "ok"


def cluster_bootstrap(df: pd.DataFrame, reps: int, seed: int, min_events: int,
                      support_levels=None, min_usable: int = 20):
    """Patient bootstrap with multiplicity and a fixed target support.

    Cluster multiplicities are applied as row weights, avoiding per-replicate dataframe
    copies while preserving repeat admissions. Every bootstrap replicate uses the same
    supplied support so that it cannot quietly change the target parameter.
    """
    rng = np.random.default_rng(seed)
    score = df.score.to_numpy(float)
    y = df.outcome.to_numpy(float)
    g = df.grp.to_numpy(int)
    cluster_codes, cluster_index_all = np.unique(df.pid.to_numpy(), return_inverse=True)
    n_clusters = len(cluster_codes)
    levels = _levels_for_estimator(score, g, support_levels)
    if not len(levels):
        return np.nan, np.nan, 0, dict(no_support=reps, few_events=0, lost_levels=0, ok=0)
    pos_idx = np.searchsorted(levels, score)
    inside = (pos_idx < len(levels)) & (levels[np.clip(pos_idx, 0, len(levels) - 1)] == score)
    score, y, g = score[inside], y[inside], g[inside]
    cluster_index = cluster_index_all[inside]
    li = np.searchsorted(levels, score)
    if n_clusters == 0:
        return np.nan, np.nan, 0, dict(no_support=reps, few_events=0, lost_levels=0, ok=0)
    k = len(levels)
    count1 = np.zeros((n_clusters, k), dtype=float)
    count0 = np.zeros((n_clusters, k), dtype=float)
    event1 = np.zeros((n_clusters, k), dtype=float)
    event0 = np.zeros((n_clusters, k), dtype=float)
    m1, m0 = g == 1, g == 0
    np.add.at(count1, (cluster_index[m1], li[m1]), 1.0)
    np.add.at(count0, (cluster_index[m0], li[m0]), 1.0)
    np.add.at(event1, (cluster_index[m1], li[m1]), y[m1])
    np.add.at(event0, (cluster_index[m0], li[m0]), y[m0])
    n_reps = max(0, int(reps))
    # A multinomial count vector is exactly equivalent to drawing G patient IDs with
    # replacement. Matrix products evaluate all requested replicates in one pass.
    multiplicities = rng.multinomial(n_clusters, np.full(n_clusters, 1 / n_clusters), size=n_reps)
    n1 = multiplicities @ count1
    n0 = multiplicities @ count0
    e1 = multiplicities @ event1
    e0 = multiplicities @ event0
    has_all_levels = np.all((n1 > 0) & (n0 > 0), axis=1)
    few_events = (np.minimum(e1.sum(axis=1), e0.sum(axis=1)) < min_events) & has_all_levels
    valid = has_all_levels & ~few_events
    ns = n1[valid] + n0[valid]
    values = np.sum(ns * (e1[valid] / n1[valid] - e0[valid] / n0[valid]), axis=1) / ns.sum(axis=1)
    values = values[np.isfinite(values)]
    fails = dict(no_support=0, few_events=int(few_events.sum()),
                 lost_levels=int((~has_all_levels).sum()), ok=int(len(values)))
    vals = np.asarray(values, dtype=float)
    lo, hi = (np.percentile(vals, [2.5, 97.5]) if len(vals) >= min_usable
              else (np.nan, np.nan))
    return lo, hi, len(vals), fails


# ----------------------------------------------------------------------------- reporting
def _arg(args, key, default):
    return getattr(args, key, default) if args is not None else default


def audit(df: pd.DataFrame, args) -> dict:
    """Run the full C policy and return its estimate, interval state, and refusal reasons."""
    problems = validate(df)
    raw_n = len(df)
    missing_counts = {
        "patient_id": int(df["_pid_missing"].sum()) if "_pid_missing" in df else int(df.pid.isna().sum()),
        "score": int(df.score.isna().sum()),
        "outcome": int(df.outcome.isna().sum()),
        "definition": (int(df["_definition_missing"].sum()) if "_definition_missing" in df
                       else int(df.definition.isna().sum())),
        "unclassified_definition": int(df.grp.isna().sum()),
    }
    expected_levels = _arg(args, "expected_levels", None)
    support_label = ("prespecified expected levels" if expected_levels is not None
                     else "observed common support; no extrapolation")
    metadata = {
        "diagnosis_semantics": _arg(args, "semantics", "unspecified") or "unspecified",
        "primary_definition_value": str(_arg(args, "primary", "1")),
        "never_definition_values_or_rule": str(_arg(args, "never", ">1")),
        "score_window": _arg(args, "score_window", "unspecified") or "unspecified",
        "outcome_window": _arg(args, "outcome_window", "unspecified") or "unspecified",
        "row_unit": _arg(args, "row_unit", "admission"),
        "cluster_unit": _arg(args, "cluster_unit", "patient"),
        "weighting_unit": "record",
        "missingness_assumption": _arg(args, "missingness_assumption", "unknown") or "unknown",
        "missing_data_handling": (_arg(args, "missing_data_handling", None)
                                  or _arg(args, "missing", None)
                                  or "complete-case: drop missing score, outcome, or definition group"),
        "missing_counts_before_filtering": missing_counts,
        "support_definition": support_label,
        "expected_support_levels": (list(map(float, expected_levels)) if expected_levels is not None else None),
    }
    min_events = int(_arg(args, "min_events", 10))
    min_level_n = int(_arg(args, "min_level_n", 20))
    min_arm_n = int(_arg(args, "min_arm_n", 10))
    min_clusters = int(_arg(args, "min_clusters", 20))
    reps = int(_arg(args, "reps", 400))
    seed = int(_arg(args, "seed", 20261103))
    min_usable_bootstrap = int(_arg(args, "min_usable_bootstrap", 20))
    rules = {
        "min_records_per_score_level": {"value": min_level_n, "unit": "records"},
        "min_records_per_score_definition_cell": {"value": min_arm_n, "unit": "records"},
        "min_distinct_patients_total": {"value": min_clusters, "unit": "patients"},
        "min_distinct_patients_per_score_definition_cell": {"value": min_clusters, "unit": "patients"},
        "nondegenerate_outcome_per_score_definition_cell": True,
        "min_events_per_definition_in_bootstrap": {"value": min_events, "unit": "events"},
        "bootstrap_replicates": reps,
        "min_usable_bootstrap_replicates": min_usable_bootstrap,
    }
    fatal = next((p for p in problems if p.startswith("outcome is not binary") or
                  p.startswith("patient identifier missing")), None)
    if fatal:
        return dict(tool_version=VERSION, dataset=_arg(args, "database", "unspecified"),
                    disease=_arg(args, "disease", "unspecified"),
                    instrument=_arg(args, "score_col", "score"), metadata=metadata, rules=rules,
                    input_problems=problems, flow={}, common_support={},
                    stratified_rd_pp=None, observed_supported_rd_pp=None, population_target_rd_pp=None,
                    stratified_rd_ci_pp=None, model_rd_pp=None, model_status="not attempted",
                    delta_ci_pp=None, delta_se_pp=None, per_level=[], bootstrap={},
                    refusal_reasons=["invalid_input"], interval_status="not computed (invalid input)",
                    target_support_status="not assessed", verdict="not estimable: " + fatal)

    complete = df.dropna(subset=["score", "outcome", "grp"]).copy()
    flow = {("principal" if k == 0 else "never-principal"): int((complete.grp == k).sum())
            for k in (0, 1)}
    flow["patients"] = int(complete.pid.nunique())
    flow["rows"] = int(len(complete))
    flow["rows_before_filtering"] = int(raw_n)
    flow["rows_dropped_complete_case_or_unclassified"] = int(raw_n - len(complete))
    flow["unclassified_definition_rows"] = missing_counts["unclassified_definition"]
    flow["duplicate_rows_per_patient"] = round(len(complete) / max(complete.pid.nunique(), 1), 2)

    s = complete.score.to_numpy(float)
    y = complete.outcome.to_numpy(float)
    g = complete.grp.to_numpy(int)
    pid = complete.pid.to_numpy()
    observed_levels = np.intersect1d(np.unique(s[g == 0]), np.unique(s[g == 1]))
    target_levels = _levels_for_estimator(s, g, expected_levels)
    lost_target = (expected_levels is not None and
                   not set(target_levels).issubset(set(observed_levels)))
    observed_rd, observed_share, observed_nlevels, observed_detail = stratified_rd(s, y, g)
    target_rd, support, n_levels, detail = stratified_rd(s, y, g, target_levels)
    if len(target_levels):
        support = float(np.isin(s, target_levels).sum() / max(len(s), 1))
    # Keep a descriptive estimate on the observed common support if the prespecified population
    # support lost a positive-probability cell. It is explicitly labelled as a changed target.
    if lost_target:
        display_rd, display_detail = observed_rd, observed_detail
        estimate_label = "observed-supported estimate; target support changed"
        target_support_status = "target_support_lost"
        target_rd = np.nan
    else:
        display_rd, display_detail = target_rd, detail
        estimate_label = ("prespecified population support" if expected_levels is not None
                          else "observed common support")
        target_support_status = "complete"

    support_set = set(target_levels if not lost_target else observed_levels)
    display_levels = sorted(support_set)
    weight_by_level = {float(d["level"]): float(d["weight"])
                       for d in (display_detail or []) if "weight" in d}
    display_detail = per_level_inference(
        complete, display_levels, min_patients=min_clusters,
        min_records_per_arm=min_arm_n, min_records_per_level=min_level_n)
    for row in display_detail:
        row["weight"] = weight_by_level.get(float(row["level"]))
    se, _ = stratified_rd_se(s, y, g, pid, support_levels=sorted(support_set))
    legacy_se, _ = stratified_rd_se(s, y, g, pid, support_levels=sorted(support_set),
                                    fixed_weights={float(d["level"]): float(d["weight"])
                                                   for d in (display_detail or [])})
    # Fixed-weight mode above receives the weights observed among the same support levels; this
    # is a diagnostic for the omitted weight-IF term, not the benchmark's population target.

    if _arg(args, "model_check", True) and np.isfinite(target_rd):
        mrd, mstatus = model_rd(complete, target_levels)
    elif _arg(args, "model_check", True):
        mrd, mstatus = np.nan, "target support lost or absent"
    else:
        mrd, mstatus = np.nan, "not requested"

    refusal_reasons = []
    if not len(observed_levels):
        refusal_reasons.append("no_common_support")
    if lost_target:
        refusal_reasons.append("target_support_lost")
    if np.isfinite(display_rd) and not lost_target:
        in_target = complete.score.isin(target_levels)
        n_clusters = int(complete.loc[in_target, "pid"].nunique())
        if n_clusters < min_clusters:
            refusal_reasons.append("too_few_distinct_patients_total")
        thin_cells = []
        for lv in target_levels:
            for grp_value, name in ((1, "never"), (0, "principal")):
                cell = complete[(complete.score == lv) & (complete.grp == grp_value)]
                n_records = len(cell)
                n_patients = int(cell.pid.nunique())
                if n_records < min_arm_n:
                    thin_cells.append((float(lv), name, "records", n_records))
                if n_patients < min_clusters:
                    thin_cells.append((float(lv), name, "patients", n_patients))
        if thin_cells:
            if any(item[2] == "records" for item in thin_cells):
                refusal_reasons.append("too_few_records_per_score_definition_cell")
            if any(item[2] == "patients" for item in thin_cells):
                refusal_reasons.append("too_few_distinct_patients_per_score_definition_cell")
        if detail and min(int(d["n"]) for d in detail) < min_level_n:
            refusal_reasons.append("too_few_records_per_score_level")
        degenerate = [d for d in detail
                      if d["events_never"] <= 0 or d["events_never"] >= d["n_never"] or
                      d["events_primary"] <= 0 or d["events_primary"] >= d["n_primary"]]
        if degenerate:
            refusal_reasons.append("degenerate_outcome_cell")

    # Run the expensive bootstrap only after all deterministic refusal rules pass. The C decision still
    # uses the original minimum usable-bootstrap gate, but sparse/degenerate samples do not spend time on
    # replicates whose result cannot change the decision.
    lo = hi = np.nan
    n_ok = 0
    fails = dict(no_support=0, few_events=0, lost_levels=0, ok=0)
    bootstrap_status = "skipped after deterministic refusal rule"
    if np.isfinite(target_rd) and not refusal_reasons:
        lo, hi, n_ok, fails = cluster_bootstrap(
            complete, reps, seed, min_events, support_levels=target_levels,
            min_usable=min_usable_bootstrap)
        bootstrap_status = "computed"
        if n_ok < min_usable_bootstrap:
            refusal_reasons.append("too_few_usable_bootstrap_replicates")

    interval_status = "computed" if not refusal_reasons else "not computed (" + ", ".join(refusal_reasons) + ")"
    delta_ci = ([round(100 * (target_rd - 1.96 * se), 2), round(100 * (target_rd + 1.96 * se), 2)]
                if interval_status == "computed" and np.isfinite(se) and np.isfinite(target_rd) else None)
    boot_ci = ([round(100 * lo, 2), round(100 * hi, 2)]
               if interval_status == "computed" and np.isfinite(lo) and np.isfinite(hi) else None)
    if not len(observed_levels):
        verdict = "not estimable: the two definitions share no score level"
    elif lost_target:
        verdict = "target_support_lost: observed-supported estimate retained; population-target interval withheld"
    elif refusal_reasons:
        verdict = "interval withheld: " + ", ".join(refusal_reasons)
    else:
        verdict = "estimable"

    return dict(
        tool_version=VERSION, dataset=_arg(args, "database", "unspecified"),
        disease=_arg(args, "disease", "unspecified"), instrument=_arg(args, "score_col", "score"),
        metadata=metadata, rules=rules, input_problems=problems, flow=flow,
        common_support=dict(share_pct=round(100 * support, 1), n_levels=int(n_levels),
                            observed_levels=list(map(float, observed_levels)),
                            target_levels=list(map(float, target_levels)),
                            share_observed_pct=round(100 * observed_share, 1)),
        stratified_rd_pp=round(100 * display_rd, 2) if np.isfinite(display_rd) else None,
        observed_supported_rd_pp=round(100 * observed_rd, 2) if np.isfinite(observed_rd) else None,
        population_target_rd_pp=round(100 * target_rd, 2) if np.isfinite(target_rd) else None,
        estimate_label=estimate_label, target_support_status=target_support_status,
        stratified_rd_ci_pp=boot_ci, model_rd_pp=round(100 * mrd, 2) if np.isfinite(mrd) else None,
        delta_ci_pp=delta_ci, delta_se_pp=round(100 * se, 2) if np.isfinite(se) else None,
        legacy_fixed_weight_se_pp=round(100 * legacy_se, 2) if np.isfinite(legacy_se) else None,
        model_status=mstatus, interval_status=interval_status,
        refusal_reasons=refusal_reasons, per_level=display_detail or [],
        bootstrap=dict(reps=reps, usable=n_ok, failures=fails, status=bootstrap_status), verdict=verdict)


def audit_v2(frame: pd.DataFrame, score_col="score", outcome_col="y", group_col="grp", pid_col="pid",
             expected_levels=None, metadata=None, config=None) -> dict:
    """Stable DataFrame API for v2 audits and simulations.

    ``group_col`` must contain 0 for principal and 1 for never-principal records.
    ``expected_levels`` fixes the population support for simulation or a predeclared audit.
    Config keys override the C thresholds and runtime defaults recorded in the result.
    """
    config = dict(config or {})
    metadata = dict(metadata or {})
    needed = [score_col, outcome_col, group_col, pid_col]
    missing = [column for column in needed if column not in frame.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    d = pd.DataFrame({
        "pid": frame[pid_col],
        "score": pd.to_numeric(frame[score_col], errors="coerce"),
        "outcome": pd.to_numeric(frame[outcome_col], errors="coerce"),
        "grp": pd.to_numeric(frame[group_col], errors="coerce"),
        "definition": frame[group_col].astype(str),
        "_pid_missing": frame[pid_col].isna(),
    })
    if not set(d.grp.dropna().unique()).issubset({0, 1}):
        raise ValueError("group_col must use 0=principal and 1=never-principal")
    d["grp"] = d.grp.astype(float)
    d["_definition_missing"] = frame[group_col].isna()
    class _Args:
        pass
    args = _Args()
    defaults = dict(database="unspecified", disease="unspecified", score_col=score_col,
                    semantics="unspecified", primary="0", never="1", score_window="unspecified",
                    outcome_window="unspecified", row_unit="admission", cluster_unit="patient",
                    missingness_assumption="unknown", missing_data_handling=None, missing=None,
                    reps=400, seed=20261103, min_events=10, min_level_n=20, min_arm_n=10,
                    min_clusters=20, min_usable_bootstrap=20, model_check=False,
                    expected_levels=expected_levels)
    defaults.update(metadata)
    defaults.update(config)
    defaults["expected_levels"] = expected_levels
    for key, value in defaults.items():
        setattr(args, key, value)
    result = audit(d, args)
    result["api"] = "audit_v2"
    return result


def to_markdown(a: dict) -> str:
    md = [f"# Cohort-definition audit — {a['dataset']} / {a['disease']} / {a['instrument']}",
          "", f"Tool version {a['tool_version']}.", "", "## Verdict", "",
          f"**{a['verdict']}**", "", "## Input contract", ""]
    for k, v in a["metadata"].items():
        md.append(f"- {k.replace('_', ' ')}: {v if v else '**not stated**'}")
    if a["input_problems"]:
        md += ["", "Input problems detected:", ""] + [f"- {p}" for p in a["input_problems"]]
    if not a.get("flow"):
        md += ["", "No estimate was produced. The audit stops at the input contract rather than reporting a",
               "number for an input it cannot interpret.", ""]
        return "\n".join(md)
    md += ["", "## Cohort flow", "",
           f"- rows {a['flow']['rows']:,}; patients {a['flow']['patients']:,} "
           f"({a['flow']['duplicate_rows_per_patient']} rows per patient)",
           f"- principal diagnosis {a['flow']['principal']:,}; "
           f"never principal {a['flow']['never-principal']:,}", ""]
    if a["input_problems"]:
        md += ["Input problems detected:", ""] + [f"- {p}" for p in a["input_problems"]] + [""]
    md += ["## Common support", "",
           f"- score levels shared by both definitions: **{a['common_support']['n_levels']}**",
           f"- support definition: {a['metadata']['support_definition']}",
           f"- share of the sample inside the shared support: "
           f"**{a['common_support']['share_pct']}%**", ""]
    md += ["## Risk at the same score", "",
           "| score | n | never | principal | risk never | risk principal | difference |",
           "|---:|---:|---:|---:|---:|---:|---:|"]
    for d in a["per_level"]:
        md.append(f"| {d['level']:g} | {d['n']:,} | {d['n_never']:,} | {d['n_primary']:,} | "
                  f"{d['risk_never']}% | {d['risk_primary']}% | {d['diff_pp']:+} pp |")
    if a["stratified_rd_pp"] is None:
        md += ["", "No risk difference is reported for this input. The audit stopped before producing one.",
               ""]
        return "\n".join(md)
    md += ["", f"**{a.get('estimate_label', 'Model-free standardised risk difference')}: "
           f"{a['stratified_rd_pp']} pp**"]
    if a.get("delta_ci_pp"):
        md.append(f"- cluster-robust direct-standardisation 95% CI: {a['delta_ci_pp'][0]} to {a['delta_ci_pp'][1]} pp "
                  "(patient-cluster influence-function interval)")
    if a["stratified_rd_ci_pp"]:
        md.append(f"- cluster-bootstrap 95% CI: {a['stratified_rd_ci_pp'][0]} to "
                  f"{a['stratified_rd_ci_pp'][1]} pp (patient-cluster percentile bootstrap)")
    md.append(f"- interval state: {a.get('interval_status', 'not computed')}")
    if a.get("refusal_reasons"):
        md.append(f"- refusal reasons: {', '.join(a['refusal_reasons'])}")
    md += [
           "", f"Model-based cross-check: {a['model_rd_pp']} pp ({a['model_status']}).", ""]
    b = a["bootstrap"]
    min_usable = a.get("rules", {}).get("min_usable_bootstrap_replicates", 20)
    md += ["## What failed, and how often", "",
           f"- bootstrap status: {b.get('status', 'unknown')}; requested replicates {b['reps']}; "
           f"usable **{b['usable']}** (minimum {min_usable})",
           f"- no shared support {b['failures']['no_support']}; too few events "
           f"{b['failures']['few_events']}; lost a score level {b['failures']['lost_levels']}", "",
           "A result below the configured minimum number of usable replicates is reported without an interval rather than as a "
           "wide interval, because a wide interval from a failed procedure is not a weaker answer — it is "
           "not an answer.", ""]
    md += ["## Rule inputs", ""]
    for name, value in a.get("rules", {}).items():
        md.append(f"- {name.replace('_', ' ')}: {value}")
    return "\n".join(md)


# ----------------------------------------------------------------------------- self test
def selftest() -> int:
    """Exercise the failure modes the tool is supposed to catch."""
    rng = np.random.default_rng(7)
    ok = True

    def mk(n, sep=False, slope=0.5, events=True):
        s = rng.integers(0, 6, n)
        g = (s < 2).astype(int) if sep else rng.integers(0, 2, n)
        p = sigmoid(-2.0 + slope * s + (0.6 if events else 0.0) * g)
        y = rng.binomial(1, p)
        return pd.DataFrame(dict(pid=np.arange(n), score=s.astype(float), outcome=y.astype(float),
                                 grp=g))

    # 1. no common support must be detected, not averaged
    d = mk(600, sep=True)
    rd, sup, lv, _ = stratified_rd(d.score.to_numpy(), d.outcome.to_numpy(), d.grp.to_numpy())
    print(f"[selftest] no common support -> rd={rd}, levels={lv}")
    ok &= not np.isfinite(rd)

    # 2. multiplicity: a bootstrap draw must be able to duplicate patients
    d = mk(400)
    pids = d.pid.unique()
    pick = rng.choice(pids, len(pids), replace=True)
    counts = pd.Series(pick).value_counts()
    pos = {p: gg.index.to_numpy() for p, gg in d.groupby("pid")}
    idx = np.concatenate([pos[p] for p, k in counts.items() for _ in range(k)])
    dup_ok = len(idx) == len(pick) and len(idx) > len(set(pick))
    print(f"[selftest] bootstrap keeps multiplicity -> {dup_ok} ({len(idx)} rows from "
          f"{len(set(pick))} distinct patients)")
    ok &= dup_ok

    # 3. zero events in one group must be flagged, not silently estimated
    d = mk(300)
    d.loc[d.grp == 1, "outcome"] = 0.0
    lo, hi, n_ok, fails = cluster_bootstrap(d, 50, 1, min_events=10)
    print(f"[selftest] zero events in one group -> usable={n_ok}, few_events={fails['few_events']}")
    ok &= (n_ok == 0)

    # 4. negative slope in the fitted model must be visible
    d = mk(500, slope=-0.4)
    mrd, status = model_rd(d)
    print(f"[selftest] negative slope -> model_rd={mrd}, status={status}")
    ok &= np.isfinite(mrd)

    # 5. a known effect must be recovered in the right direction
    d = mk(4000, slope=0.45)
    rd, _, _, _ = stratified_rd(d.score.to_numpy(), d.outcome.to_numpy(), d.grp.to_numpy())
    print(f"[selftest] known positive effect -> rd={rd:+.4f}")
    ok &= rd > 0

    # 6. patient leakage: splitting by row instead of by patient is detectable
    d = pd.DataFrame(dict(pid=np.repeat(np.arange(200), 3), score=rng.integers(0, 6, 600),
                          outcome=rng.binomial(1, 0.3, 600), grp=rng.integers(0, 2, 600)))
    rng2 = np.random.default_rng(1)
    row_half = rng2.integers(0, 2, len(d))
    leak = len(set(d.pid[row_half == 0]) & set(d.pid[row_half == 1]))
    by_pid = dict(zip(d.pid.unique(), rng2.integers(0, 2, d.pid.nunique())))
    half = d.pid.map(by_pid)
    leak2 = len(set(d.pid[half == 0]) & set(d.pid[half == 1]))
    print(f"[selftest] leakage: row split shares {leak} patients, patient split shares {leak2}")
    ok &= (leak > 0 and leak2 == 0)

    # 7. DEGENERATE VARIANCE. Every patient at the same score, one group all deaths and the other all
    # survivors: the risk difference is exactly 1 and its standard error must be 0. An earlier version
    # returned 0.0709 here, which is how it was caught.
    s = np.zeros(200)
    g = np.r_[np.zeros(100), np.ones(100)].astype(int)
    y = np.r_[np.zeros(100), np.ones(100)]
    se, _ = stratified_rd_se(s, y, g)
    print(f"[selftest] degenerate variance -> SE={se:.6g} (must be ~0)")
    ok &= (np.isfinite(se) and se < 1e-9)

    # 8. ANALYTIC AGREEMENT. One stratum with independent rows: the cluster-robust variance must equal
    # sqrt(p1(1-p1)/n1 + p0(1-p0)/n0) to numerical precision.
    rng3 = np.random.default_rng(11)
    g = np.r_[np.zeros(500), np.ones(500)].astype(int)
    s = np.zeros(1000)
    y = np.r_[rng3.binomial(1, 0.2, 500), rng3.binomial(1, 0.3, 500)].astype(float)
    se, _ = stratified_rd_se(s, y, g)
    p1, p0 = y[g == 1].mean(), y[g == 0].mean()
    closed = np.sqrt(p1 * (1 - p1) / 500 + p0 * (1 - p0) / 500)
    ratio = se / closed if closed else np.nan
    print(f"[selftest] analytic agreement -> SE={se:.6f}, closed form={closed:.6f}, "
          f"ratio={ratio:.4f}")
    ok &= bool(np.isfinite(ratio) and abs(ratio - 1) < 0.01)

    # 9. CLUSTER INFLATION. With two rows per patient whose outcomes are identical, the effective sample
    # size halves, so the cluster-robust variance must exceed the naive one. This is the property the
    # tool needs to carry repeated admissions honestly.
    n_pat = 400
    pid = np.repeat(np.arange(n_pat), 2)
    g = np.repeat(rng3.integers(0, 2, n_pat), 2)
    y_pat = rng3.binomial(1, 0.3, n_pat).astype(float)
    y = np.repeat(y_pat, 2)
    s = np.zeros(len(pid))
    se_cl, _ = stratified_rd_se(s, y, g, pid)
    se_naive, _ = stratified_rd_se(s, y, g)
    print(f"[selftest] cluster inflation -> clustered SE={se_cl:.5f} vs naive SE={se_naive:.5f}")
    ok &= bool(np.isfinite(se_cl) and np.isfinite(se_naive) and se_cl > se_naive * 1.2)

    # 10. CROSS-STRATUM CLUSTERING. A patient whose records fall in two different score strata must have
    # their signed contributions summed before squaring. With two strata and perfectly correlated records,
    # the cluster standard error is exactly sqrt(2) times the row-level one. An earlier version squared
    # inside each cell and added the cells, which gives a ratio of 1.0 and hides the correlation.
    rows = []
    for k in range(300):
        yk = float(rng3.binomial(1, 0.3))
        gk = 1 if k % 2 else 0
        for sc in (0, 1):
            rows.append((f"p{k}", float(sc), gk, yk))
    dd = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
    se_row, _ = stratified_rd_se(dd.score.to_numpy(float), dd.y.to_numpy(float),
                                 dd.grp.to_numpy(int))
    se_cross, _ = stratified_rd_se(dd.score.to_numpy(float), dd.y.to_numpy(float),
                                   dd.grp.to_numpy(int), dd.pid.to_numpy())
    ratio = se_cross / se_row if se_row else np.nan
    print(f"[selftest] cross-stratum clustering -> row SE={se_row:.5f}, cluster SE={se_cross:.5f}, "
          f"ratio={ratio:.4f} (must be ~1.4142)")
    ok &= bool(np.isfinite(ratio) and abs(ratio - np.sqrt(2)) < 0.02)

    # 11. DEFINITION SPEC PARSING. The README documents --never ">1"; an earlier version compared it as a
    # literal string and silently produced an empty never-group.
    class _Args:
        primary = "1"
        never = ">1"

    class _Args2:
        primary = "1"
        never = "2,3"

    probe = pd.DataFrame({"definition": ["1", "1", "2", "3", "4"]})
    got_cmp = assign_groups(probe, _Args()).grp.tolist()
    got_cat = assign_groups(probe, _Args2()).grp.tolist()
    cmp_ok = got_cmp[:2] == [0, 0] and all(v == 1 for v in got_cmp[2:])
    cat_ok = got_cat[:2] == [0, 0] and got_cat[2] == 1 and got_cat[3] == 1 and pd.isna(got_cat[4])
    print(f"[selftest] definition spec -> '>1'={got_cmp}, '2,3'={got_cat}")
    ok &= bool(cmp_ok and cat_ok)

    # 12. CROSS-GROUP PATIENTS. A patient with records in both definition groups must have the two
    # groups' contributions summed WITH OPPOSITE SIGNS before squaring. With the same sign, identical
    # outcomes in both groups produce a spurious interval instead of none, and complementary outcomes
    # produce none instead of a real one. Every earlier test put each patient in a single group, which is
    # why eleven passing checks missed this.
    def _cross(case):
        rows = []
        for k in range(4):
            base = k % 2
            for grp in (0, 1):
                yv = base if case == "same" else (base if grp == 0 else 1 - base)
                for sc in (0, 1):
                    rows.append((f"p{k}", float(sc), grp, float(yv)))
        d = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
        return stratified_rd_se(d.score.to_numpy(float), d.y.to_numpy(float),
                                d.grp.to_numpy(int), d.pid.to_numpy())[0]

    se_same = _cross("same")
    se_comp = _cross("complement")
    print(f"[selftest] cross-group patients -> identical SE={se_same:.6f} (want 0), "
          f"complementary SE={se_comp:.6f} (want non-zero)")
    ok &= bool(np.isfinite(se_same) and se_same < 1e-9 and np.isfinite(se_comp) and se_comp > 0.1)

    print("\n[selftest]", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ----------------------------------------------------------------------------- cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--input")
    ap.add_argument("--id-col", default="pid")
    ap.add_argument("--score-col", default="score")
    ap.add_argument("--outcome-col", default="outcome")
    ap.add_argument("--definition-col", default="definition")
    ap.add_argument("--primary", default="1")
    ap.add_argument("--never", default=">1", help="comma-separated values meaning not-principal")
    ap.add_argument("--database", default="unspecified")
    ap.add_argument("--disease", default="unspecified")
    ap.add_argument("--semantics", default="", help="how the diagnosis position is recorded")
    ap.add_argument("--score-window", default="", help="e.g. first 24 h of ICU stay")
    ap.add_argument("--outcome-window", default="", help="e.g. in-hospital death")
    ap.add_argument("--row-unit", default="admission", help="unit represented by one row")
    ap.add_argument("--cluster-unit", default="patient", help="independent sampling/cluster unit")
    ap.add_argument("--missingness-assumption", default="unknown",
                    choices=["unknown", "MCAR", "MAR", "MNAR"],
                    help="assumption about the missingness mechanism")
    ap.add_argument("--missing-data-handling", default="",
                    help="analysis handling of missing values; default is complete case")
    ap.add_argument("--missing", default="", help="deprecated alias for missing-data-handling")
    ap.add_argument("--expected-levels", default="",
                    help="optional comma-separated prespecified common-support score levels")
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20261103)
    ap.add_argument("--min-events", type=int, default=10)
    ap.add_argument("--min-level-n", type=int, default=20,
                    help="minimum records across both definitions per score level")
    ap.add_argument("--min-clusters", type=int, default=20,
                    help="minimum distinct patients overall and within each score-definition cell")
    ap.add_argument("--min-arm-n", type=int, default=10,
                    help="minimum records per definition within a score level")
    ap.add_argument("--min-usable-bootstrap", type=int, default=20,
                    help="minimum usable patient-bootstrap replicates required for an interval")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--out", default="audit_report.md")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.input:
        ap.error("--input is required unless --selftest is given")

    try:
        args.expected_levels = ([float(v.strip()) for v in args.expected_levels.split(",") if v.strip()]
                                if args.expected_levels.strip() else None)
    except ValueError as exc:
        ap.error(f"--expected-levels must be a comma-separated list of numbers: {exc}")

    df = assign_groups(load_input(args.input, args), args)
    a = audit(df, args)
    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, args.out), "w", encoding="utf-8") as fh:
        fh.write(to_markdown(a))
    with open(os.path.join(args.outdir, "audit_metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(a, fh, indent=2, ensure_ascii=False)
    pd.DataFrame(a["per_level"]).to_csv(os.path.join(args.outdir, "per_level.csv"), index=False)
    print(f"[audit] {a['verdict']}")
    if a.get("bootstrap"):
        print(f"[audit] model-free RD {a['stratified_rd_pp']} pp, "
              f"{a['bootstrap']['usable']} usable replicates")
    print(f"[audit] wrote {args.out}, audit_metrics.json, per_level.csv to {args.outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

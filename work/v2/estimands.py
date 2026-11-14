"""Direct empirical contrasts and paired cluster influences for revised analyses.

All risks are proportions. Public tables convert them to percentage points.
The audit module owns interval emission. These routines expose numerical
quantities for independent checks and prespecified paired sensitivity analyses.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass
class Contrast:
    estimate: float
    se: float
    levels: pd.DataFrame
    cluster_influence: pd.Series
    support_share: float
    n_records: int
    n_patients: int
    n_inference_clusters: int = 0


def direct_contrast(frame: pd.DataFrame, level_col: str = 'score',
                    record_weight_col: str | None = None,
                    fixed_weights: dict | None = None) -> Contrast:
    """Compute never-primary minus primary risk within common discrete levels.

    Required columns are pid, grp, y and level_col. grp is 1 for never-primary.
    Weight uncertainty is included unless external fixed_weights are supplied.
    All input patients enter the finite-sample correction. Patients entirely
    outside target support have zero influence contributions.
    """
    d = frame.copy()
    required = ['pid', 'grp', 'y', level_col]
    if d[required].isna().any().any():
        raise ValueError('The numerical contrast requires complete identifiers, groups, outcomes and scores.')
    if not d.grp.isin([0, 1]).all() or not d.y.isin([0, 1]).all():
        raise ValueError('Binary groups and outcomes are required.')
    d['_weight'] = 1.0 if record_weight_col is None else pd.to_numeric(d[record_weight_col])
    if (~np.isfinite(d._weight)).any() or (d._weight <= 0).any():
        raise ValueError('Record weights must be finite and positive.')
    input_patients = pd.Index(d.pid.unique())
    available = [set(d.loc[d.grp == group, level_col]) for group in (0, 1)]
    levels = sorted(available[0].intersection(available[1]))
    if fixed_weights is not None:
        missing = set(fixed_weights).difference(levels)
        if missing:
            raise ValueError('A fixed target level lacks an observed arm.')
        levels = sorted(fixed_weights)
    inside = d[level_col].isin(levels)
    share = float(d.loc[inside, '_weight'].sum() / d._weight.sum()) if len(d) else 0.0
    d = d.loc[inside].copy()
    if not len(d):
        return Contrast(np.nan, np.nan, pd.DataFrame(), pd.Series(0.0, index=input_patients),
                        share, 0, 0, len(input_patients))
    total_weight = d._weight.sum()
    rows = []
    for level, cell in d.groupby(level_col, sort=True):
        a = cell.loc[cell.grp == 1]
        b = cell.loc[cell.grp == 0]
        p1 = np.average(a.y, weights=a._weight)
        p0 = np.average(b.y, weights=b._weight)
        rows.append(dict(level=level, n=len(cell), n_never=len(a), n_primary=len(b),
                         patients_never=a.pid.nunique(), patients_primary=b.pid.nunique(),
                         deaths_never=int(a.y.sum()), deaths_primary=int(b.y.sum()),
                         risk_never=p1, risk_primary=p0, delta=p1 - p0,
                         weight=cell._weight.sum() / total_weight,
                         mass_never=a._weight.sum(), mass_primary=b._weight.sum()))
    detail = pd.DataFrame(rows)
    if fixed_weights is not None:
        supplied = np.array([fixed_weights[level] for level in detail.level], dtype=float)
        if not np.isfinite(supplied).all() or (supplied < 0).any() or supplied.sum() <= 0:
            raise ValueError('Fixed target weights must be finite nonnegative and sum to a positive value.')
        detail['weight'] = supplied / supplied.sum()
    estimate = float(np.dot(detail.weight, detail.delta))
    contribution = np.zeros(len(d))
    for row in detail.itertuples(index=False):
        level_mask = d[level_col].to_numpy() == row.level
        if fixed_weights is None:
            contribution[level_mask] += (d.loc[level_mask, '_weight'].to_numpy() / total_weight
                                         * (row.delta - estimate))
        for group, sign, risk, mass in [(1, 1, row.risk_never, row.mass_never),
                                         (0, -1, row.risk_primary, row.mass_primary)]:
            mask = level_mask & (d.grp.to_numpy() == group)
            contribution[mask] += (sign * row.weight * d.loc[mask, '_weight'].to_numpy()
                                   * (d.loc[mask, 'y'].to_numpy() - risk) / mass)
    supported_patients = d.pid.nunique()
    cluster = pd.Series(contribution, index=d.pid.to_numpy()).groupby(level=0).sum()
    cluster = cluster.reindex(input_patients, fill_value=0.0)
    count = len(cluster)
    variance = count / (count - 1) * np.dot(cluster, cluster) if count > 1 else np.nan
    return Contrast(estimate, float(np.sqrt(variance)), detail, cluster, share, len(d), supported_patients, count)


def paired_difference(left: Contrast, right: Contrast) -> dict:
    """Return right-minus-left with shared-patient covariance retained."""
    a, b = left.cluster_influence.align(right.cluster_influence, join='outer', fill_value=0.0)
    influence = b - a
    count = len(influence)
    variance = count / (count - 1) * np.dot(influence, influence) if count > 1 else np.nan
    se = float(np.sqrt(variance))
    estimate = right.estimate - left.estimate
    z = norm.ppf(0.975)
    return dict(difference=estimate, se=se, lo=estimate - z * se,
                hi=estimate + z * se, n_patients=count,
                ci_status='numerical only, audit gates must also be satisfied')


def incomplete_score_bounds(frame: pd.DataFrame, max_score: int) -> pd.DataFrame:
    """Separate-level worst-case mortality bounds for binary component sums.

    score_lower/score_upper identify compatible integer totals. Their extremes
    can differ between score levels. These bounds contain no sampling interval.
    """
    d = frame.dropna(subset=['grp', 'y', 'score_lower', 'score_upper'])
    if not d.y.isin([0, 1]).all():
        raise ValueError('Binary outcomes are required for missingness bounds.')
    if ((d.score_lower < 0) | (d.score_upper > max_score)
        | (d.score_lower > d.score_upper)).any():
        raise ValueError('Invalid score range.')
    rows = []
    for level in range(max_score + 1):
        cell = dict(level=level, estimand='delta_s missingness identification bounds')
        risks = {}
        for group, name in [(0, 'primary'), (1, 'never')]:
            g = d.loc[d.grp == group]
            mandatory = g.loc[(g.score_lower == level) & (g.score_upper == level)]
            compatible = g.loc[(g.score_lower <= level) & (g.score_upper >= level)]
            optional = compatible.loc[compatible.score_lower != compatible.score_upper]
            deaths = int(mandatory.y.sum())
            count = len(mandatory)
            optional_deaths = int(optional.y.sum())
            optional_survivors = len(optional) - optional_deaths
            if not len(compatible):
                lower = upper = np.nan
            else:
                min_denominator = count + optional_survivors
                max_denominator = count + optional_deaths
                lower = deaths / min_denominator if min_denominator else 1.0
                upper = (deaths + optional_deaths) / max_denominator if max_denominator else 0.0
            risks[group] = (lower, upper)
            cell.update({f'n_fixed_{name}': count, f'n_optional_{name}': len(optional),
                         f'risk_lower_{name}': lower, f'risk_upper_{name}': upper})
        cell['delta_lower'] = risks[1][0] - risks[0][1]
        cell['delta_upper'] = risks[1][1] - risks[0][0]
        rows.append(cell)
    return pd.DataFrame(rows)


def test_regressions() -> None:
    """Check derivatives, patient dependence, fixed weights and score bounds."""
    base = pd.DataFrame(dict(pid=list('abcdaefgbceh'), score=[0] * 8 + [1] * 4,
                             grp=[0] * 4 + [1] * 4 + [0] * 2 + [1] * 2,
                             y=[0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0]))
    base['rw'] = 1.0
    result = direct_contrast(base, record_weight_col='rw')
    assert abs(result.cluster_influence.sum()) < 1e-12
    assert result.n_patients == 8
    assert np.isclose(result.estimate, 1 / 6)
    for pid in base.pid.unique():
        perturbed = base.copy()
        epsilon = 1e-5
        perturbed.loc[perturbed.pid == pid, 'rw'] += epsilon
        derivative = (direct_contrast(perturbed, record_weight_col='rw').estimate
                      - result.estimate) / epsilon
        assert np.isclose(derivative, result.cluster_influence[pid], atol=1e-6)
    fixed = direct_contrast(base, fixed_weights={0: 0.5, 1: 0.5})
    assert np.isclose(fixed.estimate, 0.0)
    assert not np.isclose(fixed.se, result.se)
    assert np.isclose(paired_difference(result, result)['se'], 0.0)
    partial_support = pd.concat([base, pd.DataFrame(dict(pid=['z'], score=[2], grp=[0], y=[1], rw=[1.0]))], ignore_index=True)
    partial = direct_contrast(partial_support, record_weight_col='rw')
    assert partial.n_inference_clusters == 9 and partial.n_patients == 8
    assert partial.cluster_influence['z'] == 0
    assert np.isclose(partial.se / result.se, np.sqrt(63 / 64))
    bounds_data = pd.DataFrame(dict(grp=[0, 0, 1, 1], y=[1, 0, 0, 1],
                                     score_lower=[0, 0, 0, 0], score_upper=[0, 1, 0, 1]))
    bounds = incomplete_score_bounds(bounds_data, 1)
    assert np.isclose(bounds.loc[0, 'delta_lower'], -1)
    assert np.isclose(bounds.loc[0, 'delta_upper'], 0)
    print('PASS independent direct-contrast derivative, paired covariance and missingness-bound regressions')


if __name__ == '__main__':
    test_regressions()

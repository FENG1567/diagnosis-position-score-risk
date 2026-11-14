"""Patient-cluster Hoeffding interval for a conditional-design mean contrast.

The observed complete-case design, common support and record weights are fixed.
Mutually independent patient clusters conditional on that design are required.
"""
from math import log, sqrt

import numpy as np
import pandas as pd


def conditional_design_interval(frame, alpha=0.05):
    """Return pointwise bounds for E(sum_i a_i Y_i | observed design)."""
    if not 0 < alpha < 1:
        raise ValueError('alpha must lie between zero and one')
    required = ['pid', 'score', 'grp', 'y']
    if frame[required].isna().any().any():
        raise ValueError('Complete patient identifiers, scores, groups and outcomes are required')
    if not frame.grp.isin([0, 1]).all() or not frame.y.isin([0, 1]).all():
        raise ValueError('Groups and outcomes must be binary')
    score = frame.score.to_numpy(float)
    if not np.isfinite(score).all() or not np.equal(score, np.floor(score)).all():
        raise ValueError('Scores must be finite integers')
    levels = np.intersect1d(frame.loc[frame.grp == 0, 'score'].unique(),
                           frame.loc[frame.grp == 1, 'score'].unique())
    result = dict(target='conditional-design mean contrast theta_D',
                  confidence_level=1 - alpha,
                  assumption='independent patient clusters conditional on the observed complete-case design',
                  n_input_records=len(frame), n_input_patients=frame.pid.nunique(),
                  levels=len(levels))
    if not len(levels):
        return dict(result, state='no common support', point=np.nan, lower=np.nan,
                    upper=np.nan, halfwidth=np.nan, width=np.nan, full_range=False,
                    halfwidth_ge_one=False, n_supported_records=0, n_supported_patients=0,
                    sum_squared_cluster_ranges=np.nan)
    supported = frame.loc[frame.score.isin(levels)].copy()
    weights = supported.groupby('score').size() / len(supported)
    counts = supported.groupby(['score', 'grp']).y.transform('size')
    coefficient = supported.score.map(weights).to_numpy(float) / counts.to_numpy(float)
    coefficient *= np.where(supported.grp.to_numpy() == 1, 1.0, -1.0)
    ranges = pd.Series(np.abs(coefficient), index=supported.index).groupby(supported.pid).sum()
    sum_squares = float(np.square(ranges.to_numpy()).sum())
    margin = sqrt(log(2 / alpha) * sum_squares / 2)
    point = float(coefficient @ supported.y.to_numpy(float))
    lower, upper = max(-1.0, point - margin), min(1.0, point + margin)
    return dict(result, state='conditional interval computed', point=point,
                lower=lower, upper=upper, halfwidth=margin, width=upper - lower,
                full_range=lower == -1.0 and upper == 1.0,
                halfwidth_ge_one=margin >= 1.0,
                n_supported_records=len(supported), n_supported_patients=supported.pid.nunique(),
                sum_squared_cluster_ranges=sum_squares)

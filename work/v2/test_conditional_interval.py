from math import log, sqrt

import numpy as np
import pandas as pd
import pytest

from conditional_interval import conditional_design_interval
from estimands import direct_contrast


def test_point_and_cluster_range_with_cross_group_patients():
    frame = pd.DataFrame(dict(pid=[1, 2, 1, 3, 4, 5, 4, 6],
                              score=[0, 0, 0, 0, 1, 1, 1, 1],
                              grp=[0, 0, 1, 1, 0, 0, 1, 1],
                              y=[0, 1, 1, 1, 0, 0, 0, 1]))
    result = conditional_design_interval(frame)
    assert np.isclose(result['point'], direct_contrast(frame).estimate)
    # Each coefficient has magnitude 1/4. Two patients have two records.
    assert np.isclose(result['sum_squared_cluster_ranges'], 2 * 0.5**2 + 4 * 0.25**2)
    assert np.isclose(result['halfwidth'], sqrt(log(40) * 0.75 / 2))


def test_large_margin_and_clipped_full_range_are_distinct():
    frame = pd.DataFrame(dict(pid=[1, 2], score=[0, 0], grp=[0, 1], y=[0, 1]))
    result = conditional_design_interval(frame)
    assert result['halfwidth_ge_one']
    assert not result['full_range']
    assert result['upper'] == 1


def test_no_support_and_input_validation():
    frame = pd.DataFrame(dict(pid=[1, 2], score=[0, 1], grp=[0, 1], y=[0, 1]))
    assert conditional_design_interval(frame)['state'] == 'no common support'
    with pytest.raises(ValueError):
        conditional_design_interval(frame.assign(y=[0, np.nan]))
    with pytest.raises(ValueError):
        conditional_design_interval(frame.assign(score=[0, 1.5]))


def test_zero_event_arms_still_have_design_based_uncertainty():
    frame = pd.DataFrame(dict(pid=np.arange(40), score=np.zeros(40),
                              grp=np.repeat([0, 1], 20), y=np.zeros(40)))
    result = conditional_design_interval(frame)
    assert result['point'] == 0
    assert result['lower'] < 0 < result['upper']

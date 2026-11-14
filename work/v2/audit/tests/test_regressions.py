import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cohort_definition_audit import (
    audit_v2,
    per_level_inference,
    stratified_rd,
    stratified_rd_se,
    stratified_rd_var,
)


def _weighted_fixture():
    rows = []
    pid = 0
    # p1-p0 = +0.3 at score 0 and -0.3 at score 1; the pooled record weights vary
    # across repeated samples, so estimated-weight uncertainty must be nonzero.
    for score, outcomes in (
        (0, {1: [0, 0, 1, 1, 0, 0, 1, 0, 0, 1], 0: [0, 0, 0, 1, 0, 0, 0, 0, 1, 0]}),
        (1, {1: [0, 0, 0, 1, 0, 0, 0, 0, 0, 1], 0: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]}),
    ):
        for grp in (0, 1):
            for y in outcomes[grp]:
                rows.append((pid, score, grp, y))
                pid += 1
    return pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])


def test_estimated_weight_if_includes_score_distribution_term():
    d = _weighted_fixture()
    s, y, g, pid = (d.score.to_numpy(float), d.y.to_numpy(float),
                    d.grp.to_numpy(int), d.pid.to_numpy())
    _, _, _, levels = stratified_rd(s, y, g)
    w = {row["level"]: row["weight"] for row in levels}
    se_estimated, _ = stratified_rd_se(s, y, g, pid)
    se_fixed, _ = stratified_rd_se(s, y, g, pid, fixed_weights=w)
    assert se_estimated > se_fixed


def test_fixed_reference_weights_define_a_separate_estimator():
    d = _weighted_fixture()
    estimate, _, _, detail = stratified_rd(
        d.score.to_numpy(float), d.y.to_numpy(float), d.grp.to_numpy(int),
        support_levels=[0, 1], fixed_weights={0.0: 0.8, 1.0: 0.2})
    risks = {row["level"]: (row["risk_never"] - row["risk_primary"]) / 100
             for row in detail}
    assert np.isclose(estimate, 0.8 * risks[0.0] + 0.2 * risks[1.0])


def test_cluster_if_sums_signed_cross_definition_contributions_first():
    rows = []
    for pid, y in enumerate([0, 1] * 20):
        rows.extend([(pid, 0.0, 0, float(y)), (pid, 0.0, 1, float(y))])
    d = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
    se, _ = stratified_rd_se(d.score.to_numpy(float), d.y.to_numpy(float),
                             d.grp.to_numpy(int), d.pid.to_numpy())
    assert se < 1e-12


def test_prespecified_support_loss_keeps_changed_support_point_but_withholds_interval():
    rows = []
    for score in (0, 1):
        for grp in (0, 1):
            if score == 1 and grp == 1:
                continue
            for j in range(30):
                rows.append((f"{score}-{grp}-{j}", score, grp, int(j % 3 == 0)))
    d = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
    result = audit_v2(d, expected_levels=[0, 1], config={"reps": 0})
    assert result["target_support_status"] == "target_support_lost"
    assert result["population_target_rd_pp"] is None
    assert result["observed_supported_rd_pp"] is not None
    assert result["delta_ci_pp"] is None
    assert "target_support_lost" in result["refusal_reasons"]


def test_exact_event_counts_do_not_refuse_rare_but_nonzero_risk_as_degenerate():
    n = 30_000
    rows = [(f"p{j}", 0.0, 1, int(j == 0)) for j in range(n)]
    rows += [(f"q{j}", 0.0, 0, int(j < 10)) for j in range(n)]
    d = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
    result = audit_v2(
        d, expected_levels=[0],
        config={"reps": 0, "min_clusters": 1, "min_arm_n": 1,
                "min_level_n": 1, "min_usable_bootstrap": 1})
    assert result["per_level"][0]["risk_never"] == 0.0  # rounded display value
    assert "degenerate_outcome_cell" not in result["refusal_reasons"]


def test_per_level_intervals_are_independent_of_summary_refusal():
    rows = []
    for score in (0, 1):
        n_by_group = {0: 30, 1: (30 if score == 0 else 5)}
        for grp in (0, 1):
            for j in range(n_by_group[grp]):
                # Score 0 has variation in both groups; score 1's never group has no events.
                y = int((j % 4 == 0) if score == 0 else (grp == 0 and j % 3 == 0))
                rows.append((f"{score}-{grp}-{j}", score, grp, y))
    d = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
    result = audit_v2(
        d, expected_levels=[0, 1],
        config={"reps": 0, "min_clusters": 10, "min_arm_n": 10,
                "min_level_n": 20, "min_usable_bootstrap": 1})
    assert result["delta_ci_pp"] is None
    by_level = {row["level"]: row for row in result["per_level"]}
    assert by_level[0.0]["delta_ci_pp"] is not None
    assert by_level[1.0]["delta_ci_pp"] is None
    assert by_level[0.0]["risk_never_ci_pp"] is not None
    assert by_level[1.0]["risk_never_ci_pp"] is None


def test_cluster_variance_uses_patient_finite_sample_correction():
    d = _weighted_fixture()
    var, n = stratified_rd_var(d.score.to_numpy(float), d.y.to_numpy(float),
                               d.grp.to_numpy(int), d.pid.to_numpy())
    se, _ = stratified_rd_se(d.score.to_numpy(float), d.y.to_numpy(float),
                             d.grp.to_numpy(int), d.pid.to_numpy())
    assert n == len(d)
    assert np.isclose(var, se ** 2)

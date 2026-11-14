import sys
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import benchmark
from cohort_definition_audit import stratified_rd, stratified_rd_se


def test_frozen_design_targets_and_weights_are_reproducible():
    cfg = benchmark.load_config(Path(__file__).resolve().parents[1] / "benchmark_config.json")
    assert cfg["outer_replicates_per_design"] >= 1000
    design = next(item for item in cfg["designs"] if item["name"] == "partial_structural_support")
    truth, weights = benchmark.truth_and_weights(design)
    assert design["expected_support"] == [2, 3]
    assert weights == {2.0: 0.5, 3.0: 0.5}
    assert truth == 0.2


def test_B_checks_a_missing_prespecified_target_cell():
    d = pd.DataFrame({"score": [0] * 30, "grp": [0] * 15 + [1] * 15})
    assert not benchmark.strategy_b(d, levels=[0, 1], minimum=10)


def test_conditional_weight_truth_is_separate_and_missing_after_support_loss():
    design = {
        "scores": [0, 1], "expected_support": [0, 1],
        "joint_probabilities_group_score": [[0.25, 0.25], [0.25, 0.25]],
        "risks_principal": [0.1, 0.2], "risks_never": [0.3, 0.4],
    }
    complete = pd.DataFrame({"score": [0] * 30 + [1] * 20 + [0] * 10 + [1] * 40,
                             "grp": [0] * 50 + [1] * 50})
    conditional, status = benchmark.conditional_observed_weight_truth(complete, design)
    assert conditional == 0.2
    assert status == "complete"
    lost = pd.DataFrame({"score": [0] * 40, "grp": [0] * 20 + [1] * 20})
    conditional_lost, status_lost = benchmark.conditional_observed_weight_truth(lost, design)
    assert conditional_lost is None
    assert status_lost == "target_support_lost"


def test_gaussian_copula_generator_reproduces_configured_marginals_in_large_sample():
    design = {
        "n_patients": 5000,
        "cluster_sizes": [[1, 1.0]],
        "outcome_icc": 0.0,
        "scores": [0],
        "joint_probabilities_group_score": [[0.5], [0.5]],
        "risks_principal": [0.20],
        "risks_never": [0.40],
        "expected_support": [0],
    }
    d = benchmark.simulate_dataset(design, __import__("numpy").random.default_rng(5481))
    means = d.groupby("grp").y.mean().to_dict()
    assert abs(means[0] - 0.20) < 0.04
    assert abs(means[1] - 0.40) < 0.04


def test_A_B_C_D_use_identical_full_precision_interval_at_coverage_boundary(monkeypatch):
    rows = []
    for score in (0, 1):
        for grp in (0, 1):
            for j in range(100):
                event = int(j % (5 + score + grp) == 0)
                rows.append((f"p-{score}-{grp}-{j}", score, grp, event))
    frame = pd.DataFrame(rows, columns=["pid", "score", "grp", "y"])
    rd, _, _, _ = stratified_rd(frame.score.to_numpy(float), frame.y.to_numpy(float),
                                frame.grp.to_numpy(int))
    se, _ = stratified_rd_se(frame.score.to_numpy(float), frame.y.to_numpy(float),
                             frame.grp.to_numpy(int), frame.pid.to_numpy())
    exact_lower_bound = rd - 1.96 * se
    design = {
        "name": "rounding_boundary_test", "expected_support": [0, 1],
        "scores": [0, 1], "risks_principal": [0.2, 0.2],
        "risks_never": [0.3, 0.3],
    }
    monkeypatch.setattr(benchmark, "simulate_dataset", lambda design, rng: frame.copy())
    monkeypatch.setattr(benchmark, "truth_and_weights",
                        lambda design: (exact_lower_bound, {0.0: 0.5, 1.0: 0.5}))
    records = benchmark.evaluate_design(design, 0,
                                        {"seed": 10, "outer_replicates_per_design": 1},
                                        bootstrap_reps=60)
    main = {row["policy"]: row for row in records if row["policy"] in {"A", "B", "C", "D"}}
    assert set(main) == {"A", "B", "C", "D"}
    assert all(row["interval_emitted"] for row in main.values())
    reference = (main["A"]["point"], main["A"]["se"],
                 main["A"]["interval_width"], main["A"]["covered"])
    for policy in ("B", "C", "D"):
        candidate = (main[policy]["point"], main[policy]["se"],
                     main[policy]["interval_width"], main[policy]["covered"])
        assert candidate == reference
    assert main["A"]["covered"] is True

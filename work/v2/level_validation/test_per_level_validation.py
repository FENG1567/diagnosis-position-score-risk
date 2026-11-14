"""Focused contract checks against the frozen shared per-level CI function."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_per_level_validation import _summary_metric, analyze, load_sources  # noqa: E402


class PerLevelInferenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, inference = load_sources()
        cls.per_level_inference = staticmethod(inference)

    def test_zero_events_suppress_group_and_delta_intervals(self):
        n_per_group = 500
        frame = pd.DataFrame({
            "pid": np.arange(2 * n_per_group),
            "score": np.zeros(2 * n_per_group),
            "grp": np.repeat([0, 1], n_per_group),
            "outcome": np.zeros(2 * n_per_group),
        })
        [result] = self.per_level_inference(frame, [0.0])

        self.assertEqual(result["risk_primary_ci_status"],
                         "degenerate outcome: point estimate only")
        self.assertEqual(result["risk_never_ci_status"],
                         "degenerate outcome: point estimate only")
        self.assertEqual(result["delta_ci_status"],
                         "degenerate outcome: point estimate only")
        self.assertIsNone(result["risk_primary_ci_pp"])
        self.assertIsNone(result["risk_never_ci_pp"])
        self.assertIsNone(result["delta_ci_pp"])

    def test_large_independent_cells_cover_known_risks_on_shared_function_path(self):
        # Each record is a distinct patient, so the configured inference call sees
        # independent Bernoulli cells with known risks 0.30 and 0.40.
        n_per_group = 25_000
        rng = np.random.default_rng(20261112)
        principal = rng.binomial(1, 0.30, size=n_per_group).astype(float)
        never = rng.binomial(1, 0.40, size=n_per_group).astype(float)
        frame = pd.DataFrame({
            "pid": np.arange(2 * n_per_group),
            "score": np.zeros(2 * n_per_group),
            "grp": np.repeat([0, 1], n_per_group),
            "outcome": np.concatenate([principal, never]),
        })

        # Read and validate the interval arrays returned directly by the frozen tool;
        # the test does not implement a second CI formula.
        [result] = self.per_level_inference(frame, [0.0])
        self.assertEqual(result["risk_primary_ci_status"], "computed")
        self.assertEqual(result["risk_never_ci_status"], "computed")
        self.assertEqual(result["delta_ci_status"], "computed")
        self.assertTrue(result["risk_primary_ci_pp"][0] <= 30.0 <=
                        result["risk_primary_ci_pp"][1])
        self.assertTrue(result["risk_never_ci_pp"][0] <= 40.0 <=
                        result["risk_never_ci_pp"][1])
        self.assertTrue(result["delta_ci_pp"][0] <= 10.0 <=
                        result["delta_ci_pp"][1])
        self.assertEqual(result["risk_primary_ci_pp"], [29.49, 30.63])
        self.assertEqual(result["risk_never_ci_pp"], [39.61, 40.82])
        self.assertEqual(result["delta_ci_pp"], [9.32, 10.99])

    def test_summary_adapter_preserves_refusals_and_arm_counts(self):
        metric_items = [{
            "ci_status": "computed", "ci_bounds": [9.0, 11.0], "point_pp": 10.0,
            "n0": 100, "n1": 120, "patients0": 100, "patients1": 120,
            "events0": 30, "events1": 40,
        }, {
            "ci_status": "below record-count threshold", "ci_bounds": None,
            "point_pp": 10.0, "n0": 5, "n1": 7, "patients0": 5,
            "patients1": 7, "events0": 2, "events1": 3,
        }]
        summary = _summary_metric(metric_items, 10.0, "delta_s", "ci_status",
                                  "ci_bounds", "point_pp", True)

        self.assertEqual(summary["n_eligible_replicates"], 2)
        self.assertEqual(summary["n_ci_emitted"], 1)
        self.assertEqual(summary["conditional_coverage"], 1.0)
        self.assertEqual(summary["principal_records_mean"], 52.5)
        self.assertEqual(summary["never_records_mean"], 63.5)
        self.assertEqual(summary["refusal_counts_json"],
                         '{"below record-count threshold": 1}')

    def test_all_eleven_designs_complete_two_replicate_pipeline_pilot(self):
        repo_root = HERE.parents[2]
        config_path = HERE / "per_level_validation_config.json"
        output_dir = repo_root / "_generated" / "tests" / "per_level_pilot_seed_27112028"
        manifest = analyze(config_path, output_dir, pilot=True)

        self.assertEqual(manifest["run_mode"], "pipeline_pilot")
        self.assertEqual(manifest["seed"], 27112028)
        self.assertEqual(manifest["replicates_per_design"], 2)
        self.assertEqual(manifest["design_count"], 11)
        self.assertEqual(manifest["dataset_count"], 22)
        self.assertEqual(len(manifest["per_design_checkpoints"]), 11)

        recovered = analyze(config_path, output_dir, pilot=True, aggregate_only=True)
        self.assertEqual(recovered["run_mode"], "pipeline_pilot_aggregate_only")
        self.assertEqual(recovered["dataset_count"], 22)

        summary = pd.read_csv(output_dir / "per_level_summary.csv")
        required_count_fields = {"principal_records_mean", "never_records_mean",
                                 "principal_patients_mean", "never_patients_mean"}
        self.assertTrue(required_count_fields.issubset(summary.columns))
        no_support = summary[(summary["design"] == "no_common_support") &
                             (summary["estimand"] == "delta_s")]
        self.assertEqual(len(no_support), 4)
        self.assertFalse(no_support["truth_defined"].any())
        self.assertTrue(no_support["n_eligible_replicates"].eq(0).all())

        partial = summary[(summary["design"] == "partial_structural_support") &
                          (summary["estimand"] == "delta_s")]
        self.assertEqual(int(partial["truth_defined"].sum()), 2)
        self.assertTrue(partial.loc[partial["truth_defined"],
                                    "n_eligible_replicates"].eq(2).all())
        self.assertEqual(len(list((output_dir / "replicate_checkpoints").glob("*.csv"))), 11)


if __name__ == "__main__":
    unittest.main()

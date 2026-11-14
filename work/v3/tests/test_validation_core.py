"""Synthetic checks for v3 splits, logistic fitting, and clustered losses."""

import math
import sys
import unittest
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from scipy.optimize import brentq


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "work" / "v3" / "validation"))

import count_eligibility as eligibility  # noqa: E402
import fit_and_validate as validation  # noqa: E402


class ValidationCoreTests(unittest.TestCase):
    def test_shared_boundary_quasi_separation_is_refused_both_directions(self):
        samples = (
            ([{"score": 0, "outcome": 0}] * 4
             + [{"score": 1, "outcome": 0}] * 2
             + [{"score": 1, "outcome": 1}] * 2
             + [{"score": 2, "outcome": 1}] * 4),
            ([{"score": 0, "outcome": 1}] * 4
             + [{"score": 1, "outcome": 0}] * 2
             + [{"score": 1, "outcome": 1}] * 2
             + [{"score": 2, "outcome": 0}] * 4),
        )
        for records in samples:
            with self.subTest(direction=records[0]["outcome"]):
                stats = validation.grouped_stats(records, lambda row: row["score"])
                self.assertTrue(validation.separated(stats))
                with self.assertRaises(validation.FitFailure):
                    validation.fit_logistic(records, lambda row: row["score"], "synthetic-quasi")

    def test_logistic_mle_matches_independent_logit_and_score_equations(self):
        score_cells = {0: (8, 2), 1: (10, 4), 2: (12, 8)}
        records = [
            {"score": score, "outcome": outcome}
            for score, (n, events) in score_cells.items()
            for outcome in ([1] * events + [0] * (n - events))
        ]
        result = validation.fit_logistic(records, lambda row: row["score"], "synthetic-mle")
        x = np.asarray([row["score"] for row in records], dtype=float)
        y = np.asarray([row["outcome"] for row in records], dtype=float)
        reference = sm.Logit(y, np.column_stack((np.ones(len(x)), x))).fit(disp=False)
        self.assertTrue(
            np.allclose([result["beta0"], result["beta1"]], reference.params,
                        atol=1e-8, rtol=1e-8)
        )
        probabilities = np.asarray([
            validation.expit(result["beta0"] + result["beta1"] * value) for value in x
        ])
        self.assertLess(abs(float(np.sum(y - probabilities))), 1e-7)
        self.assertLess(abs(float(np.sum((y - probabilities) * x))), 1e-7)

    def test_offset_intercept_matches_independent_root(self):
        records = []
        for score, outcomes in (
            (0, [1] + [0] * 7),
            (1, [1] * 3 + [0] * 7),
            (2, [1] * 7 + [0] * 5),
        ):
            records.extend({"score": score, "outcome": outcome} for outcome in outcomes)
        eta = lambda row: -1.5 + 0.65 * row["score"]
        result = validation.fit_offset_intercept(records, eta, "synthetic-offset")
        offsets = np.asarray([eta(row) for row in records], dtype=float)
        events = sum(row["outcome"] for row in records)
        reference = brentq(
            lambda delta: sum(validation.expit(value + delta) for value in offsets) - events,
            -80,
            80,
        )
        self.assertAlmostEqual(result["delta"], reference, places=8)

    def test_extreme_logit_losses_remain_finite(self):
        records = [
            {"outcome": outcome, "eta": eta}
            for outcome, eta in ((0, -1000.0), (1, 1000.0), (1, -1000.0), (0, 1000.0))
        ]
        result = validation.point_losses(records, lambda row: row["eta"])
        self.assertTrue(math.isfinite(result["brier"]))
        self.assertTrue(math.isfinite(result["log_loss"]))
        self.assertAlmostEqual(result["brier"], 0.5, places=12)
        self.assertAlmostEqual(result["log_loss"], 500.0, places=12)

    def test_patient_bootstrap_is_record_weighted_and_paired_across_maps(self):
        records = []

        def add(patient, group, outcome, score):
            index = len(records)
            base = -0.9 + 0.37 * score + 0.03 * index
            records.append({
                "pid": patient,
                "admission_id": f"synthetic-admission-{index}",
                "hospital": "synthetic-hospital",
                "group": group,
                "outcome": outcome,
                "score": score,
                "etas": {
                    "primary_only_fixed": base,
                    "broad_fixed": base + 0.23,
                    "primary_only_recalibrated": base - 0.17,
                    "broad_recalibrated": base + 0.41,
                },
            })

        for row in (
            ("synthetic-p1", 0, 0, 0), ("synthetic-p1", 0, 1, 1), ("synthetic-p1", 0, 0, 1),
            ("synthetic-p2", 0, 1, 2),
            ("synthetic-p3", 1, 0, 0), ("synthetic-p3", 1, 1, 2),
            ("synthetic-p4", 0, 0, 0), ("synthetic-p4", 1, 1, 1), ("synthetic-p4", 1, 0, 2),
        ):
            add(*row)

        old_reps = validation.BOOTSTRAP_REPS
        validation.BOOTSTRAP_REPS = 17
        try:
            result = validation.patient_bootstrap(records, "synthetic-db", "synthetic-disease")
        finally:
            validation.BOOTSTRAP_REPS = old_reps

        patients = sorted({row["pid"] for row in records})
        probabilities = np.full(len(patients), 1.0 / len(patients), dtype=float)
        probabilities /= probabilities.sum()
        draws = np.random.default_rng(result["rng_seed"]).multinomial(
            len(patients), probabilities, size=17
        )
        expected_metrics = {
            group: {name: {loss: [] for loss in validation.LOSS_NAMES}
                    for name in validation.MAP_NAMES}
            for group in validation.GROUPS
        }
        expected_contrasts = {
            group: {name: {loss: [] for loss in validation.LOSS_NAMES}
                    for name, _, _ in validation.CONTRASTS}
            for group in validation.GROUPS
        }

        for multiplicities in draws:
            means_by_group = {}
            denominators = {}
            for group in validation.GROUPS:
                selected = [
                    row for row in records
                    if group == "all"
                    or (group == "primary" and row["group"] == 0)
                    or (group == "never_primary" and row["group"] == 1)
                ]
                weights = [int(multiplicities[patients.index(row["pid"])]) for row in selected]
                denominator = sum(weights)
                denominators[group] = denominator
                means_by_group[group] = {}
                if denominator == 0:
                    continue
                for map_name in validation.MAP_NAMES:
                    sums = {loss: 0.0 for loss in validation.LOSS_NAMES}
                    for row, weight in zip(selected, weights):
                        eta = row["etas"][map_name]
                        probability = validation.expit(eta)
                        sums["brier"] += weight * (probability - row["outcome"]) ** 2
                        sums["log_loss"] += weight * (
                            validation.log1pexp(eta) - row["outcome"] * eta
                        )
                    means_by_group[group][map_name] = {
                        loss: sums[loss] / denominator for loss in validation.LOSS_NAMES
                    }
                    for loss in validation.LOSS_NAMES:
                        expected_metrics[group][map_name][loss].append(
                            means_by_group[group][map_name][loss]
                        )
            self.assertEqual(
                denominators["all"], denominators["primary"] + denominators["never_primary"]
            )
            for group in validation.GROUPS:
                for contrast, left, right in validation.CONTRASTS:
                    for loss in validation.LOSS_NAMES:
                        expected_contrasts[group][contrast][loss].append(
                            means_by_group[group][left][loss] - means_by_group[group][right][loss]
                        )

        for group in validation.GROUPS:
            for map_name in validation.MAP_NAMES:
                for loss in validation.LOSS_NAMES:
                    np.testing.assert_allclose(
                        result["metric_draws"][group][map_name][loss],
                        expected_metrics[group][map_name][loss],
                        atol=1e-12,
                        rtol=1e-12,
                    )
            for contrast, _, _ in validation.CONTRASTS:
                for loss in validation.LOSS_NAMES:
                    np.testing.assert_allclose(
                        result["contrast_draws"][group][contrast][loss],
                        expected_contrasts[group][contrast][loss],
                        atol=1e-12,
                        rtol=1e-12,
                    )

        models = {
            "primary_only": {"beta0": -1.2, "beta1": 0.4},
            "broad": {"beta0": -1.0, "beta1": 0.3},
        }
        deltas = {"primary_only": -0.17, "broad": 0.41}
        metric_rows = validation.build_metric_rows(
            "synthetic-db", "synthetic-disease", records, models, deltas, result
        )
        for group in validation.GROUPS:
            group_rows = [row for row in metric_rows if row["test_group"] == group]
            record_counts = {row["prediction"]: row["records"] for row in group_rows}
            self.assertEqual(set(record_counts), set(validation.MAP_NAMES))
            self.assertEqual(len(set(record_counts.values())), 1)
            expected_n = len(records) if group == "all" else sum(
                row["group"] == (0 if group == "primary" else 1) for row in records
            )
            self.assertEqual(next(iter(record_counts.values())), expected_n)

    def test_eicu_and_mimic_roles_are_deterministic_and_disjoint(self):
        def hospital_for(target):
            for index in range(10000):
                candidate = f"synthetic-hospital-{target}-{index}"
                if eligibility.bucket_role(
                    eligibility.hash_bucket("eICU-hospital", candidate)
                ) == target:
                    return candidate
            self.fail("No synthetic hospital bucket found")

        train_hospital, recal_hospital, test_hospital = [
            hospital_for(role) for role in eligibility.ROLES
        ]
        eicu_rows = [
            {"pid": f"synthetic-role-p-{role}", "hospital": hospital,
             "role": None, "role_reason": None}
            for role, hospital in zip(
                eligibility.ROLES, (train_hospital, recal_hospital, test_hospital)
            )
        ]
        eicu_copy = [dict(row) for row in eicu_rows]
        eligibility.assign_eicu(eicu_rows)
        eligibility.assign_eicu(eicu_copy)
        self.assertEqual([row["role"] for row in eicu_rows], list(eligibility.ROLES))
        self.assertEqual([row["role"] for row in eicu_rows], [row["role"] for row in eicu_copy])
        zero_overlap = {
            "patient_role_overlap": 0,
            "hospital_role_overlap": 0,
            "multihospital_patient_overlap": 0,
        }
        self.assertEqual(validation.check_role_disjointness(eicu_rows, "eICU"), zero_overlap)

        cross_role = [
            {"pid": "synthetic-cross-role", "hospital": train_hospital,
             "role": None, "role_reason": None},
            {"pid": "synthetic-cross-role", "hospital": test_hospital,
             "role": None, "role_reason": None},
        ]
        eligibility.assign_eicu(cross_role)
        self.assertTrue(all(row["role"] is None for row in cross_role))
        self.assertEqual(validation.check_role_disjointness(cross_role, "eICU"), zero_overlap)

        mimic_rows = [
            {"pid": "synthetic-mimic-p1", "anchor_group": "2008-2013",
             "anchor_year": 2010, "admit_year": 2010, "role": None, "role_reason": None},
            {"pid": "synthetic-mimic-p2", "anchor_group": "2014-2015",
             "anchor_year": 2014, "admit_year": 2014, "role": None, "role_reason": None},
            {"pid": "synthetic-mimic-p3", "anchor_group": "2017-2018",
             "anchor_year": 2017, "admit_year": 2017, "role": None, "role_reason": None},
            {"pid": "synthetic-mimic-cross", "anchor_group": "2008-2013",
             "anchor_year": 2010, "admit_year": 2010, "role": None, "role_reason": None},
            {"pid": "synthetic-mimic-cross", "anchor_group": "2017-2018",
             "anchor_year": 2017, "admit_year": 2017, "role": None, "role_reason": None},
        ]
        mimic_copy = [dict(row) for row in mimic_rows]
        metadata = eligibility.assign_mimic(mimic_rows)
        eligibility.assign_mimic(mimic_copy)
        self.assertTrue(metadata["temporal_metadata_identifiable"])
        self.assertEqual([row["role"] for row in mimic_rows[:3]], list(eligibility.ROLES))
        self.assertEqual([row["role"] for row in mimic_rows], [row["role"] for row in mimic_copy])
        self.assertIsNone(mimic_rows[3]["role"])
        self.assertIsNone(mimic_rows[4]["role"])
        self.assertEqual(validation.check_role_disjointness(mimic_rows, "MIMIC-IV"), zero_overlap)


if __name__ == "__main__":
    unittest.main()

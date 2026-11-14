"""Synthetic regression checks for the eICU v2 extraction rules."""
from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

import build_eicu_v2 as eicu


class EicuRulesTest(unittest.TestCase):
    def test_icd_code_tokens_do_not_concatenate(self):
        codes = eicu.parse_codes("428.0, 402.01; I50.9")
        self.assertEqual(codes, ("4280", "40201", "I509"))
        self.assertFalse(eicu.has_prefix(codes, ("4280402",)))

    def test_narrow_broad_and_legacy_phenotypes_are_distinct(self):
        hf_without_failure = eicu.matches(eicu.parse_codes("402.00"), "", "heart_failure")
        self.assertFalse(hf_without_failure["narrow"])
        self.assertTrue(hf_without_failure["broad"])
        self.assertTrue(hf_without_failure["legacy_v1"])

        hf_with_failure = eicu.matches(eicu.parse_codes("402.01"), "", "heart_failure")
        self.assertTrue(hf_with_failure["narrow"])

        copd_bronchiectasis = eicu.matches(eicu.parse_codes("494.0"), "", "copd")
        self.assertFalse(copd_bronchiectasis["narrow"])
        self.assertTrue(copd_bronchiectasis["broad"])
        self.assertTrue(copd_bronchiectasis["legacy_v1"])

        chronic_pancreatitis = eicu.matches(eicu.parse_codes("577.1"), "", "pancreatitis")
        self.assertFalse(chronic_pancreatitis["narrow"])
        self.assertFalse(chronic_pancreatitis["broad"])
        self.assertTrue(chronic_pancreatitis["legacy_v1"])

    def test_score_missingness_is_not_zero_and_bounds_are_retained(self):
        index = pd.DataFrame({
            "index_patientunitstayid": [1],
            "admission_id": ["A"],
            "age": [68.0],
            "sex": ["female"],
            "died": [0.0],
        })
        measurements = pd.DataFrame({
            "rr_max": [25.0],
            "sbp_min": [np.nan],
            "dbp_min": [75.0],
            "gcs_min": [15.0],
            "gcs_valid_observation_count": [1],
            "confusion_chart_sensitivity": [np.nan],
            "urea_mmol_l_max": [8.0],
            "bun_mgdl_max": [23.0],
            "temperature_min": [37.0],
            "temperature_max": [37.0],
            "heartrate_max": [80.0],
            "wbc_k_ul_min": [3.0],
            "wbc_k_ul_max": [6.0],
        }, index=pd.Index([1], name="index_patientunitstayid"))
        scored = eicu.make_scores(index, measurements).iloc[0]
        self.assertFalse(bool(scored.qsofa_gcs13_complete))
        self.assertTrue(math.isnan(scored.qsofa_gcs13_score))
        self.assertEqual(scored.qsofa_gcs13_lower, 1.0)
        self.assertEqual(scored.qsofa_gcs13_upper, 2.0)
        self.assertEqual(scored.sirs_wbc_point, 1.0)

    def test_gcs_components_must_share_observation_time(self):
        rows = pd.DataFrame([
            [1, 0, "eye", 4.0],
            [1, 0, "motor", 6.0],
            [1, 0, "verbal", 5.0],
            [1, 60, "eye", 1.0],
            [2, 0, "eye", 4.0],
            [2, 0, "motor", 6.0],
            [3, 0, "total", 9.0],
        ], columns=["patientunitstayid", "offset", "role", "value"])
        out = eicu.summarize_gcs_rows(rows, {1, 2, 3, 4})
        self.assertEqual(out.loc[1, "gcs_min"], 15.0)
        self.assertTrue(pd.isna(out.loc[2, "gcs_min"]))
        self.assertEqual(out.loc[3, "gcs_min"], 9.0)
        self.assertTrue(pd.isna(out.loc[4, "gcs_min"]))

    def test_chunk_extrema_collapse_across_boundaries(self):
        a = pd.DataFrame({"rr_max": [21.0, 30.0]}, index=pd.Index([1, 2], name="patientunitstayid"))
        b = pd.DataFrame({"rr_max": [24.0, 18.0]}, index=pd.Index([1, 2], name="patientunitstayid"))
        maximum = eicu.collapse_parts([a, b], "rr_max", "max")
        self.assertEqual(maximum.loc[1], 24.0)
        self.assertEqual(maximum.loc[2], 30.0)
        source = pd.DataFrame({"patientunitstayid": [1, 1, 2], "respiration": [18, 24, 30]})
        parts = []
        eicu._extrema_parts(source, "respiration", "max", parts, "rr_max")
        self.assertEqual(eicu.collapse_parts(parts, "rr_max", "max").loc[1], 24.0)

    def test_first_unit_selection_uses_visit_then_hospital_chronology(self):
        p = pd.DataFrame({
            "patienthealthsystemstayid": ["A", "A", "A", "B"],
            "patientunitstayid": [100, 99, 98, 200],
            "unitvisitnumber": [2, 1, 1, 1],
            "hospitaladmitoffset": [-1000, -500, -400, -700],
            "elapsed_hospital_minutes_at_icu_admit": [1000, 500, 400, 700],
        })
        selected = eicu.select_first_stay(p).set_index("patienthealthsystemstayid")
        self.assertEqual(selected.loc["A", "patientunitstayid"], 98)
        self.assertEqual(selected.loc["B", "patientunitstayid"], 200)

    def test_diagnosis_offsets_align_to_hospital_admission(self):
        self.assertEqual(eicu.hospital_time_offset(0, -720), 720)
        self.assertEqual(eicu.hospital_time_offset(800, -700), 1500)
        self.assertEqual(eicu.hospital_time_offset(0, -5040), 5040)
        self.assertTrue(math.isnan(eicu.hospital_time_offset(np.nan, -720)))

    def test_primary_group_is_full_course_and_codes_are_never1_primary0(self):
        self.assertEqual(eicu.position_group(True, False), 1.0)
        self.assertEqual(eicu.position_group(True, True), 0.0)
        self.assertTrue(math.isnan(eicu.position_group(False, True)))
        self.assertTrue(math.isnan(eicu.position_group(True, np.nan)))


if __name__ == "__main__":
    unittest.main()

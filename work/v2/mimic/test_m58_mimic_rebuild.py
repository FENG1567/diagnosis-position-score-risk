"""Synthetic invariants for the MIMIC-IV extractor; contains no patient data."""
from __future__ import annotations

import gzip
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import m58_mimic_rebuild as m58


class MembershipTests(unittest.TestCase):
    def test_narrow_broad_and_legacy_phenotypes_are_separate(self):
        dx = pd.DataFrame([
            # Principal pneumonia code belongs to narrow and broad.
            {"subject_id": 1, "hadm_id": 10, "seq_num": 1, "icd_code": "J15.9", "icd_version": 10},
            # Secondary aspiration pneumonia is broad only.
            {"subject_id": 2, "hadm_id": 20, "seq_num": 2, "icd_code": "J69.0", "icd_version": 10},
            # Acute pancreatitis is exact 5770; chronic 5771 must not enter main.
            {"subject_id": 3, "hadm_id": 30, "seq_num": 1, "icd_code": "577.0", "icd_version": 9},
            {"subject_id": 4, "hadm_id": 40, "seq_num": 1, "icd_code": "577.1", "icd_version": 9},
            # Hypertensive heart disease without HF is legacy-only.
            {"subject_id": 5, "hadm_id": 50, "seq_num": 1, "icd_code": "I11.9", "icd_version": 10},
            # J47 bronchiectasis is legacy COPD only.
            {"subject_id": 6, "hadm_id": 60, "seq_num": 1, "icd_code": "J47.9", "icd_version": 10},
        ])
        out = m58.build_memberships(dx).set_index(["disease", "hadm_id"])
        self.assertEqual(int(out.loc[("pneumonia", 10), "narrow_inclusion"]), 1)
        self.assertEqual(int(out.loc[("pneumonia", 20), "narrow_inclusion"]), 0)
        self.assertIn(("pancreatitis", 30), out.index)
        self.assertIn(("pancreatitis", 40), out.index)
        self.assertEqual(int(out.loc[("pancreatitis", 40), "broad_inclusion"]), 0)
        self.assertEqual(int(out.loc[("pancreatitis", 40), "legacy_broad_inclusion"]), 1)
        self.assertTrue(pd.isna(out.loc[("pancreatitis", 40), "grp"]))
        self.assertIn(("heart failure", 50), out.index)
        self.assertEqual(int(out.loc[("heart failure", 50), "broad_inclusion"]), 0)
        self.assertEqual(int(out.loc[("heart failure", 50), "legacy_broad_inclusion"]), 1)
        self.assertIn(("COPD", 60), out.index)
        self.assertEqual(int(out.loc[("COPD", 60), "legacy_broad_inclusion"]), 1)
        self.assertEqual(int(out.loc[("COPD", 60), "broad_inclusion"]), 0)

    def test_diagnosis_sequence_audit_counts_unranked_values(self):
        dx = pd.DataFrame({"seq_num": [1, 2, None, 0, "bad"]})
        got = m58._diagnosis_sequence_position_audit(dx)
        self.assertEqual(got["diagnosis_rows"], 5)
        self.assertEqual(got["seq_num_missing_rows"], 1)
        self.assertEqual(got["seq_num_invalid_nonmissing_rows"], 1)
        self.assertEqual(got["seq_num_nonpositive_rows"], 1)
        self.assertEqual(got["seq_num_unranked_rows"], 3)
        self.assertFalse(got["matching_diagnosis_unranked_rows_proven_zero"])


class WindowTests(unittest.TestCase):
    def test_known_death_caps_window_before_discharge_and_outtime(self):
        intime = pd.Timestamp("2020-01-01 00:00:00")
        f = pd.DataFrame({
            "intime": [intime],
            "dischtime": [intime + pd.Timedelta(hours=8)],
            "deathtime": [intime + pd.Timedelta(hours=4)],
            "outtime": [intime + pd.Timedelta(hours=12)],
            "died": [1],
        })
        got = m58.add_observation_windows(f)
        end = got.loc[0, "chart_window_end"]
        self.assertEqual(end, intime + pd.Timedelta(hours=4))
        self.assertEqual(int(got.loc[0, "death_within_24h_of_index_icu"]), 1)
        observations = pd.Series([intime + pd.Timedelta(hours=3), intime + pd.Timedelta(hours=6)])
        included = observations.le(end)
        self.assertEqual(included.tolist(), [True, False])
        self.assertEqual(got.loc[0, "observation_window_end_reason"], "death")

    def test_inconsistent_pre_icu_discharge_or_death_invalidates_window(self):
        intime = pd.Timestamp("2020-01-01 00:00:00")
        f = pd.DataFrame({
            "intime": [intime, intime],
            "dischtime": [intime - pd.Timedelta(hours=1), pd.NaT],
            "deathtime": [pd.NaT, intime - pd.Timedelta(minutes=5)],
            "died": [0, 1],
        })
        got = m58.add_observation_windows(f)
        self.assertTrue(got["window_anchor_inconsistent"].all())
        self.assertTrue(got["chart_window_end"].isna().all())
        self.assertTrue(got["lab_window_end"].isna().all())
        self.assertTrue(pd.isna(got.loc[1, "death_within_24h_of_index_icu"]))

    def test_index_hash_changes_when_observation_end_changes(self):
        t0 = pd.Timestamp("2020-01-01")
        row = {
            "subject_id": 1, "hadm_id": 10, "stay_id": 100, "disease": "sepsis",
            "pos": 1, "grp": 0, "narrow_inclusion": 1, "pos_narrow": 1,
            "legacy_broad_inclusion": 1, "pos_legacy": 1,
            "admittime": t0 - pd.Timedelta(hours=2), "intime": t0,
            "outtime": t0 + pd.Timedelta(hours=30), "dischtime": t0 + pd.Timedelta(hours=8),
            "chart_window_start": t0, "chart_window_end": t0 + pd.Timedelta(hours=4),
            "lab_window_start": t0 - pd.Timedelta(hours=6), "lab_window_end": t0 + pd.Timedelta(hours=4),
            "window_anchor_inconsistent": False, "observation_window_end_reason": "death",
            "age_at_admit": 70,
        }
        frame = pd.DataFrame([row])
        before = m58._index_hash(frame)
        frame.loc[0, "chart_window_end"] = t0 + pd.Timedelta(hours=5)
        self.assertNotEqual(before, m58._index_hash(frame))

    def test_index_hash_is_stable_across_csv_dtype_roundtrip(self):
        t0 = pd.Timestamp("2020-01-01")
        frame = pd.DataFrame([{
            "subject_id": 1, "hadm_id": 10, "stay_id": 100, "disease": "sepsis",
            "pos": 2, "grp": 1, "narrow_inclusion": 1, "pos_narrow": 2,
            "legacy_broad_inclusion": 1, "pos_legacy": 2,
            "admittime": t0 - pd.Timedelta(hours=2), "intime": t0,
            "outtime": t0 + pd.Timedelta(hours=30), "dischtime": t0 + pd.Timedelta(hours=8),
            "chart_window_start": t0, "chart_window_end": t0 + pd.Timedelta(hours=4),
            "lab_window_start": t0 - pd.Timedelta(hours=6), "lab_window_end": t0 + pd.Timedelta(hours=4),
            "window_anchor_inconsistent": False, "observation_window_end_reason": "death",
            "age_at_admit": 70,
        }])
        for col in ("grp", "narrow_inclusion", "pos_narrow"):
            frame[col] = frame[col].astype("Int8")
        before = m58._index_hash(frame)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.csv"
            frame.to_csv(path, index=False)
            roundtrip = pd.read_csv(path, parse_dates=[
                "admittime", "intime", "outtime", "dischtime", "chart_window_start",
                "chart_window_end", "lab_window_start", "lab_window_end"])
        self.assertEqual(before, m58._index_hash(roundtrip))


class ScoreTests(unittest.TestCase):
    def _base(self, n=1):
        return pd.DataFrame({
            "rr_max": [np.nan] * n, "sbp_min": [np.nan] * n, "dbp_min": [np.nan] * n,
            "hr_max": [np.nan] * n, "temp_c_min": [np.nan] * n, "temp_c_max": [np.nan] * n,
            "wbc_min": [np.nan] * n, "wbc_max": [np.nan] * n, "bun_max": [np.nan] * n,
            "urea_mmol_l": [np.nan] * n, "gcs_worst": [np.nan] * n, "age_at_admit": [np.nan] * n,
        })

    def test_qsofa_gcs_threshold_and_missing_bounds(self):
        f = self._base(3)
        f.loc[0, ["rr_max", "sbp_min", "gcs_worst"]] = [22, 100, 13]
        f.loc[1, ["rr_max", "sbp_min", "gcs_worst"]] = [22, 100, 14]
        f.loc[2, "rr_max"] = 22
        got = m58.score_panel(f)
        self.assertEqual(int(got.loc[0, "qsofa"]), 3)
        self.assertEqual(int(got.loc[0, "qsofa_gcs15"]), 3)
        self.assertEqual(int(got.loc[1, "qsofa"]), 2)
        self.assertEqual(int(got.loc[1, "qsofa_gcs15"]), 3)
        self.assertTrue(pd.isna(got.loc[2, "qsofa"]))
        self.assertEqual(int(got.loc[2, "qsofa_lower"]), 1)
        self.assertEqual(int(got.loc[2, "qsofa_upper"]), 3)
        self.assertEqual(int(got.loc[2, "qsofa_components_observed"]), 1)

    def test_sirs_unknowns_produce_bisap_interval(self):
        f = self._base(2)
        f.loc[0, ["temp_c_min", "temp_c_max", "hr_max"]] = [35.0, 37.0, 95.0]
        f.loc[1, ["bun_max", "gcs_worst", "age_at_admit"]] = [30.0, 15.0, 61.0]
        got = m58.score_panel(f)
        self.assertEqual(int(got.loc[0, "sirs_lower"]), 2)
        self.assertEqual(int(got.loc[0, "sirs_upper"]), 4)
        self.assertEqual(int(got.loc[0, "bisap_sirs2"]), 1)
        self.assertEqual(int(got.loc[1, "bisap4_lower"]), 2)
        self.assertEqual(int(got.loc[1, "bisap4_upper"]), 3)
        self.assertTrue(pd.isna(got.loc[1, "bisap4"]))

    def test_sirs_bands_or_wbc_preserves_unknown_and_positive_results(self):
        f = self._base(4)
        f.loc[0, ["wbc_min", "wbc_max"]] = [5, 6]
        f.loc[1, ["wbc_min", "wbc_max", "bands_pct_max"]] = [5, 6, 10]
        f.loc[2, "bands_pct_max"] = 11
        f.loc[3, "wbc_min"] = 3
        got = m58.score_panel(f)
        self.assertTrue(pd.isna(got.loc[0, "sirs_wbc"]))
        self.assertEqual(int(got.loc[1, "sirs_wbc"]), 0)
        self.assertEqual(int(got.loc[2, "sirs_wbc"]), 1)
        self.assertEqual(int(got.loc[3, "sirs_wbc"]), 1)

    def test_curb_blood_pressure_or_is_tri_state(self):
        f = self._base(3)
        f.loc[0, "sbp_min"] = 85
        f.loc[1, ["sbp_min", "dbp_min"]] = [95, 60]
        f.loc[2, "sbp_min"] = 95
        got = m58.score_panel(f)
        self.assertEqual(int(got.loc[0, "curb_bp"]), 1)
        self.assertEqual(int(got.loc[1, "curb_bp"]), 1)
        self.assertTrue(pd.isna(got.loc[2, "curb_bp"]))


class AggregationTests(unittest.TestCase):
    def test_ett_unassessable_overrides_numeric_gcs_fallback(self):
        frame = pd.DataFrame({
            "itemid": [223900, 223900],
            "value": ["No Response-ETT", "No Response - ETT"],
            "valuenum": [0, 1],
        })
        primary = m58._map_gcs_values(frame)
        sensitivity = m58._map_gcs_values(frame, ett_as_one=True)
        self.assertTrue(primary.isna().all())
        self.assertEqual(sensitivity.tolist(), [1.0, 1.0])

    def test_gcs_primary_skips_ett_time_and_keeps_ett_as_one_sensitivity(self):
        rows = [
            [1, 100, "2020-01-01 08:00:00", 220739, np.nan, "Spontaneously"],
            [1, 100, "2020-01-01 08:00:00", 223900, 1, "No Response-ETT"],
            [1, 100, "2020-01-01 08:00:00", 223901, np.nan, "Obeys Commands"],
            [1, 100, "2020-01-01 09:00:00", 220739, np.nan, "To pain"],
            [1, 100, "2020-01-01 09:00:00", 223900, np.nan, "Oriented"],
            [1, 100, "2020-01-01 09:00:00", 223901, np.nan, "Obeys Commands"],
        ]
        frame = pd.DataFrame(rows, columns=["stay_id", "hadm_id", "charttime", "itemid", "valuenum", "value"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.csv.gz"
            frame.to_csv(path, index=False, compression="gzip")
            got, _ = m58.aggregate_chart_cache(path)
        self.assertEqual(float(got.loc[0, "gcs_worst"]), 13.0)
        self.assertEqual(float(got.loc[0, "gcs_worst_ett_as1"]), 11.0)

    def test_timed_gcs_complete_triple_and_extrema(self):
        rows = []
        for item, value in [(220739, "None"), (223900, "Oriented"), (223901, "Obeys Commands")]:
            rows.append([1, 100, "2020-01-01 08:00:00", item, np.nan, value])
        for item, value in [(220739, "Spontaneously"), (223900, "None"), (223901, "None")]:
            rows.append([1, 100, "2020-01-01 09:00:00", item, np.nan, value])
        rows += [
            [1, 100, "2020-01-01 10:00:00", 220210, 24.0, "24"],
            [1, 100, "2020-01-01 11:00:00", 220210, 31.0, "31"],
            [1, 100, "2020-01-01 10:00:00", 223761, 100.0, "100"],
            [1, 100, "2020-01-01 11:00:00", 223762, 35.5, "35.5"],
            [1, 100, "2020-01-01 10:00:00", 220050, 90.0, "90"],
            [1, 100, "2020-01-01 11:00:00", 220179, 80.0, "80"],
        ]
        frame = pd.DataFrame(rows, columns=["stay_id", "hadm_id", "charttime", "itemid", "valuenum", "value"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.csv.gz"
            frame.to_csv(path, index=False, compression="gzip")
            got, _ = m58.aggregate_chart_cache(path)
        self.assertEqual(int(got.loc[0, "gcs_worst"]), 6)
        self.assertAlmostEqual(float(got.loc[0, "rr_max"]), 31.0)
        self.assertAlmostEqual(float(got.loc[0, "temp_c_min"]), 35.5)
        self.assertGreater(float(got.loc[0, "temp_c_max"]), 37.7)
        self.assertAlmostEqual(float(got.loc[0, "sbp_min"]), 80.0)

    def test_cross_time_gcs_components_are_never_summed(self):
        rows = [
            [1, 100, "2020-01-01 08:00:00", 220739, np.nan, "None"],
            [1, 100, "2020-01-01 08:00:00", 223900, np.nan, "Oriented"],
            [1, 100, "2020-01-01 08:00:00", 223901, np.nan, "Obeys Commands"],
            [1, 100, "2020-01-01 09:00:00", 220739, np.nan, "Spontaneously"],
            [1, 100, "2020-01-01 09:00:00", 223900, np.nan, "None"],
            [1, 100, "2020-01-01 09:00:00", 223901, np.nan, "None"],
        ]
        frame = pd.DataFrame(rows, columns=["stay_id", "hadm_id", "charttime", "itemid", "valuenum", "value"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.csv.gz"
            frame.to_csv(path, index=False, compression="gzip")
            got, _ = m58.aggregate_chart_cache(path)
        self.assertEqual(int(got.loc[0, "gcs_worst"]), 6)
        self.assertNotEqual(int(got.loc[0, "gcs_worst"]), 1 + 1 + 1)

    def test_lab_aggregates_bun_high_and_wbc_both_directions(self):
        frame = pd.DataFrame([
            [100, "2020-01-01", 51006, 15], [100, "2020-01-02", 51006, 30],
            [100, "2020-01-01", 51301, 3], [100, "2020-01-02", 51300, 13],
        ], columns=["hadm_id", "charttime", "itemid", "valuenum"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lab.csv.gz"
            frame.to_csv(path, index=False, compression="gzip")
            got, _ = m58.aggregate_lab_cache(path)
        self.assertEqual(float(got.loc[0, "bun_max"]), 30)
        self.assertEqual(float(got.loc[0, "wbc_min"]), 3)
        self.assertEqual(float(got.loc[0, "wbc_max"]), 13)


class IndexBuildIntegrationTests(unittest.TestCase):
    @staticmethod
    def _add_nested_gzip_csv(zf, name, frame):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(frame.to_csv(index=False).encode("utf-8"))
        zf.writestr(name, buf.getvalue())

    def test_small_zip_runs_full_index_entrypoint_and_retains_stats(self):
        dx = pd.DataFrame([
            [1, 100, 1, "A41", 10], [1, 100, 2, "J15.9", 10],
            [1, 101, 1, "I50.9", 10], [2, 200, 1, "577.1", 9],
        ], columns=["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"])
        adm = pd.DataFrame([
            [1, 100, "2020-01-01 00:00:00", "2020-01-01 08:00:00", "2020-01-01 04:00:00", 1],
            [1, 101, "2021-01-01 00:00:00", "2021-01-03 00:00:00", "", 0],
            [2, 200, "2020-06-01 00:00:00", "2020-06-02 00:00:00", "", ""],
        ], columns=["subject_id", "hadm_id", "admittime", "dischtime", "deathtime", "hospital_expire_flag"])
        pat = pd.DataFrame([
            [1, "F", 70, 2019, "2017 - 2019"], [2, "M", 35, 2020, "2017 - 2019"],
        ], columns=["subject_id", "gender", "anchor_age", "anchor_year", "anchor_year_group"])
        stays = pd.DataFrame([
            [1, 100, 1000, "2020-01-01 01:00:00", "2020-01-01 12:00:00"],
            [1, 100, 999, "2020-01-01 00:00:00", "2020-01-01 11:00:00"],
            [1, 101, 1001, "2021-01-02 00:00:00", "2021-01-04 00:00:00"],
            [2, 200, 2000, "2020-06-01 02:00:00", "2020-06-02 00:00:00"],
        ], columns=["subject_id", "hadm_id", "stay_id", "intime", "outtime"])
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "synthetic_mimic.zip"
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                self._add_nested_gzip_csv(zf, m58.MEMBERS["diagnoses"], dx)
                self._add_nested_gzip_csv(zf, m58.MEMBERS["admissions"], adm)
                self._add_nested_gzip_csv(zf, m58.MEMBERS["patients"], pat)
                self._add_nested_gzip_csv(zf, m58.MEMBERS["icustays"], stays)
            index, stats = m58.build_index(zip_path)
        by_cell = index.set_index(["disease", "hadm_id"])
        self.assertEqual(stats["diagnosis_rows"], len(dx))
        self.assertEqual(int(by_cell.loc[("sepsis", 100), "stay_id"]), 999)
        self.assertEqual(int(by_cell.loc[("sepsis", 100), "grp"]), 0)
        self.assertEqual(int(by_cell.loc[("pneumonia", 100), "grp"]), 1)
        self.assertEqual(float(by_cell.loc[("sepsis", 100), "age_at_admit"]), 71.0)
        self.assertEqual(by_cell.loc[("sepsis", 100), "chart_window_end"], pd.Timestamp("2020-01-01 04:00:00"))
        self.assertEqual(int(by_cell.loc[("sepsis", 100), "death_within_24h_of_index_icu"]), 1)
        self.assertTrue(bool(by_cell.loc[("sepsis", 100), "first_eligible_admission_any_disease"]))
        self.assertEqual(int(by_cell.loc[("pancreatitis", 200), "broad_inclusion"]), 0)
        self.assertEqual(int(by_cell.loc[("pancreatitis", 200), "legacy_broad_inclusion"]), 1)
        self.assertTrue(pd.isna(by_cell.loc[("pancreatitis", 200), "grp"]))
        self.assertTrue(pd.isna(by_cell.loc[("pancreatitis", 200), "died"]))


if __name__ == "__main__":
    unittest.main()

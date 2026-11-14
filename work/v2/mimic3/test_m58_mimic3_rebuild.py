"""Synthetic MIMIC-III adapter checks; no patient data or large table scans."""
from __future__ import annotations

import gzip
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

import m58_mimic3_rebuild as m3


class AgeAndGcsTests(unittest.TestCase):
    def test_calendar_age_and_shifted_dob_topcode(self):
        dob = pd.Series(["1980-11-13 00:00:00", "1980-11-13 00:00:00",
                         "1800-11-13 00:00:00"], dtype="string")
        intime = pd.Series(pd.to_datetime(["2020-11-12", "2020-11-13", "2100-11-13"]))
        age, topcoded, exact = m3._age_from_dob(dob, intime)
        self.assertEqual(age.tolist(), [39.0, 40.0, 90.0])
        self.assertEqual(topcoded.astype(int).tolist(), [0, 0, 1])
        self.assertEqual(exact.astype(int).tolist(), [1, 1, 0])

    def test_carevue_total_gcs_uses_direct_item_198_minimum(self):
        frame = pd.DataFrame([
            [10, 100, "2100-01-01 08:00:00", 198, 12, "12"],
            [10, 100, "2100-01-01 09:00:00", 198, 10, "10"],
            [10, 100, "2100-01-01 10:00:00", 198, 16, "16"],
        ], columns=["stay_id", "hadm_id", "charttime", "itemid", "valuenum", "value"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.csv.gz"
            frame.to_csv(path, index=False, compression="gzip")
            got, stats = m3._aggregate_carevue_gcs(path)
        self.assertEqual(float(got.loc[0, "gcs_total_worst"]), 10.0)
        self.assertEqual(got.loc[0, "gcs_total_worst_charttime"], pd.Timestamp("2100-01-01 09:00:00"))
        self.assertEqual(stats["invalid_carevue_total_values"], 1)

    def test_direct_gcs_overrides_components_only_when_worse(self):
        chart = pd.DataFrame({
            "stay_id": [10, 20], "gcs_worst": [12.0, 8.0],
            "gcs_worst_charttime": pd.to_datetime(["2100-01-01 08:00", "2100-01-01 08:00"]),
            "gcs_worst_ett_as1": [12.0, 8.0],
            "gcs_worst_ett_as1_charttime": pd.to_datetime(["2100-01-01 08:00", "2100-01-01 08:00"]),
            "gcs_eye_at_time": [3.0, 2.0], "gcs_verbal_at_time": [4.0, 2.0],
            "gcs_motor_at_time": [5.0, 4.0],
        })
        carevue = pd.DataFrame({
            "stay_id": [10, 20], "gcs_total_worst": [10.0, 14.0],
            "gcs_total_worst_charttime": pd.to_datetime(["2100-01-01 09:00", "2100-01-01 09:00"]),
        })
        got = m3._combine_gcs(chart, carevue).set_index("stay_id")
        self.assertEqual(float(got.loc[10, "gcs_worst"]), 10.0)
        self.assertEqual(got.loc[10, "gcs_worst_source"], "carevue_total_item_198")
        self.assertEqual(float(got.loc[10, "gcs_worst_ett_as1"]), 10.0)
        self.assertEqual(got.loc[10, "gcs_worst_ett_as1_source"], "carevue_total_item_198")
        self.assertEqual(float(got.loc[20, "gcs_worst"]), 8.0)
        self.assertEqual(got.loc[20, "gcs_worst_source"], "metavision_complete_components")


class DiagnosisSequenceTests(unittest.TestCase):
    def test_unranked_matches_are_included_but_primary_group_stays_unknown(self):
        dx = pd.DataFrame([
            [1, 100, 1, "038.9", 9], [1, 100, None, "038.9", 9],
            [2, 200, 2, "038.9", 9],
            [3, 300, 2, "038.9", 9], [3, 300, None, "038.9", 9],
            [4, 400, None, "038.9", 9],
            [5, 500, 0, "038.9", 9],
            [6, 600, None, "9959", 9],
            [7, 700, 3, "9959", 9],
        ], columns=["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"])
        got, audit = m3._memberships_with_sequence_quality(dx)
        sepsis = got.loc[got["disease"].eq("sepsis")].set_index("hadm_id")

        self.assertEqual(int(sepsis.loc[100, "broad_inclusion"]), 1)
        self.assertEqual(int(sepsis.loc[100, "pos"]), 1)
        self.assertEqual(int(sepsis.loc[100, "grp"]), 0)
        self.assertEqual(int(sepsis.loc[100, "unranked_match_count_broad"]), 1)

        self.assertEqual(int(sepsis.loc[200, "pos"]), 2)
        self.assertEqual(int(sepsis.loc[200, "grp"]), 1)

        self.assertEqual(int(sepsis.loc[300, "pos"]), 2)
        self.assertTrue(pd.isna(sepsis.loc[300, "grp"]))
        self.assertEqual(int(sepsis.loc[300, "unranked_match_count_broad"]), 1)

        self.assertEqual(int(sepsis.loc[400, "broad_inclusion"]), 1)
        self.assertTrue(pd.isna(sepsis.loc[400, "pos"]))
        self.assertTrue(pd.isna(sepsis.loc[400, "grp"]))
        self.assertEqual(int(sepsis.loc[400, "narrow_inclusion"]), 1)
        self.assertTrue(pd.isna(sepsis.loc[400, "grp_narrow"]))

        self.assertEqual(int(sepsis.loc[500, "broad_inclusion"]), 1)
        self.assertTrue(pd.isna(sepsis.loc[500, "pos"]))
        self.assertTrue(pd.isna(sepsis.loc[500, "grp"]))
        self.assertEqual(int(sepsis.loc[600, "broad_inclusion"]), 0)
        self.assertEqual(int(sepsis.loc[600, "legacy_broad_inclusion"]), 1)
        self.assertTrue(pd.isna(sepsis.loc[600, "pos_legacy"]))
        self.assertTrue(pd.isna(sepsis.loc[600, "grp_legacy_broad"]))
        self.assertEqual(int(sepsis.loc[700, "legacy_broad_inclusion"]), 1)
        self.assertEqual(int(sepsis.loc[700, "pos_legacy"]), 3)
        self.assertEqual(int(sepsis.loc[700, "grp_legacy_broad"]), 1)
        self.assertEqual(audit["sepsis"]["broad"]["matching_unranked_diagnosis_rows"], 4)
        self.assertEqual(audit["sepsis"]["broad"]["admissions_with_unranked_match_and_no_seq1"], 3)


class DictionaryAuditTests(unittest.TestCase):
    @staticmethod
    def _add_nested_gzip_csv(zf, name, frame):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(frame.to_csv(index=False).encode("utf-8"))
        zf.writestr(name, buf.getvalue())

    def test_small_dictionary_audit_reports_gcs_bands_and_unused_pco2(self):
        items = pd.DataFrame([
            [198, "GCS Total", "CareVue", "Scores", "", "chartevents"],
            [220739, "GCS - Eye Opening", "MetaVision", "Neurological", "", "chartevents"],
        ], columns=["ITEMID", "LABEL", "DBSOURCE", "CATEGORY", "UNITNAME", "LINKSTO"])
        labs = pd.DataFrame([
            [51144, "Bands", "Blood", "Hematology"],
            [50818, "pCO2", "Blood", "Blood Gas"],
        ], columns=["ITEMID", "LABEL", "FLUID", "CATEGORY"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = root / "small_mimic3.zip"
            private = root / "private"
            private.mkdir()
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                self._add_nested_gzip_csv(zf, m3.MEMBERS["d_items"], items)
                self._add_nested_gzip_csv(zf, m3.MEMBERS["d_labitems"], labs)
            stats = m3._audit_small_dictionaries(zip_path, private)
            chart_audit = pd.read_csv(private / "mimic_iii_v2_chart_dictionary_audit.csv")
            lab_audit = pd.read_csv(private / "mimic_iii_v2_lab_dictionary_audit.csv")
        self.assertTrue(stats["bands_itemid_51144_present"])
        self.assertIn(50818, stats["unused_pco2_candidate_itemids"])
        self.assertIn(198, set(chart_audit["itemid"]))
        self.assertIn(51144, set(lab_audit["itemid"]))
        self.assertNotIn(50818, m3.LAB_IDS)


class EventCacheTests(unittest.TestCase):
    @staticmethod
    def _add_nested_gzip_csv(zf, name, frame):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(frame.to_csv(index=False).encode("utf-8"))
        zf.writestr(name, buf.getvalue())

    @staticmethod
    def _index():
        t0 = pd.Timestamp("2100-01-01 00:00:00")
        return pd.DataFrame([{
            "subject_id": 1, "hadm_id": 100, "stay_id": 10, "disease": "sepsis",
            "pos": 1, "grp": 0, "narrow_inclusion": 1, "pos_narrow": 1,
            "legacy_broad_inclusion": 1, "pos_legacy": 1,
            "admittime": t0 - pd.Timedelta(hours=2), "intime": t0,
            "outtime": t0 + pd.Timedelta(hours=30), "dischtime": t0 + pd.Timedelta(hours=30),
            "deathtime": pd.NaT, "chart_window_start": t0,
            "chart_window_end": t0 + pd.Timedelta(hours=24),
            "lab_window_start": t0 - pd.Timedelta(hours=6),
            "lab_window_end": t0 + pd.Timedelta(hours=24),
            "window_anchor_inconsistent": False, "observation_window_end_reason": "full_24h",
            "age_at_admit": 70,
        }])

    def test_chart_mapping_and_percent_only_bands_cache(self):
        t0 = pd.Timestamp("2100-01-01 00:00:00")
        chart = pd.DataFrame([
            [1, 1, 100, 10, t0 + pd.Timedelta(hours=2), 198, 11, "11"],
            [2, 1, 100, 10, t0 + pd.Timedelta(hours=2), 51, 80, "80"],
            [3, 1, 100, 10, t0 + pd.Timedelta(hours=2), 455, 90, "90"],
            [4, 1, 100, 10, t0 + pd.Timedelta(hours=2), 618, 22, "22"],
            [5, 1, 100, 10, t0 + pd.Timedelta(hours=25), 51, 70, "70"],
        ], columns=["ROW_ID", "SUBJECT_ID", "HADM_ID", "ICUSTAY_ID", "CHARTTIME",
                    "ITEMID", "VALUENUM", "VALUE"])
        labs = pd.DataFrame([
            [1, 1, 100, 51006, t0 - pd.Timedelta(hours=2), "12", 12, "mg/dL", ""],
            [2, 1, 100, 51144, t0 + pd.Timedelta(hours=1), "11", 11, "%", ""],
            [3, 1, 100, 51144, t0 + pd.Timedelta(hours=1), "99", 99, "cells", ""],
            [4, 1, 100, 51301, t0 + pd.Timedelta(hours=1), "7", 7, "K/uL", ""],
        ], columns=["ROW_ID", "SUBJECT_ID", "HADM_ID", "ITEMID", "CHARTTIME", "VALUE",
                    "VALUENUM", "VALUEUOM", "FLAG"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = root / "small_mimic3.zip"
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                self._add_nested_gzip_csv(zf, m3.MEMBERS["chartevents"], chart)
                self._add_nested_gzip_csv(zf, m3.MEMBERS["labevents"], labs)
            index = self._index()
            chart_cache = root / "chart.csv.gz"
            lab_cache = root / "lab.csv.gz"
            n_chart = m3._atomic_filtered_cache(
                zip_path, m3.MEMBERS["chartevents"], chart_cache,
                table="chartevents", index=index, chunksize=2)
            n_lab = m3._atomic_filtered_cache(
                zip_path, m3.MEMBERS["labevents"], lab_cache,
                table="labevents", index=index, chunksize=2)
            cached_chart = pd.read_csv(chart_cache, compression="gzip")
            cached_labs = pd.read_csv(lab_cache, compression="gzip")
            self.assertTrue(m3._cache_is_valid(
                chart_cache, zip_path, m3.MEMBERS["chartevents"], m3.common._index_hash(index)))
            self.assertTrue(m3._cache_is_valid(
                lab_cache, zip_path, m3.MEMBERS["labevents"], m3.common._index_hash(index)))
        self.assertEqual(n_chart, 4)
        self.assertEqual(set(cached_chart["itemid"]), {198, 220050, 220179, 220210})
        self.assertEqual(n_lab, 3)
        self.assertEqual(int(cached_labs["itemid"].eq(51144).sum()), 1)
        self.assertEqual(float(cached_labs.loc[cached_labs["itemid"].eq(51144), "valuenum"].iloc[0]), 11.0)


class NormalEntryTests(unittest.TestCase):
    """Exercise the guarded CLI path through index, caches, aggregation and manifest."""

    @staticmethod
    def _add_nested_gzip_csv(zf, name, frame):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(frame.to_csv(index=False).encode("utf-8"))
        zf.writestr(name, buf.getvalue())

    def test_main_requires_scan_flag_then_writes_primary_and_ett_sensitivity(self):
        t0 = pd.Timestamp("2001-01-01 00:00:00")
        chart = pd.DataFrame([
            [1, 1, 100, 10, t0 + pd.Timedelta(hours=1), 618, 18, "18"],
            [2, 1, 100, 10, t0 + pd.Timedelta(hours=1), 6, 120, "120"],
            [3, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220050, 110, "110"],
            [4, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220051, 75, "75"],
            [5, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220179, 89, "89"],
            [6, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220180, 59, "59"],
            [7, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220739, 4, "Spontaneously"],
            [8, 1, 100, 10, t0 + pd.Timedelta(hours=1), 223900, 5, "Oriented"],
            [9, 1, 100, 10, t0 + pd.Timedelta(hours=1), 223901, 6, "Obeys Commands"],
            [10, 1, 100, 10, t0 + pd.Timedelta(hours=2), 220739, 4, "Spontaneously"],
            [11, 1, 100, 10, t0 + pd.Timedelta(hours=2), 223900, 1, "No Response-ETT"],
            [12, 1, 100, 10, t0 + pd.Timedelta(hours=2), 223901, 6, "Obeys Commands"],
            [13, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220210, 18, "18"],
            [14, 1, 100, 10, t0 + pd.Timedelta(hours=1), 220045, 90, "90"],
            [15, 1, 100, 10, t0 + pd.Timedelta(hours=1), 223761, 98.6, "98.6"],
            [16, 1, 100, 10, t0 + pd.Timedelta(hours=1), 223762, 37.0, "37.0"],
            [17, 1, 100, 10, t0 + pd.Timedelta(hours=1), 224690, 20, "20"],
        ], columns=["ROW_ID", "SUBJECT_ID", "HADM_ID", "ICUSTAY_ID", "CHARTTIME",
                    "ITEMID", "VALUENUM", "VALUE"])
        labs = pd.DataFrame([
            [1, 1, 100, 51006, t0 + pd.Timedelta(hours=1), "21", 21, "mg/dL", ""],
            [2, 1, 100, 51144, t0 + pd.Timedelta(hours=1), "11", 11, "%", ""],
        ], columns=["ROW_ID", "SUBJECT_ID", "HADM_ID", "ITEMID", "CHARTTIME", "VALUE",
                    "VALUENUM", "VALUEUOM", "FLAG"])
        diagnoses = pd.DataFrame([[1, 100, 1, "038.9"]],
                                 columns=["SUBJECT_ID", "HADM_ID", "SEQ_NUM", "ICD9_CODE"])
        admissions = pd.DataFrame([[1, 100, t0, t0 + pd.Timedelta(days=2), "", 0]],
                                  columns=["SUBJECT_ID", "HADM_ID", "ADMITTIME", "DISCHTIME",
                                           "DEATHTIME", "HOSPITAL_EXPIRE_FLAG"])
        patients = pd.DataFrame([[1, "F", "1970-01-01 00:00:00"]],
                                columns=["SUBJECT_ID", "GENDER", "DOB"])
        stays = pd.DataFrame([[1, 100, 10, t0, t0 + pd.Timedelta(days=1)]],
                             columns=["SUBJECT_ID", "HADM_ID", "ICUSTAY_ID", "INTIME", "OUTTIME"])
        d_items = pd.DataFrame([
            [6, "Arterial BP Systolic", "CareVue", "Vitals", "mmHg", "chartevents"],
            [198, "GCS Total", "CareVue", "Scores", "", "chartevents"],
            [618, "Respiratory Rate", "CareVue", "Vitals", "bpm", "chartevents"],
            [220050, "Arterial Blood Pressure systolic", "MetaVision", "Vitals", "mmHg", "chartevents"],
            [220051, "Arterial Blood Pressure diastolic", "MetaVision", "Vitals", "mmHg", "chartevents"],
            [220179, "Non Invasive Blood Pressure systolic", "MetaVision", "Vitals", "mmHg", "chartevents"],
            [220180, "Non Invasive Blood Pressure diastolic", "MetaVision", "Vitals", "mmHg", "chartevents"],
            [220210, "Respiratory Rate", "MetaVision", "Vitals", "insp/min", "chartevents"],
            [220045, "Heart Rate", "MetaVision", "Vitals", "bpm", "chartevents"],
            [223761, "Temperature Fahrenheit", "MetaVision", "Vitals", "F", "chartevents"],
            [223762, "Temperature Celsius", "MetaVision", "Vitals", "C", "chartevents"],
            [220739, "GCS Eye Opening", "MetaVision", "Neurological", "", "chartevents"],
            [223900, "GCS Verbal Response", "MetaVision", "Neurological", "", "chartevents"],
            [223901, "GCS Motor Response", "MetaVision", "Neurological", "", "chartevents"],
        ], columns=["ITEMID", "LABEL", "DBSOURCE", "CATEGORY", "UNITNAME", "LINKSTO"])
        d_labitems = pd.DataFrame([[51144, "Bands", "Blood", "Hematology"]],
                                  columns=["ITEMID", "LABEL", "FLUID", "CATEGORY"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = root / "small_mimic3.zip"
            out_dir, private_dir, cache_dir = root / "out", root / "private", root / "cache"
            tables = {
                "DIAGNOSES_ICD.csv.gz": diagnoses,
                "ADMISSIONS.csv.gz": admissions,
                "PATIENTS.csv.gz": patients,
                "ICUSTAYS.csv.gz": stays,
                "CHARTEVENTS.csv.gz": chart,
                "LABEVENTS.csv.gz": labs,
                "D_ITEMS.csv.gz": d_items,
                "D_LABITEMS.csv.gz": d_labitems,
            }
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for filename, frame in tables.items():
                    self._add_nested_gzip_csv(zf, m3.PREFIX + filename, frame)

            with self.assertRaisesRegex(SystemExit, "without --allow-event-scan"):
                m3.main(["--zip", str(zip_path), "--out-dir", str(out_dir),
                         "--private-dir", str(private_dir), "--cache-dir", str(cache_dir)])
            self.assertFalse(private_dir.exists())

            rc = m3.main(["--zip", str(zip_path), "--out-dir", str(out_dir),
                          "--private-dir", str(private_dir), "--cache-dir", str(cache_dir),
                          "--allow-event-scan", "--chart-chunksize", "2", "--lab-chunksize", "2"])
            self.assertEqual(rc, 0)
            panel_path = private_dir / "mimic_iii_v2_score_panel.csv.gz"
            manifest_path = out_dir / "mimic_iii_v2_run_manifest.json"
            panel = pd.read_csv(panel_path, compression="gzip")
            filtered_chart = pd.read_csv(
                cache_dir / "mimic_iii_chartevents_filtered.csv.gz", compression="gzip")
            run_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            index_manifest = json.loads(
                (private_dir / "mimic_iii_v2_index_manifest.json").read_text(encoding="utf-8"))
            index_hash = index_manifest["index_filter_sha256"]
            self.assertEqual(len(panel), 1)
            self.assertEqual(float(panel.loc[0, "gcs_worst"]), 15.0)
            self.assertEqual(float(panel.loc[0, "gcs_worst_ett_as1"]), 11.0)
            self.assertEqual(float(panel.loc[0, "q_gcs13"]), 0.0)
            self.assertEqual(int(panel.loc[0, "q_gcs13_ett_as1"]), 1)
            self.assertEqual(float(panel.loc[0, "sbp_a_min"]), 110.0)
            self.assertEqual(float(panel.loc[0, "dbp_a_min"]), 75.0)
            self.assertEqual(float(panel.loc[0, "sbp_n_min"]), 89.0)
            self.assertEqual(float(panel.loc[0, "dbp_n_min"]), 59.0)
            self.assertEqual(float(panel.loc[0, "sbp_min"]), 89.0)
            self.assertEqual(float(panel.loc[0, "dbp_min"]), 59.0)
            self.assertEqual(float(panel.loc[0, "rr_max"]), 20.0)
            self.assertEqual(float(panel.loc[0, "hr_max"]), 90.0)
            self.assertAlmostEqual(float(panel.loc[0, "temp_c_min"]), 37.0, places=1)
            self.assertAlmostEqual(float(panel.loc[0, "temp_c_max"]), 37.0, places=1)
            self.assertEqual(float(panel.loc[0, "qsofa"]), 1.0)
            self.assertEqual(int(panel.loc[0, "qsofa_ett_as1"]), 2)
            self.assertEqual(float(panel.loc[0, "curb65"]), 2.0)
            canonical_metavision_ids = {
                220050, 220051, 220179, 220180, 220210, 220045,
                223761, 223762, 220739, 223900, 223901,
            }
            self.assertTrue(canonical_metavision_ids.issubset(m3.CHART_IDS))
            self.assertTrue(canonical_metavision_ids.issubset(set(filtered_chart["itemid"])))
            self.assertEqual({item: m3.CHART_MAP[item] for item in canonical_metavision_ids},
                             {item: item for item in canonical_metavision_ids})
            self.assertEqual(float(panel.loc[0, "bands_pct_max"]), 11.0)
            self.assertEqual(int(panel.loc[0, "sirs_wbc"]), 1)
            self.assertEqual(run_manifest["panel_rows"], 1)
            self.assertIn("mimic_iii_v2_score_coverage.csv", run_manifest["files"])
            self.assertTrue(m3._cache_is_valid(
                cache_dir / "mimic_iii_chartevents_filtered.csv.gz", zip_path,
                m3.MEMBERS["chartevents"], index_hash))
            self.assertTrue(m3._cache_is_valid(
                cache_dir / "mimic_iii_labevents_filtered.csv.gz", zip_path,
                m3.MEMBERS["labevents"], index_hash))


if __name__ == "__main__":
    unittest.main()

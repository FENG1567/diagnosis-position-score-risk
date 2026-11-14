#!/usr/bin/env python3
"""Rebuild an admission-level MIMIC-IV score panel from the v3.1.0 release ZIP.

The script reads the nested CSV.GZ members directly from the ZIP, retains a filtered
event cache for repeatable scoring, and writes only private row-level files plus
aggregate QA. It never prints patient-level rows.

Primary cohort definitions and score adaptations are documented in README.md.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import os
import sqlite3
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
import pandas as pd

VERSION = "m58-mimic-iv-rebuild-2.3.0"
ZIP_DEFAULT = Path(r"D:\数据库集合\mimic数据\mimic-iv_3.1.0.zip")
HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
OUT_DEFAULT = WORKSPACE / "outputs" / "v2" / "mimic"
PRIVATE_DEFAULT = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\mimic")
CACHE_DEFAULT = PRIVATE_DEFAULT / "cache"

MEMBERS = {
    "icustays": "mimic-iv-3.1/icu/icustays.csv.gz",
    "chartevents": "mimic-iv-3.1/icu/chartevents.csv.gz",
    "labevents": "mimic-iv-3.1/hosp/labevents.csv.gz",
    "diagnoses": "mimic-iv-3.1/hosp/diagnoses_icd.csv.gz",
    "admissions": "mimic-iv-3.1/hosp/admissions.csv.gz",
    "patients": "mimic-iv-3.1/hosp/patients.csv.gz",
    "d_labitems": "mimic-iv-3.1/hosp/d_labitems.csv.gz",
    "d_icd_diagnoses": "mimic-iv-3.1/hosp/d_icd_diagnoses.csv.gz",
}

CHART_ITEM_FEATURE = {
    220210: "rr_max",       # Respiratory Rate
    220050: "sbp_a_min",    # Arterial Blood Pressure systolic
    220051: "dbp_a_min",    # Arterial Blood Pressure diastolic
    220179: "sbp_n_min",    # Non-invasive Blood Pressure systolic
    220180: "dbp_n_min",    # Non-invasive Blood Pressure diastolic
    220045: "hr_max",       # Heart Rate
    223761: "temp_c",       # Temperature Fahrenheit; converted before extrema
    223762: "temp_c",       # Temperature Celsius
    220739: "gcs_eye",
    223900: "gcs_verbal",
    223901: "gcs_motor",
}
CHART_IDS = set(CHART_ITEM_FEATURE)
GCS_IDS = {220739, 223900, 223901}
CHART_CHUNK_SIZE = 1_500_000
LAB_CHUNK_SIZE = 1_500_000
FILTER_CACHE_SCHEMA = "mimic-iv-first-icu-filter-v2"

# Plausibility bounds are extraction rules, not score cut points. BP channels are
# kept separately; the score uses the lowest valid value observed in either channel.
VALID_RANGES = {
    "rr": (1.0, 100.0),
    "sbp": (30.0, 300.0),
    "dbp": (10.0, 200.0),
    "hr": (20.0, 250.0),
    "temp_c": (25.0, 45.0),
    "bun": (0.0, 300.0),
    "wbc": (0.1, 500.0),
    "bands_pct": (0.0, 100.0),
}

GCS_MAP = {
    220739: {
        "spontaneously": 4, "spontaneous": 4, "to speech": 3,
        "to voice": 3, "to pain": 2, "none": 1, "no response": 1,
    },
    223900: {
        "oriented": 5, "confused": 4, "inappropriate words": 3,
        "incomprehensible sounds": 2, "none": 1, "no response": 1,
    },
    223901: {
        "obeys commands": 6, "localizes pain": 5, "flexion withdrawal": 4,
        "abnormal flexion": 3, "extension": 2, "none": 1,
        "no response": 1,
    },
}
GCS_ETT_AS1_MAP = {
    220739: {"no response-ett": 1, "no response ett": 1},
    223900: {"no response-ett": 1, "no response ett": 1},
    223901: {},
}
GCS_UNASSESSABLE_PATTERN = r"\bno response\s*[-–]\s*ett\b|\bett\b|\bintubat\w*\b|\bunassessable\b|\bunable to assess\b"

# Prefixes are applied after removing dots and upper-casing ICD codes. The primary
# HF/COPD lists were narrowed after the phenotype audit; v1 broad lists are kept
# as an explicit sensitivity definition. Sepsis/pneumonia lists reproduce m94.
DISEASES = {
    "heart failure": {
        "main10": ("I50", "I110", "I130", "I132"),
        "main9": ("428", "40201", "40211", "40291", "40401", "40403", "40411", "40413", "40491", "40493"),
        "legacy10": ("I50", "I11", "I13"),
        "legacy9": ("428", "402", "404"),
    },
    "pneumonia": {
        "main10": ("J12", "J13", "J14", "J15", "J16", "J17", "J18", "J69"),
        "main9": ("480", "481", "482", "483", "484", "485", "486", "507"),
        "narrow10": ("J13", "J14", "J15", "J16", "J17"),
        "narrow9": ("481", "482", "483"),
        "legacy10": ("J12", "J13", "J14", "J15", "J16", "J17", "J18", "J69"),
        "legacy9": ("480", "481", "482", "483", "484", "485", "486", "507"),
    },
    "COPD": {
        "main10": ("J43", "J44"),
        "main9": ("4912", "492", "496"),
        "legacy10": ("J40", "J41", "J42", "J43", "J44", "J47"),
        "legacy9": ("490", "491", "492", "494", "496"),
    },
    "sepsis": {
        "main10": ("A40", "A41", "R652"),
        "main9": ("038", "99591", "99592", "78552"),
        "narrow10": ("A41",),
        "narrow9": ("038",),
        "legacy10": ("A40", "A41", "R652"),
        "legacy9": ("038", "9959", "78552"),
    },
    "pancreatitis": {
        "main10": ("K85",),
        "main9_exact": ("5770",),
        "legacy10": ("K85",),
        "legacy9_prefix": ("577",),
    },
}
DISEASE_ORDER = tuple(DISEASES)
SCORE_NAMES = ("qsofa", "qsofa_gcs15", "curb65", "bisap4",
               "qsofa_ett_as1", "qsofa_gcs15_ett_as1", "curb65_ett_as1", "bisap4_ett_as1")

LAB_IDS = {51006: "bun", 51301: "wbc", 51300: "wbc_alt", 51144: "bands_pct"}


def _csv_member(zip_path: Path, member: str, **kwargs) -> pd.DataFrame:
    """Read one nested CSV.GZ member without extracting it."""
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as member_file:
            with gzip.GzipFile(fileobj=member_file, mode="rb") as gz:
                return pd.read_csv(gz, **kwargs)


def _member_chunks(zip_path: Path, member: str, *, chunksize: int,
                   usecols: list[str], dtype: dict | None = None) -> Iterator[pd.DataFrame]:
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(member)
        with zf.open(info) as member_file:
            with gzip.GzipFile(fileobj=member_file, mode="rb") as gz:
                reader = pd.read_csv(gz, chunksize=chunksize, usecols=usecols,
                                     dtype=dtype, low_memory=False, keep_default_na=False,
                                     na_values=[""])
                started = time.monotonic()
                total = 0
                for i, chunk in enumerate(reader, 1):
                    total += len(chunk)
                    if i == 1 or i % 5 == 0:
                        elapsed = max(time.monotonic() - started, 1e-6)
                        rate = total / elapsed
                        member_read = member_file.tell()
                        pct = 100 * member_read / max(info.file_size, 1)
                        print(f"   {member}: chunk={i} rows={total:,} "
                              f"member_payload={member_read / 2**30:.2f}/"
                              f"{info.file_size / 2**30:.2f} GiB ({pct:.1f}%) "
                              f"rows_per_s={rate:,.0f}", flush=True)
                    yield chunk


def _source_fingerprint(zip_path: Path, member: str) -> dict:
    stat = zip_path.stat()
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(member)
        return {"zip_size": stat.st_size, "zip_mtime_ns": stat.st_mtime_ns,
                "member": member, "member_crc32": f"{info.CRC:08x}",
                "member_zip_size": info.compress_size, "member_payload_size": info.file_size}


def _archive_fingerprint(zip_path: Path) -> dict:
    """Fingerprint all ZIP directory entries without reading table payloads."""
    stat = zip_path.stat()
    with zipfile.ZipFile(zip_path) as zf:
        entries = sorted((i.filename, i.CRC, i.file_size, i.compress_size) for i in zf.infolist())
    payload = json.dumps(entries, separators=(",", ":")).encode("utf-8")
    return {"zip_size": stat.st_size, "zip_mtime_ns": stat.st_mtime_ns,
            "member_count": len(entries), "central_directory_fingerprint_sha256": hashlib.sha256(payload).hexdigest()}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _percent_unit_mask(values: pd.Series) -> pd.Series:
    """Recognize explicit percent units for MIMIC-IV differential bands."""
    units = values.fillna("").astype("string").str.strip().str.casefold()
    return units.isin({"%", "pct", "percent", "percentage", "per cent"})


def _normalized_codes(dx: pd.DataFrame) -> pd.Series:
    return (dx["icd_code"].fillna("").astype("string").str.upper()
            .str.replace(".", "", regex=False).str.strip())


def _diagnosis_sequence_position_audit(dx: pd.DataFrame) -> dict:
    """Summarize seq_num completeness over the source diagnosis rows."""
    raw = dx["seq_num"].astype("string").str.strip()
    missing = raw.isna() | raw.eq("")
    seq_num = pd.to_numeric(raw, errors="coerce")
    invalid_nonmissing = ~missing & seq_num.isna()
    nonpositive = seq_num.notna() & seq_num.le(0)
    unranked = missing | invalid_nonmissing | nonpositive
    return {
        "scope": "all diagnosis rows in diagnoses_icd.csv.gz",
        "diagnosis_rows": int(len(dx)),
        "seq_num_missing_rows": int(missing.sum()),
        "seq_num_invalid_nonmissing_rows": int(invalid_nonmissing.sum()),
        "seq_num_nonpositive_rows": int(nonpositive.sum()),
        "seq_num_unranked_rows": int(unranked.sum()),
        "matching_diagnosis_unranked_rows_proven_zero": bool(not unranked.any()),
    }


def _prefix_hit(codes: pd.Series, prefixes: tuple[str, ...]) -> pd.Series:
    if not prefixes:
        return pd.Series(False, index=codes.index)
    return codes.str.startswith(prefixes, na=False)


def _diagnosis_frame(dx: pd.DataFrame, disease: str, definition: str,
                     prefixes10: tuple[str, ...], prefixes9: tuple[str, ...],
                     exact9: tuple[str, ...] = ()) -> pd.DataFrame:
    v = pd.to_numeric(dx["icd_version"], errors="coerce")
    code = dx["code"]
    hit10 = (v == 10) & _prefix_hit(code, prefixes10)
    hit9 = (v == 9) & (_prefix_hit(code, prefixes9) if prefixes9 else False)
    if exact9:
        hit9 |= (v == 9) & code.isin(exact9)
    x = dx.loc[hit10 | hit9, ["subject_id", "hadm_id", "seq_num", "icd_version", "icd_code", "code"]].copy()
    if x.empty:
        return pd.DataFrame(columns=["subject_id", "hadm_id", f"pos_{definition}",
                                     f"code_{definition}", f"version_{definition}", "disease"])
    x["seq_num"] = pd.to_numeric(x["seq_num"], errors="coerce")
    x = x.sort_values(["hadm_id", "seq_num", "code", "icd_version"], kind="mergesort")
    x = x.drop_duplicates("hadm_id", keep="first")
    x = x.rename(columns={"seq_num": f"pos_{definition}", "code": f"code_{definition}",
                          "icd_version": f"version_{definition}"})
    x["disease"] = disease
    return x[["subject_id", "hadm_id", f"pos_{definition}", f"code_{definition}",
              f"version_{definition}", "disease"]]


def build_memberships(dx: pd.DataFrame) -> pd.DataFrame:
    """One row per admission × primary disease phenotype, with independent definitions."""
    dx = dx.copy()
    dx["code"] = _normalized_codes(dx)
    dx["icd_version"] = pd.to_numeric(dx["icd_version"], errors="coerce")
    frames = []
    for disease, spec in DISEASES.items():
        print(f"   [membership] {disease}: matching primary and legacy definitions", flush=True)
        if "main9_exact" in spec:
            main = _diagnosis_frame(dx, disease, "broad", spec["main10"], (), spec["main9_exact"])
        else:
            main = _diagnosis_frame(dx, disease, "broad", spec["main10"], spec.get("main9", ()))
        main = main.rename(columns={"subject_id": "dx_subject_id"})
        # Preserve the old broad extraction as a labeled sensitivity phenotype.
        if "legacy9_prefix" in spec:
            legacy = _diagnosis_frame(dx, disease, "legacy", spec["legacy10"], spec["legacy9_prefix"])
        else:
            legacy = _diagnosis_frame(dx, disease, "legacy", spec["legacy10"], spec.get("legacy9", ()))
        legacy = legacy.rename(columns={"subject_id": "dx_subject_id"})
        if main.empty and legacy.empty:
            print(f"   [membership] {disease}: no matches", flush=True)
            continue
        main = main.drop(columns=["disease"])
        legacy = legacy.drop(columns=["disease"])
        main = main.merge(legacy, on=["dx_subject_id", "hadm_id"], how="outer",
                          validate="one_to_one")
        main["disease"] = disease
        main["broad_inclusion"] = main["pos_broad"].notna().astype("Int8")
        main["legacy_broad_inclusion"] = main["pos_legacy"].notna().astype("Int8")
        if "narrow10" in spec:
            narrow = _diagnosis_frame(dx, disease, "narrow", spec["narrow10"], spec["narrow9"])
            narrow = narrow.rename(columns={"subject_id": "dx_subject_id"})
            main = main.merge(narrow.drop(columns=["disease"]), on=["dx_subject_id", "hadm_id"],
                              how="left", validate="one_to_one")
            main["narrow_inclusion"] = main["pos_narrow"].notna().astype("Int8")
        else:
            main["narrow_inclusion"] = pd.Series(pd.NA, index=main.index, dtype="Int8")
            main["pos_narrow"] = np.nan
            main["code_narrow"] = pd.NA
            main["version_narrow"] = pd.NA
        main["pos"] = main["pos_broad"]
        main["grp"] = pd.Series(pd.NA, index=main.index, dtype="Int8")
        main_present = main["pos"].notna()
        main.loc[main_present, "grp"] = np.where(main.loc[main_present, "pos"].eq(1), 0, 1)
        main["grp_broad"] = main["grp"]
        main["grp_narrow"] = pd.Series(pd.NA, index=main.index, dtype="Int8")
        narrow_present = main["pos_narrow"].notna()
        main.loc[narrow_present, "grp_narrow"] = np.where(main.loc[narrow_present, "pos_narrow"].eq(1), 0, 1)
        main["grp_legacy_broad"] = pd.Series(pd.NA, index=main.index, dtype="Int8")
        legacy_present = main["pos_legacy"].notna()
        main.loc[legacy_present, "grp_legacy_broad"] = np.where(main.loc[legacy_present, "pos_legacy"].eq(1), 0, 1)
        print(f"   [membership] {disease}: primary={int(main['broad_inclusion'].sum()):,}; "
              f"legacy={int(main['legacy_broad_inclusion'].sum()):,}; "
              f"narrow={int(main['narrow_inclusion'].fillna(0).sum()):,}", flush=True)
        frames.append(main)
    if not frames:
        raise ValueError("No target diagnosis codes matched the configured definitions")
    out = pd.concat(frames, ignore_index=True)
    out["subject_id"] = out["dx_subject_id"]
    out["narrow_inclusion"] = out["narrow_inclusion"].astype("Int8")
    out["legacy_broad_inclusion"] = out["legacy_broad_inclusion"].astype("Int8")
    return out


def add_observation_windows(frame: pd.DataFrame) -> pd.DataFrame:
    """Set ICU-relative 24-hour windows, capped at discharge/death; flag bad anchors."""
    out = frame.copy()
    full24_end = out["intime"] + pd.Timedelta(hours=24)
    disch_before = out["dischtime"].notna() & out["dischtime"].lt(out["intime"])
    death_before = out["deathtime"].notna() & out["deathtime"].lt(out["intime"])
    invalid = disch_before | death_before
    end = full24_end.copy()
    valid_discharge = out["dischtime"].notna() & out["dischtime"].ge(out["intime"])
    discharge_cap = valid_discharge & out["dischtime"].lt(end)
    end = end.where(~discharge_cap, out["dischtime"])
    valid_death = out["deathtime"].notna() & out["deathtime"].ge(out["intime"])
    death_cap = valid_death & out["deathtime"].lt(end)
    end = end.where(~death_cap, out["deathtime"])
    end = end.mask(invalid)
    out["window_anchor_inconsistent"] = invalid
    out["dischtime_before_intime"] = disch_before
    out["deathtime_before_intime"] = death_before
    out["chart_window_start"] = out["intime"].mask(invalid)
    out["chart_window_end"] = end
    out["lab_window_start"] = (out["intime"] - pd.Timedelta(hours=6)).mask(invalid)
    out["lab_window_end"] = end
    out["chart_window_truncated_by_discharge"] = discharge_cap & ~death_cap
    out["chart_window_truncated_by_death"] = death_cap
    out["lab_window_truncated_by_discharge"] = out["chart_window_truncated_by_discharge"]
    out["lab_window_truncated_by_death"] = out["chart_window_truncated_by_death"]
    reason = pd.Series("full_24h", index=out.index, dtype="string")
    reason.loc[discharge_cap & ~death_cap] = "discharge"
    reason.loc[death_cap] = "death"
    reason.loc[invalid] = "invalid_anchor"
    out["observation_window_end_reason"] = reason
    out["death_within_24h_of_index_icu"] = pd.Series(pd.NA, index=out.index, dtype="Int8")
    valid_death_time = valid_death
    out.loc[valid_death_time, "death_within_24h_of_index_icu"] = (
        out.loc[valid_death_time, "deathtime"] <= full24_end.loc[valid_death_time]).astype("int8")
    out.loc[out["died"].eq(0).fillna(False), "death_within_24h_of_index_icu"] = 0
    out["survived_first_24h_of_index_icu"] = pd.Series(pd.NA, index=out.index, dtype="Int8")
    out.loc[out["death_within_24h_of_index_icu"].eq(0), "survived_first_24h_of_index_icu"] = 1
    out.loc[out["death_within_24h_of_index_icu"].eq(1), "survived_first_24h_of_index_icu"] = 0
    return out


def build_index(zip_path: Path) -> tuple[pd.DataFrame, dict]:
    """Load small source tables and create adult, first-ICU admission rows."""
    print("[index] reading diagnosis codes", flush=True)
    dx = _csv_member(zip_path, MEMBERS["diagnoses"],
                     dtype={"icd_code": "string", "icd_version": "Int8"},
                     usecols=["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"])
    diagnosis_row_count = len(dx)
    diagnosis_seq_audit = _diagnosis_sequence_position_audit(dx)
    print(f"[index] diagnosis rows={diagnosis_row_count:,}; matching definitions", flush=True)
    members = build_memberships(dx)
    del dx
    print(f"[index] disease membership rows={len(members):,}; reading admissions", flush=True)
    adm = _csv_member(zip_path, MEMBERS["admissions"],
                      dtype={"hospital_expire_flag": "Float64"},
                      usecols=["subject_id", "hadm_id", "admittime", "dischtime",
                               "deathtime", "hospital_expire_flag"])
    print(f"[index] admissions rows={len(adm):,}; reading patients", flush=True)
    pat = _csv_member(zip_path, MEMBERS["patients"],
                      usecols=["subject_id", "gender", "anchor_age", "anchor_year", "anchor_year_group"])
    print(f"[index] patient rows={len(pat):,}; reading ICU stays", flush=True)
    stays = _csv_member(zip_path, MEMBERS["icustays"],
                        usecols=["subject_id", "hadm_id", "stay_id", "intime", "outtime"])
    print(f"[index] ICU stay rows={len(stays):,}; selecting earliest per admission", flush=True)
    stays["intime"] = pd.to_datetime(stays["intime"], errors="coerce")
    stays["outtime"] = pd.to_datetime(stays["outtime"], errors="coerce")
    stays["hadm_id"] = pd.to_numeric(stays["hadm_id"], errors="coerce")
    stays = stays.dropna(subset=["hadm_id", "intime"])
    stays = stays.sort_values(["hadm_id", "intime", "stay_id"], kind="mergesort")
    stays = stays.drop_duplicates("hadm_id", keep="first")
    for col in ("admittime", "dischtime", "deathtime"):
        adm[col] = pd.to_datetime(adm[col], errors="coerce")
    adm["hospital_expire_flag"] = pd.to_numeric(adm["hospital_expire_flag"], errors="coerce")
    pat["anchor_age"] = pd.to_numeric(pat["anchor_age"], errors="coerce")
    pat["anchor_year"] = pd.to_numeric(pat["anchor_year"], errors="coerce")
    out = members.merge(stays, on=["subject_id", "hadm_id"], how="inner", validate="many_to_one")
    out = out.merge(adm, on=["subject_id", "hadm_id"], how="left", validate="many_to_one")
    out = out.merge(pat, on="subject_id", how="left", validate="many_to_one")
    out["admission_year"] = out["admittime"].dt.year
    out["age_year_delta"] = out["admission_year"] - out["anchor_year"]
    out["age_at_admit"] = out["anchor_age"] + out["age_year_delta"]
    # MIMIC-IV top-codes age >89 to 91; retain the value but label it as a bound.
    out["age_topcoded_91"] = out["anchor_age"].eq(91)
    out["age_exact"] = out["anchor_age"].notna() & ~out["age_topcoded_91"]
    out = out[out["age_at_admit"].ge(18)].copy()
    out = out.rename(columns={"subject_id": "subject_id", "hadm_id": "hadm_id",
                              "hospital_expire_flag": "died"})
    out["pid"] = out["subject_id"]
    out["admission_id"] = out["hadm_id"]
    out = add_observation_windows(out)
    # Chronological first qualifying admission overall and within each disease.
    eligible = out[["subject_id", "hadm_id", "admittime", "disease"]].drop_duplicates()
    first_any = (eligible.sort_values(["subject_id", "admittime", "hadm_id"], kind="mergesort")
                 .drop_duplicates("subject_id").set_index("hadm_id").index)
    out["first_eligible_admission_any_disease"] = out["hadm_id"].isin(first_any)
    first_disease = (eligible.sort_values(["subject_id", "disease", "admittime", "hadm_id"], kind="mergesort")
                     .drop_duplicates(["subject_id", "disease"]).set_index(["hadm_id", "disease"]).index)
    out["first_eligible_admission_disease"] = pd.MultiIndex.from_frame(out[["hadm_id", "disease"]]).isin(first_disease)
    out = out.sort_values(["disease", "hadm_id"], kind="mergesort").reset_index(drop=True)
    stats = {
        "diagnosis_rows": diagnosis_row_count, "adult_disease_admissions": int(out["hadm_id"].nunique()),
        "diagnosis_seq_num_quality": diagnosis_seq_audit,
        "admission_disease_rows": len(out), "diseases": {str(k): int(v) for k, v in out.groupby("disease").size().items()},
        "patients_anchor_age_91": int(pat["anchor_age"].eq(91).sum()),
        "patients_anchor_age_300": int(pat["anchor_age"].eq(300).sum()),
        "adult_topcoded_rows": int(out["age_topcoded_91"].sum()),
        "missing_hospital_expire_flag": int(out["died"].isna().sum()),
        "chart_window_truncated_by_discharge": int(out["chart_window_truncated_by_discharge"].sum()),
        "chart_window_truncated_by_death": int(out["chart_window_truncated_by_death"].sum()),
        "dischtime_before_intime": int(out["dischtime_before_intime"].sum()),
        "deathtime_before_intime": int(out["deathtime_before_intime"].sum()),
        "window_anchor_inconsistent": int(out["window_anchor_inconsistent"].sum()),
        "death_within_24h_observed": int(out["death_within_24h_of_index_icu"].notna().sum()),
    }
    return out, stats


def _index_hash(index: pd.DataFrame) -> str:
    cols = index[["subject_id", "hadm_id", "stay_id", "disease", "pos", "grp",
                  "narrow_inclusion", "pos_narrow", "legacy_broad_inclusion", "pos_legacy",
                  "admittime", "intime", "outtime", "dischtime", "chart_window_start",
                  "chart_window_end", "lab_window_start", "lab_window_end", "window_anchor_inconsistent",
                  "observation_window_end_reason", "age_at_admit"]].copy()
    int_cols = ["subject_id", "hadm_id", "stay_id", "pos", "grp", "narrow_inclusion",
                "pos_narrow", "legacy_broad_inclusion", "pos_legacy", "age_at_admit"]
    for col in int_cols:
        values = pd.to_numeric(cols[col], errors="coerce")
        if (values.notna() & values.mod(1).ne(0)).any():
            raise ValueError(f"non-integral value in hashed index column {col}")
        cols[col] = values.astype("Int64").astype("string")
    datetime_cols = ["admittime", "intime", "outtime", "dischtime", "chart_window_start",
                     "chart_window_end", "lab_window_start", "lab_window_end"]
    for col in datetime_cols:
        values = pd.to_datetime(cols[col], errors="coerce")
        cols[col] = values.dt.strftime("%Y-%m-%dT%H:%M:%S.%f").astype("string")
    for col in ("disease", "observation_window_end_reason"):
        cols[col] = cols[col].astype("string")
    cols["window_anchor_inconsistent"] = cols["window_anchor_inconsistent"].astype("boolean").astype("string")
    payload = (cols.sort_values(["hadm_id", "disease"], kind="mergesort")
               .to_csv(index=False, na_rep="", lineterminator="\n").encode("utf-8"))
    return hashlib.sha256(payload).hexdigest()


def _window_maps(index: pd.DataFrame) -> tuple[dict[int, pd.Timestamp], dict[int, pd.Timestamp], set[int], set[int]]:
    unique = index.drop_duplicates("hadm_id")
    start_by_stay = dict(zip(unique["stay_id"].astype("int64"), unique["intime"]))
    end_by_stay = dict(zip(unique["stay_id"].astype("int64"), unique["chart_window_end"]))
    stay_ids = set(start_by_stay)
    hadm_ids = set(unique["hadm_id"].astype("int64"))
    return start_by_stay, end_by_stay, stay_ids, hadm_ids


def _cache_manifest_path(cache: Path) -> Path:
    return cache.with_suffix(cache.suffix + ".json")


def _cache_config() -> dict:
    return {
        "version": VERSION,
        "schema": FILTER_CACHE_SCHEMA,
        "chart_itemids": sorted(CHART_IDS), "lab_itemids": sorted(LAB_IDS),
        "chart_window": "[earliest ICU intime, min(intime+24h, valid dischtime, valid inpatient deathtime)]",
        "lab_window": "[earliest ICU intime-6h, min(intime+24h, valid dischtime, valid inpatient deathtime)]",
        "valid_ranges": VALID_RANGES,
        "lab_unit_filters": {"51144": ["%", "pct", "percent", "percentage", "per cent"]},
        "gcs_ett_handling": {
            "primary": "No Response-ETT/intubated/unassessable values are missing, including numeric fallback",
            "sensitivity": "No Response-ETT maps to 1",
        },
        "scores": {
            "qsofa_main": {"rr_ge": 22, "sbp_le": 100, "gcs_le": 13},
            "qsofa_gcs15_sensitivity": {"rr_ge": 22, "sbp_le": 100, "gcs_lt": 15},
            "curb65": {"gcs_lt": 15, "urea_mmol_l_gt": 7, "rr_ge": 30, "sbp_lt": 90, "dbp_le": 60, "age_ge": 65},
            "bisap4": {"bun_mg_dl_gt": 25, "gcs_lt": 15, "sirs_ge": 2, "age_gt": 60,
                       "omits_pleural_effusion": True},
            "sirs_operational": ["temperature", "heart_rate", "respiratory_rate",
                                 "WBC_or_bands_gt_10_percent"],
        },
        "diagnosis_definitions": DISEASES,
    }


def _config_fingerprint() -> str:
    return hashlib.sha256(json.dumps(_cache_config(), sort_keys=True, default=str,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _cache_is_valid(cache: Path, zip_path: Path, member: str, index_hash: str) -> bool:
    manifest_path = _cache_manifest_path(cache)
    if not cache.exists() or not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = _source_fingerprint(zip_path, member)
        return (manifest.get("schema") == FILTER_CACHE_SCHEMA
                and manifest.get("source") == expected
                and manifest.get("archive_fingerprint") == _archive_fingerprint(zip_path)
                and manifest.get("index_sha256") == index_hash
                and manifest.get("config_sha256") == _config_fingerprint()
                and manifest.get("code_sha256") == _sha256(Path(__file__))
                and manifest.get("cache_size") == cache.stat().st_size
                and manifest.get("cache_sha256") == _sha256(cache))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        return False


def _write_cache_manifest(cache: Path, zip_path: Path, member: str,
                          index_hash: str, row_count: int) -> None:
    manifest = {
        "schema": FILTER_CACHE_SCHEMA, "version": VERSION,
        "source": _source_fingerprint(zip_path, member),
        "archive_fingerprint": _archive_fingerprint(zip_path),
        "index_sha256": index_hash, "config_sha256": _config_fingerprint(),
        "code_sha256": _sha256(Path(__file__)), "cache_name": cache.name,
        "cache_size": cache.stat().st_size, "cache_sha256": _sha256(cache),
        "rows": int(row_count),
    }
    _write_json(_cache_manifest_path(cache), manifest)


def _index_cache_manifest_path(private_dir: Path) -> Path:
    return private_dir / "mimic_iv_v2_index_manifest.json"


def _index_cache_valid(private_dir: Path, zip_path: Path) -> bool:
    index_path = private_dir / "mimic_iv_v2_index.csv.gz"
    manifest_path = _index_cache_manifest_path(private_dir)
    if not index_path.exists() or not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return (manifest.get("version") == VERSION
                and manifest.get("archive_fingerprint") == _archive_fingerprint(zip_path)
                and manifest.get("code_sha256") == _sha256(Path(__file__))
                and manifest.get("config_sha256") == _config_fingerprint()
                and manifest.get("index_size") == index_path.stat().st_size
                and manifest.get("index_sha256") == _sha256(index_path))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        return False


def _read_index_cache(private_dir: Path) -> tuple[pd.DataFrame, dict, dict]:
    index_path = private_dir / "mimic_iv_v2_index.csv.gz"
    manifest = json.loads(_index_cache_manifest_path(private_dir).read_text(encoding="utf-8"))
    date_cols = ["admittime", "dischtime", "deathtime", "intime", "outtime",
                 "chart_window_start", "chart_window_end", "lab_window_start", "lab_window_end"]
    index = pd.read_csv(index_path, compression="gzip", parse_dates=date_cols,
                        low_memory=False)
    return index, manifest["index_stats"], manifest["dictionary_audit"]


def _write_index_cache(index: pd.DataFrame, index_stats: dict, dict_stats: dict,
                       private_dir: Path, zip_path: Path) -> dict:
    private_dir.mkdir(parents=True, exist_ok=True)
    index_path = private_dir / "mimic_iv_v2_index.csv.gz"
    tmp = index_path.with_name(index_path.name + ".partial")
    index.to_csv(tmp, index=False, compression="gzip")
    os.replace(tmp, index_path)
    manifest = {
        "version": VERSION, "source_zip": str(zip_path),
        "source_zip_size": zip_path.stat().st_size,
        "archive_fingerprint": _archive_fingerprint(zip_path),
        "code_sha256": _sha256(Path(__file__)), "config_sha256": _config_fingerprint(),
        "index_rows": len(index), "index_size": index_path.stat().st_size,
        "index_sha256": _sha256(index_path), "index_filter_sha256": _index_hash(index),
        "index_stats": index_stats,
        "diagnosis_seq_num_quality": index_stats.get("diagnosis_seq_num_quality"),
        "dictionary_audit": dict_stats,
    }
    _write_json(_index_cache_manifest_path(private_dir), manifest)
    return manifest


def _copy_dictionary_audits(private_dir: Path, out_dir: Path) -> None:
    for name in ("mimic_iv_v2_lab_dictionary_audit.csv", "mimic_iv_v2_icd_dictionary_audit.csv"):
        src = private_dir / name
        if src.exists():
            out = out_dir / name
            if not out.exists() or src.stat().st_mtime_ns > out.stat().st_mtime_ns:
                import shutil
                shutil.copy2(src, out)


def _atomic_filtered_cache(zip_path: Path, member: str, cache: Path,
                           *, table: str, index: pd.DataFrame,
                           chunksize: int) -> int:
    cache.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(cache.suffix + ".partial")
    tmp.unlink(missing_ok=True)
    start_by_stay, end_by_stay, stay_ids, hadm_ids = _window_maps(index)
    count = 0
    columns = ["stay_id", "hadm_id", "charttime", "itemid", "valuenum", "value"] if table == "chartevents" else [
        "hadm_id", "charttime", "itemid", "valuenum", "valueuom"]
    if table == "chartevents":
        usecols = columns
        dtype = {"stay_id": "Int64", "hadm_id": "Int64", "itemid": "int32", "value": "string"}
        ids = CHART_IDS
        id_col = "stay_id"
        start_map = start_by_stay
        end_map = end_by_stay
        before = pd.Timedelta(0)
    else:
        usecols = columns
        dtype = {"hadm_id": "Int64", "itemid": "int32"}
        ids = set(LAB_IDS)
        id_col = "hadm_id"
        start_map = dict(zip(index.drop_duplicates("hadm_id")["hadm_id"].astype("int64"),
                             index.drop_duplicates("hadm_id")["intime"]))
        end_map = dict(zip(index.drop_duplicates("hadm_id")["hadm_id"].astype("int64"),
                           index.drop_duplicates("hadm_id")["lab_window_end"]))
        before = pd.Timedelta(hours=-6)
    info = _source_fingerprint(zip_path, member)
    started = time.monotonic()
    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as writer:
        wrote_header = False
        for i, chunk in enumerate(_member_chunks(zip_path, member, chunksize=chunksize,
                                                  usecols=usecols, dtype=dtype), 1):
            chunk = chunk[chunk["itemid"].isin(ids)]
            if chunk.empty:
                continue
            if table == "labevents":
                percent_bands = chunk["itemid"].eq(51144) & _percent_unit_mask(chunk["valueuom"])
                chunk = chunk[~chunk["itemid"].eq(51144) | percent_bands]
                if chunk.empty:
                    continue
            chunk[id_col] = pd.to_numeric(chunk[id_col], errors="coerce")
            if table == "chartevents":
                chunk = chunk[chunk["stay_id"].isin(stay_ids)]
            else:
                chunk = chunk[chunk["hadm_id"].isin(hadm_ids)]
            if chunk.empty:
                continue
            chunk["charttime"] = pd.to_datetime(chunk["charttime"], errors="coerce")
            chunk["t0"] = chunk[id_col].map(start_map)
            chunk["window_end"] = chunk[id_col].map(end_map)
            chunk = chunk[(chunk["charttime"] >= chunk["t0"] + before)
                          & (chunk["charttime"] <= chunk["window_end"])]
            if chunk.empty:
                continue
            chunk = chunk[columns]
            chunk.to_csv(writer, index=False, header=not wrote_header, na_rep="")
            wrote_header = True
            count += len(chunk)
            if i == 1 or i % 5 == 0:
                elapsed = max(time.monotonic() - started, 1e-6)
                print(f"   {table} cache chunk={i} selected={count:,} "
                      f"rows_per_s={count / elapsed:,.0f}", flush=True)
        if not wrote_header:
            pd.DataFrame(columns=columns).to_csv(writer, index=False)
    os.replace(tmp, cache)
    _write_cache_manifest(cache, zip_path, member, _index_hash(index), count)
    return count


def _read_cache_chunks(path: Path, *, chunksize: int, dtype: dict | None = None) -> Iterator[pd.DataFrame]:
    with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as f:
        yield from pd.read_csv(f, chunksize=chunksize, dtype=dtype, low_memory=False,
                               keep_default_na=False, na_values=[""])


def _valid_numeric(values: pd.Series, low: float, high: float) -> tuple[pd.Series, int]:
    x = pd.to_numeric(values, errors="coerce")
    valid = x.between(low, high, inclusive="both")
    return x.where(valid), int((x.notna() & ~valid).sum())


def _merge_extreme(state: dict[int, float], values: pd.Series, how: str) -> None:
    if values.empty:
        return
    grouped = values.groupby(level=0).max() if how == "max" else values.groupby(level=0).min()
    for key, value in grouped.items():
        k, x = int(key), float(value)
        old = state.get(k)
        if old is None or (x > old if how == "max" else x < old):
            state[k] = x


def _map_gcs_values(frame: pd.DataFrame, *, ett_as_one: bool = False) -> pd.Series:
    raw = (frame["value"].astype("string").str.strip().str.lower()
           .str.replace(r"\s*[-–]\s*", "-", regex=True))
    unassessable = raw.str.contains(GCS_UNASSESSABLE_PATTERN, regex=True, na=False)
    out = pd.Series(np.nan, index=frame.index, dtype="float64")
    for itemid, mapping in GCS_MAP.items():
        sel = frame["itemid"].eq(itemid)
        item_mapping = mapping
        if ett_as_one:
            item_mapping = {**mapping, **GCS_ETT_AS1_MAP.get(itemid, {})}
        out.loc[sel] = raw.loc[sel].map(item_mapping)
        # Some exports store the integer level in valuenum; accept only in-range integers.
        num = pd.to_numeric(frame.loc[sel, "valuenum"], errors="coerce")
        maximum = {220739: 4, 223900: 5, 223901: 6}[itemid]
        numeric_ok = num.between(1, maximum) & np.isclose(num.fillna(0) % 1, 0)
        selected_index = frame.index[sel]
        fallback = out.loc[selected_index].isna() & numeric_ok & ~unassessable.loc[selected_index]
        out.loc[selected_index[fallback.to_numpy()]] = num.loc[fallback]
    return out


def _reduce_gcs_timepoints(parts: list[pd.DataFrame], *, ett_as_one: bool) -> pd.DataFrame:
    """Sum only complete same-time triples and retain each GCS interpretation."""
    if ett_as_one:
        empty = pd.DataFrame({
            "stay_id": pd.Series(dtype="int64"),
            "gcs_worst_ett_as1": pd.Series(dtype="float64"),
            "gcs_worst_ett_as1_charttime": pd.Series(dtype="datetime64[ns]"),
            "gcs_ett_as1_n_complete_times": pd.Series(dtype="int64"),
        })
    else:
        empty = pd.DataFrame({
            "stay_id": pd.Series(dtype="int64"), "gcs_worst": pd.Series(dtype="float64"),
            "gcs_worst_charttime": pd.Series(dtype="datetime64[ns]"),
            "gcs_eye_at_time": pd.Series(dtype="float64"),
            "gcs_verbal_at_time": pd.Series(dtype="float64"),
            "gcs_motor_at_time": pd.Series(dtype="float64"),
            "gcs_n_complete_times": pd.Series(dtype="int64"),
        })
    if not parts:
        return empty
    gcs = pd.concat(parts, ignore_index=True)
    gcs = (gcs.groupby(["stay_id", "charttime", "itemid"], as_index=False)["gcs_value"].min()
           .pivot(index=["stay_id", "charttime"], columns="itemid", values="gcs_value"))
    gcs = gcs.reindex(columns=[220739, 223900, 223901])
    gcs.columns = ["gcs_eye_at_time", "gcs_verbal_at_time", "gcs_motor_at_time"]
    gcs["gcs_total_at_time"] = gcs.sum(axis=1, min_count=3)
    gcs = gcs.dropna(subset=["gcs_total_at_time"]).reset_index()
    if gcs.empty:
        return empty
    gcs = gcs.sort_values(["stay_id", "gcs_total_at_time", "charttime"], kind="mergesort")
    worst = gcs.drop_duplicates("stay_id", keep="first")
    n_times = gcs.groupby("stay_id").size()
    if ett_as_one:
        out = worst[["stay_id", "gcs_total_at_time", "charttime"]].rename(columns={
            "gcs_total_at_time": "gcs_worst_ett_as1",
            "charttime": "gcs_worst_ett_as1_charttime",
        })
        out["gcs_ett_as1_n_complete_times"] = out["stay_id"].map(n_times).astype("int64")
        return out
    out = worst[["stay_id", "gcs_total_at_time", "charttime", "gcs_eye_at_time",
                 "gcs_verbal_at_time", "gcs_motor_at_time"]].rename(columns={
        "gcs_total_at_time": "gcs_worst", "charttime": "gcs_worst_charttime",
    })
    out["gcs_n_complete_times"] = out["stay_id"].map(n_times).astype("int64")
    return out


def aggregate_chart_cache(cache: Path) -> tuple[pd.DataFrame, dict]:
    """Aggregate valid extrema by feature, and complete GCS triples by timestamp."""
    features: dict[str, dict[int, float]] = {
        "rr_max": {}, "sbp_a_min": {}, "dbp_a_min": {}, "sbp_n_min": {},
        "dbp_n_min": {}, "hr_max": {}, "temp_c_min": {}, "temp_c_max": {},
    }
    invalid: dict[str, int] = {}
    valid_counts: dict[str, int] = {}
    gcs_parts: list[pd.DataFrame] = []
    gcs_parts_ett_as1: list[pd.DataFrame] = []
    for chunk in _read_cache_chunks(cache, chunksize=1_000_000,
                                    dtype={"stay_id": "Int64", "itemid": "int32"}):
        chunk["stay_id"] = pd.to_numeric(chunk["stay_id"], errors="coerce")
        chunk["itemid"] = pd.to_numeric(chunk["itemid"], errors="coerce")
        chunk["charttime"] = pd.to_datetime(chunk["charttime"], errors="coerce")
        g = chunk[chunk["itemid"].isin(GCS_IDS) & chunk["stay_id"].notna()
                   & chunk["charttime"].notna()].copy()
        if not g.empty:
            g["gcs_value"] = _map_gcs_values(g)
            g["gcs_value_ett_as1"] = _map_gcs_values(g, ett_as_one=True)
            primary = g[g["gcs_value"].notna()]
            if not primary.empty:
                gcs_parts.append(primary[["stay_id", "charttime", "itemid", "gcs_value"]])
            ett_sensitivity = g[g["gcs_value_ett_as1"].notna()]
            if not ett_sensitivity.empty:
                gcs_parts_ett_as1.append(
                    ett_sensitivity[["stay_id", "charttime", "itemid", "gcs_value_ett_as1"]]
                    .rename(columns={"gcs_value_ett_as1": "gcs_value"}))
        for itemid, feature in CHART_ITEM_FEATURE.items():
            if itemid in GCS_IDS:
                continue
            x = chunk[chunk["itemid"].eq(itemid) & chunk["stay_id"].notna()].copy()
            if x.empty:
                continue
            value = pd.to_numeric(x["valuenum"], errors="coerce")
            if itemid in (220050, 220179):
                value, nbad = _valid_numeric(value, *VALID_RANGES["sbp"])
                how = "min"
                feature = "sbp_a_min" if itemid == 220050 else "sbp_n_min"
            elif itemid in (220051, 220180):
                value, nbad = _valid_numeric(value, *VALID_RANGES["dbp"])
                how = "min"
                feature = "dbp_a_min" if itemid == 220051 else "dbp_n_min"
            elif itemid == 220210:
                value, nbad = _valid_numeric(value, *VALID_RANGES["rr"])
                how = "max"
            elif itemid == 220045:
                value, nbad = _valid_numeric(value, *VALID_RANGES["hr"])
                how = "max"
            elif itemid == 223761:
                value = (value - 32.0) * 5.0 / 9.0
                value, nbad = _valid_numeric(value, *VALID_RANGES["temp_c"])
                how = "minmax"
            elif itemid == 223762:
                value, nbad = _valid_numeric(value, *VALID_RANGES["temp_c"])
                how = "minmax"
            else:
                continue
            invalid[feature] = invalid.get(feature, 0) + nbad
            valid_counts[feature] = valid_counts.get(feature, 0) + int(value.notna().sum())
            vals = pd.Series(value.to_numpy(), index=x["stay_id"].to_numpy()).dropna()
            if how == "minmax":
                _merge_extreme(features["temp_c_min"], vals, "min")
                _merge_extreme(features["temp_c_max"], vals, "max")
            else:
                _merge_extreme(features[feature], vals, how)
    out = pd.DataFrame({"stay_id": pd.Series(
        sorted(set().union(*(set(x) for x in features.values()))), dtype="int64")})
    for feature, values in features.items():
        out[feature] = out["stay_id"].map(values)
    primary_gcs = _reduce_gcs_timepoints(gcs_parts, ett_as_one=False)
    ett_gcs = _reduce_gcs_timepoints(gcs_parts_ett_as1, ett_as_one=True)
    out = out.merge(primary_gcs, on="stay_id", how="outer", validate="one_to_one")
    out = out.merge(ett_gcs, on="stay_id", how="outer", validate="one_to_one")
    for col in features:
        if col not in out:
            out[col] = np.nan
    for col in ("gcs_worst", "gcs_worst_charttime", "gcs_eye_at_time",
                "gcs_verbal_at_time", "gcs_motor_at_time", "gcs_n_complete_times",
                "gcs_worst_ett_as1", "gcs_worst_ett_as1_charttime",
                "gcs_ett_as1_n_complete_times"):
        if col not in out:
            out[col] = pd.NaT if col in ("gcs_worst_charttime", "gcs_worst_ett_as1_charttime") else np.nan
    out["sbp_min"] = out[["sbp_a_min", "sbp_n_min"]].min(axis=1)
    out["dbp_min"] = out[["dbp_a_min", "dbp_n_min"]].min(axis=1)
    return out, {"invalid_numeric_values": invalid, "valid_numeric_values": valid_counts,
                 "valid_complete_gcs_timepoints": int(out["gcs_n_complete_times"].fillna(0).sum()),
                 "valid_complete_gcs_timepoints_ett_as1": int(
                     out["gcs_ett_as1_n_complete_times"].fillna(0).sum())}


def aggregate_lab_cache(cache: Path) -> tuple[pd.DataFrame, dict]:
    """Worst BUN, WBC extrema, and percent-qualified bands over the lab window."""
    states: dict[str, dict[int, float]] = {
        "bun_max": {}, "wbc_min": {}, "wbc_max": {}, "bands_pct_max": {},
    }
    invalid: dict[str, int] = {}
    counts: dict[str, int] = {}
    for chunk in _read_cache_chunks(cache, chunksize=1_000_000,
                                    dtype={"hadm_id": "Int64", "itemid": "int32"}):
        chunk["hadm_id"] = pd.to_numeric(chunk["hadm_id"], errors="coerce")
        chunk["itemid"] = pd.to_numeric(chunk["itemid"], errors="coerce")
        for itemid in LAB_IDS:
            x = chunk[chunk["itemid"].eq(itemid) & chunk["hadm_id"].notna()]
            if x.empty:
                continue
            value = pd.to_numeric(x["valuenum"], errors="coerce")
            if itemid == 51006:
                value, nbad = _valid_numeric(value, *VALID_RANGES["bun"])
                invalid["bun"] = invalid.get("bun", 0) + nbad
                counts["bun"] = counts.get("bun", 0) + int(value.notna().sum())
                _merge_extreme(states["bun_max"], pd.Series(value.to_numpy(), index=x["hadm_id"].to_numpy()).dropna(), "max")
            elif itemid == 51144:
                # The extraction filter retains this item only when valueuom is
                # an explicit percentage unit; do not infer units from the label.
                value, nbad = _valid_numeric(value, *VALID_RANGES["bands_pct"])
                invalid["bands_pct"] = invalid.get("bands_pct", 0) + nbad
                counts["bands_pct"] = counts.get("bands_pct", 0) + int(value.notna().sum())
                _merge_extreme(states["bands_pct_max"],
                               pd.Series(value.to_numpy(), index=x["hadm_id"].to_numpy()).dropna(), "max")
            else:
                value, nbad = _valid_numeric(value, *VALID_RANGES["wbc"])
                invalid["wbc"] = invalid.get("wbc", 0) + nbad
                counts["wbc"] = counts.get("wbc", 0) + int(value.notna().sum())
                vals = pd.Series(value.to_numpy(), index=x["hadm_id"].to_numpy()).dropna()
                _merge_extreme(states["wbc_min"], vals, "min")
                _merge_extreme(states["wbc_max"], vals, "max")
    ids = sorted(set().union(*(set(x) for x in states.values())))
    out = pd.DataFrame({"hadm_id": ids})
    for feature, values in states.items():
        out[feature] = out["hadm_id"].map(values)
    out["wbc"] = out["wbc_max"]
    out["urea_mmol_l"] = out["bun_max"] / 2.8
    return out, {"invalid_lab_values": invalid, "valid_lab_values": counts}


def _tri_threshold(values: pd.Series, threshold: float, *, op: str) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce")
    out = pd.Series(pd.NA, index=values.index, dtype="Int8")
    valid = x.notna()
    if op == "ge":
        out.loc[valid] = x.loc[valid].ge(threshold).astype("int8")
    elif op == "gt":
        out.loc[valid] = x.loc[valid].gt(threshold).astype("int8")
    elif op == "le":
        out.loc[valid] = x.loc[valid].le(threshold).astype("int8")
    elif op == "lt":
        out.loc[valid] = x.loc[valid].lt(threshold).astype("int8")
    else:
        raise ValueError(op)
    return out


def _tri_or(a: pd.Series, b: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=a.index, dtype="Int8")
    out.loc[a.eq(1).fillna(False) | b.eq(1).fillna(False)] = 1
    out.loc[a.eq(0).fillna(False) & b.eq(0).fillna(False)] = 0
    return out


def _score_bounds(frame: pd.DataFrame, components: list[str], name: str) -> None:
    x = frame[components].astype("Int8")
    observed = x.notna().sum(axis=1).astype("int16")
    lower = x.fillna(0).astype("int16").sum(axis=1)
    unknown = len(components) - observed
    upper = lower + unknown
    frame[name] = lower.where(unknown.eq(0), pd.NA).astype("Int64")
    frame[f"{name}_lower"] = lower.astype("Int64")
    frame[f"{name}_upper"] = upper.astype("Int64")
    frame[f"{name}_observed_points"] = lower.astype("Int64")
    frame[f"{name}_components_observed"] = observed.astype("Int8")
    frame[f"{name}_components_required"] = len(components)
    frame[f"{name}_unknown_components"] = unknown.astype("Int8")
    frame[f"{name}_complete"] = unknown.eq(0)


def score_panel(frame: pd.DataFrame) -> pd.DataFrame:
    """Add canonical scores, component flags, complete-score counts, and bounds."""
    m = frame.copy()
    if "bands_pct_max" not in m:
        m["bands_pct_max"] = np.nan
    if "gcs_worst_ett_as1" not in m:
        m["gcs_worst_ett_as1"] = np.nan
    # qSOFA's cited primary GCS threshold is <=13; retain the common <15 variant.
    m["q_rr"] = _tri_threshold(m["rr_max"], 22, op="ge")
    m["q_sbp"] = _tri_threshold(m["sbp_min"], 100, op="le")
    m["q_gcs13"] = _tri_threshold(m["gcs_worst"], 13, op="le")
    m["q_gcs15"] = _tri_threshold(m["gcs_worst"], 15, op="lt")
    _score_bounds(m, ["q_rr", "q_sbp", "q_gcs13"], "qsofa")
    _score_bounds(m, ["q_rr", "q_sbp", "q_gcs15"], "qsofa_gcs15")
    m["q_gcs13_ett_as1"] = _tri_threshold(m["gcs_worst_ett_as1"], 13, op="le")
    m["q_gcs15_ett_as1"] = _tri_threshold(m["gcs_worst_ett_as1"], 15, op="lt")
    _score_bounds(m, ["q_rr", "q_sbp", "q_gcs13_ett_as1"], "qsofa_ett_as1")
    _score_bounds(m, ["q_rr", "q_sbp", "q_gcs15_ett_as1"], "qsofa_gcs15_ett_as1")

    m["curb_confusion_proxy"] = _tri_threshold(m["gcs_worst"], 15, op="lt")
    m["curb_confusion_proxy_ett_as1"] = _tri_threshold(m["gcs_worst_ett_as1"], 15, op="lt")
    m["curb_urea"] = _tri_threshold(m["urea_mmol_l"], 7, op="gt")
    m["curb_rr"] = _tri_threshold(m["rr_max"], 30, op="ge")
    m["curb_sbp_lt90"] = _tri_threshold(m["sbp_min"], 90, op="lt")
    m["curb_dbp_le60"] = _tri_threshold(m["dbp_min"], 60, op="le")
    m["curb_bp"] = _tri_or(m["curb_sbp_lt90"], m["curb_dbp_le60"])
    m["curb_age65"] = _tri_threshold(m["age_at_admit"], 65, op="ge")
    _score_bounds(m, ["curb_confusion_proxy", "curb_urea", "curb_rr", "curb_bp", "curb_age65"], "curb65")
    _score_bounds(m, ["curb_confusion_proxy_ett_as1", "curb_urea", "curb_rr", "curb_bp", "curb_age65"],
                  "curb65_ett_as1")

    m["sirs_temp"] = pd.Series(pd.NA, index=m.index, dtype="Int8")
    temp_known = m["temp_c_min"].notna() & m["temp_c_max"].notna()
    temp_bad = m["temp_c_min"].lt(36) | m["temp_c_max"].gt(38)
    m.loc[temp_known, "sirs_temp"] = temp_bad.loc[temp_known].astype("int8")
    m["sirs_hr"] = _tri_threshold(m["hr_max"], 90, op="gt")
    m["sirs_rr"] = _tri_threshold(m["rr_max"], 20, op="gt")
    m["sirs_wbc"] = pd.Series(pd.NA, index=m.index, dtype="Int8")
    wbc_known = m["wbc_min"].notna() & m["wbc_max"].notna()
    wbc_bad = m["wbc_min"].lt(4) | m["wbc_max"].gt(12)
    wbc_component = pd.Series(pd.NA, index=m.index, dtype="Int8")
    wbc_bad = wbc_bad.fillna(False)
    wbc_component.loc[wbc_bad] = 1
    wbc_component.loc[wbc_known & ~wbc_bad] = 0
    bands_component = _tri_threshold(m["bands_pct_max"], 10, op="gt")
    m["sirs_wbc"] = _tri_or(wbc_component, bands_component)
    sirs = m[["sirs_temp", "sirs_hr", "sirs_rr", "sirs_wbc"]].astype("Int8")
    sirs_known = sirs.notna().sum(axis=1)
    sirs_lower = sirs.fillna(0).astype("int8").sum(axis=1)
    sirs_upper = sirs_lower + (4 - sirs_known)
    m["sirs"] = sirs_lower.where(sirs_known.eq(4), pd.NA).astype("Int64")
    m["sirs_lower"] = sirs_lower.astype("Int64")
    m["sirs_upper"] = sirs_upper.astype("Int64")
    m["sirs_components_observed"] = sirs_known.astype("Int8")
    m["bisap_bun"] = _tri_threshold(m["bun_max"], 25, op="gt")
    m["bisap_gcs_proxy"] = _tri_threshold(m["gcs_worst"], 15, op="lt")
    m["bisap_gcs_proxy_ett_as1"] = _tri_threshold(m["gcs_worst_ett_as1"], 15, op="lt")
    m["bisap_sirs2"] = pd.Series(pd.NA, index=m.index, dtype="Int8")
    m.loc[sirs_lower.ge(2), "bisap_sirs2"] = 1
    m.loc[sirs_upper.lt(2), "bisap_sirs2"] = 0
    m["bisap_age60"] = _tri_threshold(m["age_at_admit"], 60, op="gt")
    _score_bounds(m, ["bisap_bun", "bisap_gcs_proxy", "bisap_sirs2", "bisap_age60"], "bisap4")
    _score_bounds(m, ["bisap_bun", "bisap_gcs_proxy_ett_as1", "bisap_sirs2", "bisap_age60"],
                  "bisap4_ett_as1")
    return m


def audit_small_dictionaries(zip_path: Path, out_dir: Path) -> dict:
    """Write a small item/code dictionary audit; this reads no patient observations."""
    lab = _csv_member(zip_path, MEMBERS["d_labitems"], usecols=["itemid", "label", "fluid", "category"])
    lab["label_norm"] = lab["label"].fillna("").astype(str).str.lower()
    lab_audit = lab[lab["itemid"].isin([51006, 51300, 51301, 51144])
                    | lab["label_norm"].str.contains(r"band|pco2|carbon dioxide", regex=True)]
    lab_audit.to_csv(out_dir / "mimic_iv_v2_lab_dictionary_audit.csv", index=False)
    icd = _csv_member(zip_path, MEMBERS["d_icd_diagnoses"],
                      dtype={"icd_code": "string", "icd_version": "Int8"},
                      usecols=["icd_code", "icd_version", "long_title"])
    codes = {"I110", "I130", "I132", "40201", "40211", "40291", "40401", "40403", "40411", "40413", "40491", "40493",
             "J43", "J44", "4912", "492", "496", "5770", "5771", "5772", "A40", "A41", "R652", "038", "99591", "99592", "78552"}
    icd["code_norm"] = icd["icd_code"].fillna("").astype("string").str.upper().str.replace(".", "", regex=False)
    icd_audit = icd[icd["code_norm"].isin(codes)]
    icd_audit.to_csv(out_dir / "mimic_iv_v2_icd_dictionary_audit.csv", index=False)
    return {
        "lab_dictionary_items_matching_candidates": int(len(lab_audit)),
        "lab_dictionary_band_itemids": [int(x) for x in lab.loc[lab["label_norm"].str.contains("band", na=False), "itemid"].dropna().unique()],
        "lab_dictionary_pco2_itemids": [int(x) for x in lab.loc[lab["label_norm"].str.contains(r"pco2|carbon dioxide", regex=True, na=False), "itemid"].dropna().unique()],
        "icd_dictionary_rows_audited": int(len(icd_audit)),
    }


def _merge_aggregate(index: pd.DataFrame, chart: pd.DataFrame, labs: pd.DataFrame) -> pd.DataFrame:
    panel = index.merge(chart, on="stay_id", how="left", validate="many_to_one")
    panel = panel.merge(labs, on="hadm_id", how="left", validate="many_to_one")
    # Keep the window anchors explicit in the row-level provenance.
    return score_panel(panel)


def _definition_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    definitions = []
    for disease in DISEASES:
        definitions.append((disease, panel["disease"].eq(disease) & panel["broad_inclusion"].eq(1), "grp"))
    for disease in ("sepsis", "pneumonia"):
        definitions.append((f"{disease}_narrow",
                            panel["disease"].eq(disease) & panel["narrow_inclusion"].eq(1),
                            "grp_narrow"))
    for disease in DISEASES:
        if disease not in {"sepsis", "pneumonia"}:
            definitions.append((f"{disease}_legacy_broad",
                                panel["disease"].eq(disease) & panel["legacy_broad_inclusion"].eq(1),
                                "grp_legacy_broad"))
    for definition_name, mask, group_col in definitions:
        sub = panel.loc[mask].copy()
        if sub.empty:
            continue
        sub["definition"] = definition_name if definition_name.endswith(("_narrow", "_legacy_broad")) else sub["disease"]
        grouped = sub.groupby(["definition", group_col], dropna=False)
        for (definition, grp), g in grouped:
            for score in SCORE_NAMES:
                rows.append({
                    "definition": definition, "grp": grp, "score": score,
                    "n_rows": len(g), "n_hadm": int(g["hadm_id"].nunique()),
                    "n_pid": int(g["pid"].nunique()),
                    "n_died_observed": int(g["died"].notna().sum()),
                    "n_died": int(g["died"].eq(1).sum()),
                    "n_score_complete": int(g[score].notna().sum()),
                    "n_score_partial": int((g[f"{score}_components_observed"].gt(0)
                                             & g[f"{score}_components_observed"].lt(g[f"{score}_components_required"])).sum()),
                    "n_score_any_observed_component": int(g[f"{score}_components_observed"].gt(0).sum()),
                    "observed_points_total": int(g[f"{score}_observed_points"].sum()),
                    "mean_score_lower": float(g[f"{score}_lower"].mean()),
                    "mean_score_upper": float(g[f"{score}_upper"].mean()),
                    "n_score_all_components_unknown": int(g[f"{score}_components_observed"].eq(0).sum()),
                    "n_outcome_missing": int(g["died"].isna().sum()),
                })
    return pd.DataFrame(rows)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, default=ZIP_DEFAULT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--private-dir", type=Path, default=PRIVATE_DEFAULT,
                        help="private row-level index, panel, and filtered cache directory")
    parser.add_argument("--cache-dir", type=Path, default=None,
                        help="defaults to <private-dir>/cache")
    parser.add_argument("--index-only", action="store_true", help="build the small admission index, no vital/lab scan")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="require verified private index/event caches and reduce them without source-table reads")
    parser.add_argument("--force-rescan", action="store_true", help="ignore filtered event caches and scan source members")
    parser.add_argument("--chart-chunksize", type=int, default=CHART_CHUNK_SIZE)
    parser.add_argument("--lab-chunksize", type=int, default=LAB_CHUNK_SIZE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    zip_path = args.zip.resolve()
    if not zip_path.is_file():
        raise FileNotFoundError(zip_path)
    if args.index_only and args.aggregate_only:
        raise SystemExit("--index-only and --aggregate-only cannot be combined")
    if args.aggregate_only and args.force_rescan:
        raise SystemExit("--aggregate-only cannot be combined with --force-rescan")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.private_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.cache_dir or (args.private_dir / "cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{VERSION}] source={zip_path} ({zip_path.stat().st_size:,} bytes)", flush=True)
    index_path = args.private_dir / "mimic_iv_v2_index.csv.gz"
    if args.aggregate_only and not _index_cache_valid(args.private_dir, zip_path):
        raise SystemExit("--aggregate-only requires a verified cached admission index")
    if not args.force_rescan and _index_cache_valid(args.private_dir, zip_path):
        print("[index] reuse verified private admission index", flush=True)
        index, index_stats, dict_stats = _read_index_cache(args.private_dir)
        index_manifest = json.loads(_index_cache_manifest_path(args.private_dir).read_text(encoding="utf-8"))
    else:
        print("[index] cache miss; building adult first-ICU admission index", flush=True)
        index, index_stats = build_index(zip_path)
        print("[index] auditing small item/code dictionaries", flush=True)
        dict_stats = audit_small_dictionaries(zip_path, args.private_dir)
        index_manifest = _write_index_cache(index, index_stats, dict_stats, args.private_dir, zip_path)
    if not all((args.private_dir / name).exists() for name in
               ("mimic_iv_v2_lab_dictionary_audit.csv", "mimic_iv_v2_icd_dictionary_audit.csv")):
        dict_stats = audit_small_dictionaries(zip_path, args.private_dir)
        index_manifest["dictionary_audit"] = dict_stats
        _write_json(_index_cache_manifest_path(args.private_dir), index_manifest)
    _copy_dictionary_audits(args.private_dir, args.out_dir)
    print(f"   index rows={len(index):,} admissions={index['hadm_id'].nunique():,}; "
          f"disease rows={index_stats['diseases']}; topcoded anchor_age=91 rows="
          f"{index_stats['adult_topcoded_rows']:,}", flush=True)
    _write_json(args.out_dir / "mimic_iv_v2_index_manifest.json", index_manifest)
    if args.index_only:
        print(f"[index-only] wrote {index_path}", flush=True)
        return 0

    ihash = index_manifest["index_filter_sha256"]
    chart_cache = cache_dir / "mimic_iv_chartevents_filtered.csv.gz"
    lab_cache = cache_dir / "mimic_iv_labevents_filtered.csv.gz"
    if args.aggregate_only:
        if not _cache_is_valid(chart_cache, zip_path, MEMBERS["chartevents"], ihash):
            raise SystemExit("--aggregate-only requires a verified filtered chartevents cache")
        if not _cache_is_valid(lab_cache, zip_path, MEMBERS["labevents"], ihash):
            raise SystemExit("--aggregate-only requires a verified filtered labevents cache")
        n_chart = int(json.loads(_cache_manifest_path(chart_cache).read_text()).get("rows", 0))
        n_lab = int(json.loads(_cache_manifest_path(lab_cache).read_text()).get("rows", 0))
        print(f"[cache-only] verified chart rows={n_chart:,}; lab rows={n_lab:,}; no source event reads", flush=True)
    elif args.force_rescan or not _cache_is_valid(chart_cache, zip_path, MEMBERS["chartevents"], ihash):
        print("[chart] streaming selected itemids/stays to a filtered cache", flush=True)
        n_chart = _atomic_filtered_cache(zip_path, MEMBERS["chartevents"], chart_cache,
                                         table="chartevents", index=index,
                                         chunksize=args.chart_chunksize)
    else:
        n_chart = int(json.loads(_cache_manifest_path(chart_cache).read_text()).get("rows", 0))
        print(f"[chart] reuse verified filtered cache rows={n_chart:,}", flush=True)
    if not args.aggregate_only and (args.force_rescan or not _cache_is_valid(lab_cache, zip_path, MEMBERS["labevents"], ihash)):
        print("[labs] streaming selected itemids/admissions to a filtered cache", flush=True)
        n_lab = _atomic_filtered_cache(zip_path, MEMBERS["labevents"], lab_cache,
                                       table="labevents", index=index,
                                       chunksize=args.lab_chunksize)
    else:
        n_lab = int(json.loads(_cache_manifest_path(lab_cache).read_text()).get("rows", 0))
        print(f"[labs] reuse verified filtered cache rows={n_lab:,}", flush=True)
    print("[aggregate] reducing filtered caches", flush=True)
    chart, chart_stats = aggregate_chart_cache(chart_cache)
    labs, lab_stats = aggregate_lab_cache(lab_cache)
    panel = _merge_aggregate(index, chart, labs)
    panel_path = args.private_dir / "mimic_iv_v2_score_panel.csv.gz"
    panel.to_csv(panel_path, index=False, compression="gzip")
    summary = _definition_summary(panel)
    summary_path = args.out_dir / "mimic_iv_v2_score_coverage.csv"
    summary.to_csv(summary_path, index=False)
    manifest = {
        "version": VERSION, "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "source_zip": str(zip_path), "source_zip_size": zip_path.stat().st_size,
        "source_zip_mtime_ns": zip_path.stat().st_mtime_ns,
        "archive_fingerprint": _archive_fingerprint(zip_path),
        "members": {name: _source_fingerprint(zip_path, member) for name, member in MEMBERS.items()},
        "index_stats": index_stats,
        "diagnosis_seq_num_quality": index_stats.get("diagnosis_seq_num_quality"),
        "dictionary_audit": dict_stats,
        "filtered_chart_rows": n_chart, "filtered_lab_rows": n_lab,
        "chart_aggregation": chart_stats, "lab_aggregation": lab_stats,
        "panel_rows": len(panel), "unique_admissions": int(panel["hadm_id"].nunique()),
        "unique_patients": int(panel["pid"].nunique()),
        "missing_outcome_rows": int(panel["died"].isna().sum()),
        "gcs_ett_as1_sensitivity": "No Response-ETT/unassessable primary GCS values are missing; alternate score fields map No Response-ETT to 1.",
        "score_complete_counts": {s: int(panel[s].notna().sum()) for s in SCORE_NAMES},
        "score_all_missing_component_counts": {s: int(panel[f"{s}_components_observed"].eq(0).sum()) for s in SCORE_NAMES},
        "private_directory": str(args.private_dir),
        "filtered_cache_directory": str(cache_dir),
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": _sha256(p)}
                  for p in (index_path, panel_path, summary_path)},
    }
    _write_json(args.out_dir / "mimic_iv_v2_run_manifest.json", manifest)
    print(f"[done] rows={len(panel):,}; admissions={panel['hadm_id'].nunique():,}; "
          f"patients={panel['pid'].nunique():,}; missing outcomes={panel['died'].isna().sum():,}", flush=True)
    for score in SCORE_NAMES:
        print(f"   {score}: complete={panel[score].notna().sum():,}; "
              f"partial={(panel[f'{score}_components_observed'].gt(0) & ~panel[f'{score}_complete']).sum():,}; "
              f"all-components-unknown={panel[f'{score}_components_observed'].eq(0).sum():,}", flush=True)
    return 0


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)


if __name__ == "__main__":
    raise SystemExit(main())

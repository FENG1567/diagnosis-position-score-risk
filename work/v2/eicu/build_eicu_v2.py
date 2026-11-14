#!/usr/bin/env python3
"""Build admission-level, first-ICU eICU score panels for Paper B."""
from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
WORK = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "v2" / "eicu"
EICU = Path(os.environ.get("EICU_ROOT", r"D:\数据库集合\eicu数据库"))
CHUNK = 500_000
WINDOW_END = 1440
VERSION = "eicu-paperb-v2.1"
SOURCES = {
    "patient": "https://eicu.mit.edu/eicutables/patient/",
    "diagnosis": "https://eicu.mit.edu/eicutables/diagnosis/",
    "admissionDx": "https://eicu.mit.edu/eicutables/admissiondx/",
    "apacheApsVar": "https://eicu.mit.edu/eicutables/apacheapsvar/",
    "vitalPeriodic": "https://eicu.mit.edu/eicutables/vitalperiodic/",
    "vitalAperiodic": "https://eicu.mit.edu/eicutables/vitalaperiodic/",
    "nurseCharting": "https://eicu.mit.edu/eicutables/nursecharting/",
    "lab": "https://eicu.mit.edu/eicutables/lab/",
}

# Narrow and broad membership flags are computed from tokenized ICD codes and
# diagnosis text. Each legacy flag preserves the original m56 code/text logic.
DEFS: dict[str, dict[str, Any]] = {
    "heart_failure": {
        "narrow_codes": ("428", "40201", "40211", "40291", "40401", "40403",
                         "40411", "40413", "40491", "40493", "I50", "I110", "I130", "I132"),
        "broad_extra_codes": ("402", "404", "I11", "I13"),
        "narrow_text": r"\bheart failure\b|\bcongestive heart failure\b",
        "broad_extra_text": r"\bcardiac failure\b",
        "legacy_codes": ("428", "402", "404", "I50", "I11", "I13"),
        "legacy_text": r"heart failure|congestive",
        "instrument": "qsofa",
        "main": "narrow",
    },
    "pneumonia": {
        "narrow_codes": ("480", "481", "482", "483", "484", "485", "486",
                         "J12", "J13", "J14", "J15", "J16", "J17", "J18"),
        "broad_extra_codes": ("507", "J69"),
        "narrow_text": r"\bpneumonia\b",
        "broad_extra_text": r"\baspiration pneumonitis\b",
        "legacy_codes": ("480", "481", "482", "483", "484", "485", "486", "507"),
        "legacy_text": r"pneumonia",
        "instrument": "curb65",
        "main": "broad",
    },
    "copd": {
        "narrow_codes": ("4912", "492", "496", "J44", "J43"),
        "broad_extra_codes": ("490", "491", "494", "J40", "J42", "J47"),
        "narrow_text": r"\bcopd\b|\bchronic obstructive pulmonary disease\b",
        "broad_extra_text": r"\bobstructive lung disease\b",
        "legacy_codes": ("490", "491", "492", "494", "496"),
        "legacy_text": r"copd|chronic obstructive",
        "instrument": "qsofa",
        "main": "narrow",
    },
    "sepsis": {
        "narrow_codes": ("038", "99591", "99592", "78552", "A40", "A41", "R652"),
        "broad_extra_codes": ("T802",),
        "narrow_text": r"sepsis|septic",
        "broad_extra_text": r"\bbacteremia\b|\bbacteraemia\b|\bsystemic infection\b",
        "legacy_codes": ("038", "9959", "78552"),
        "legacy_text": r"sepsis|septic",
        "instrument": "qsofa",
        "main": "narrow",
    },
    "pancreatitis": {
        "narrow_codes": ("5770", "K85"),
        "broad_extra_codes": (),
        "narrow_text": r"\bacute pancreatitis\b",
        "broad_extra_text": r"\bacute pancreatic inflammation\b",
        "legacy_codes": ("577",),
        "legacy_text": r"pancreatitis",
        "instrument": "bisap4",
        "main": "narrow",
    },
}
CODE_RE = re.compile(r"(?<![A-Z0-9])(?:[A-Z]\d{2,3}|\d{3,5})(?:\.[A-Z0-9]{1,4})?(?![A-Z0-9])", re.I)
NUMBER_RE = re.compile(r"^\s*[-+]?(?:\d+(?:\.\d*)?|\.\d+)\s*$")
PREFIXES = {
    disease: {
        key: tuple(re.sub(r"[^A-Z0-9]", "", value.upper()) for value in spec[source_key])
        for key, source_key in (
            ("narrow", "narrow_codes"),
            ("broad_extra", "broad_extra_codes"),
            ("legacy_v1", "legacy_codes"),
        )
    }
    for disease, spec in DEFS.items()
}
TEXT_PATTERNS = {
    disease: {
        "narrow": re.compile(spec["narrow_text"], re.I),
        "broad_extra": re.compile(spec["broad_extra_text"], re.I),
        "legacy_v1": re.compile(spec["legacy_text"], re.I),
    }
    for disease, spec in DEFS.items()
}


def log(message: str) -> None:
    print(message, flush=True)


def norm_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().lower()


def norm_code(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def parse_codes(value: Any) -> tuple[str, ...]:
    if value is None or pd.isna(value):
        return ()
    return tuple(norm_code(m.group(0)) for m in CODE_RE.finditer(str(value).upper()))


def has_prefix(codes: tuple[str, ...], prefixes: tuple[str, ...]) -> bool:
    if not prefixes:
        return False
    normalized = tuple(p if re.fullmatch(r"[A-Z0-9]+", p.upper()) else norm_code(p) for p in prefixes)
    return any(c.startswith(prefix) for c in codes for prefix in normalized)


def _has_cached_prefix(codes: tuple[str, ...], prefixes: tuple[str, ...]) -> bool:
    return any(code.startswith(prefix) for code in codes for prefix in prefixes)


def matches(codes: tuple[str, ...], text: str, disease: str) -> dict[str, bool]:
    narrow = _has_cached_prefix(codes, PREFIXES[disease]["narrow"]) or bool(TEXT_PATTERNS[disease]["narrow"].search(text))
    broad = narrow or _has_cached_prefix(codes, PREFIXES[disease]["broad_extra"]) or bool(
        TEXT_PATTERNS[disease]["broad_extra"].search(text)
    )
    legacy = _has_cached_prefix(codes, PREFIXES[disease]["legacy_v1"]) or bool(
        TEXT_PATTERNS[disease]["legacy_v1"].search(text)
    )
    return {"narrow": narrow, "broad": broad, "legacy_v1": legacy}


def as_float(value: Any) -> float:
    if value is None or pd.isna(value) or not NUMBER_RE.fullmatch(str(value).strip()):
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def parse_age(value: Any) -> tuple[float, int]:
    text = norm_text(value)
    if text.startswith(">") and "89" in text:
        return 90.0, 1
    v = as_float(text)
    if math.isfinite(v) and 18 <= v <= 110:
        return v, 0
    return math.nan, 0


def outcome(value: Any) -> float:
    text = norm_text(value)
    if re.search(r"\b(expired|dead|died)\b", text):
        return 1.0
    if text == "alive":
        return 0.0
    return math.nan


def select_first_stay(frame: pd.DataFrame) -> pd.DataFrame:
    """One index ICU stay per hospital admission, with deterministic chronology."""
    ordered = frame.sort_values(
        ["patienthealthsystemstayid", "unitvisitnumber",
         "elapsed_hospital_minutes_at_icu_admit", "patientunitstayid"],
        ascending=[True, True, True, True], na_position="last", kind="mergesort"
    )
    return ordered.groupby("patienthealthsystemstayid", sort=False).head(1).copy()


def hospital_time_offset(diagnosis_offset: Any, hospital_admit_offset: Any) -> float:
    """Translate unit-relative diagnosis offset to hospital-admission time."""
    d = as_float(diagnosis_offset)
    h = as_float(hospital_admit_offset)
    return d - h if math.isfinite(d) and math.isfinite(h) else math.nan


def position_group(member: Any, has_primary_full_course: Any) -> float:
    """Locked grp coding: 1=never primary, 0=primary at least once."""
    if member is None or pd.isna(member) or not bool(member):
        return math.nan
    if has_primary_full_course is None or pd.isna(has_primary_full_course):
        return math.nan
    return 0.0 if bool(has_primary_full_course) else 1.0


def collapse_parts(parts: list[pd.DataFrame], value: str, method: str) -> pd.Series:
    if not parts:
        return pd.Series(dtype=float, name=value)
    frame = pd.concat(parts)
    result = getattr(frame.groupby(level=0)[value], method)()
    result.name = value
    return result


def summarize_gcs_rows(g: pd.DataFrame, index_ids: set[int] | None = None) -> pd.DataFrame:
    """Use direct valid totals or complete components at the same timestamp."""
    if g.empty:
        idx = pd.Index(index_ids or [], name="patientunitstayid")
        return pd.DataFrame(index=idx, columns=["gcs_min", "gcs_valid_observation_count"])
    parts = g.loc[g.role.isin(["eye", "motor", "verbal"])].pivot_table(
        index=["patientunitstayid", "offset"], columns="role", values="value", aggfunc="min"
    )
    for col in ("eye", "motor", "verbal"):
        if col not in parts:
            parts[col] = np.nan
    complete = parts[["eye", "motor", "verbal"]].notna().all(axis=1)
    component_totals = parts.loc[complete, ["eye", "motor", "verbal"]].sum(axis=1).rename("gcs")
    component_totals = component_totals.reset_index()[["patientunitstayid", "gcs"]]
    direct = g.loc[g.role.eq("total"), ["patientunitstayid", "value"]].rename(columns={"value": "gcs"})
    values = pd.concat([component_totals, direct], ignore_index=True)
    out = values.groupby("patientunitstayid").gcs.agg(["min", "count"]).rename(
        columns={"min": "gcs_min", "count": "gcs_valid_observation_count"}
    )
    if index_ids is not None:
        out = out.reindex(pd.Index(index_ids, name="patientunitstayid"))
    return out


def read_index() -> tuple[pd.DataFrame, pd.DataFrame, dict[int, str]]:
    p = pd.read_csv(EICU / "patient.csv.gz", compression="gzip", usecols=[
        "patientunitstayid", "patienthealthsystemstayid", "uniquepid", "hospitalid",
        "unitvisitnumber", "hospitaladmitoffset", "unitdischargeoffset", "hospitaldischargeoffset",
        "hospitaldischargeyear", "hospitaldischargetime24", "age", "gender", "hospitaldischargestatus",
    ], dtype={"patienthealthsystemstayid": "string", "uniquepid": "string", "age": "string"})
    p["patientunitstayid"] = pd.to_numeric(p.patientunitstayid, errors="coerce")
    p["unitvisitnumber"] = pd.to_numeric(p.unitvisitnumber, errors="coerce")
    p["hospitaladmitoffset"] = pd.to_numeric(p.hospitaladmitoffset, errors="coerce")
    p["unitdischargeoffset"] = pd.to_numeric(p.unitdischargeoffset, errors="coerce")
    p["hospitaldischargeoffset"] = pd.to_numeric(p.hospitaldischargeoffset, errors="coerce")
    p["unitdischargeoffset"] = pd.to_numeric(p.unitdischargeoffset, errors="coerce")
    p["hospitaldischargeoffset"] = pd.to_numeric(p.hospitaldischargeoffset, errors="coerce")
    p["hospitalid"] = pd.to_numeric(p.hospitalid, errors="coerce").astype("Int64")
    p = p.dropna(subset=["patientunitstayid", "patienthealthsystemstayid"]).copy()
    p["patientunitstayid"] = p.patientunitstayid.astype("int64")
    p["patienthealthsystemstayid"] = p.patienthealthsystemstayid.astype("string").str.strip()
    p["elapsed_hospital_minutes_at_icu_admit"] = -p.hospitaladmitoffset
    index = select_first_stay(p)
    n = p.groupby("patienthealthsystemstayid").size().rename("n_icu_episodes")
    index = index.merge(n, on="patienthealthsystemstayid", validate="one_to_one")
    # Resolve hospital mortality only when all non-missing stay-level statuses agree.
    def resolve(s: pd.Series) -> float:
        vals = set(float(v) for v in s.dropna())
        return next(iter(vals)) if len(vals) == 1 else math.nan
    p["died_row"] = p.hospitaldischargestatus.map(outcome)
    status = p.groupby("patienthealthsystemstayid").died_row.agg(
        status_count="count", status_levels="nunique"
    )
    death = p.groupby("patienthealthsystemstayid").died_row.apply(resolve).rename("died")
    index = index.merge(death, on="patienthealthsystemstayid", validate="one_to_one")
    index = index.merge(status, on="patienthealthsystemstayid", validate="one_to_one")
    index["hospital_death_status_conflict"] = index.status_levels.gt(1)
    index["hospital_death_status_missing"] = index.status_count.eq(0)
    index["age"], index["age_topcoded_gt89"] = zip(*index.age.map(parse_age))
    end_candidates = pd.concat([
        index["unitdischargeoffset"].where(index["unitdischargeoffset"].ge(0)),
        index["hospitaldischargeoffset"].where(index["hospitaldischargeoffset"].ge(0)),
        pd.Series(WINDOW_END, index=index.index, dtype=float),
    ], axis=1)
    index["index_observation_window_end_min"] = end_candidates.min(axis=1).clip(upper=WINDOW_END)
    index["index_discharge_boundary_known"] = (
        index["unitdischargeoffset"].ge(0) | index["hospitaldischargeoffset"].ge(0)
    )
    index["sex"] = index.gender.map(lambda x: norm_text(x) if norm_text(x) in {"female", "male", "unknown", "other"} else None)
    index = index.rename(columns={
        "patienthealthsystemstayid": "admission_id",
        "patientunitstayid": "index_patientunitstayid",
        "uniquepid": "pid",
        "unitvisitnumber": "index_unitvisitnumber",
        "hospitaladmitoffset": "index_hospitaladmitoffset",
    }).reset_index(drop=True)
    index["admission_id"] = index.admission_id.astype("string")
    index["pid"] = index.pid.astype("string")
    stay_to_admission = p.set_index("patientunitstayid").patienthealthsystemstayid.to_dict()
    log(
        f"[index] unit_stays={p.patientunitstayid.nunique():,}; admissions={len(index):,}; "
        f"multi-ICU={int((index.n_icu_episodes>1).sum()):,}; "
        f"missing outcome={int(index.died.isna().sum()):,}; "
        f"conflicting status={int(index.hospital_death_status_conflict.sum()):,}; "
        f"missing unique pid={int(index.pid.isna().sum()):,}; missing hospitalid={int(index.hospitalid.isna().sum()):,}"
    )
    return index, p, stay_to_admission


def _match_frame(frame: pd.DataFrame, code: str, text: str) -> dict[str, pd.DataFrame]:
    code_series = frame[code].map(parse_codes)
    text_series = frame[text].fillna("").astype(str).str.lower()
    result: dict[str, pd.DataFrame] = {}
    for disease in DEFS:
        narrow_code = code_series.map(lambda codes: _has_cached_prefix(codes, PREFIXES[disease]["narrow"]))
        narrow_text = text_series.str.contains(TEXT_PATTERNS[disease]["narrow"], na=False)
        extra_code = code_series.map(lambda codes: _has_cached_prefix(codes, PREFIXES[disease]["broad_extra"]))
        extra_text = text_series.str.contains(TEXT_PATTERNS[disease]["broad_extra"], na=False)
        legacy_code = code_series.map(lambda codes: _has_cached_prefix(codes, PREFIXES[disease]["legacy_v1"]))
        legacy_text = text_series.str.contains(TEXT_PATTERNS[disease]["legacy_v1"], na=False)
        narrow = narrow_code | narrow_text
        result[disease] = pd.DataFrame({
            "narrow": narrow,
            "broad": narrow | extra_code | extra_text,
            "legacy_v1": legacy_code | legacy_text,
        }, index=frame.index).astype(bool)
        if code == "icd9code":
            current = result[disease]
            log(
                f"[diagnosis-match:{disease}] rows={len(frame):,}; "
                f"narrow={int(current.narrow.sum()):,}; broad={int(current.broad.sum()):,}; "
                f"legacy-v1={int(current.legacy_v1.sum()):,}"
            )
    return result


def diagnosis_summary(index: pd.DataFrame, patient: pd.DataFrame, stay_map: dict[int, str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    log("[diagnosis] reading diagnosis.csv.gz and admissionDx.csv.gz")
    read_started = time.monotonic()
    dx = pd.read_csv(EICU / "diagnosis.csv.gz", compression="gzip", usecols=[
        "patientunitstayid", "icd9code", "diagnosisstring", "diagnosispriority", "diagnosisoffset",
    ], dtype={"icd9code": "string", "diagnosisstring": "string", "diagnosispriority": "string"})
    dx["patientunitstayid"] = pd.to_numeric(dx.patientunitstayid, errors="coerce")
    dx["diagnosisoffset"] = pd.to_numeric(dx.diagnosisoffset, errors="coerce")
    dx = dx.dropna(subset=["patientunitstayid"]).copy()
    dx["patientunitstayid"] = dx.patientunitstayid.astype("int64")
    dx["admission_id"] = dx.patientunitstayid.map(stay_map)
    dx = dx.dropna(subset=["admission_id"]).copy()
    dx["admission_id"] = dx.admission_id.astype("string")
    log(f"[diagnosis] linked rows={len(dx):,}; read/link elapsed={time.monotonic()-read_started:.1f}s")
    dx["is_primary"] = dx.diagnosispriority.fillna("").str.strip().str.casefold().eq("primary")
    index_by_adm = index.set_index("admission_id").index_patientunitstayid.to_dict()
    dx["is_index_unit"] = dx.admission_id.map(index_by_adm).eq(dx.patientunitstayid)
    dx["hospital_admit_offset"] = dx.patientunitstayid.map(
        patient.set_index("patientunitstayid").hospitaladmitoffset
    )
    dx["hospital_dx_offset"] = dx.diagnosisoffset - dx.hospital_admit_offset
    index_origin = index.set_index("admission_id").index_hospitaladmitoffset
    dx["index_relative_offset"] = dx.hospital_dx_offset + dx.admission_id.map(index_origin)
    dx["by_index_24h"] = dx.index_relative_offset.ge(0) & dx.index_relative_offset.le(WINDOW_END)
    out = index[["admission_id"]].copy().set_index("admission_id")
    summary: dict[str, Any] = {
        "diagnosis_rows_linked": int(len(dx)),
        "diagnosis_rows_primary": int(dx.is_primary.sum()),
        "diagnosis_rows_by_index_icu_24h": int(dx.by_index_24h.sum()),
    }
    flags = _match_frame(dx.assign(_text=dx.diagnosisstring.fillna("")), "icd9code", "_text")
    for disease, flag in flags.items():
        for definition in ("narrow", "broad", "legacy_v1"):
            hit = flag[definition]
            if disease != "pancreatitis" and definition == "legacy_v1":
                pass
            d = dx.loc[hit, ["admission_id", "patientunitstayid", "is_primary", "is_index_unit", "by_index_24h"]].copy()
            prefix = f"{disease}_{definition}"
            if d.empty:
                for suffix in ("member", "primary_all_icu", "primary_firstunit", "by24_classifiable",
                               "primary_by24", "firstunit_by24_classifiable", "primary_firstunit_by24"):
                    out[f"{prefix}_{suffix}"] = False if suffix.endswith("classifiable") or suffix == "member" else np.nan
                continue
            d["primary_in_index"] = d.is_primary & d.is_index_unit
            d["primary_by24"] = d.is_primary & d.by_index_24h
            d["firstunit_by24"] = d.is_index_unit & d.by_index_24h
            d["primary_firstunit_by24"] = d.is_primary & d.is_index_unit & d.by_index_24h
            grouped = d.groupby("admission_id").agg(
                member=("is_primary", "size"),
                primary_all=("is_primary", "max"),
                firstunit_class=("is_index_unit", "max"),
                primary_firstunit=("primary_in_index", "max"),
                by24_class=("by_index_24h", "max"),
                primary_by24=("primary_by24", "max"),
                firstunit_by24_class=("firstunit_by24", "max"),
                primary_firstunit_by24=("primary_firstunit_by24", "max"),
            )
            grouped["primary_firstunit"] = grouped.primary_firstunit.where(grouped.firstunit_class)
            grouped["primary_by24"] = grouped.primary_by24.where(grouped.by24_class)
            grouped["primary_firstunit_by24"] = grouped.primary_firstunit_by24.where(grouped.firstunit_by24_class)
            grouped = grouped.reindex(out.index)
            out[f"{prefix}_member"] = grouped.member.notna()
            out[f"{prefix}_primary_all_icu"] = grouped.primary_all
            out[f"{prefix}_firstunit_classifiable"] = grouped.firstunit_class.fillna(False)
            out[f"{prefix}_primary_firstunit"] = grouped.primary_firstunit
            out[f"{prefix}_by24_classifiable"] = grouped.by24_class.fillna(False)
            out[f"{prefix}_primary_by24"] = grouped.primary_by24
            out[f"{prefix}_firstunit_by24_classifiable"] = grouped.firstunit_by24_class.fillna(False)
            out[f"{prefix}_primary_firstunit_by24"] = grouped.primary_firstunit_by24
            summary[f"{prefix}_n"] = int(out[f"{prefix}_member"].sum())
            summary[f"{prefix}_by24_classifiable_n"] = int(out[f"{prefix}_by24_classifiable"].sum())

    adm = pd.read_csv(EICU / "admissionDx.csv.gz", compression="gzip", usecols=[
        "patientunitstayid", "admitdxpath", "admitdxname", "admitdxtext",
    ], dtype="string")
    adm["patientunitstayid"] = pd.to_numeric(adm.patientunitstayid, errors="coerce")
    adm = adm.dropna(subset=["patientunitstayid"]).copy()
    adm["patientunitstayid"] = adm.patientunitstayid.astype("int64")
    idx_ids = set(index.index_patientunitstayid.astype("int64"))
    adm = adm.loc[adm.patientunitstayid.isin(idx_ids)].copy()
    adm["admission_id"] = adm.patientunitstayid.map(stay_map)
    adm["admit_text"] = (
        adm.admitdxpath.fillna("") + " | " + adm.admitdxname.fillna("") + " | " + adm.admitdxtext.fillna("")
    )
    adm_flags = _match_frame(adm.assign(_blank=""), "_blank", "admit_text")
    out["index_icu_admissiondx_present"] = adm.groupby("admission_id").size().reindex(out.index).notna()
    for disease, flag in adm_flags.items():
        for definition in ("narrow", "broad"):
            adm[f"{disease}_admissiondx_{definition}"] = flag[definition]
            out[f"{disease}_admissiondx_match_{definition}"] = adm.groupby("admission_id")[
                f"{disease}_admissiondx_{definition}"
            ].max().reindex(out.index)
    result = out.reset_index()
    log(
        f"[diagnosis] linked rows={len(dx):,}; within index-ICU hours 0-24={int(dx.by_index_24h.sum()):,}; "
        f"index ICU admissionDx present={int(result.index_icu_admissiondx_present.fillna(False).sum()):,}"
    )
    return result, summary


def _extrema_parts(
    frame: pd.DataFrame, value: str, method: str, parts: list[pd.DataFrame], output_name: str | None = None
) -> None:
    vals = pd.to_numeric(frame[value], errors="coerce")
    valid = vals.notna()
    if not valid.any():
        return
    out_name = output_name or value
    temp = pd.DataFrame({
        "patientunitstayid": frame.loc[valid, "patientunitstayid"].astype("int64"),
        out_name: vals.loc[valid],
    })
    parts.append(getattr(temp.groupby("patientunitstayid")[out_name], method)().to_frame())


def _combine_parts(parts: list[pd.DataFrame], value: str) -> pd.Series:
    if not parts:
        return pd.Series(dtype=float, name=value)
    all_parts = pd.concat(parts)
    result = getattr(all_parts.groupby(level=0)[value], "max" if value.endswith("_max") else "min")()
    result.name = value
    return result


def _window_filter(frame: pd.DataFrame, id_col: str, offset_col: str, window_end: dict[int, float]) -> pd.DataFrame:
    frame[offset_col] = pd.to_numeric(frame[offset_col], errors="coerce")
    ends = frame[id_col].map(window_end).fillna(WINDOW_END)
    return frame.loc[frame[offset_col].ge(0) & frame[offset_col].le(ends)]


def extract_vitals(index: pd.DataFrame, index_ids: set[int]) -> tuple[pd.DataFrame, dict[str, Any]]:
    end_by_id = dict(zip(index.index_patientunitstayid.astype(int), index.index_observation_window_end_min))
    all_ids = pd.Index(index_ids, name="patientunitstayid")
    meta: dict[str, Any] = {}
    result = pd.DataFrame(index=all_ids)
    # Periodic: 5-minute monitor medians for respiratory rate, temperature,
    # heart rate and invasive systemic pressures.
    path = EICU / "vitalPeriodic.csv.gz"
    cols = ["patientunitstayid", "observationoffset", "respiration", "temperature", "heartrate",
            "systemicsystolic", "systemicdiastolic"]
    parts: dict[str, list[pd.DataFrame]] = {x: [] for x in (
        "rr_max", "temperature_min", "temperature_max", "heartrate_max",
        "arterial_sbp_min", "arterial_dbp_min",
    )}
    nread = ntarget = nwindow = 0
    t0 = time.monotonic()
    for i, c in enumerate(pd.read_csv(path, compression="gzip", usecols=cols, chunksize=CHUNK), 1):
        nread += len(c)
        ids = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = c.loc[ids.isin(index_ids)].copy()
        if c.empty:
            continue
        ntarget += len(c)
        c["patientunitstayid"] = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = _window_filter(c, "patientunitstayid", "observationoffset", end_by_id)
        nwindow += len(c)
        for col in cols[2:]:
            c[col] = pd.to_numeric(c[col], errors="coerce")
        bounds = {
            "respiration": (1, 100), "temperature": (25, 45), "heartrate": (1, 300),
            "systemicsystolic": (20, 300), "systemicdiastolic": (10, 200),
        }
        for col, (lo, hi) in bounds.items():
            c.loc[~c[col].between(lo, hi), col] = np.nan
        for col, val, method in (
            ("respiration", "rr_max", "max"),
            ("temperature", "temperature_min", "min"),
            ("temperature", "temperature_max", "max"),
            ("heartrate", "heartrate_max", "max"),
            ("systemicsystolic", "arterial_sbp_min", "min"),
            ("systemicdiastolic", "arterial_dbp_min", "min"),
        ):
            _extrema_parts(c, col, method, parts[val], val)
        if i % 10 == 0:
            log(f"[scan:vitalPeriodic] chunks={i:,}; rows={nread:,}; index rows={ntarget:,}; elapsed={time.monotonic()-t0:.1f}s")
    for value, pp in parts.items():
        if pp:
            result[value] = collapse_parts(pp, value, "max" if value.endswith("_max") else "min").reindex(all_ids)
    meta["vitalPeriodic"] = {
        "raw_rows": nread, "index_stay_rows": ntarget, "within_valid_window_rows": nwindow,
        "elapsed_seconds": round(time.monotonic() - t0, 2),
    }
    log(f"[scan:vitalPeriodic] done rows={nread:,}; index={ntarget:,}; in-window={nwindow:,}; {meta['vitalPeriodic']['elapsed_seconds']:.1f}s")

    # Aperiodic non-invasive BP is irregularly captured and is the primary
    # pressure source for qSOFA and CURB-65. Arterial pressures stay separate.
    path = EICU / "vitalAperiodic.csv.gz"
    cols = ["patientunitstayid", "observationoffset", "noninvasivesystolic", "noninvasivediastolic"]
    parts = {"sbp_min": [], "dbp_min": []}
    nread = ntarget = nwindow = 0
    t0 = time.monotonic()
    for i, c in enumerate(pd.read_csv(path, compression="gzip", usecols=cols, chunksize=CHUNK), 1):
        nread += len(c)
        ids = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = c.loc[ids.isin(index_ids)].copy()
        if c.empty:
            continue
        ntarget += len(c)
        c["patientunitstayid"] = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = _window_filter(c, "patientunitstayid", "observationoffset", end_by_id)
        nwindow += len(c)
        for col in ("noninvasivesystolic", "noninvasivediastolic"):
            c[col] = pd.to_numeric(c[col], errors="coerce")
        c.loc[~c.noninvasivesystolic.between(20, 300), "noninvasivesystolic"] = np.nan
        c.loc[~c.noninvasivediastolic.between(10, 200), "noninvasivediastolic"] = np.nan
        _extrema_parts(c.rename(columns={"noninvasivesystolic": "sbp_min"}), "sbp_min", "min", parts["sbp_min"])
        _extrema_parts(c.rename(columns={"noninvasivediastolic": "dbp_min"}), "dbp_min", "min", parts["dbp_min"])
        if i % 10 == 0:
            log(f"[scan:vitalAperiodic] chunks={i:,}; rows={nread:,}; index rows={ntarget:,}; elapsed={time.monotonic()-t0:.1f}s")
    for value, pp in parts.items():
        if pp:
            result[value] = collapse_parts(pp, value, "min").reindex(all_ids)
    meta["vitalAperiodic"] = {
        "raw_rows": nread, "index_stay_rows": ntarget, "within_valid_window_rows": nwindow,
        "elapsed_seconds": round(time.monotonic() - t0, 2),
    }
    log(f"[scan:vitalAperiodic] done rows={nread:,}; index={ntarget:,}; in-window={nwindow:,}; {meta['vitalAperiodic']['elapsed_seconds']:.1f}s")
    return result, meta


def _unit(value: Any) -> str:
    s = norm_text(value).replace(" ", "").replace("μ", "u").replace("µ", "u")
    return s.replace("deciliter", "dl").replace("millimole", "mmol").replace("milligram", "mg").replace("liter", "l").replace("litre", "l")


def convert_urea(value: float, analyte: str, unit: Any) -> tuple[float, float]:
    """Convert to BUN mg/dL and urea mmol/L; unknown units stay missing."""
    if not math.isfinite(value):
        return math.nan, math.nan
    u = _unit(unit)
    if u in {"mg/dl", "mg%"}:
        if analyte == "bun":
            return value, value / 2.8
        if analyte == "urea":
            mmol = value / 6.006
            return mmol * 2.8, mmol
    if u in {"mmol/l", "mmoll"}:
        return value * 2.8, value
    return math.nan, math.nan


def extract_labs(index: pd.DataFrame, index_ids: set[int]) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = EICU / "lab.csv.gz"
    cols = ["patientunitstayid", "labresultoffset", "labname", "labresult",
            "labmeasurenamesystem", "labmeasurenameinterface"]
    end_by_id = dict(zip(index.index_patientunitstayid.astype(int), index.index_observation_window_end_min))
    bun_parts: list[pd.DataFrame] = []
    urea_parts: list[pd.DataFrame] = []
    wbc_min_parts: list[pd.DataFrame] = []
    wbc_max_parts: list[pd.DataFrame] = []
    analytes: Counter[str] = Counter()
    units: Counter[str] = Counter()
    nread = ntarget = nwindow = nurea = nconverted = 0
    t0 = time.monotonic()
    for i, c in enumerate(pd.read_csv(path, compression="gzip", usecols=cols, chunksize=CHUNK), 1):
        nread += len(c)
        ids = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = c.loc[ids.isin(index_ids)].copy()
        if c.empty:
            continue
        ntarget += len(c)
        c["patientunitstayid"] = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = _window_filter(c, "patientunitstayid", "labresultoffset", end_by_id)
        nwindow += len(c)
        names = c.labname.fillna("").astype(str).str.lower()
        c["analyte"] = np.where(names.str.contains(r"\b(bun|blood urea nitrogen|urea nitrogen)\b", regex=True), "bun",
                                 np.where(names.str.contains(r"\burea\b", regex=True), "urea",
                                 np.where(names.str.contains(r"\bwbc\b|\bwhite blood cell", regex=True), "wbc",
                                 np.where(names.str.contains(r"\bbands?\b", regex=True), "bands",
                                 np.where(names.str.contains(r"\b(paco2|pa co2|pco2)\b", regex=True), "paco2", "")))))
        selected = c.loc[c.analyte.ne("")].copy()
        if selected.empty:
            continue
        for name, group in selected.groupby("labname"):
            analytes[str(name)[:100]] += len(group)
        system = selected.labmeasurenamesystem.fillna("").astype(str)
        interface = selected.labmeasurenameinterface.fillna("").astype(str)
        selected["unit"] = system.where(system.str.strip().ne(""), interface)
        for u in selected.unit:
            units[str(u)[:80]] += 1
        values = pd.to_numeric(selected.labresult, errors="coerce")
        selected["lab_value"] = values
        bun_mask = selected.analyte.isin(["bun", "urea"])
        if bun_mask.any():
            converted = [
                convert_urea(v, a, u)
                for v, a, u in zip(selected.loc[bun_mask, "lab_value"], selected.loc[bun_mask, "analyte"], selected.loc[bun_mask, "unit"])
            ]
            use = selected.loc[bun_mask, ["patientunitstayid"]].copy()
            use["bun_mgdl"] = [z[0] for z in converted]
            use["urea_mmol_l"] = [z[1] for z in converted]
            nurea += len(use)
            nconverted += int(use[["bun_mgdl", "urea_mmol_l"]].notna().all(axis=1).sum())
            use.loc[~use.bun_mgdl.between(0.5, 300), "bun_mgdl"] = np.nan
            use.loc[~use.urea_mmol_l.between(0.1, 110), "urea_mmol_l"] = np.nan
            _extrema_parts(use, "bun_mgdl", "max", bun_parts, "bun_mgdl_max")
            _extrema_parts(use, "urea_mmol_l", "max", urea_parts, "urea_mmol_l_max")

        # Secondary SIRS support. Units are validated explicitly; no numeric
        # magnitude guessing is used.
        wbc = selected.loc[selected.analyte.eq("wbc"), ["patientunitstayid", "lab_value", "unit"]].copy()
        if len(wbc):
            vals = []
            for v, u in zip(wbc.lab_value, wbc.unit):
                unit = _unit(u)
                if unit in {"10^9/l", "10e9/l", "x10^9/l", "10^3/ul", "10^3/u l", "k/ul", "k/u l", "thousand/ul"}:
                    vals.append(v)
                elif unit in {"cells/ul", "cells/mm3", "cell/ul", "cell/mm3"}:
                    vals.append(v / 1000 if math.isfinite(v) else math.nan)
                else:
                    vals.append(math.nan)
            wbc["wbc_k_ul"] = vals
            wbc.loc[~wbc.wbc_k_ul.between(0.1, 500), "wbc_k_ul"] = np.nan
            _extrema_parts(wbc, "wbc_k_ul", "min", wbc_min_parts, "wbc_k_ul_min")
            _extrema_parts(wbc, "wbc_k_ul", "max", wbc_max_parts, "wbc_k_ul_max")
        if i % 10 == 0:
            log(f"[scan:lab] chunks={i:,}; rows={nread:,}; index={ntarget:,}; in-window={nwindow:,}; elapsed={time.monotonic()-t0:.1f}s")
    ids = pd.Index(index_ids, name="patientunitstayid")
    out = pd.DataFrame(index=ids)
    for name, parts, method in (
        ("bun_mgdl_max", bun_parts, "max"),
        ("urea_mmol_l_max", urea_parts, "max"),
        ("wbc_k_ul_min", wbc_min_parts, "min"),
        ("wbc_k_ul_max", wbc_max_parts, "max"),
    ):
        if parts:
            out[name] = collapse_parts(parts, name, method).reindex(ids)
    for name in ("bun_mgdl_max", "urea_mmol_l_max", "wbc_k_ul_min", "wbc_k_ul_max"):
        if name not in out:
            out[name] = np.nan
    meta = {
        "raw_rows": nread, "index_stay_rows": ntarget, "within_valid_window_rows": nwindow,
        "urea_candidate_rows": nurea, "urea_unit_convertible_rows": nconverted,
        "lab_names_top40": dict(analytes.most_common(40)), "units_top40": dict(units.most_common(40)),
        "elapsed_seconds": round(time.monotonic()-t0, 2),
    }
    log(f"[scan:lab] done rows={nread:,}; index={ntarget:,}; in-window={nwindow:,}; urea={nurea:,}; convertible={nconverted:,}; {meta['elapsed_seconds']:.1f}s")
    return out, meta


def gcs_role(label: Any, value_name: Any) -> str | None:
    label_n = re.sub(r"[^a-z0-9]", "", norm_text(label))
    name_n = re.sub(r"[^a-z0-9]", "", norm_text(value_name))
    text = label_n + name_n
    if "gcs" in text or "glasgow" in text:
        if any(x in text for x in ("eye", "eyes")):
            return "eye"
        if "motor" in text:
            return "motor"
        if "verbal" in text:
            return "verbal"
        if "total" in text or "score" in text or text.endswith("gcs"):
            return "total"
    return None


def gcs_value(value: Any, role: str) -> float:
    v = as_float(value)
    lo, hi = {"eye": (1, 4), "motor": (1, 6), "verbal": (1, 5), "total": (3, 15)}[role]
    if math.isfinite(v) and v.is_integer() and lo <= v <= hi:
        return v
    text = norm_text(value)
    maps = {
        "eye": {"no response": 1, "to pain": 2, "to speech": 3, "spontaneous": 4},
        "motor": {"no response": 1, "extension": 2, "abnormal extension": 2, "flexion": 3,
                  "abnormal flexion": 3, "withdrawal": 4, "localizes": 5, "obeys commands": 6},
        "verbal": {"no response": 1, "incomprehensible": 2, "inappropriate": 3, "confused": 4, "oriented": 5},
        "total": {},
    }
    return float(maps[role].get(text, math.nan))


def confusion_value(value: Any) -> float:
    text = norm_text(value)
    if re.search(r"\b(not confused|no confusion|oriented|alert and oriented|a&o)\b", text):
        return 0.0
    if re.search(r"\b(confused|confusion|disoriented|disorientation)\b", text):
        return 1.0
    return math.nan


def extract_nurse(index: pd.DataFrame, index_ids: set[int]) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = EICU / "nurseCharting.csv.gz"
    cols = ["patientunitstayid", "nursingchartoffset", "nursingchartcelltypevallabel",
            "nursingchartcelltypevalname", "nursingchartvalue"]
    end_by_id = dict(zip(index.index_patientunitstayid.astype(int), index.index_observation_window_end_min))
    gcs_rows: list[pd.DataFrame] = []
    confusion_parts: list[pd.DataFrame] = []
    label_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    value_class_counts: Counter[str] = Counter()
    nread = ntarget = nwindow = nmental = 0
    t0 = time.monotonic()
    for i, c in enumerate(pd.read_csv(path, compression="gzip", usecols=cols, chunksize=CHUNK), 1):
        nread += len(c)
        ids = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = c.loc[ids.isin(index_ids)].copy()
        if c.empty:
            continue
        ntarget += len(c)
        c["patientunitstayid"] = pd.to_numeric(c.patientunitstayid, errors="coerce")
        c = _window_filter(c, "patientunitstayid", "nursingchartoffset", end_by_id)
        nwindow += len(c)
        labels = c.nursingchartcelltypevallabel.fillna("").astype(str)
        names = c.nursingchartcelltypevalname.fillna("").astype(str)
        combined = labels + " " + names
        mask = combined.str.contains(r"glasgow|gcs|confus|orientation|oriented|mental status", case=False, regex=True)
        sub = c.loc[mask].copy()
        if sub.empty:
            continue
        nmental += len(sub)
        sub["_role"] = [
            gcs_role(l, n) for l, n in zip(sub.nursingchartcelltypevallabel, sub.nursingchartcelltypevalname)
        ]
        for l, n, role in zip(sub.nursingchartcelltypevallabel, sub.nursingchartcelltypevalname, sub._role):
            label_counts[(str(l)[:80] + " | " + str(n)[:80])] += 1
            role_counts[role or "mental_status"] += 1
        sub["_gcs"] = [
            gcs_value(v, role) if role else math.nan for v, role in zip(sub.nursingchartvalue, sub._role)
        ]
        g = sub.loc[sub._role.notna() & sub._gcs.notna(), [
            "patientunitstayid", "nursingchartoffset", "_role", "_gcs"
        ]].rename(columns={"nursingchartoffset": "offset", "_role": "role", "_gcs": "value"})
        if len(g):
            gcs_rows.append(g)
        mental_mask = combined.loc[sub.index].str.contains(
            r"confus|orientation|oriented|mental status", case=False, regex=True
        )
        if mental_mask.any():
            mental = sub.loc[mental_mask, ["patientunitstayid", "nursingchartvalue"]].copy()
            mental["confusion"] = mental.nursingchartvalue.map(confusion_value)
            for raw in mental.nursingchartvalue.fillna("").astype(str):
                z = norm_text(raw)
                if not z:
                    value_class_counts["empty"] += 1
                elif confusion_value(raw) == 1:
                    value_class_counts["explicit_confused"] += 1
                elif confusion_value(raw) == 0:
                    value_class_counts["explicit_oriented"] += 1
                else:
                    value_class_counts["other_uninterpreted"] += 1
            mental = mental.loc[mental.confusion.notna()]
            if len(mental):
                confusion_parts.append(mental.groupby("patientunitstayid").confusion.max().to_frame())
        if i % 10 == 0:
            log(f"[scan:nurseCharting] chunks={i:,}; rows={nread:,}; index={ntarget:,}; in-window={nwindow:,}; mental/GCS rows={nmental:,}; elapsed={time.monotonic()-t0:.1f}s")
    all_ids = pd.Index(index_ids, name="patientunitstayid")
    g = pd.concat(gcs_rows, ignore_index=True) if gcs_rows else pd.DataFrame(
        columns=["patientunitstayid", "offset", "role", "value"]
    )
    out = summarize_gcs_rows(g, index_ids)
    if confusion_parts:
        confusion = pd.concat(confusion_parts).groupby(level=0).confusion.max().rename("confusion_chart_sensitivity")
        out = out.join(confusion, how="left")
    else:
        out["confusion_chart_sensitivity"] = np.nan
    meta = {
        "raw_rows": nread, "index_stay_rows": ntarget, "within_valid_window_rows": nwindow,
        "candidate_mental_gcs_rows": nmental, "gcs_role_counts": dict(role_counts),
        "relevant_label_name_counts_top40": dict(label_counts.most_common(40)),
        "explicit_confusion_value_categories": dict(value_class_counts),
        "index_stays_with_valid_gcs": int(out.gcs_min.notna().sum()),
        "index_stays_with_confusion_sensitivity": int(out.confusion_chart_sensitivity.notna().sum()),
        "elapsed_seconds": round(time.monotonic()-t0, 2),
    }
    log(f"[scan:nurseCharting] done rows={nread:,}; index={ntarget:,}; in-window={nwindow:,}; GCS-stays={meta['index_stays_with_valid_gcs']:,}; {meta['elapsed_seconds']:.1f}s")
    return out, meta


def point(value: Any, predicate) -> float:
    if value is None or pd.isna(value):
        return math.nan
    try:
        return float(bool(predicate(float(value))))
    except (TypeError, ValueError):
        return math.nan


def any_abnormal(*values: Any) -> float:
    if any(pd.notna(v) and float(v) == 1 for v in values):
        return 1.0
    if all(pd.notna(v) for v in values):
        return 0.0
    return math.nan


def score(points: pd.DataFrame, name: str, maximum: int) -> pd.DataFrame:
    p = points.apply(pd.to_numeric, errors="coerce")
    miss = p.isna().sum(axis=1)
    lower = p.fillna(0).sum(axis=1)
    upper = (lower + miss).clip(upper=maximum)
    out = pd.DataFrame(index=p.index)
    out[f"{name}_complete"] = miss.eq(0)
    out[f"{name}_score"] = lower.where(miss.eq(0), np.nan)
    out[f"{name}_lower"] = lower
    out[f"{name}_upper"] = upper
    out[f"{name}_n_components_observed"] = p.notna().sum(axis=1).astype("int8")
    return out


def make_scores(index: pd.DataFrame, measurements: pd.DataFrame) -> pd.DataFrame:
    m = index.set_index("index_patientunitstayid").join(measurements, how="left")
    # Primary qSOFA GCS threshold is <=13 per the original Seymour operationalisation.
    m["qsofa_rr_point"] = m.rr_max.map(lambda x: point(x, lambda v: v >= 22))
    m["qsofa_sbp_point"] = m.sbp_min.map(lambda x: point(x, lambda v: v <= 100))
    m["qsofa_gcs13_point"] = m.gcs_min.map(lambda x: point(x, lambda v: v <= 13))
    m["qsofa_gcs15_point"] = m.gcs_min.map(lambda x: point(x, lambda v: v < 15))
    q13 = score(m[["qsofa_rr_point", "qsofa_sbp_point", "qsofa_gcs13_point"]], "qsofa_gcs13", 3)
    q15 = score(m[["qsofa_rr_point", "qsofa_sbp_point", "qsofa_gcs15_point"]], "qsofa_gcs15", 3)
    m = m.join(q13).join(q15)
    m["qsofa_score"] = m.qsofa_gcs13_score
    m["qsofa_lower"] = m.qsofa_gcs13_lower
    m["qsofa_upper"] = m.qsofa_gcs13_upper
    m["qsofa_complete"] = m.qsofa_gcs13_complete
    m["qsofa"] = m.qsofa_gcs13_score
    m["qsofa_gcs15"] = m.qsofa_gcs15_score

    m["curb65_confusion_proxy_point"] = m.gcs_min.map(lambda x: point(x, lambda v: v < 15))
    m["curb65_confusion_chart_sensitivity_point"] = m.confusion_chart_sensitivity
    m["curb65_urea_point"] = m.urea_mmol_l_max.map(lambda x: point(x, lambda v: v > 7))
    m["curb65_rr_point"] = m.rr_max.map(lambda x: point(x, lambda v: v >= 30))
    low_sbp = m.sbp_min.map(lambda x: point(x, lambda v: v < 90))
    low_dbp = m.dbp_min.map(lambda x: point(x, lambda v: v <= 60))
    m["curb65_bp_point"] = [any_abnormal(a, b) for a, b in zip(low_sbp, low_dbp)]
    m["curb65_age_point"] = m.age.map(lambda x: point(x, lambda v: v >= 65))
    curb_cols = ["curb65_confusion_proxy_point", "curb65_urea_point", "curb65_rr_point",
                 "curb65_bp_point", "curb65_age_point"]
    m = m.join(score(m[curb_cols], "curb65", 5))
    m["curb65_score_gcs_proxy"] = m.curb65_score
    m["curb65_lower_gcs_proxy"] = m.curb65_lower
    m["curb65_upper_gcs_proxy"] = m.curb65_upper
    m["curb65_complete_gcs_proxy"] = m.curb65_complete
    m["curb65"] = m.curb65_score
    curb_direct = m[curb_cols].drop(columns="curb65_confusion_proxy_point").copy()
    curb_direct["confusion_direct"] = m.curb65_confusion_chart_sensitivity_point
    m = m.join(score(curb_direct, "curb65_direct_confusion", 5))

    temp_point = [
        1.0 if (pd.notna(lo) and lo < 36) or (pd.notna(hi) and hi > 38)
        else (0.0 if pd.notna(lo) and pd.notna(hi) else np.nan)
        for lo, hi in zip(m.temperature_min, m.temperature_max)
    ]
    m["sirs_temperature_point"] = temp_point
    m["sirs_heartrate_point"] = m.heartrate_max.map(lambda x: point(x, lambda v: v > 90))
    m["sirs_rr_point"] = m.rr_max.map(lambda x: point(x, lambda v: v > 20))
    m["sirs_wbc_point"] = [
        1.0 if (pd.notna(lo) and lo < 4) or (pd.notna(hi) and hi > 12)
        else (0.0 if pd.notna(lo) and pd.notna(hi) else np.nan)
        for lo, hi in zip(m.wbc_k_ul_min, m.wbc_k_ul_max)
    ]
    sirs_cols = ["sirs_temperature_point", "sirs_heartrate_point", "sirs_rr_point", "sirs_wbc_point"]
    m = m.join(score(m[sirs_cols], "sirs_operationalized", 4))
    m["sirs_ge2_point"] = np.where(
        m.sirs_operationalized_lower >= 2, 1.0,
        np.where(m.sirs_operationalized_upper < 2, 0.0, np.nan),
    )
    m["bisap_bun_point"] = m.bun_mgdl_max.map(lambda x: point(x, lambda v: v > 25))
    m["bisap_gcs_point"] = m.gcs_min.map(lambda x: point(x, lambda v: v < 15))
    m["bisap_sirs_operationalized_point"] = m.sirs_ge2_point
    m["bisap_age_point"] = m.age.map(lambda x: point(x, lambda v: v > 60))
    m = m.join(score(m[["bisap_bun_point", "bisap_gcs_point", "bisap_sirs_operationalized_point", "bisap_age_point"]], "bisap4", 4))
    m["bisap4"] = m.bisap4_score
    return m.reset_index()


def panels(index: pd.DataFrame, dx: pd.DataFrame, scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    wide = scored.merge(dx, on="admission_id", how="left", validate="one_to_one")
    for col in wide.columns:
        if col.endswith("_member"):
            wide[col] = wide[col].fillna(False).astype("int8")
    long_parts = []
    for disease, spec in DEFS.items():
        narrow_col = f"{disease}_narrow_member"
        broad_col = f"{disease}_broad_member"
        legacy_col = f"{disease}_legacy_v1_member"
        main_definition = spec["main"]
        main_col = f"{disease}_{main_definition}_member"
        # Retain every phenotype member for downstream sensitivity analyses.
        # The locked primary group below is still assigned only to main members.
        keep = wide[narrow_col].eq(1) | wide[broad_col].eq(1) | wide[legacy_col].eq(1)
        item = wide.loc[keep].copy()
        if item.empty:
            continue
        item["disease_key"] = disease
        item["disease"] = {
            "heart_failure": "heart failure",
            "copd": "COPD",
            "pancreatitis": "acute pancreatitis",
        }.get(disease, disease)
        item["instrument"] = spec["instrument"]
        item["main_code_list"] = main_definition
        item["cohort_main"] = item[main_col].astype("int8")
        item["cohort_narrow"] = item[narrow_col].astype("int8")
        item["cohort_broad"] = item[broad_col].astype("int8")
        item["cohort_legacy_v1_sensitivity"] = item[legacy_col].astype("int8")
        p = f"{disease}_{main_definition}"
        item["diagnosis_fullcourse_classifiable"] = item[main_col].eq(1)
        item["diagnosis_fullcourse_has_primary"] = item[f"{p}_primary_all_icu"]
        item["diagnosis_by24h_classifiable"] = item[f"{p}_by24_classifiable"].astype("boolean")
        item["diagnosis_by24h_has_primary"] = item[f"{p}_primary_by24"]
        item["diagnosis_first_unit_classifiable"] = item[f"{p}_firstunit_by24_classifiable"].astype("boolean")
        item["diagnosis_first_unit_has_primary"] = item[f"{p}_primary_firstunit"]
        item["diagnosis_first_unit_by24h_classifiable"] = item[f"{p}_firstunit_by24_classifiable"].astype("boolean")
        item["diagnosis_first_unit_by24h_has_primary"] = item[f"{p}_primary_firstunit_by24"]
        item["diagnosis_all_icu_has_primary"] = item[f"{p}_primary_all_icu"]
        # Locked primary group: full-course Primary anywhere across all ICU
        # diagnosis rows linked to this hospital admission. 1=never Primary,
        # 0=Primary at least once. By-first-ICU-24h is a separate sensitivity.
        item["grp"] = [
            position_group(member, primary)
            for member, primary in zip(item.diagnosis_fullcourse_classifiable, item.diagnosis_fullcourse_has_primary)
        ]
        item["grp"] = pd.array(item.grp, dtype="Int8")
        item["position_scope"] = "full-course diagnosis rows across all ICU units linked to hospital admission"
        long_parts.append(item)
    long = pd.concat(long_parts, ignore_index=True) if long_parts else pd.DataFrame()
    if len(long) and long.duplicated(["admission_id", "disease"]).any():
        raise AssertionError("long panel contains duplicate admission-disease rows")
    return wide, long


def aggregate_outputs(wide: pd.DataFrame, long: pd.DataFrame, meta: dict[str, Any], elapsed: float) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    work_wide = WORK / "eicu_admission_components.csv.gz"
    work_long = WORK / "eicu_disease_panel.csv.gz"
    wide.to_csv(work_wide, index=False, compression="gzip")
    long.to_csv(work_long, index=False, compression="gzip")

    rows = []
    for disease in DEFS:
        for definition in ("narrow", "broad", "legacy_v1"):
            member = wide.loc[wide[f"{disease}_{definition}_member"].eq(1)]
            pri = f"{disease}_{definition}_primary_all_icu"
            by24_pri = f"{disease}_{definition}_primary_by24"
            by24_cls = f"{disease}_{definition}_by24_classifiable"
            positions = {
                "primary_full_course": member[pri].eq(True),
                "never_primary_full_course": member[pri].eq(False),
                "not_classifiable_by_index24_sensitivity": ~member[by24_cls].fillna(False),
                "primary_by_index24_sensitivity": member[by24_cls].fillna(False) & member[by24_pri].eq(True),
                "never_primary_by_index24_sensitivity": member[by24_cls].fillna(False) & member[by24_pri].eq(False),
            }
            for position, mask in positions.items():
                sub = member.loc[mask]
                known = sub.died.notna()
                rows.append({
                    "disease": {
                        "heart_failure": "heart failure", "copd": "COPD",
                        "pancreatitis": "acute pancreatitis",
                    }.get(disease, disease),
                    "disease_key": disease, "code_list": definition,
                    "position_scope_or_sensitivity": position,
                    "n_admissions": int(len(sub)), "n_known_outcome": int(known.sum()),
                    "deaths": int(sub.died.sum(skipna=True)),
                    "mortality": float(sub.loc[known, "died"].mean()) if known.any() else np.nan,
                    "qsofa_gcs13_complete_n": int(sub.qsofa_gcs13_complete.fillna(False).sum()),
                    "qsofa_gcs13_mean_complete": float(sub.qsofa_gcs13_score.dropna().mean()) if sub.qsofa_gcs13_score.notna().any() else np.nan,
                    "qsofa_gcs15_complete_n": int(sub.qsofa_gcs15_complete.fillna(False).sum()),
                    "curb65_complete_n": int(sub.curb65_complete.fillna(False).sum()),
                    "bisap4_complete_n": int(sub.bisap4_complete.fillna(False).sum()),
                })
    pd.DataFrame(rows).to_csv(OUT / "eicu_v2_cohort_position_summary.csv", index=False)

    score_rows = []
    score_specs = [
        ("qsofa_gcs13", "qsofa_gcs13_complete", "qsofa_gcs13_lower", "qsofa_gcs13_upper"),
        ("qsofa_gcs15_sensitivity", "qsofa_gcs15_complete", "qsofa_gcs15_lower", "qsofa_gcs15_upper"),
        ("curb65_gcs_proxy", "curb65_complete", "curb65_lower", "curb65_upper"),
        ("curb65_direct_confusion_sensitivity", "curb65_direct_confusion_complete",
         "curb65_direct_confusion_lower", "curb65_direct_confusion_upper"),
        ("bisap4_operationalized", "bisap4_complete", "bisap4_lower", "bisap4_upper"),
    ]
    for disease in DEFS:
        sub = wide.loc[wide[f"{disease}_broad_member"].eq(1)]
        for score_name, complete_col, lower_col, upper_col in score_specs:
            comp = sub[complete_col].fillna(False)
            score_rows.append({
                "disease": disease, "score": score_name, "n_cohort": int(len(sub)),
                "n_complete": int(comp.sum()), "n_incomplete": int((~comp).sum()),
                "n_lower_equals_upper": int(sub[lower_col].eq(sub[upper_col]).sum()),
                "n_partial_bounds": int(sub[lower_col].lt(sub[upper_col]).sum()),
            })
    pd.DataFrame(score_rows).to_csv(OUT / "eicu_v2_score_availability.csv", index=False)

    input_files = {}
    for f in ("patient.csv.gz", "diagnosis.csv.gz", "admissionDx.csv.gz",
              "vitalPeriodic.csv.gz", "vitalAperiodic.csv.gz", "nurseCharting.csv.gz", "lab.csv.gz"):
        p = EICU / f
        input_files[f] = {"size_bytes": p.stat().st_size, "mtime_epoch": int(p.stat().st_mtime)}
    manifest = {
        "schema_version": VERSION,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "input_root": str(EICU),
        "input_files": input_files,
        "private_wide_path": str(work_wide.resolve()),
        "private_long_path": str(work_long.resolve()),
        "aggregate_dir": str(OUT.resolve()),
        "index_rule": "one admission per patienthealthsystemstayid; minimum unitvisitnumber; tie-break by minimum elapsed hospital time (-hospitaladmitoffset); stable patientunitstayid",
        "observation_window": "[0, min(1440, observed index unit/hospital discharge offset)] minutes from index ICU admission",
        "admission_outcome": "hospitaldischargestatus reconciled across all linked unit stays; conflicting or unknown statuses remain missing",
        "cluster": "uniquepid",
        "hospital": "hospitalid from index unit stay",
        "diagnosis_scope": "locked primary position is full-course any Primary across all linked ICU diagnosis rows; index-ICU 0-24h sensitivity aligns each unit diagnosis via (diagnosisoffset - hospitaladmitoffset) + index_hospitaladmitoffset",
        "first_unit_sensitivity": "same classifications restricted to index patientunitstayid",
        "admissionDx": "APACHE ICU admission diagnosis match on index unit only; separate descriptor, not used for position or cohort eligibility",
        "missing_components": "threshold component is missing without a valid observation; primary score is missing unless all required components are known; lower/upper scores retained",
        "score_window_semantics": "worst valid first-day component values are combined; this is a window score, not a simultaneous single-time bedside score",
        "qsofa_primary": "RR >=22, non-invasive SBP <=100, GCS <=13",
        "qsofa_gcs15_sensitivity": "same components, GCS <15",
        "curb65": "confusion adapted as GCS <15 proxy; urea >7 mmol/L; RR >=30; SBP <90 or DBP <=60; age >=65",
        "curb65_actual_confusion": "explicit confusion/orientation labels are stored as a sensitivity if confidently classifiable; no inference from ambiguous free text",
        "bisap4": "BUN >25 mg/dL; GCS <15; operationalized SIRS >=2; age >60; pleural effusion omitted",
        "sirs_operationalized": "temperature <36 or >38 C, heart rate >90, respiration >20, WBC <4 or >12 x10^9/L; PaCO2/band-count criteria are not included",
        "pancreatitis_main": "acute ICD-9 5770/ICD-10 K85 plus acute-pancreatitis text; ICD-9 577 legacy definition is sensitivity only",
        "phenotype_notes": {
            "heart_failure": "primary is narrow HF-specific codes/text; broad and old all-subcodes 402/404 remain sensitivity flags",
            "copd": "primary is narrow explicit COPD/emphysema codes/text; broad and legacy 490/491/492/494/496 remain sensitivity flags",
            "pneumonia": "primary is broad original pneumonia list, including aspiration; narrow excludes aspiration",
            "sepsis": "primary is the previous explicit sepsis/septic code/text definition; bacteremia and T80.2 are broad sensitivity only",
            "pancreatitis": "primary is acute 5770/K85 and acute-pancreatitis text; ICD-9 577 is legacy sensitivity only",
        },
        "files": meta,
        "elapsed_seconds": round(elapsed, 2),
        "documentation": SOURCES,
        "output_policy": "patient-level deidentified analysis rows are in work/v2/eicu; outputs/v2/eicu contains aggregates and metadata only",
    }
    priority_qa_path = WORK / "cache" / "eicu_diagnosis_priority_qa.json"
    if priority_qa_path.exists():
        manifest["diagnosis_priority_qa"] = json.loads(priority_qa_path.read_text(encoding="utf-8"))
    (OUT / "eicu_v2_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"[write] private wide={len(wide):,} admissions; long={len(long):,} disease rows; elapsed={elapsed:.1f}s")


def save_cache(index: pd.DataFrame, dx: pd.DataFrame, measurements: pd.DataFrame, meta: dict[str, Any], elapsed: float) -> None:
    cache = WORK / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    index.to_csv(cache / "eicu_index.csv.gz", index=False, compression="gzip")
    dx.to_csv(cache / "eicu_diagnosis_summary.csv.gz", index=False, compression="gzip")
    measurements.rename_axis("patientunitstayid").reset_index().to_csv(
        cache / "eicu_timed_measurements.csv.gz", index=False, compression="gzip"
    )
    state = {
        "schema_version": VERSION,
        "saved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "raw_extraction_elapsed_seconds": round(elapsed, 2),
        "aggregate_metadata": meta,
    }
    (cache / "eicu_run_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    log("[cache] saved index, diagnosis summary, timed components, and aggregate run state")


def load_cache() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], float]:
    cache = WORK / "cache"
    required = [
        cache / "eicu_index.csv.gz", cache / "eicu_diagnosis_summary.csv.gz",
        cache / "eicu_timed_measurements.csv.gz", cache / "eicu_run_state.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("postprocess-only cache incomplete: " + ", ".join(missing))
    index = pd.read_csv(required[0], compression="gzip", dtype={"admission_id": "string", "pid": "string"})
    dx = pd.read_csv(required[1], compression="gzip", dtype={"admission_id": "string"})
    measurements = pd.read_csv(required[2], compression="gzip").set_index("patientunitstayid")
    state = json.loads(required[3].read_text(encoding="utf-8"))
    return index, dx, measurements, state["aggregate_metadata"], float(state["raw_extraction_elapsed_seconds"])


def run(postprocess_only: bool = False) -> int:
    run_started = time.monotonic()
    if postprocess_only:
        log("[run] loading private caches; no raw eICU table scan")
        index, dx, measurements, meta, elapsed = load_cache()
    else:
        t0 = time.monotonic()
        index, patient, stay_map = read_index()
        dx, dx_meta = diagnosis_summary(index, patient, stay_map)
        cache = WORK / "cache"
        cache.mkdir(parents=True, exist_ok=True)
        index.to_csv(cache / "eicu_index.csv.gz", index=False, compression="gzip")
        dx.to_csv(cache / "eicu_diagnosis_summary.csv.gz", index=False, compression="gzip")
        ids = set(index.index_patientunitstayid.astype("int64"))
        # Sequential passes intentionally avoid concurrent large reads from D:.
        vitals, vital_meta = extract_vitals(index, ids)
        labs, lab_meta = extract_labs(index, ids)
        nurse, nurse_meta = extract_nurse(index, ids)
        measurements = vitals.join(labs, how="outer").join(nurse, how="outer").reindex(pd.Index(ids, name="patientunitstayid"))
        for col in ("rr_max", "temperature_min", "temperature_max", "heartrate_max", "sbp_min", "dbp_min",
                    "bun_mgdl_max", "urea_mmol_l_max", "wbc_k_ul_min", "wbc_k_ul_max", "gcs_min",
                    "gcs_valid_observation_count", "confusion_chart_sensitivity"):
            if col not in measurements:
                measurements[col] = np.nan
        meta = {
            "index": {
                "hospital_admissions": int(len(index)),
                "index_stays_with_discharge_boundary": int(index.index_discharge_boundary_known.sum()),
                "index_icu_stays": int(index.index_patientunitstayid.nunique()),
                "repeated_uniquepid_admissions": int(index.pid.duplicated(keep=False).sum()),
                "known_hospital_outcomes": int(index.died.notna().sum()),
                "conflicting_hospital_status_admissions": int(index.hospital_death_status_conflict.sum()),
                "missing_hospital_status_admissions": int(index.hospital_death_status_missing.sum()),
            },
            "diagnosis": dx_meta,
            "vitals": vital_meta,
            "labs": lab_meta,
            "nurseCharting": nurse_meta,
        }
        elapsed = time.monotonic() - t0
        save_cache(index, dx, measurements, meta, elapsed)
    scored = make_scores(index, measurements)
    wide, long = panels(index, dx, scored)
    meta["score_coverage"] = {
        "qsofa_gcs13_complete": int(scored.qsofa_gcs13_complete.sum()),
        "qsofa_gcs15_complete": int(scored.qsofa_gcs15_complete.sum()),
        "curb65_complete": int(scored.curb65_complete.sum()),
        "bisap4_complete": int(scored.bisap4_complete.sum()),
        "hospital_outcome_known": int(scored.died.notna().sum()),
    }
    aggregate_outputs(wide, long, meta, time.monotonic() - run_started)
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postprocess-only", action="store_true", help="rebuild scores/aggregates from work/v2/eicu/cache without rereading raw tables")
    raise SystemExit(run(postprocess_only=parser.parse_args().postprocess_only))

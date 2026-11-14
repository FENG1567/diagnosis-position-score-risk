"""Rebuild the Amsterdam qSOFA application with approved dictionary unit recovery.

This is a separately versioned measurement-policy repair. It does not edit the
frozen mapping lock or strict-row-unit outputs. Only blank event-unit labels can
be filled, and only by one unambiguous APPROVED/EQUAL mapping in the locked
Amsterdam dictionary. Explicitly conflicting event labels remain excluded.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import os
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "work" / "v2" / "amsterdam"
OUT = ROOT / "outputs" / "v2" / "amsterdam" / "dictionary_unit_repair"
STRICT_OUT = ROOT / "outputs" / "v2" / "amsterdam" / "strict_row_units"
STRICT_SNAPSHOT = STRICT_OUT / "snapshot_manifest.json"
LOCK_PATH = ROOT / "outputs" / "v2" / "amsterdam" / "mapping_lock.json"
DICTIONARY = ROOT / "work" / "v2" / "sources" / "amsterdam_metadata" / "dictionary.csv"
NUMERIC_ZIP = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\archive\numericitems.zip")
PRIVATE = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\private")
PRIVATE_LISTITEMS = PRIVATE / "listitems_qsofa_nice.csv.gz"
STRICT_PANEL_PRE = PRIVATE / "qsofa_sepsis_icu_preoutcome.csv.gz"
STRICT_PANEL_OUTCOME = PRIVATE / "qsofa_sepsis_icu_outcome.csv.gz"
RAW_SELECTED_CACHE = PRIVATE / "numeric_qsofa_target_raw_before_unit_window.csv.gz"
REPAIRED_PANEL_PRE = PRIVATE / "qsofa_sepsis_icu_dictionary_unit_repair_preoutcome.csv.gz"
REPAIRED_PANEL_OUTCOME = PRIVATE / "qsofa_sepsis_icu_dictionary_unit_repair_outcome.csv.gz"
PROGRESS = WORK / "dictionary_unit_repair_progress.json"
CACHE_AGGREGATION_PROGRESS = WORK / "dictionary_unit_repair_cache_aggregation.json"
EXPECTED_LOCK_SHA256 = "b38ffd0f17a94d58857ce8dfa6e1cb04e8f3756430fbad0b0552a91c89e63669"
EXPECTED_DICTIONARY_SHA256 = "3dfb898825434282de6104f057dd858671cbc4ccfde1e2d1e76965b1c21bfe30"

ADMISSION_COLUMNS = ["patientid", "admissionid", "location", "admittedat", "dischargedat"]
NUMERIC_COLUMNS = ["admissionid", "itemid", "value", "unitid", "unit", "measuredat"]
OUTCOME_CONFIG = {
    "reps": 60, "seed": 20261112, "min_clusters": 20, "min_events": 10,
    "min_level_n": 20, "min_arm_n": 10, "min_usable_bootstrap": 20,
    "model_check": False,
}

sys.path.insert(0, str(WORK))
import run_amsterdam_audit as strict  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def atomic_gzip_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    frame.to_csv(temporary, index=False, compression={"method": "gzip", "compresslevel": 1})
    temporary.replace(path)


def load_strict_module():
    return strict


def normalize_unit(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return "".join(str(value).strip().casefold().replace("µ", "u").split())


def unit_compatible(component: str, unit: str) -> bool:
    return strict.unit_ok(component, unit)


def unit_rows_for_item(rows: list[dict[str, str]], itemid: int) -> tuple[str | None, str]:
    """Return a unique approved exact unit or a machine-readable refusal reason."""
    source_rows = [
        row for row in rows
        if row.get("source_vocabulary_id") == "AUMC Numeric Unit"
        and str(row.get("source_code", "")).strip() == str(int(itemid))
    ]
    if not source_rows:
        return None, "no_dictionary_row"
    approved_equal = [
        row for row in source_rows
        if str(row.get("mapping_status", "")).strip().upper() == "APPROVED"
        and str(row.get("equivalence", "")).strip().upper() == "EQUAL"
        and normalize_unit(row.get("concept_code"))
    ]
    units = {normalize_unit(row.get("concept_code")) for row in approved_equal}
    if not units:
        return None, "no_approved_equal_mapping"
    if len(units) != 1:
        return None, "ambiguous_approved_equal_mappings"
    unit = next(iter(units))
    return unit, "approved_equal_unique_unit"


def build_dictionary_unit_map(rows: list[dict[str, str]], itemids: set[int]) -> tuple[dict[int, str], dict[str, dict]]:
    mapping: dict[int, str] = {}
    diagnostics: dict[str, dict] = {}
    for itemid in sorted(itemids):
        unit, status = unit_rows_for_item(rows, itemid)
        diagnostics[str(itemid)] = {"unit": unit, "status": status}
        if unit is not None:
            mapping[itemid] = unit
    return mapping, diagnostics


def resolve_unit_label(event_unit, itemid: int, component: str,
                       dictionary_units: dict[int, str], *, allow_dictionary: bool = True) -> dict:
    """Keep explicit conflicts; use dictionary only when the event label is blank."""
    raw = "" if event_unit is None or pd.isna(event_unit) else str(event_unit).strip()
    if raw:
        if unit_compatible(component, raw):
            return {"accepted": True, "unit_source": "event_row", "effective_unit": raw,
                    "reason": "event_unit_compatible"}
        return {"accepted": False, "unit_source": "event_row", "effective_unit": raw,
                "reason": "explicit_event_unit_conflict"}
    if not allow_dictionary:
        return {"accepted": False, "unit_source": "missing", "effective_unit": None,
                "reason": "missing_event_unit_strict_policy"}
    mapped = dictionary_units.get(int(itemid))
    if mapped is None:
        return {"accepted": False, "unit_source": "missing", "effective_unit": None,
                "reason": "missing_or_ambiguous_dictionary_unit"}
    if not unit_compatible(component, mapped):
        return {"accepted": False, "unit_source": "dictionary", "effective_unit": mapped,
                "reason": "dictionary_unit_incompatible_with_component"}
    return {"accepted": True, "unit_source": "dictionary", "effective_unit": mapped,
            "reason": "approved_dictionary_unit_recovery"}


def measurement_in_window(measuredat, admittedat, dischargedat) -> bool:
    if pd.isna(measuredat) or pd.isna(admittedat):
        return False
    delta = float(measuredat) - float(admittedat)
    if delta < 0 or delta > 86_400_000:
        return False
    return pd.isna(dischargedat) or float(measuredat) <= float(dischargedat)


def read_dictionary_and_verify(lock: dict) -> tuple[list[dict[str, str]], str]:
    actual_sha = sha256(DICTIONARY)
    expected_sha = lock["source"]["dictionary_sha256"]
    if actual_sha != expected_sha or actual_sha != EXPECTED_DICTIONARY_SHA256:
        raise RuntimeError("The dictionary differs from the frozen pre-outcome source hash")
    with DICTIONARY.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return rows, actual_sha


def verify_strict_snapshot(lock_hash: str) -> dict:
    snapshot = json.loads(STRICT_SNAPSHOT.read_text(encoding="utf-8"))
    verified = []
    for record in snapshot:
        relative = Path(record["snapshot"])
        path = ROOT / relative
        if not path.is_file() or sha256(path) != record["sha256"]:
            raise RuntimeError(f"Strict-row-unit snapshot verification failed: {path}")
        verified.append(record["snapshot"])
    if sha256(STRICT_OUT / "mapping_lock.json") != lock_hash:
        raise RuntimeError("Frozen strict mapping-lock copy changed")
    return {"files_verified": len(verified), "mapping_lock_sha256": lock_hash,
            "strict_artifacts_unchanged": True}


def create_base_inputs(lock: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict, dict]:
    icu_admissions, admissions_validation = strict.load_admissions_preoutcome()
    selected = pd.read_csv(
        PRIVATE_LISTITEMS,
        dtype={"admissionid": "int64", "itemid": "int32", "valueid": "float64",
               "measuredat": "float64", "registeredby": "string", "updatedat": "float64"},
        low_memory=False,
    )
    target, diagnosis_validation = strict.diagnosis_groups(selected, icu_admissions, lock)
    gcs_summary, gcs_validation = strict.calculate_gcs(selected, target, lock)
    return target, gcs_summary, selected, admissions_validation, {
        "diagnosis_validation": diagnosis_validation,
        "gcs_validation": gcs_validation,
        "listitems_cache_rows": int(len(selected)),
        "listitems_cache_sha256": sha256(PRIVATE_LISTITEMS),
    }


def _update_admission_extrema(target_ids: set[int], values: pd.DataFrame,
                              accepted: pd.Series) -> dict[int, dict[str, float]]:
    summary = {int(aid): {"rr_max": np.nan, "rr_observed": False,
                          "sbp_min": np.nan, "sbp_observed": False} for aid in target_ids}
    valid = values.loc[accepted]
    if valid.empty:
        return summary
    for item_component, group in valid.groupby(["admissionid", "component"], sort=False):
        admissionid, component = item_component
        record = summary[int(admissionid)]
        if component == "rr":
            value = float(group["value_num"].max())
            record["rr_max"] = max(value, record["rr_max"]) if record["rr_observed"] else value
            record["rr_observed"] = True
        else:
            value = float(group["value_num"].min())
            record["sbp_min"] = min(value, record["sbp_min"]) if record["sbp_observed"] else value
            record["sbp_observed"] = True
    return summary


def scan_numeric_with_unit_repair(target: pd.DataFrame, lock: dict, dictionary_units: dict[int, str]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rr_ids = {int(row["itemid"]) for row in lock["qsofa"]["numeric_items"]["respiratory_rate"]}
    sbp_ids = {int(row["itemid"]) for row in lock["qsofa"]["numeric_items"]["systolic_blood_pressure"]}
    if rr_ids & sbp_ids:
        raise RuntimeError("RR and SBP item maps overlap")
    component_by_item = {**{item: "rr" for item in rr_ids}, **{item: "sbp" for item in sbp_ids}}
    itemids = set(component_by_item)
    target_ids = set(target["admissionid"].astype("int64"))
    admission_lookup = target.set_index("admissionid")[["admittedat", "dischargedat"]]
    strict_values: dict[int, dict[str, float | bool]] = {}
    repaired_values: dict[int, dict[str, float | bool]] = {}
    raw_unit_counts: dict[str, Counter[str]] = defaultdict(Counter)
    rows_by_item: Counter[str] = Counter()
    rows_in_window: Counter[str] = Counter()
    bad_numeric: Counter[str] = Counter()
    nonpositive: Counter[str] = Counter()
    observed_extrema: dict[str, list[float]] = defaultdict(list)
    policy_counts: dict[str, Counter[str]] = defaultdict(Counter)
    imputed_dictionary_rows: Counter[str] = Counter()
    explicit_conflicts: Counter[str] = Counter()
    numeric_rows_scanned = 0
    matched_rows = 0
    cache_rows = 0
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    temp_cache = RAW_SELECTED_CACHE.with_name(RAW_SELECTED_CACHE.name + ".partial")

    if NUMERIC_ZIP.stat().st_size != 8_161_018_961:
        raise RuntimeError("numericitems.zip size differs from the inspected source archive")
    with gzip.open(temp_cache, "wt", encoding="utf-8", newline="", compresslevel=1) as cache_stream:
        with zipfile.ZipFile(NUMERIC_ZIP) as archive:
            info = archive.getinfo("numericitems.csv")
            if info.file_size != 80_177_836_504 or info.CRC != 0x475539F6:
                raise RuntimeError("numericitems.csv size/CRC differs from the inspected source archive")
            atomic_json(PROGRESS, {
                "status": "in_progress", "started_at_utc": utc_now(),
                "member": info.filename, "member_uncompressed_bytes": info.file_size,
                "member_crc32_expected": f"{info.CRC:08x}",
                "selected_event_cache": str(RAW_SELECTED_CACHE),
                "cache_phase": "write target item rows before time-window and unit filtering",
                "mapping_lock_sha256": sha256(LOCK_PATH),
                "dictionary_sha256": sha256(DICTIONARY),
            })
            with archive.open(info, "r") as raw:
                reader = pd.read_csv(
                    raw, usecols=NUMERIC_COLUMNS,
                    dtype={"admissionid": "int64", "itemid": "int32", "value": "string",
                           "unitid": "string", "unit": "string", "measuredat": "float64"},
                    chunksize=1_000_000, low_memory=False, encoding="utf-8", encoding_errors="replace",
                )
                cache_header = True
                for number, chunk in enumerate(reader, start=1):
                    numeric_rows_scanned += len(chunk)
                    keep = chunk["itemid"].isin(itemids) & chunk["admissionid"].isin(target_ids)
                    data = chunk.loc[keep, NUMERIC_COLUMNS].copy()
                    if not data.empty:
                        matched_rows += len(data)
                        cache_rows += len(data)
                        data.to_csv(cache_stream, index=False, header=cache_header)
                        cache_header = False
                        data["component"] = data["itemid"].map(component_by_item)
                        data["value_num"] = pd.to_numeric(data["value"], errors="coerce")
                        for itemid, frame in data.groupby("itemid", sort=False):
                            key = str(int(itemid))
                            rows_by_item[key] += len(frame)
                            raw_unit_counts[key].update(
                                frame["unit"].fillna("<missing>").astype(str).value_counts().to_dict())
                            bad_numeric[key] += int(frame["value_num"].isna().sum())
                            nonpositive[key] += int((frame["value_num"].fillna(0) <= 0).sum())
                            numeric = frame["value_num"].dropna()
                            if not numeric.empty:
                                observed_extrema[key].extend([float(numeric.min()), float(numeric.max())])

                        admitted = data["admissionid"].map(admission_lookup["admittedat"])
                        discharged = data["admissionid"].map(admission_lookup["dischargedat"])
                        delta = data["measuredat"] - admitted
                        in_window = delta.between(0, 86_400_000, inclusive="both")
                        in_stay = discharged.isna() | data["measuredat"].le(discharged)
                        window = data.loc[in_window & in_stay].copy()
                        if not window.empty:
                            for itemid, frame in window.groupby("itemid", sort=False):
                                rows_in_window[str(int(itemid))] += len(frame)
                            window["strict_unit_ok"] = False
                            window["repair_unit_ok"] = False
                            window["unit_source"] = "missing"
                            window["unit_resolution_reason"] = ""
                            for idx, row in window.iterrows():
                                itemid = int(row["itemid"])
                                item_key = str(itemid)
                                resolution = resolve_unit_label(
                                    row["unit"], itemid, row["component"], dictionary_units,
                                )
                                strict_resolution = resolve_unit_label(
                                    row["unit"], itemid, row["component"], dictionary_units,
                                    allow_dictionary=False,
                                )
                                window.at[idx, "strict_unit_ok"] = strict_resolution["accepted"]
                                window.at[idx, "repair_unit_ok"] = resolution["accepted"]
                                window.at[idx, "unit_source"] = resolution["unit_source"]
                                window.at[idx, "unit_resolution_reason"] = resolution["reason"]
                                policy_counts[item_key][resolution["reason"]] += 1
                                if resolution["unit_source"] == "dictionary" and resolution["accepted"]:
                                    imputed_dictionary_rows[item_key] += 1
                                if resolution["reason"] == "explicit_event_unit_conflict":
                                    explicit_conflicts[item_key] += 1
                            positive_numeric = window["value_num"].notna() & window["value_num"].gt(0)
                            strict_ok = window["strict_unit_ok"].astype(bool) & positive_numeric
                            repair_ok = window["repair_unit_ok"].astype(bool) & positive_numeric
                            strict_chunk = _update_admission_extrema(target_ids, window, strict_ok)
                            repair_chunk = _update_admission_extrema(target_ids, window, repair_ok)
                            for admissionid, values in strict_chunk.items():
                                current = strict_values.setdefault(admissionid, {
                                    "rr_max": np.nan, "rr_observed": False,
                                    "sbp_min": np.nan, "sbp_observed": False,
                                })
                                _merge_extrema(current, values)
                            for admissionid, values in repair_chunk.items():
                                current = repaired_values.setdefault(admissionid, {
                                    "rr_max": np.nan, "rr_observed": False,
                                    "sbp_min": np.nan, "sbp_observed": False,
                                })
                                _merge_extrema(current, values)

                    if number % 8 == 0:
                        elapsed = round(time.time() - started, 1)
                        print(f"[numericitems] chunks={number} rows={numeric_rows_scanned} "
                              f"matched={matched_rows} cache_rows={cache_rows} elapsed_s={elapsed}", flush=True)
                        atomic_json(PROGRESS, {
                            "status": "in_progress", "updated_at_utc": utc_now(),
                            "member": info.filename, "member_uncompressed_bytes": info.file_size,
                            "member_crc32_expected": f"{info.CRC:08x}", "chunks_completed": number,
                            "rows_scanned": numeric_rows_scanned, "matched_target_item_rows": matched_rows,
                            "cache_rows_written": cache_rows, "elapsed_seconds": elapsed,
                        })
            # Full iteration to EOF above makes ZipExtFile verify its member CRC.

    # Publish only after the member is fully parsed and its CRC has been checked.
    temp_cache.replace(RAW_SELECTED_CACHE)
    target_ids_sorted = sorted(target_ids)
    strict_summary = pd.DataFrame.from_records([
        {"admissionid": aid, **strict_values.get(aid, {"rr_max": np.nan, "rr_observed": False,
         "sbp_min": np.nan, "sbp_observed": False})} for aid in target_ids_sorted
    ])
    repaired_summary = pd.DataFrame.from_records([
        {"admissionid": aid, **repaired_values.get(aid, {"rr_max": np.nan, "rr_observed": False,
         "sbp_min": np.nan, "sbp_observed": False})} for aid in target_ids_sorted
    ])
    numeric_validation = {
        "numeric_member": info.filename,
        "numeric_member_uncompressed_bytes": info.file_size,
        "numeric_member_crc32": f"{info.CRC:08x}",
        "numeric_rows_scanned": int(numeric_rows_scanned),
        "matched_target_item_rows_before_window": int(matched_rows),
        "selected_event_cache_rows_before_window_and_unit_filter": int(cache_rows),
        "selected_event_cache_path_private": str(RAW_SELECTED_CACHE),
        "rows_by_itemid_before_window": dict(sorted(rows_by_item.items(), key=lambda kv: int(kv[0]))),
        "rows_by_itemid_in_window_before_unit_check": dict(sorted(rows_in_window.items(), key=lambda kv: int(kv[0]))),
        "non_numeric_by_itemid": dict(sorted(bad_numeric.items(), key=lambda kv: int(kv[0]))),
        "nonpositive_by_itemid": dict(sorted(nonpositive.items(), key=lambda kv: int(kv[0]))),
        "unit_counts_by_itemid_before_window": {
            itemid: dict(sorted(counts.items())) for itemid, counts in raw_unit_counts.items()},
        "observed_extrema_by_itemid_before_window": {
            itemid: {"min": min(values), "max": max(values)}
            for itemid, values in observed_extrema.items() if values},
        "unit_policy_resolution_counts_in_window": {
            itemid: dict(sorted(counts.items())) for itemid, counts in policy_counts.items()},
        "dictionary_imputed_accepted_rows_in_window_by_itemid": dict(sorted(imputed_dictionary_rows.items(),
                                                                                key=lambda kv: int(kv[0]))),
        "explicit_conflict_rows_in_window_by_itemid": dict(sorted(explicit_conflicts.items(),
                                                                   key=lambda kv: int(kv[0]))),
        "strict_rr_observed_admissions": int(strict_summary["rr_observed"].sum()),
        "strict_sbp_observed_admissions": int(strict_summary["sbp_observed"].sum()),
        "repaired_rr_observed_admissions": int(repaired_summary["rr_observed"].sum()),
        "repaired_sbp_observed_admissions": int(repaired_summary["sbp_observed"].sum()),
        "strict_row_units_policy_preserved": True,
        "dictionary_fallback_only_for_missing_event_unit": True,
        "explicit_conflicts_rejected": True,
        "zip_member_crc_checked": True,
        "raw_cache_sha256": sha256(RAW_SELECTED_CACHE),
    }
    atomic_json(PROGRESS, {
        "status": "complete", "completed_at_utc": utc_now(),
        "member": info.filename, "member_uncompressed_bytes": info.file_size,
        "member_crc32_expected": f"{info.CRC:08x}", "member_crc32_verified": f"{info.CRC:08x}",
        "chunks_completed": number, "rows_scanned": numeric_rows_scanned,
        "matched_target_item_rows": matched_rows, "cache_rows_written": cache_rows,
        "cache_sha256": numeric_validation["raw_cache_sha256"],
        "elapsed_seconds": round(time.time() - started, 1),
        "crc_verified_by": "zipfile.ZipExtFile full-member EOF read",
    })
    print(json.dumps({"numeric_rows_scanned": numeric_rows_scanned,
                      "matched_target_item_rows": matched_rows,
                      "raw_cache_rows": cache_rows,
                      "crc32": f"{info.CRC:08x}",
                      "cache_sha256": numeric_validation["raw_cache_sha256"]}, indent=2), flush=True)
    return strict_summary, repaired_summary, numeric_validation


def aggregate_selected_event_cache(target: pd.DataFrame, lock: dict,
                                   dictionary_units: dict[int, str]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Aggregate the CRC-verified private selected-row cache without rereading the source archive."""
    scan_state = json.loads(PROGRESS.read_text(encoding="utf-8"))
    if (scan_state.get("status") != "complete"
            or scan_state.get("member_crc32_verified") != "475539f6"
            or not RAW_SELECTED_CACHE.is_file()
            or sha256(RAW_SELECTED_CACHE) != scan_state.get("cache_sha256")):
        raise RuntimeError("A complete, hash-verified selected-event cache is required")
    rr_ids = {int(row["itemid"]) for row in lock["qsofa"]["numeric_items"]["respiratory_rate"]}
    sbp_ids = {int(row["itemid"]) for row in lock["qsofa"]["numeric_items"]["systolic_blood_pressure"]}
    component_by_item = {**{item: "rr" for item in rr_ids}, **{item: "sbp" for item in sbp_ids}}
    target_ids = set(target["admissionid"].astype("int64"))
    admission_lookup = target.set_index("admissionid")[["admittedat", "dischargedat"]]
    strict_values: dict[int, dict[str, float | bool]] = {}
    repaired_values: dict[int, dict[str, float | bool]] = {}
    raw_unit_counts: dict[str, Counter[str]] = defaultdict(Counter)
    rows_by_item: Counter[str] = Counter()
    rows_in_window: Counter[str] = Counter()
    bad_numeric: Counter[str] = Counter()
    nonpositive: Counter[str] = Counter()
    observed_extrema: dict[str, list[float]] = defaultdict(list)
    policy_counts: dict[str, Counter[str]] = defaultdict(Counter)
    imputed_dictionary_rows: Counter[str] = Counter()
    explicit_conflicts: Counter[str] = Counter()
    cached_rows = 0
    started = time.time()
    for chunk_number, data in enumerate(pd.read_csv(
            RAW_SELECTED_CACHE,
            dtype={"admissionid": "int64", "itemid": "int32", "value": "string",
                   "unitid": "string", "unit": "string", "measuredat": "float64"},
            chunksize=500_000, low_memory=False, encoding="utf-8", encoding_errors="replace"), start=1):
        cached_rows += len(data)
        data["component"] = data["itemid"].map(component_by_item)
        data["value_num"] = pd.to_numeric(data["value"], errors="coerce")
        for itemid, frame in data.groupby("itemid", sort=False):
            key = str(int(itemid))
            rows_by_item[key] += len(frame)
            raw_unit_counts[key].update(frame["unit"].fillna("<missing>").astype(str).value_counts().to_dict())
            bad_numeric[key] += int(frame["value_num"].isna().sum())
            nonpositive[key] += int((frame["value_num"].fillna(0) <= 0).sum())
            numeric = frame["value_num"].dropna()
            if not numeric.empty:
                observed_extrema[key].extend([float(numeric.min()), float(numeric.max())])

        admitted = data["admissionid"].map(admission_lookup["admittedat"])
        discharged = data["admissionid"].map(admission_lookup["dischargedat"])
        delta = data["measuredat"] - admitted
        in_window = delta.between(0, 86_400_000, inclusive="both")
        in_stay = discharged.isna() | data["measuredat"].le(discharged)
        window = data.loc[in_window & in_stay].copy()
        if not window.empty:
            for itemid, frame in window.groupby("itemid", sort=False):
                rows_in_window[str(int(itemid))] += len(frame)
            window["strict_unit_ok"] = False
            window["repair_unit_ok"] = False
            window["unit_source"] = "missing"
            window["unit_resolution_reason"] = ""
            for idx, row in window.iterrows():
                itemid = int(row["itemid"])
                item_key = str(itemid)
                resolution = resolve_unit_label(row["unit"], itemid, row["component"], dictionary_units)
                strict_resolution = resolve_unit_label(
                    row["unit"], itemid, row["component"], dictionary_units, allow_dictionary=False)
                window.at[idx, "strict_unit_ok"] = strict_resolution["accepted"]
                window.at[idx, "repair_unit_ok"] = resolution["accepted"]
                window.at[idx, "unit_source"] = resolution["unit_source"]
                window.at[idx, "unit_resolution_reason"] = resolution["reason"]
                policy_counts[item_key][resolution["reason"]] += 1
                if resolution["unit_source"] == "dictionary" and resolution["accepted"]:
                    imputed_dictionary_rows[item_key] += 1
                if resolution["reason"] == "explicit_event_unit_conflict":
                    explicit_conflicts[item_key] += 1
            positive_numeric = window["value_num"].notna() & window["value_num"].gt(0)
            strict_ok = window["strict_unit_ok"].astype(bool) & positive_numeric
            repair_ok = window["repair_unit_ok"].astype(bool) & positive_numeric
            strict_chunk = _update_admission_extrema(target_ids, window, strict_ok)
            repair_chunk = _update_admission_extrema(target_ids, window, repair_ok)
            for admissionid, values in strict_chunk.items():
                current = strict_values.setdefault(admissionid, {
                    "rr_max": np.nan, "rr_observed": False,
                    "sbp_min": np.nan, "sbp_observed": False,
                })
                _merge_extrema(current, values)
            for admissionid, values in repair_chunk.items():
                current = repaired_values.setdefault(admissionid, {
                    "rr_max": np.nan, "rr_observed": False,
                    "sbp_min": np.nan, "sbp_observed": False,
                })
                _merge_extrema(current, values)

        if chunk_number % 4 == 0:
            elapsed = round(time.time() - started, 1)
            atomic_json(CACHE_AGGREGATION_PROGRESS, {
                "status": "in_progress", "updated_at_utc": utc_now(),
                "chunks_completed": chunk_number, "cache_rows_read": cached_rows,
                "elapsed_seconds": elapsed,
                "raw_cache_sha256": scan_state["cache_sha256"],
            })

    strict_summary = pd.DataFrame.from_records([
        {"admissionid": aid, **strict_values.get(aid, {"rr_max": np.nan, "rr_observed": False,
         "sbp_min": np.nan, "sbp_observed": False})} for aid in sorted(target_ids)
    ])
    repaired_summary = pd.DataFrame.from_records([
        {"admissionid": aid, **repaired_values.get(aid, {"rr_max": np.nan, "rr_observed": False,
         "sbp_min": np.nan, "sbp_observed": False})} for aid in sorted(target_ids)
    ])
    validation = {
        "numeric_member": scan_state["member"],
        "numeric_member_uncompressed_bytes": scan_state["member_uncompressed_bytes"],
        "numeric_member_crc32": scan_state["member_crc32_verified"],
        "numeric_rows_scanned": int(scan_state["rows_scanned"]),
        "matched_target_item_rows_before_window": int(cached_rows),
        "selected_event_cache_rows_before_window_and_unit_filter": int(cached_rows),
        "selected_event_cache_path_private": str(RAW_SELECTED_CACHE),
        "rows_by_itemid_before_window": dict(sorted(rows_by_item.items(), key=lambda kv: int(kv[0]))),
        "rows_by_itemid_in_window_before_unit_check": dict(sorted(rows_in_window.items(), key=lambda kv: int(kv[0]))),
        "non_numeric_by_itemid": dict(sorted(bad_numeric.items(), key=lambda kv: int(kv[0]))),
        "nonpositive_by_itemid": dict(sorted(nonpositive.items(), key=lambda kv: int(kv[0]))),
        "unit_counts_by_itemid_before_window": {
            itemid: dict(sorted(counts.items())) for itemid, counts in raw_unit_counts.items()},
        "observed_extrema_by_itemid_before_window": {
            itemid: {"min": min(values), "max": max(values)}
            for itemid, values in observed_extrema.items() if values},
        "unit_policy_resolution_counts_in_window": {
            itemid: dict(sorted(counts.items())) for itemid, counts in policy_counts.items()},
        "dictionary_imputed_accepted_rows_in_window_by_itemid": dict(sorted(imputed_dictionary_rows.items(),
                                                                                key=lambda kv: int(kv[0]))),
        "explicit_conflict_rows_in_window_by_itemid": dict(sorted(explicit_conflicts.items(),
                                                                   key=lambda kv: int(kv[0]))),
        "strict_rr_observed_admissions": int(strict_summary["rr_observed"].sum()),
        "strict_sbp_observed_admissions": int(strict_summary["sbp_observed"].sum()),
        "repaired_rr_observed_admissions": int(repaired_summary["rr_observed"].sum()),
        "repaired_sbp_observed_admissions": int(repaired_summary["sbp_observed"].sum()),
        "strict_row_units_policy_preserved": True,
        "dictionary_fallback_only_for_missing_event_unit": True,
        "explicit_conflicts_rejected": True,
        "zip_member_crc_checked": True,
        "raw_cache_sha256": scan_state["cache_sha256"],
    }
    atomic_json(CACHE_AGGREGATION_PROGRESS, {
        "status": "complete", "completed_at_utc": utc_now(),
        "chunks_completed": chunk_number, "cache_rows_read": cached_rows,
        "elapsed_seconds": round(time.time() - started, 1),
        "raw_cache_sha256": scan_state["cache_sha256"],
    })
    return strict_summary, repaired_summary, validation


def _merge_extrema(target: dict, source: dict) -> None:
    if source["rr_observed"]:
        target["rr_max"] = (max(float(target["rr_max"]), float(source["rr_max"]))
                            if target["rr_observed"] else float(source["rr_max"]))
        target["rr_observed"] = True
    if source["sbp_observed"]:
        target["sbp_min"] = (min(float(target["sbp_min"]), float(source["sbp_min"]))
                             if target["sbp_observed"] else float(source["sbp_min"]))
        target["sbp_observed"] = True


def compose_panel(target: pd.DataFrame, gcs_summary: pd.DataFrame,
                  numeric_summary: pd.DataFrame) -> pd.DataFrame:
    panel = target.merge(gcs_summary, on="admissionid", how="left", validate="one_to_one")
    panel = panel.merge(numeric_summary, on="admissionid", how="left", validate="one_to_one")
    panel["rr_point"] = panel["rr_observed"].fillna(False) & panel["rr_max"].ge(22)
    panel["sbp_point"] = panel["sbp_observed"].fillna(False) & panel["sbp_min"].le(100)
    panel["gcs_main_point"] = panel["min_gcs"].le(13)
    panel["gcs_sensitivity_point"] = panel["min_gcs"].lt(15)
    panel["qsofa_complete"] = (panel["rr_observed"].fillna(False) & panel["sbp_observed"].fillna(False)
                               & panel["min_gcs"].notna())
    panel["qsofa_main"] = np.where(
        panel["qsofa_complete"],
        panel["rr_point"].astype("int8") + panel["sbp_point"].astype("int8")
        + panel["gcs_main_point"].astype("int8"), np.nan,
    )
    panel["qsofa_gcs_lt15"] = np.where(
        panel["qsofa_complete"],
        panel["rr_point"].astype("int8") + panel["sbp_point"].astype("int8")
        + panel["gcs_sensitivity_point"].astype("int8"), np.nan,
    )
    return panel


def compare_strict_reconstruction(reconstructed: pd.DataFrame, baseline_path: Path) -> dict:
    baseline = pd.read_csv(baseline_path, low_memory=False)
    fields = ["admissionid", "grp", "rr_max", "rr_observed", "sbp_min", "sbp_observed",
              "min_gcs", "qsofa_complete", "qsofa_main", "qsofa_gcs_lt15"]
    left = reconstructed[fields].copy()
    right = baseline[fields].copy()
    left_ids = pd.to_numeric(left["admissionid"], errors="coerce")
    right_ids = pd.to_numeric(right["admissionid"], errors="coerce")
    if (left_ids.isna().any() or right_ids.isna().any()
            or (left_ids % 1).ne(0).any() or (right_ids % 1).ne(0).any()):
        return {"pass": False, "reason": "admission IDs contain missing or non-integer values",
                "rows_reconstructed": len(left), "rows_baseline": len(right)}
    # Normalize pandas nullable Int64 and NumPy int64 columns to the same semantic type.
    left["admissionid"] = left_ids.astype("int64")
    right["admissionid"] = right_ids.astype("int64")
    left = left.sort_values("admissionid").reset_index(drop=True)
    right = right.sort_values("admissionid").reset_index(drop=True)
    if not np.array_equal(left["admissionid"].to_numpy(), right["admissionid"].to_numpy()):
        return {"pass": False, "reason": "admission id order/content differs", "rows_reconstructed": len(left),
                "rows_baseline": len(right),
                "normalized_admission_ids_match": False}
    mismatches = {}
    missingness_mismatches = {}
    for col in fields[1:]:
        a = left[col]
        b = right[col]
        a_missing = a.isna().to_numpy(dtype=bool)
        b_missing = b.isna().to_numpy(dtype=bool)
        if pd.api.types.is_numeric_dtype(a) or pd.api.types.is_numeric_dtype(b):
            a_numeric = pd.to_numeric(a, errors="coerce")
            b_numeric = pd.to_numeric(b, errors="coerce")
            av = a_numeric.to_numpy(dtype="float64", na_value=np.nan)
            bv = b_numeric.to_numpy(dtype="float64", na_value=np.nan)
            a_invalid = (~a_missing) & a_numeric.isna().to_numpy(dtype=bool)
            b_invalid = (~b_missing) & b_numeric.isna().to_numpy(dtype=bool)
            equal_values = av == bv
            equal = ((a_missing == b_missing)
                     & (a_missing | (equal_values & ~a_invalid & ~b_invalid)))
        else:
            a_text = a.astype("string")
            b_text = b.astype("string")
            equal_values = a_text.fillna("").to_numpy() == b_text.fillna("").to_numpy()
            equal = (a_missing == b_missing) & (a_missing | equal_values)
        mismatches[col] = int((~equal).sum())
        missingness_mismatches[col] = int((a_missing != b_missing).sum())
    return {"pass": all(value == 0 for value in mismatches.values()),
            "fields_compared": fields, "row_count": len(left), "mismatch_count_by_field": mismatches,
            "missingness_mismatch_count_by_field": missingness_mismatches,
            "admission_ids_normalized_to_int64": True,
            "baseline_private_panel_sha256": sha256(baseline_path)}


def score_distribution(panel: pd.DataFrame) -> dict:
    result = {}
    for grp, frame in panel.groupby("grp", dropna=False):
        name = "primary" if int(grp) == 0 else "secondary_only"
        result[name] = {
            "admissions": int(len(frame)), "patients": int(frame["patientid"].nunique()),
            "qsofa_complete": int(frame["qsofa_complete"].sum()),
            "qsofa_main_distribution": {
                str(int(k)): int(v) for k, v in frame["qsofa_main"].dropna().value_counts().sort_index().items()},
            "qsofa_gcs_lt15_distribution": {
                str(int(k)): int(v) for k, v in frame["qsofa_gcs_lt15"].dropna().value_counts().sort_index().items()},
        }
    return result


def preoutcome_phase() -> dict:
    lock, lock_hash = strict.load_lock()
    if lock_hash != EXPECTED_LOCK_SHA256:
        raise RuntimeError("Frozen mapping lock hash differs from the authorized version")
    strict_snapshot = verify_strict_snapshot(lock_hash)
    dictionary_rows, dictionary_hash = read_dictionary_and_verify(lock)
    target, gcs_summary, selected, admissions_validation, base_validation = create_base_inputs(lock)
    numeric_map = lock["qsofa"]["numeric_items"]
    rr_ids = {int(row["itemid"]) for row in numeric_map["respiratory_rate"]}
    sbp_ids = {int(row["itemid"]) for row in numeric_map["systolic_blood_pressure"]}
    expected_component = {**{item: "rr" for item in rr_ids}, **{item: "sbp" for item in sbp_ids}}
    dictionary_units, dictionary_unit_qa = build_dictionary_unit_map(dictionary_rows, set(expected_component))
    for itemid in expected_component:
        resolved = dictionary_units.get(itemid)
        if resolved is not None and not unit_compatible(expected_component[itemid], resolved):
            dictionary_unit_qa[str(itemid)]["status"] = "approved_equal_unit_incompatible_with_expected_component"
            dictionary_units.pop(itemid)
    if dictionary_unit_qa.get("8874", {}).get("unit") != "/min":
        raise RuntimeError("Approved AUMC dictionary mapping for item 8874 is not UCUM /min")
    if dictionary_unit_qa.get("8874", {}).get("status") != "approved_equal_unique_unit":
        raise RuntimeError("Unit 8874 is not represented by one approved exact dictionary unit")

    scan_state = json.loads(PROGRESS.read_text(encoding="utf-8")) if PROGRESS.is_file() else {}
    if scan_state.get("status") == "complete" and RAW_SELECTED_CACHE.is_file():
        strict_numeric, repaired_numeric, numeric_validation = aggregate_selected_event_cache(
            target, lock, dictionary_units,
        )
    else:
        strict_numeric, repaired_numeric, numeric_validation = scan_numeric_with_unit_repair(
            target, lock, dictionary_units,
        )
    strict_panel = compose_panel(target, gcs_summary, strict_numeric)
    repaired_panel = compose_panel(target, gcs_summary, repaired_numeric)
    strict_reconstruction = compare_strict_reconstruction(strict_panel, STRICT_PANEL_PRE)
    if not strict_reconstruction["pass"]:
        atomic_json(OUT / "strict_reconstruction_failure.json", strict_reconstruction)
        print(json.dumps({"strict_panel_reconstruction": strict_reconstruction}, indent=2), flush=True)
        raise AssertionError("Reconstructed strict-row-unit panel differs from frozen private strict panel")
    atomic_gzip_csv(repaired_panel, REPAIRED_PANEL_PRE)

    strict_validation = json.loads((STRICT_OUT / "preoutcome_field_validation.json").read_text(encoding="utf-8"))
    strict_dist = strict_validation["qsofa_preoutcome_summary_by_group"]
    repaired_dist = score_distribution(repaired_panel)
    repair_delta = {
        group: {
            "admissions": repaired_dist[group]["admissions"],
            "strict_qsofa_complete": strict_dist[group]["qsofa_complete"],
            "repaired_qsofa_complete": repaired_dist[group]["qsofa_complete"],
            "additional_complete": repaired_dist[group]["qsofa_complete"] - strict_dist[group]["qsofa_complete"],
            "strict_qsofa_main_distribution": strict_dist[group]["qsofa_main_distribution"],
            "repaired_qsofa_main_distribution": repaired_dist[group]["qsofa_main_distribution"],
            "strict_qsofa_gcs_lt15_distribution": strict_dist[group]["qsofa_gcs_lt15_distribution"],
            "repaired_qsofa_gcs_lt15_distribution": repaired_dist[group]["qsofa_gcs_lt15_distribution"],
        } for group in ("primary", "secondary_only")
    }
    result = {
        "phase": "dictionary_unit_repair_preoutcome_validation",
        "outcome_field_loaded": False,
        "repair_timing": {
            "strict_outcome_results_had_been_examined_before_repair": True,
            "unit_mapping_source_was_locked_preoutcome_dictionary": True,
            "no_outcome_values_used_to_select_unit_mapping_or_thresholds": True,
            "interpretation": "Post-hoc measurement-policy correction; report strictly-unit-filtered results as the prespecified measurement sensitivity.",
        },
        "mapping_lock_sha256_unchanged": lock_hash,
        "dictionary_sha256": dictionary_hash,
        "strict_snapshot_verification": strict_snapshot,
        "strict_panel_reconstruction": strict_reconstruction,
        "unit_policy": {
            "fallback_rule": "Only a blank event unit may be filled, and only by a unique APPROVED/EQUAL dictionary mapping compatible with the locked component unit.",
            "explicit_conflict_rule": "A nonblank incompatible event unit is rejected and never overridden by dictionary metadata.",
            "dictionary_unit_map": dictionary_unit_qa,
            "dictionary_mapped_measurement_concept": {
                "8874": "Ademfrequentie Monitor; LOINC 9279-1 respiratory rate; UCUM /min.",
            },
        },
        "admissions_validation": admissions_validation,
        "listitems_validation": base_validation,
        "diagnosis_validation": base_validation["diagnosis_validation"],
        "gcs_validation": base_validation["gcs_validation"],
        "numeric_validation": numeric_validation,
        "strict_score_distribution_by_group": strict_dist,
        "repaired_score_distribution_by_group": repaired_dist,
        "score_completeness_and_allocation_change": repair_delta,
        "private_repaired_panel_path": str(REPAIRED_PANEL_PRE),
        "private_raw_selected_event_cache_path": str(RAW_SELECTED_CACHE),
    }
    atomic_json(OUT / "preoutcome_repair_validation.json", result)
    print(json.dumps({"validation_path": str((OUT / "preoutcome_repair_validation.json").relative_to(ROOT)),
                      "strict_reconstruction_pass": strict_reconstruction["pass"],
                      "strict_complete": strict_dist, "repaired_complete": repaired_dist,
                      "dictionary_imputations": numeric_validation["dictionary_imputed_accepted_rows_in_window_by_itemid"],
                      "crc_checked": numeric_validation["zip_member_crc_checked"]}, ensure_ascii=False, indent=2), flush=True)
    return result


def audit_frame(audit_function, panel: pd.DataFrame, score_col: str, title: str,
                config: dict | None = None) -> tuple[dict, object]:
    from estimands import direct_contrast

    frame = panel[["patientid", "grp", "icu_death", score_col]].rename(columns={score_col: "score"})
    metadata = {
        "database": "AmsterdamUMCdb 1.0.2",
        "disease": "sepsis by locked NICE APACHE-IV diagnosis values",
        "semantics": "primary NICE APACHE-IV itemid 18671 vs secondary-only NICE APACHE-IV itemid 18673; fixed dictionary value lists",
        "score_window": "worst component qSOFA over first 24 hours of ICU admission episode; components may occur at separate times; GCS E/M/V complete at one timestamp",
        "outcome_window": "destination at ICU/MCU discharge; Overleden is death",
        "row_unit": "ICU admission episode (admissionid)",
        "cluster_unit": "patientid",
        "missingness_assumption": "unknown",
        "missing_data_handling": "complete-case qSOFA components; unknown or blank destination remains missing",
        "measurement_version": "dictionary unit repair; blank event units resolved only from unambiguous approved equal source dictionary mappings",
        "repair_timing": "strict-row-unit outcomes were inspected before this dictionary-based repair; unit rules were not selected using outcome values",
        "score_col": title,
    }
    result = audit_function(
        frame, score_col="score", outcome_col="icu_death", group_col="grp", pid_col="patientid",
        metadata=metadata, config=(config or OUTCOME_CONFIG),
    )
    complete = frame.dropna(subset=["patientid", "grp", "icu_death", "score"]).rename(
        columns={"patientid": "pid", "icu_death": "y"}
    )
    direct = direct_contrast(complete)
    direct_estimate_pp = 100 * direct.estimate
    direct_se_pp = 100 * direct.se
    estimate_match = (result.get("stratified_rd_pp") is None
                      or float(result["stratified_rd_pp"]) == round(direct_estimate_pp, 2))
    se_match = (result.get("delta_se_pp") is None
                or float(result["delta_se_pp"]) == round(direct_se_pp, 2))
    if not estimate_match:
        raise AssertionError(f"audit_v2 and root direct_contrast disagree for {title}")
    if not se_match:
        raise AssertionError(f"audit_v2 and root direct_contrast SE disagree for {title}")
    result["root_estimand_crosscheck"] = {
        "estimator": "work/v2/estimands.py::direct_contrast",
        "estimate_pp": direct_estimate_pp,
        "numerical_cluster_se_pp": direct_se_pp,
        "audit_reported_estimate_pp": result.get("stratified_rd_pp"),
        "audit_reported_se_pp": result.get("delta_se_pp"),
        "estimate_matches_audit_at_reported_precision": estimate_match,
        "se_matches_audit_at_reported_precision": se_match,
        "difference_from_audit_estimate_pp": (None if result.get("stratified_rd_pp") is None else
                                               direct_estimate_pp - result["stratified_rd_pp"]),
        "n_records_on_common_support": direct.n_records,
        "n_supported_patients": direct.n_patients,
        "n_inference_clusters": direct.n_inference_clusters,
        "common_support_share": direct.support_share,
        "crosscheck_passed": bool(estimate_match and se_match),
    }
    return result, direct


def outcome_flow(panel: pd.DataFrame) -> dict:
    result = {}
    for grp, frame in panel.groupby("grp", dropna=False):
        name = "primary" if int(grp) == 0 else "secondary_only"
        observed = frame["icu_death"].dropna()
        result[name] = {
            "admissions": int(len(frame)), "patients": int(frame["patientid"].nunique()),
            "outcome_observed": int(len(observed)), "outcome_missing": int(frame["icu_death"].isna().sum()),
            "icu_mcu_discharge_deaths": int((observed == 1).sum()),
            "icu_mcu_discharge_deaths_pct": round(100 * float(observed.mean()), 2) if len(observed) else None,
        }
    return result


def flatten_ci_row(version: str, score: str, audit: dict) -> dict:
    normal = audit.get("delta_ci_pp")
    bootstrap = audit.get("stratified_rd_ci_pp")
    return {
        "measurement_version": version, "score": score,
        "estimate_pp": audit.get("stratified_rd_pp"),
        "normal_if_ci_lower_pp": normal[0] if normal else None,
        "normal_if_ci_upper_pp": normal[1] if normal else None,
        "normal_if_ci_status": ("computed" if normal else audit.get("interval_status")),
        "bootstrap_percentile_ci_lower_pp": bootstrap[0] if bootstrap else None,
        "bootstrap_percentile_ci_upper_pp": bootstrap[1] if bootstrap else None,
        "bootstrap_ci_status": ("computed" if bootstrap else audit.get("interval_status")),
        "interval_status": audit.get("interval_status"),
        "verdict": audit.get("verdict"),
        "refusal_reasons": ";".join(audit.get("refusal_reasons", [])),
        "common_support_share_pct": audit.get("common_support", {}).get("share_pct"),
        "n_common_support_levels": audit.get("common_support", {}).get("n_levels"),
        "n_records": audit.get("root_estimand_crosscheck", {}).get("n_records_on_common_support"),
        "n_inference_clusters": audit.get("root_estimand_crosscheck", {}).get("n_inference_clusters"),
    }


def outcome_phase(reps: int = 60, seed: int = 20261112) -> dict:
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{os.getpid()}"
    run_marker_path = OUT / "outcome_run_marker.json"
    atomic_json(run_marker_path, {
        "status": "in_progress", "run_id": run_id, "started_at_utc": utc_now(),
        "phase": "outcome", "reps": int(reps), "seed": int(seed),
        "completion_condition": "summary, interval CSVs, mortality CSV and repaired outcome panel are finalized",
    })
    lock, lock_hash = strict.load_lock()
    validation_path = OUT / "preoutcome_repair_validation.json"
    if not validation_path.is_file():
        raise RuntimeError("Outcome join refused: repaired pre-outcome validation is absent")
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if (validation.get("outcome_field_loaded") is not False
            or validation.get("mapping_lock_sha256_unchanged") != lock_hash
            or not validation.get("strict_panel_reconstruction", {}).get("pass")):
        raise RuntimeError("Outcome join refused: pre-outcome validation failed or lock changed")

    repaired_panel = pd.read_csv(REPAIRED_PANEL_PRE, low_memory=False)
    strict_panel = pd.read_csv(STRICT_PANEL_OUTCOME, low_memory=False)
    outcomes = pd.read_csv(
        PRIVATE / "admissions.csv", usecols=["admissionid", "destination"],
        dtype={"admissionid": "Int64", "destination": "string"}, low_memory=False,
        encoding="utf-8", encoding_errors="replace",
    )
    if outcomes["admissionid"].isna().any() or outcomes["admissionid"].duplicated().any():
        raise ValueError("Admissions outcomes must have one unique admissionid")
    if strict_panel["admissionid"].duplicated().any():
        raise ValueError("Strict panel contains duplicate admission rows")
    for panel in (strict_panel, repaired_panel):
        panel["destination"] = panel["admissionid"].map(
            outcomes.set_index("admissionid")["destination"])
        destination = panel["destination"].astype("string").str.strip()
        known_destination = destination.notna() & destination.ne("")
        missing_tokens = destination.str.casefold().isin(
            {"unknown", "onbekend", "n/a", "na", "n.v.t.", "nvt", "<missing>"}
        )
        known_destination &= ~missing_tokens
        deaths = destination.fillna("").eq("Overleden").astype("int8")
        panel["icu_death"] = np.where(known_destination, deaths, np.nan)
        panel["icu_death"] = pd.to_numeric(panel["icu_death"], errors="coerce")
    atomic_gzip_csv(repaired_panel, REPAIRED_PANEL_OUTCOME)

    sys.path.insert(0, str(ROOT / "work" / "v2" / "audit"))
    from cohort_definition_audit import audit_v2, to_markdown
    sys.path.insert(0, str(ROOT / "work" / "v2"))
    from estimands import direct_contrast  # noqa: F401

    audit_results: dict[str, dict] = {"strict_reference": {}, "dictionary_unit_repair": {}}
    direct_results: dict[str, object] = {"strict_reference": {}, "dictionary_unit_repair": {}}
    for version, panel in (("strict_reference", strict_panel),
                           ("dictionary_unit_repair", repaired_panel)):
        for score_col, title in (("qsofa_main", "gcs_le_13"),
                                 ("qsofa_gcs_lt15", "gcs_lt_15_sensitivity")):
            result, direct = audit_frame(
                audit_v2, panel, score_col, title,
                {**OUTCOME_CONFIG, "reps": int(reps), "seed": int(seed)},
            )
            result["audit_config"] = {**OUTCOME_CONFIG, "reps": int(reps), "seed": int(seed)}
            audit_results[version][title] = result
            direct_results[version][title] = direct

    if not all(bool(r["root_estimand_crosscheck"]["crosscheck_passed"])
               for version in audit_results.values() for r in version.values()):
        raise AssertionError("At least one direct-estimand crosscheck failed")

    # Confirm strict inputs still reproduce the byte-frozen audit's numerical results.
    strict_baseline_checks = {}
    for title in ("gcs_le_13", "gcs_lt_15_sensitivity"):
        baseline = json.loads((STRICT_OUT / f"audit_{title}.json").read_text(encoding="utf-8"))
        replay = audit_results["strict_reference"][title]
        checks = {
            "estimate_pp_equal": baseline.get("stratified_rd_pp") == replay.get("stratified_rd_pp"),
            "normal_if_ci_equal": baseline.get("delta_ci_pp") == replay.get("delta_ci_pp"),
            "bootstrap_ci_equal": baseline.get("stratified_rd_ci_pp") == replay.get("stratified_rd_ci_pp"),
            "interval_status_equal": baseline.get("interval_status") == replay.get("interval_status"),
            "verdict_equal": baseline.get("verdict") == replay.get("verdict"),
        }
        strict_baseline_checks[title] = {**checks, "pass": all(checks.values())}
        if not strict_baseline_checks[title]["pass"]:
            raise AssertionError(f"Recomputed strict audit differs from frozen baseline: {title}")

    for title, result in audit_results["dictionary_unit_repair"].items():
        atomic_json(OUT / f"audit_{title}.json", result)
        mdpath = OUT / f"audit_{title}.md"
        temp_md = mdpath.with_name(mdpath.name + ".partial")
        temp_md.write_text(to_markdown(result), encoding="utf-8")
        temp_md.replace(mdpath)
        pd.DataFrame(result.get("per_level", [])).to_csv(OUT / f"audit_{title}_per_level.csv", index=False)
        atomic_json(OUT / f"audit_strict_reference_{title}.json", audit_results["strict_reference"][title])

    comparison_rows = []
    interval_rows = []
    for score_title in ("gcs_le_13", "gcs_lt_15_sensitivity"):
        for version in ("strict_reference", "dictionary_unit_repair"):
            audit = audit_results[version][score_title]
            version_label = "strict_row_units" if version == "strict_reference" else "dictionary_unit_repair"
            flat = flatten_ci_row(version_label, score_title, audit)
            comparison_rows.append(flat)
            interval_rows.append({"measurement_version": version_label, "score": score_title,
                                  "interval_type": "normal_influence_function", "estimate_pp": flat["estimate_pp"],
                                  "ci_lower_pp": flat["normal_if_ci_lower_pp"],
                                  "ci_upper_pp": flat["normal_if_ci_upper_pp"],
                                  "interval_status": flat["normal_if_ci_status"],
                                  "canonical_for_root_tables": True})
            interval_rows.append({"measurement_version": version_label, "score": score_title,
                                  "interval_type": "patient_cluster_percentile_bootstrap", "estimate_pp": flat["estimate_pp"],
                                  "ci_lower_pp": flat["bootstrap_percentile_ci_lower_pp"],
                                  "ci_upper_pp": flat["bootstrap_percentile_ci_upper_pp"],
                                  "interval_status": flat["bootstrap_ci_status"],
                                  "canonical_for_root_tables": False})
    pd.DataFrame(comparison_rows).to_csv(OUT / "amsterdam_unit_repair_interval_comparison.csv", index=False)
    pd.DataFrame(interval_rows).to_csv(OUT / "amsterdam_unit_repair_intervals.csv", index=False)

    completeness_rows = []
    preoutcome_comparison = validation["score_completeness_and_allocation_change"]
    for group_name in ("primary", "secondary_only"):
        group_result = preoutcome_comparison[group_name]
        for score_title, strict_key, repaired_key in (
                ("gcs_le_13", "strict_qsofa_main_distribution", "repaired_qsofa_main_distribution"),
                ("gcs_lt_15_sensitivity", "strict_qsofa_gcs_lt15_distribution",
                 "repaired_qsofa_gcs_lt15_distribution")):
            strict_distribution = group_result[strict_key]
            repaired_distribution = group_result[repaired_key]
            for score_value in range(4):
                strict_count = int(strict_distribution.get(str(score_value), 0))
                repaired_count = int(repaired_distribution.get(str(score_value), 0))
                completeness_rows.append({
                    "group": group_name,
                    "score_definition": score_title,
                    "admissions": int(group_result["admissions"]),
                    "strict_qsofa_complete": int(group_result["strict_qsofa_complete"]),
                    "repaired_qsofa_complete": int(group_result["repaired_qsofa_complete"]),
                    "additional_complete": int(group_result["additional_complete"]),
                    "qsofa_score": score_value,
                    "strict_score_admissions": strict_count,
                    "repaired_score_admissions": repaired_count,
                    "score_admissions_change": repaired_count - strict_count,
                })
    completeness_path = OUT / "amsterdam_unit_repair_completeness_comparison.csv"
    pd.DataFrame(completeness_rows).to_csv(completeness_path, index=False)

    mortality_by_score = []
    for (grp, score), frame in repaired_panel.dropna(subset=["icu_death", "qsofa_main"]).groupby(["grp", "qsofa_main"]):
        events = int(frame["icu_death"].sum())
        mortality_by_score.append({
            "group": "primary" if int(grp) == 0 else "secondary_only",
            "qsofa_main": int(score), "n_admissions": int(len(frame)),
            "n_patients": int(frame["patientid"].nunique()), "icu_mcu_discharge_deaths": events,
            "mortality_pct": round(100 * events / len(frame), 2) if len(frame) else None,
        })
    outcome_result = {
        "phase": "dictionary_unit_repair_outcome_linked_supplementary_application",
        "outcome_run_id": run_id,
        "mapping_lock_sha256_unchanged": lock_hash,
        "endpoint": "ICU/MCU discharge death (admissions.destination == Overleden)",
        "outcome_scope": "ICU/MCU discharge only; no in-hospital mortality; no pooling with main hospital endpoint",
        "row_unit": "ICU admission episode (admissionid)",
        "cluster_unit": "patientid",
        "outcome_categories": {str(k): int(v) for k, v in repaired_panel["destination"].fillna("<missing>").value_counts().items()},
        "outcome_flow_by_group_strict_reference": outcome_flow(strict_panel),
        "outcome_flow_by_group_dictionary_unit_repair": outcome_flow(repaired_panel),
        "mortality_by_qsofa_main_score_repaired": mortality_by_score,
        "audit": audit_results,
        "direct_estimand_crosscheck": {version: {score: result["root_estimand_crosscheck"]
                                                 for score, result in audits.items()}
                                       for version, audits in audit_results.items()},
        "strict_baseline_reproduction": strict_baseline_checks,
        "audit_config": {**OUTCOME_CONFIG, "reps": int(reps), "seed": int(seed)},
        "interval_policy": "Normal cluster influence-function interval is canonical for root tables; patient-cluster percentile bootstrap is reported separately as a sensitivity interval.",
        "repair_timing": validation["repair_timing"],
        "private_repaired_panel_path": str(REPAIRED_PANEL_OUTCOME),
        "private_raw_selected_event_cache_path": str(RAW_SELECTED_CACHE),
        "completeness_comparison_csv_path": str(completeness_path.relative_to(ROOT)),
    }
    summary_path = OUT / "amsterdam_dictionary_unit_repair_outcome_summary.json"
    mortality_path = OUT / "mortality_by_qsofa_score_repaired.csv"
    comparison_path = OUT / "amsterdam_unit_repair_interval_comparison.csv"
    intervals_path = OUT / "amsterdam_unit_repair_intervals.csv"
    atomic_json(summary_path, outcome_result)
    pd.DataFrame(mortality_by_score).to_csv(mortality_path, index=False)
    atomic_json(run_marker_path, {
        "status": "complete", "run_id": run_id, "completed_at_utc": utc_now(),
        "phase": "outcome", "reps": int(reps), "seed": int(seed),
        "summary_sha256": sha256(summary_path),
        "repaired_outcome_panel_sha256": sha256(REPAIRED_PANEL_OUTCOME),
        "interval_comparison_csv_sha256": sha256(comparison_path),
        "intervals_csv_sha256": sha256(intervals_path),
        "completeness_comparison_csv_sha256": sha256(completeness_path),
        "mortality_by_score_csv_sha256": sha256(mortality_path),
        "strict_baseline_reproduction_passed": all(
            check["pass"] for check in strict_baseline_checks.values()),
        "direct_estimand_crosschecks_passed": all(
            bool(result["root_estimand_crosscheck"]["crosscheck_passed"])
            for scores in audit_results.values() for result in scores.values()),
    })
    print(json.dumps({
        "summary_path": str((OUT / "amsterdam_dictionary_unit_repair_outcome_summary.json").relative_to(ROOT)),
        "strict_baseline_reproduction": strict_baseline_checks,
        "strict_outcome_flow": outcome_result["outcome_flow_by_group_strict_reference"],
        "repaired_outcome_flow": outcome_result["outcome_flow_by_group_dictionary_unit_repair"],
        "repaired_verdicts": {k: v["verdict"] for k, v in audit_results["dictionary_unit_repair"].items()},
    }, ensure_ascii=False, indent=2), flush=True)
    return outcome_result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["preoutcome", "outcome"], required=True)
    parser.add_argument("--reps", type=int, default=60)
    parser.add_argument("--seed", type=int, default=20261112)
    args = parser.parse_args()
    if args.phase == "preoutcome":
        preoutcome_phase()
    else:
        outcome_phase(args.reps, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

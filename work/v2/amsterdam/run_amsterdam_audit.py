"""Build a private Amsterdam qSOFA panel, then join its ICU-discharge endpoint."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LOCK_PATH = ROOT / "outputs" / "v2" / "amsterdam" / "mapping_lock.json"
LOCK_SCRIPT = ROOT / "work" / "v2" / "amsterdam" / "lock_amsterdam_mapping.py"
PRIVATE = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\private")
NUMERIC_ZIP = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\archive\numericitems.zip")
ADMISSIONS = PRIVATE / "admissions.csv"
LISTITEMS = PRIVATE / "listitems.csv"
PRIVATE_LISTITEMS = PRIVATE / "listitems_qsofa_nice.csv.gz"
PRIVATE_PANEL_PRE = PRIVATE / "qsofa_sepsis_icu_preoutcome.csv.gz"
PRIVATE_PANEL_OUTCOME = PRIVATE / "qsofa_sepsis_icu_outcome.csv.gz"
OUT = ROOT / "outputs" / "v2" / "amsterdam"
WORK = ROOT / "work" / "v2" / "amsterdam"
NUMERIC_PROGRESS = WORK / "numeric_scan_progress.json"

ADMISSION_COLUMNS_PRE = ["patientid", "admissionid", "location", "admittedat", "dischargedat"]
LISTITEM_COLUMNS = ["admissionid", "itemid", "valueid", "measuredat", "registeredby", "updatedat"]
NUMERIC_COLUMNS = ["admissionid", "itemid", "value", "unitid", "unit", "measuredat"]
PROVIDER_ORDER = [
    "ICV_Medisch Staflid",
    "ICV_Medisch",
    "ANES_Anesthesiologie",
    "ICV_Physician assistant",
    "ICH_Neurochirurgie",
    "ICV_IC-Verpleegkundig",
    "ICV_MC-Verpleegkundig",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


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


def load_lock() -> tuple[dict, str]:
    raw = LOCK_PATH.read_bytes()
    lock = json.loads(raw)
    if lock.get("lock_status") != "locked_before_outcome_join":
        raise RuntimeError("Mapping lock is missing or not marked as pre-outcome")
    if lock.get("reporting", {}).get("outcome_accessed_at_lock_time") is not False:
        raise RuntimeError("Mapping lock does not attest that the outcome was unopened")
    return lock, hashlib.sha256(raw).hexdigest()


def load_admissions_preoutcome() -> tuple[pd.DataFrame, dict]:
    frame = pd.read_csv(
        ADMISSIONS,
        usecols=ADMISSION_COLUMNS_PRE,
        dtype={"patientid": "Int64", "admissionid": "Int64", "location": "string"},
        low_memory=False, encoding="utf-8", encoding_errors="replace",
    )
    frame["admittedat"] = pd.to_numeric(frame["admittedat"], errors="coerce")
    frame["dischargedat"] = pd.to_numeric(frame["dischargedat"], errors="coerce")
    if frame["admissionid"].isna().any() or frame["admissionid"].duplicated().any():
        raise ValueError("Admissions must have a unique, nonmissing admissionid")
    if frame["patientid"].isna().any():
        raise ValueError("Patient ids are needed for patient-cluster inference")
    frame["is_icu"] = frame["location"].str.contains("IC", case=False, regex=False, na=False)
    location_counts = frame["location"].fillna("<missing>").value_counts(dropna=False).sort_index()
    metadata = {
        "admissions_rows": int(len(frame)),
        "admissionid_unique": True,
        "patientid_missing": int(frame["patientid"].isna().sum()),
        "location_values_n": int(frame["location"].nunique(dropna=False)),
        "location_counts": {str(key): int(value) for key, value in location_counts.items()},
        "icu_admissions": int(frame["is_icu"].sum()),
        "icu_patients": int(frame.loc[frame["is_icu"], "patientid"].nunique()),
        "admittedat_missing_icu": int(frame.loc[frame["is_icu"], "admittedat"].isna().sum()),
        "dischargedat_missing_icu": int(frame.loc[frame["is_icu"], "dischargedat"].isna().sum()),
    }
    return frame.loc[frame["is_icu"]].copy(), metadata


def selected_listitem_ids(lock: dict) -> set[int]:
    gcs_ids = {int(itemid) for part in lock["qsofa"]["gcs_valueid_to_component_score"].values()
               for itemid in part}
    return gcs_ids | {
        int(lock["analysis_target"]["primary_diagnosis_itemid"]),
        int(lock["analysis_target"]["secondary_diagnosis_itemid"]),
    }


def scan_listitems(icu_admissions: pd.DataFrame, itemids: set[int]) -> tuple[Path, dict]:
    admission_ids = set(icu_admissions["admissionid"].astype("int64").tolist())
    counters: Counter[str] = Counter()
    row_total = 0
    source_rows_total = 0
    header = True
    chunksize = 750_000
    dtype = {
        "admissionid": "int64",
        "itemid": "int32",
        "valueid": "float64",
        "measuredat": "float64",
        "registeredby": "string",
        "updatedat": "float64",
    }
    PRIVATE.mkdir(parents=True, exist_ok=True)
    temporary = PRIVATE_LISTITEMS.with_name(PRIVATE_LISTITEMS.name + ".partial")
    with gzip.open(temporary, "wt", encoding="utf-8", newline="", compresslevel=1) as dest:
        reader = pd.read_csv(
            LISTITEMS, usecols=LISTITEM_COLUMNS, dtype=dtype, chunksize=chunksize,
            low_memory=False, encoding="utf-8", encoding_errors="replace",
        )
        for number, chunk in enumerate(reader, start=1):
            source_rows_total += len(chunk)
            keep = chunk["itemid"].isin(itemids) & chunk["admissionid"].isin(admission_ids)
            selected = chunk.loc[keep, LISTITEM_COLUMNS]
            if not selected.empty:
                selected.to_csv(dest, index=False, header=header)
                header = False
                row_total += len(selected)
                counters.update(selected["itemid"].astype(str).value_counts().to_dict())
            if number % 8 == 0:
                print(f"[listitems] chunks={number} source_rows={source_rows_total} selected_rows={row_total}", flush=True)
    temporary.replace(PRIVATE_LISTITEMS)
    return PRIVATE_LISTITEMS, {
        "source_rows_scanned": int(source_rows_total),
        "selected_rows": int(row_total),
        "selected_rows_by_itemid": dict(sorted(counters.items(), key=lambda kv: int(kv[0]))),
        "filtered_to_icu_admissions": True,
        "filtered_itemids": sorted(itemids),
        "crc_checked": "source was read to EOF without parser error",
    }


def diagnosis_groups(listitems: pd.DataFrame, icu_admissions: pd.DataFrame, lock: dict) -> tuple[pd.DataFrame, dict]:
    primary_item = int(lock["analysis_target"]["primary_diagnosis_itemid"])
    secondary_item = int(lock["analysis_target"]["secondary_diagnosis_itemid"])
    primary_values = {int(row["valueid"]) for row in lock["analysis_target"]["primary_sepsis_values"]}
    secondary_values = {int(row["valueid"]) for row in lock["analysis_target"]["secondary_sepsis_values"]}
    diagnosis = listitems.loc[listitems["itemid"].isin([primary_item, secondary_item])].copy()
    diagnosis["valueid"] = pd.to_numeric(diagnosis["valueid"], errors="coerce")
    diagnosis = diagnosis.sort_values(
        ["admissionid", "itemid", "updatedat", "measuredat", "valueid"],
        ascending=[True, True, False, False, True], na_position="first", kind="mergesort",
    ).drop_duplicates(["admissionid", "itemid"], keep="first")
    values = diagnosis.pivot(index="admissionid", columns="itemid", values="valueid")
    if primary_item not in values.columns:
        values[primary_item] = np.nan
    if secondary_item not in values.columns:
        values[secondary_item] = np.nan
    p_match = values[primary_item].isin(primary_values)
    s_match = values[secondary_item].isin(secondary_values)
    targeted = values.loc[p_match | s_match, [primary_item, secondary_item]].copy()
    targeted["primary_match"] = p_match.loc[targeted.index]
    targeted["secondary_match"] = s_match.loc[targeted.index]
    targeted["both_positions_match"] = targeted["primary_match"] & targeted["secondary_match"]
    targeted["grp"] = np.where(targeted["primary_match"], 0, 1).astype("int8")
    targeted["primary_valueid"] = targeted[primary_item]
    targeted["secondary_valueid"] = targeted[secondary_item]
    targeted = targeted.reset_index().rename(columns={"index": "admissionid"})
    target_admissions = icu_admissions.merge(
        targeted[["admissionid", "grp", "primary_match", "secondary_match", "both_positions_match",
                  "primary_valueid", "secondary_valueid"]],
        on="admissionid", how="inner", validate="one_to_one",
    )
    pos_label = {int(row["valueid"]): str(row["label"])
                 for row in lock["analysis_target"]["primary_sepsis_values"]}
    sec_label = {int(row["valueid"]): str(row["label"])
                 for row in lock["analysis_target"]["secondary_sepsis_values"]}
    target_admissions["primary_diagnosis_label"] = target_admissions["primary_valueid"].map(pos_label)
    target_admissions["secondary_diagnosis_label"] = target_admissions["secondary_valueid"].map(sec_label)
    group_counts = target_admissions["grp"].value_counts().reindex([0, 1], fill_value=0)
    composition = []
    for field, group_label in (("primary_valueid", "primary"), ("secondary_valueid", "secondary")):
        for value, count in target_admissions[field].value_counts(dropna=True).items():
            code = int(value)
            label = (pos_label if group_label == "primary" else sec_label).get(code, "non-sepsis")
            composition.append({"field": group_label, "valueid": code, "label": label, "n": int(count)})
    validation = {
        "primary_group_n": int(group_counts.loc[0]),
        "secondary_only_group_n": int(group_counts.loc[1]),
        "primary_sepsis_matches": int(target_admissions["primary_match"].sum()),
        "secondary_sepsis_matches": int(target_admissions["secondary_match"].sum()),
        "both_positions_match": int(target_admissions["both_positions_match"].sum()),
        "primary_valueid_missing_in_target": int(target_admissions["primary_valueid"].isna().sum()),
        "diagnosis_code_composition": composition,
    }
    return target_admissions, validation


def _score_formula(expression: str, value: pd.Series) -> pd.Series:
    if expression == "valueid":
        return value
    if expression.startswith("valueid - "):
        return value - float(expression.split("valueid - ", 1)[1])
    if expression.endswith(" - valueid"):
        return float(expression.split(" - valueid", 1)[0]) - value
    raise ValueError(f"Unsupported GCS formula {expression!r}")


def calculate_gcs(listitems: pd.DataFrame, target_admissions: pd.DataFrame, lock: dict) -> tuple[pd.DataFrame, dict]:
    gcs_map = lock["qsofa"]["gcs_valueid_to_component_score"]
    id_component: dict[int, str] = {}
    id_formula: dict[int, str] = {}
    for component, mapping in gcs_map.items():
        for itemid, formula in mapping.items():
            id_component[int(itemid)] = component
            id_formula[int(itemid)] = formula
    target_ids = set(target_admissions["admissionid"].astype("int64"))
    gcs = listitems.loc[
        listitems["admissionid"].isin(target_ids) & listitems["itemid"].isin(id_component)
    ].copy()
    gcs["valueid"] = pd.to_numeric(gcs["valueid"], errors="coerce")
    gcs = gcs.dropna(subset=["valueid", "measuredat"])
    gcs["component"] = gcs["itemid"].map(id_component)
    gcs["component_score"] = np.nan
    for itemid, formula in id_formula.items():
        mask = gcs["itemid"].eq(itemid)
        if mask.any():
            gcs.loc[mask, "component_score"] = _score_formula(formula, gcs.loc[mask, "valueid"])
    max_allowed = {"eyes": 4, "motor": 6, "verbal": 5}
    min_allowed = {"eyes": 1, "motor": 1, "verbal": -100}
    valid = np.zeros(len(gcs), dtype=bool)
    for component in ("eyes", "motor", "verbal"):
        mask = gcs["component"].eq(component)
        score = gcs["component_score"]
        valid |= (mask & score.ge(min_allowed[component]) & score.le(max_allowed[component])).to_numpy()
    invalid_component_rows = int((~valid).sum())
    gcs = gcs.loc[valid].copy()

    lookup = target_admissions.set_index("admissionid")[["patientid", "admittedat", "dischargedat", "grp"]]
    gcs = gcs.join(lookup, on="admissionid", how="inner", validate="many_to_one")
    gcs["delta_ms"] = gcs["measuredat"] - gcs["admittedat"]
    in_window = gcs["delta_ms"].between(0, 86_400_000, inclusive="both")
    in_stay = gcs["dischargedat"].isna() | gcs["measuredat"].le(gcs["dischargedat"])
    gcs = gcs.loc[in_window & in_stay].copy()
    if gcs.empty:
        empty = pd.DataFrame(columns=["admissionid", "min_gcs", "gcs_observations"])
        return empty, {"gcs_rows_in_window": 0, "complete_gcs_times": 0, "invalid_component_rows": invalid_component_rows}

    pieces = {}
    provider_rank = {name: index + 1 for index, name in enumerate(PROVIDER_ORDER)}
    for component, short in (("eyes", "e"), ("motor", "m"), ("verbal", "v")):
        part = gcs.loc[gcs["component"].eq(component),
                       ["admissionid", "measuredat", "component_score", "registeredby", "updatedat"]].copy()
        part = part.rename(columns={"component_score": f"{short}_score", "registeredby": f"{short}_by",
                                    "updatedat": f"{short}_updatedat"})
        part[f"{short}_rank"] = part[f"{short}_by"].map(provider_rank).fillna(8).astype("int8")
        pieces[short] = part
    complete = pieces["e"].merge(pieces["m"], on=["admissionid", "measuredat"], how="inner")
    complete = complete.merge(pieces["v"], on=["admissionid", "measuredat"], how="inner")
    if complete.empty:
        empty = pd.DataFrame(columns=["admissionid", "min_gcs", "gcs_observations"])
        return empty, {"gcs_rows_in_window": int(len(gcs)), "complete_gcs_times": 0,
                       "invalid_component_rows": invalid_component_rows}
    order = ["admissionid", "measuredat", "e_rank", "m_rank", "v_rank",
             "e_updatedat", "m_updatedat", "v_updatedat", "e_score", "m_score", "v_score"]
    ascending = [True, True, True, True, True, False, False, False, False, False, False]
    complete = complete.sort_values(order, ascending=ascending, na_position="first", kind="mergesort")
    complete = complete.drop_duplicates(["admissionid", "measuredat"], keep="first")
    complete["v_used"] = complete["v_score"].clip(lower=1)
    complete["gcs_score"] = complete["e_score"] + complete["m_score"] + complete["v_used"]
    summary = complete.groupby("admissionid", as_index=False).agg(
        min_gcs=("gcs_score", "min"), gcs_observations=("gcs_score", "size"),
        gcs_time_first=("measuredat", "min"), gcs_time_last=("measuredat", "max"),
    )
    return summary, {
        "gcs_rows_in_window": int(len(gcs)),
        "complete_gcs_times": int(len(complete)),
        "invalid_component_rows": invalid_component_rows,
        "complete_gcs_admissions": int(summary["admissionid"].nunique()),
        "gcs_score_min_observed": float(complete["gcs_score"].min()),
        "gcs_score_max_observed": float(complete["gcs_score"].max()),
    }


def _unit_norm(value) -> str:
    if pd.isna(value):
        return ""
    return "".join(str(value).strip().casefold().replace("µ", "u").split())


def unit_ok(component: str, unit: str) -> bool:
    normalized = _unit_norm(unit)
    if component == "rr":
        return normalized in {"/min", "1/min", "min-1", "breaths/min", "breath/min", "breaths/minute",
                              "breath/minute", "bpm", "perminute"}
    return normalized in {"mmhg", "mm[hg]", "mmhg."}


def scan_numeric(icu_target: pd.DataFrame, lock: dict) -> tuple[pd.DataFrame, dict]:
    rr_ids = {int(row["itemid"]) for row in lock["qsofa"]["numeric_items"]["respiratory_rate"]}
    sbp_ids = {int(row["itemid"]) for row in lock["qsofa"]["numeric_items"]["systolic_blood_pressure"]}
    itemids = rr_ids | sbp_ids
    target_ids = set(icu_target["admissionid"].astype("int64"))
    admission_lookup = icu_target.set_index("admissionid")[["patientid", "admittedat", "dischargedat", "grp"]]
    rows_by_adm: dict[int, list[tuple[str, float]]] = defaultdict(list)
    rows_per_item: Counter[str] = Counter()
    rows_per_item_in_window: Counter[str] = Counter()
    bad_numeric: Counter[str] = Counter()
    bad_unit: Counter[str] = Counter()
    nonpositive: Counter[str] = Counter()
    unit_counts: dict[str, Counter[str]] = defaultdict(Counter)
    extrema: dict[str, list[float]] = defaultdict(list)
    numeric_scanned = 0
    matched = 0
    start = time.time()
    WORK.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(NUMERIC_ZIP) as archive:
        info = archive.getinfo("numericitems.csv")
        if info.file_size != 80_177_836_504 or info.CRC != 0x475539F6:
            raise RuntimeError("numericitems.csv size/CRC differs from the inspected source archive")
        atomic_json(NUMERIC_PROGRESS, {
            "status": "in_progress", "started_at_utc": utc_now(),
            "member": info.filename, "member_uncompressed_bytes": info.file_size,
            "member_crc32_expected": f"{info.CRC:08x}", "chunksize_rows": 1_000_000,
            "resume_note": "No safe row-offset restart cache existed; this run performs one full sequential pass.",
        })
        with archive.open(info, "r") as raw:
            reader = pd.read_csv(
                raw, usecols=NUMERIC_COLUMNS,
                dtype={"admissionid": "int64", "itemid": "int32", "value": "string",
                       "unitid": "string", "unit": "string", "measuredat": "float64"},
                chunksize=1_000_000, low_memory=False, encoding="utf-8", encoding_errors="replace",
            )
            for number, chunk in enumerate(reader, start=1):
                numeric_scanned += len(chunk)
                keep = chunk["itemid"].isin(itemids) & chunk["admissionid"].isin(target_ids)
                data = chunk.loc[keep, NUMERIC_COLUMNS].copy()
                if not data.empty:
                    matched += len(data)
                    data["component"] = np.where(data["itemid"].isin(rr_ids), "rr", "sbp")
                    data["unit_norm"] = data["unit"].map(_unit_norm)
                    data["value_num"] = pd.to_numeric(data["value"], errors="coerce")
                    for itemid, frame in data.groupby("itemid", sort=False):
                        key = str(int(itemid))
                        rows_per_item[key] += len(frame)
                        unit_counts[key].update(frame["unit"].fillna("<missing>").astype(str).value_counts().to_dict())
                        numeric = frame["value_num"].dropna()
                        if not numeric.empty:
                            extrema[key].extend([float(numeric.min()), float(numeric.max())])
                        bad_numeric[key] += int(frame["value_num"].isna().sum())
                        ok_units = frame.apply(lambda r: unit_ok(r["component"], r["unit"]), axis=1)
                        bad_unit[key] += int((~ok_units).sum())
                        nonpositive[key] += int((frame["value_num"].fillna(0) <= 0).sum())
                    adm_admitted = data["admissionid"].map(admission_lookup["admittedat"])
                    adm_discharged = data["admissionid"].map(admission_lookup["dischargedat"])
                    data["delta_ms"] = data["measuredat"] - adm_admitted
                    in_window = data["delta_ms"].between(0, 86_400_000, inclusive="both")
                    in_stay = adm_discharged.isna() | data["measuredat"].le(adm_discharged)
                    data = data.loc[in_window & in_stay].copy()
                    if not data.empty:
                        for itemid, frame in data.groupby("itemid", sort=False):
                            rows_per_item_in_window[str(int(itemid))] += len(frame)
                    data["unit_valid"] = [unit_ok(c, u) for c, u in zip(data["component"], data["unit"])]
                    data = data.loc[data["unit_valid"]].copy()
                    data = data.dropna(subset=["value_num"])
                    data = data.loc[data["value_num"] > 0]
                    for admissionid, frame in data.groupby("admissionid", sort=False):
                        rr = frame.loc[frame["component"].eq("rr"), "value_num"]
                        sbp = frame.loc[frame["component"].eq("sbp"), "value_num"]
                        if not rr.empty:
                            rows_by_adm[int(admissionid)].append(("rr", float(rr.max())))
                        if not sbp.empty:
                            rows_by_adm[int(admissionid)].append(("sbp", float(sbp.min())))
                if number % 8 == 0:
                    elapsed = round(time.time() - start, 1)
                    print(f"[numericitems] chunks={number} rows={numeric_scanned} matched={matched} elapsed_s={elapsed}",
                          flush=True)
                    atomic_json(NUMERIC_PROGRESS, {
                        "status": "in_progress", "updated_at_utc": utc_now(),
                        "member": info.filename, "member_uncompressed_bytes": info.file_size,
                        "member_crc32_expected": f"{info.CRC:08x}", "chunks_completed": number,
                        "rows_scanned": numeric_scanned, "matched_target_item_rows": matched,
                        "elapsed_seconds": elapsed,
                    })
        # ZipExtFile validates the inner CRC when the full member has been read.
    records = []
    for admissionid in sorted(target_ids):
        readings = rows_by_adm.get(admissionid, [])
        rr_values = [value for component, value in readings if component == "rr"]
        sbp_values = [value for component, value in readings if component == "sbp"]
        records.append({
            "admissionid": admissionid,
            "rr_max": max(rr_values) if rr_values else np.nan,
            "rr_observed": bool(rr_values),
            "sbp_min": min(sbp_values) if sbp_values else np.nan,
            "sbp_observed": bool(sbp_values),
        })
    summary = pd.DataFrame.from_records(records)
    unit_summary = {itemid: dict(sorted(counts.items())) for itemid, counts in unit_counts.items()}
    extrema_summary = {itemid: {"min": min(vals), "max": max(vals)} for itemid, vals in extrema.items() if vals}
    validation = {
        "numeric_member": info.filename,
        "numeric_member_uncompressed_bytes": info.file_size,
        "numeric_member_crc32": f"{info.CRC:08x}",
        "numeric_rows_scanned": int(numeric_scanned),
        "matched_target_item_rows_before_window": int(matched),
        "rows_by_itemid_before_window": dict(sorted(rows_per_item.items(), key=lambda kv: int(kv[0]))),
        "rows_by_itemid_in_window_before_unit_check": dict(sorted(rows_per_item_in_window.items(), key=lambda kv: int(kv[0]))),
        "non_numeric_by_itemid": dict(sorted(bad_numeric.items(), key=lambda kv: int(kv[0]))),
        "unexpected_unit_by_itemid": dict(sorted(bad_unit.items(), key=lambda kv: int(kv[0]))),
        "nonpositive_by_itemid": dict(sorted(nonpositive.items(), key=lambda kv: int(kv[0]))),
        "unit_counts_by_itemid": unit_summary,
        "observed_extrema_by_itemid": extrema_summary,
        "rr_observed_admissions": int(summary["rr_observed"].sum()),
        "sbp_observed_admissions": int(summary["sbp_observed"].sum()),
        "zip_member_crc_checked": True,
    }
    atomic_json(NUMERIC_PROGRESS, {
        "status": "complete", "completed_at_utc": utc_now(),
        "member": info.filename, "member_uncompressed_bytes": info.file_size,
        "member_crc32_expected": f"{info.CRC:08x}", "member_crc32_verified": f"{info.CRC:08x}",
        "chunks_completed": number, "rows_scanned": numeric_scanned,
        "matched_target_item_rows": matched, "elapsed_seconds": round(time.time() - start, 1),
        "crc_verified_by": "zipfile.ZipExtFile full-member EOF read",
    })
    return summary, validation


def preoutcome_phase() -> dict:
    lock, lock_hash = load_lock()
    OUT.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    icu_admissions, admissions_validation = load_admissions_preoutcome()
    itemids = selected_listitem_ids(lock)
    listitems_path, listitems_validation = scan_listitems(icu_admissions, itemids)
    selected = pd.read_csv(
        listitems_path,
        dtype={"admissionid": "int64", "itemid": "int32", "valueid": "float64",
               "measuredat": "float64", "registeredby": "string", "updatedat": "float64"},
        low_memory=False,
    )
    target_admissions, diagnosis_validation = diagnosis_groups(selected, icu_admissions, lock)
    gcs_summary, gcs_validation = calculate_gcs(selected, target_admissions, lock)
    numeric_summary, numeric_validation = scan_numeric(target_admissions, lock)
    panel = target_admissions.merge(gcs_summary, on="admissionid", how="left", validate="one_to_one")
    panel = panel.merge(numeric_summary, on="admissionid", how="left", validate="one_to_one")
    rr_threshold = 22
    sbp_threshold = 100
    gcs_main = 13
    gcs_sensitivity = 15
    panel["rr_point"] = panel["rr_observed"].fillna(False) & panel["rr_max"].ge(rr_threshold)
    panel["sbp_point"] = panel["sbp_observed"].fillna(False) & panel["sbp_min"].le(sbp_threshold)
    panel["gcs_main_point"] = panel["min_gcs"].le(gcs_main)
    panel["gcs_sensitivity_point"] = panel["min_gcs"].lt(gcs_sensitivity)
    panel["qsofa_complete"] = (panel["rr_observed"].fillna(False) & panel["sbp_observed"].fillna(False)
                               & panel["min_gcs"].notna())
    panel["qsofa_main"] = np.where(
        panel["qsofa_complete"],
        panel["rr_point"].astype("int8") + panel["sbp_point"].astype("int8") + panel["gcs_main_point"].astype("int8"),
        np.nan,
    )
    panel["qsofa_gcs_lt15"] = np.where(
        panel["qsofa_complete"],
        panel["rr_point"].astype("int8") + panel["sbp_point"].astype("int8")
        + panel["gcs_sensitivity_point"].astype("int8"),
        np.nan,
    )
    # Private row-level records are kept only on F:.
    atomic_gzip_csv(panel, PRIVATE_PANEL_PRE)
    for_group = panel.groupby("grp", dropna=False)
    score_dist = {}
    for grp, frame in for_group:
        name = "primary" if int(grp) == 0 else "secondary_only"
        score_dist[name] = {
            "admissions": int(len(frame)),
            "patients": int(frame["patientid"].nunique()),
            "qsofa_complete": int(frame["qsofa_complete"].sum()),
            "qsofa_main_distribution": {str(int(k)): int(v) for k, v in frame["qsofa_main"].dropna().value_counts().sort_index().items()},
            "qsofa_gcs_lt15_distribution": {str(int(k)): int(v) for k, v in frame["qsofa_gcs_lt15"].dropna().value_counts().sort_index().items()},
        }
    result = {
        "phase": "preoutcome_field_validation",
        "outcome_field_loaded": False,
        "mapping_lock_sha256": lock_hash,
        "record_unit": lock["analysis_target"]["record_unit"],
        "patient_cluster_field": lock["analysis_target"]["patient_cluster_field"],
        "admissions_validation": admissions_validation,
        "listitems_validation": listitems_validation,
        "diagnosis_validation": diagnosis_validation,
        "gcs_validation": gcs_validation,
        "numeric_validation": numeric_validation,
        "qsofa_preoutcome_summary_by_group": score_dist,
        "private_panel_path": str(PRIVATE_PANEL_PRE),
        "private_panel_rows": int(len(panel)),
    }
    outpath = OUT / "preoutcome_field_validation.json"
    atomic_json(outpath, result)
    print(json.dumps({"validation_path": str(outpath.relative_to(ROOT)),
                      "panel_rows": len(panel), "diagnosis_groups": score_dist,
                      "numeric_rows_scanned": numeric_validation["numeric_rows_scanned"],
                      "numeric_crc_checked": numeric_validation["zip_member_crc_checked"],
                      "lock_sha256": lock_hash}, ensure_ascii=False, indent=2, default=str))
    return result


def outcome_phase(reps: int = 60, seed: int = 20261112) -> dict:
    lock, lock_hash = load_lock()
    validation_path = OUT / "preoutcome_field_validation.json"
    if not validation_path.exists():
        raise RuntimeError("Outcome join refused: pre-outcome field validation is absent")
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if validation.get("outcome_field_loaded") is not False or validation.get("mapping_lock_sha256") != lock_hash:
        raise RuntimeError("Outcome join refused: field validation does not match the current frozen mapping lock")
    panel = pd.read_csv(PRIVATE_PANEL_PRE, low_memory=False)
    outcomes = pd.read_csv(ADMISSIONS, usecols=["admissionid", "destination"],
                           dtype={"admissionid": "Int64", "destination": "string"}, low_memory=False,
                           encoding="utf-8", encoding_errors="replace")
    if outcomes["admissionid"].isna().any() or outcomes["admissionid"].duplicated().any():
        raise ValueError("Outcome table must have one row per admissionid")
    panel = panel.merge(outcomes, on="admissionid", how="left", validate="one_to_one")
    destination = panel["destination"].str.strip()
    known_destination = destination.notna() & destination.ne("")
    death_value = destination.fillna("").eq("Overleden").astype("int8")
    panel["icu_death"] = np.where(known_destination, death_value, np.nan)
    panel["icu_death"] = pd.to_numeric(panel["icu_death"], errors="coerce")
    atomic_gzip_csv(panel, PRIVATE_PANEL_OUTCOME)

    outcome_flow = {}
    for grp, frame in panel.groupby("grp", dropna=False):
        name = "primary" if int(grp) == 0 else "secondary_only"
        observed = frame["icu_death"].dropna()
        outcome_flow[name] = {
            "admissions": int(len(frame)),
            "patients": int(frame["patientid"].nunique()),
            "outcome_observed": int(len(observed)),
            "outcome_missing": int(frame["icu_death"].isna().sum()),
            "icu_mcu_discharge_deaths": int((observed == 1).sum()),
            "icu_mcu_discharge_deaths_pct": round(100 * float(observed.mean()), 2) if len(observed) else None,
        }

    sys.path.insert(0, str(ROOT / "work" / "v2" / "audit"))
    from cohort_definition_audit import audit_v2, to_markdown
    sys.path.insert(0, str(ROOT / "work" / "v2"))
    from estimands import direct_contrast

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
    }
    config = {"reps": int(reps), "seed": int(seed), "min_clusters": 20, "min_events": 10,
              "min_level_n": 20, "min_arm_n": 10, "min_usable_bootstrap": 20,
              "model_check": False}
    audit_results = {}
    for score_col, title in (("qsofa_main", "gcs_le_13"), ("qsofa_gcs_lt15", "gcs_lt_15_sensitivity")):
        frame = panel[["patientid", "grp", "icu_death", score_col]].rename(columns={score_col: "score"})
        result = audit_v2(
            frame, score_col="score", outcome_col="icu_death", group_col="grp", pid_col="patientid",
            metadata={**metadata, "score_col": title}, config=config,
        )
        complete = frame.dropna(subset=["patientid", "grp", "icu_death", "score"]).rename(
            columns={"patientid": "pid", "icu_death": "y"}
        )
        direct = direct_contrast(complete)
        if result.get("stratified_rd_pp") is not None and not np.isclose(
                float(result["stratified_rd_pp"]), 100 * direct.estimate, atol=0.011):
            raise AssertionError(f"audit_v2 and root direct_contrast disagree for {title}")
        if result.get("delta_se_pp") is not None and not np.isclose(
                float(result["delta_se_pp"]), 100 * direct.se, atol=0.011):
            raise AssertionError(f"audit_v2 and root direct_contrast SE disagree for {title}")
        result["root_estimand_crosscheck"] = {
            "estimator": "work/v2/estimands.py::direct_contrast",
            "estimate_pp": 100 * direct.estimate,
            "numerical_cluster_se_pp": 100 * direct.se,
            "difference_from_audit_estimate_pp": (None if result.get("stratified_rd_pp") is None else
                                                   100 * direct.estimate - result["stratified_rd_pp"]),
            "n_records_on_common_support": direct.n_records,
            "n_supported_patients": direct.n_patients,
            "n_inference_clusters": direct.n_inference_clusters,
            "common_support_share": direct.support_share,
            "crosscheck_passed": True,
        }
        audit_results[title] = result
        atomic_json(OUT / f"audit_{title}.json", result)
        mdpath = OUT / f"audit_{title}.md"
        temp_md = mdpath.with_name(mdpath.name + ".partial")
        temp_md.write_text(to_markdown(result), encoding="utf-8")
        temp_md.replace(mdpath)
        pd.DataFrame(result.get("per_level", [])).to_csv(OUT / f"audit_{title}_per_level.csv", index=False)

    mortality_by_score = []
    for (grp, score), frame in panel.dropna(subset=["icu_death", "qsofa_main"]).groupby(["grp", "qsofa_main"]):
        events = int(frame["icu_death"].sum())
        mortality_by_score.append({
            "group": "primary" if int(grp) == 0 else "secondary_only",
            "qsofa_main": int(score),
            "n_admissions": int(len(frame)),
            "n_patients": int(frame["patientid"].nunique()),
            "icu_mcu_discharge_deaths": events,
            "mortality_pct": round(100 * events / len(frame), 2) if len(frame) else None,
        })
    result = {
        "phase": "outcome_linked_supplementary_application",
        "mapping_lock_sha256": lock_hash,
        "endpoint": "ICU/MCU discharge death (admissions.destination == Overleden)",
        "outcome_scope": "ICU/MCU discharge only; no in-hospital mortality; no pooling with the main hospital endpoint",
        "row_unit": "ICU admission episode (admissionid)",
        "cluster_unit": "patientid",
        "outcome_categories": {str(k): int(v) for k, v in panel["destination"].fillna("<missing>").value_counts().items()},
        "outcome_flow_by_group": outcome_flow,
        "mortality_by_qsofa_main_score": mortality_by_score,
        "audit": {key: {"verdict": value.get("verdict"), "stratified_rd_pp": value.get("stratified_rd_pp"),
                        "stratified_rd_ci_pp": value.get("stratified_rd_ci_pp"),
                        "interval_status": value.get("interval_status"), "per_level": value.get("per_level"),
                        "flow": value.get("flow"), "target_support_status": value.get("target_support_status"),
                        "common_support": value.get("common_support"),
                        "refusal_reasons": value.get("refusal_reasons"),
                        "root_estimand_crosscheck": value.get("root_estimand_crosscheck")}
                  for key, value in audit_results.items()},
        "audit_config": config,
        "private_panel_path": str(PRIVATE_PANEL_OUTCOME),
    }
    outpath = OUT / "amsterdam_qsofa_outcome_summary.json"
    atomic_json(outpath, result)
    pd.DataFrame(mortality_by_score).to_csv(OUT / "mortality_by_qsofa_score.csv", index=False)
    print(json.dumps({"summary_path": str(outpath.relative_to(ROOT)), "outcome_flow": outcome_flow,
                      "audit_verdicts": {key: value.get("verdict") for key, value in audit_results.items()}},
                     ensure_ascii=False, indent=2, default=str))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["preoutcome", "outcome"], required=True)
    parser.add_argument("--reps", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20261112)
    args = parser.parse_args()
    if args.phase == "preoutcome":
        preoutcome_phase()
    else:
        outcome_phase(reps=args.reps, seed=args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

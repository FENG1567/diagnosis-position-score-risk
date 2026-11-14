#!/usr/bin/env python3
"""Rebuild the MIMIC-III admission-level score panel from the release ZIP.

This adapter uses the MIMIC-IV v2 cohort, observation-window, and score reducers.
It canonicalizes MIMIC-III CareVue/MetaVision itemids before using those reducers.
The large CHARTEVENTS and LABEVENTS passes require the explicit
``--allow-event-scan`` switch so they cannot start before the coordinated IV run
has finished.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "mimic"))
import m58_mimic_rebuild as common  # noqa: E402

VERSION = "m58-mimic-iii-rebuild-1.3.0"
ZIP_DEFAULT = Path(r"D:\数据库集合\mimic3\mimic-iii-clinical-database-1.4.zip")
PREFIX = "mimic-iii-clinical-database-1.4/"
OUT_DEFAULT = WORKSPACE / "outputs" / "v2" / "mimic3"
PRIVATE_DEFAULT = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\mimic3")

MEMBERS = {
    "diagnoses": PREFIX + "DIAGNOSES_ICD.csv.gz",
    "admissions": PREFIX + "ADMISSIONS.csv.gz",
    "patients": PREFIX + "PATIENTS.csv.gz",
    "icustays": PREFIX + "ICUSTAYS.csv.gz",
    "chartevents": PREFIX + "CHARTEVENTS.csv.gz",
    "labevents": PREFIX + "LABEVENTS.csv.gz",
    "d_items": PREFIX + "D_ITEMS.csv.gz",
    "d_labitems": PREFIX + "D_LABITEMS.csv.gz",
}

# MIMIC-III CareVue/MetaVision ids mapped to the MIMIC-IV reducer's canonical
# item ids. Manual and non-invasive pressure items stay in the NIBP channel.
CHART_MAP = {
    6: 220050, 51: 220050, 6701: 220050,
    220050: 220050,
    220051: 220051,
    442: 220179, 455: 220179,
    220179: 220179,
    220180: 220180,
    8364: 220051, 8368: 220051, 8555: 220051,
    8440: 220180, 8441: 220180,
    618: 220210, 220210: 220210,
    224690: 220210,  # MIMIC-III RR (Total); MIMIC-IV uses canonical item 220210.
    211: 220045, 220045: 220045,
    678: 223761, 223761: 223761,
    676: 223762, 677: 223762, 223762: 223762,
    198: 198,  # CareVue GCS total; reduced directly, never treated as a component.
    220739: 220739, 223900: 223900, 223901: 223901,
}
CHART_IDS = set(CHART_MAP)
GCS_TOTAL_ID = 198
LAB_IDS = {51006, 51300, 51301, 51144}
FILTER_CACHE_SCHEMA = "mimic-iii-first-icu-filter-v3"
CHART_CHUNK_SIZE = 1_500_000
LAB_CHUNK_SIZE = 1_500_000


def _code_sha256() -> str:
    payload = f"{common._sha256(Path(__file__))}:{common._sha256(Path(common.__file__))}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _config() -> dict:
    return {
        "version": VERSION,
        "filter_cache_schema": FILTER_CACHE_SCHEMA,
        "chart_map": CHART_MAP,
        "lab_itemids": sorted(LAB_IDS),
        "chart_window": "[earliest ICU intime, min(intime+24h, valid dischtime, valid inpatient deathtime)]",
        "lab_window": "[earliest ICU intime-6h, min(intime+24h, valid dischtime, valid inpatient deathtime)]",
        "bands_unit_filter": {"51144": ["%", "pct", "percent", "percentage", "per cent"]},
        "common_config_sha256": common._config_fingerprint(),
        "age": "integer age at ICU intime from DOB month/day; MIMIC-III shifted age >200 is top-coded to 90",
    }


def _config_sha256() -> str:
    return hashlib.sha256(json.dumps(_config(), sort_keys=True, default=str,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _source_fingerprint(zip_path: Path, member: str) -> dict:
    stat = zip_path.stat()
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(member)
    return {"zip_size": stat.st_size, "zip_mtime_ns": stat.st_mtime_ns,
            "member": member, "member_crc32": f"{info.CRC:08x}",
            "member_zip_size": info.compress_size, "member_payload_size": info.file_size}


def _manifest_path(private_dir: Path) -> Path:
    return private_dir / "mimic_iii_v2_index_manifest.json"


def _cache_manifest_path(cache: Path) -> Path:
    return cache.with_suffix(cache.suffix + ".json")


def _write_cache_manifest(cache: Path, zip_path: Path, member: str,
                          index_hash: str, row_count: int) -> None:
    manifest = {
        "schema": FILTER_CACHE_SCHEMA, "version": VERSION,
        "source": _source_fingerprint(zip_path, member),
        "archive_fingerprint": common._archive_fingerprint(zip_path),
        "index_sha256": index_hash, "config_sha256": _config_sha256(),
        "code_sha256": _code_sha256(), "cache_name": cache.name,
        "cache_size": cache.stat().st_size, "cache_sha256": common._sha256(cache),
        "rows": int(row_count),
    }
    common._write_json(_cache_manifest_path(cache), manifest)


def _cache_is_valid(cache: Path, zip_path: Path, member: str, index_hash: str) -> bool:
    manifest_path = _cache_manifest_path(cache)
    if not cache.exists() or not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return (manifest.get("schema") == FILTER_CACHE_SCHEMA
                and manifest.get("source") == _source_fingerprint(zip_path, member)
                and manifest.get("archive_fingerprint") == common._archive_fingerprint(zip_path)
                and manifest.get("index_sha256") == index_hash
                and manifest.get("config_sha256") == _config_sha256()
                and manifest.get("code_sha256") == _code_sha256()
                and manifest.get("cache_size") == cache.stat().st_size
                and manifest.get("cache_sha256") == common._sha256(cache))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        return False


def _index_cache_valid(private_dir: Path, zip_path: Path) -> bool:
    path = private_dir / "mimic_iii_v2_index.csv.gz"
    manifest_path = _manifest_path(private_dir)
    if not path.exists() or not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return (manifest.get("version") == VERSION
                and manifest.get("archive_fingerprint") == common._archive_fingerprint(zip_path)
                and manifest.get("code_sha256") == _code_sha256()
                and manifest.get("config_sha256") == _config_sha256()
                and manifest.get("index_size") == path.stat().st_size
                and manifest.get("index_sha256") == common._sha256(path))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        return False


def _read_index_cache(private_dir: Path) -> tuple[pd.DataFrame, dict, dict]:
    path = private_dir / "mimic_iii_v2_index.csv.gz"
    manifest = json.loads(_manifest_path(private_dir).read_text(encoding="utf-8"))
    date_cols = ["admittime", "dischtime", "deathtime", "intime", "outtime",
                 "chart_window_start", "chart_window_end", "lab_window_start", "lab_window_end"]
    index = pd.read_csv(path, compression="gzip", parse_dates=date_cols, low_memory=False)
    return index, manifest["index_stats"], manifest["dictionary_audit"]


def _write_index_cache(index: pd.DataFrame, index_stats: dict, dict_stats: dict,
                       private_dir: Path, zip_path: Path) -> dict:
    private_dir.mkdir(parents=True, exist_ok=True)
    path = private_dir / "mimic_iii_v2_index.csv.gz"
    tmp = path.with_name(path.name + ".partial")
    index.to_csv(tmp, index=False, compression="gzip")
    os.replace(tmp, path)
    manifest = {
        "version": VERSION, "source_zip": str(zip_path),
        "source_zip_size": zip_path.stat().st_size,
        "archive_fingerprint": common._archive_fingerprint(zip_path),
        "code_sha256": _code_sha256(), "config_sha256": _config_sha256(),
        "index_rows": len(index), "index_size": path.stat().st_size,
        "index_sha256": common._sha256(path), "index_filter_sha256": common._index_hash(index),
        "index_stats": index_stats, "diagnosis_seq_num_quality": index_stats.get("diagnosis_seq_num_quality"),
        "diagnosis_group_quality": index_stats.get("diagnosis_group_quality"),
        "dictionary_audit": dict_stats,
    }
    common._write_json(_manifest_path(private_dir), manifest)
    return manifest


def _age_from_dob(dob: pd.Series, intime: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute calendar age without converting old/shifted DOBs to nanosecond dates."""
    text = dob.astype("string").str.strip()
    parts = text.str.extract(r"^(\d{4})-(\d{2})-(\d{2})")
    birth_year = pd.to_numeric(parts[0], errors="coerce")
    birth_month = pd.to_numeric(parts[1], errors="coerce")
    birth_day = pd.to_numeric(parts[2], errors="coerce")
    valid = intime.notna() & birth_year.notna() & birth_month.notna() & birth_day.notna()
    not_yet_birthday = (intime.dt.month.lt(birth_month)
                        | (intime.dt.month.eq(birth_month) & intime.dt.day.lt(birth_day)))
    age = (intime.dt.year - birth_year - not_yet_birthday.astype("float64")).where(valid)
    topcoded = age.gt(200).fillna(False)
    age = age.mask(topcoded, 90.0)
    age = age.where(age.between(0, 110))
    exact = age.notna() & ~topcoded
    return age, topcoded.astype("Int8"), exact.astype("Int8")


def _definition_code_mask(codes: pd.Series, spec: dict, definition: str) -> pd.Series:
    """Return one MIMIC-III ICD-9 phenotype definition's matching rows."""
    if definition == "broad":
        exact = spec.get("main9_exact", ())
        return (codes.isin(exact) if exact else
                common._prefix_hit(codes, tuple(spec.get("main9", ()))))
    if definition == "narrow":
        return common._prefix_hit(codes, tuple(spec.get("narrow9", ())))
    if definition == "legacy":
        if "legacy9_prefix" in spec:
            return common._prefix_hit(codes, tuple(spec["legacy9_prefix"]))
        return common._prefix_hit(codes, tuple(spec.get("legacy9", ())))
    raise ValueError(f"unknown MIMIC-III diagnosis definition: {definition}")


def _memberships_with_sequence_quality(dx: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Keep matching unranked diagnoses and mark unresolved primary status unknown.

    The temporary sentinel only lets the shared membership reducer retain an
    unranked-only admission. It is removed from every exported position field.
    A ranked secondary diagnosis cannot establish group 1 when an unranked
    matching diagnosis could have been the principal diagnosis.
    """
    sequence = pd.to_numeric(dx["seq_num"], errors="coerce")
    valid_rank = sequence.gt(0) & np.isclose(sequence.fillna(0) % 1, 0)
    rank1 = valid_rank & sequence.eq(1)
    normalized = dx.copy()
    normalized["seq_num"] = sequence.where(valid_rank, 2_147_483_647)
    memberships = common.build_memberships(normalized)

    codes = common._normalized_codes(dx)
    metadata: dict[str, list[pd.DataFrame]] = {}
    audit: dict[str, dict] = {}
    keys = ["subject_id", "hadm_id"]
    for disease, spec in common.DISEASES.items():
        definitions = ["broad", "legacy"]
        if "narrow9" in spec:
            definitions.append("narrow")
        audit[disease] = {}
        for definition in definitions:
            mask = _definition_code_mask(codes, spec, definition)
            matched = dx.loc[mask, keys].copy()
            matched["valid_rank"] = valid_rank.loc[mask].to_numpy()
            matched["rank1"] = rank1.loc[mask].to_numpy()
            grouped = (matched.groupby(keys, as_index=False, sort=False)
                       .agg(match_count=("valid_rank", "size"),
                            valid_rank_match_count=("valid_rank", "sum"),
                            rank1_match_count=("rank1", "sum")))
            grouped["unranked_match_count"] = (grouped["match_count"]
                                                   - grouped["valid_rank_match_count"])
            grouped["disease"] = disease
            rename = {
                "match_count": f"match_count_{definition}",
                "valid_rank_match_count": f"valid_rank_match_count_{definition}",
                "rank1_match_count": f"rank1_match_count_{definition}",
                "unranked_match_count": f"unranked_match_count_{definition}",
            }
            metadata.setdefault(definition, []).append(grouped.rename(columns=rename))
            audit[disease][definition] = {
                "matching_diagnosis_rows": int(mask.sum()),
                "matching_unranked_diagnosis_rows": int((mask & ~valid_rank).sum()),
                "matching_admissions": int(len(grouped)),
                "admissions_with_unranked_match": int(grouped["unranked_match_count"].gt(0).sum()),
                "admissions_with_unranked_match_and_no_seq1": int(
                    (grouped["unranked_match_count"].gt(0)
                     & grouped["rank1_match_count"].eq(0)).sum()),
            }

    rank_metadata = None
    for frames in metadata.values():
        definition_frame = pd.concat(frames, ignore_index=True)
        if rank_metadata is None:
            rank_metadata = definition_frame
        else:
            rank_metadata = rank_metadata.merge(definition_frame, on=[*keys, "disease"],
                                                how="outer", validate="one_to_one")
    memberships = memberships.merge(rank_metadata, on=[*keys, "disease"], how="left",
                                    validate="one_to_one")
    definition_columns = {
        "broad": ("pos_broad", "broad_inclusion", "grp"),
        "narrow": ("pos_narrow", "narrow_inclusion", "grp_narrow"),
        "legacy": ("pos_legacy", "legacy_broad_inclusion", "grp_legacy_broad"),
    }
    for definition, (position, inclusion, group) in definition_columns.items():
        valid_count = pd.to_numeric(
            memberships[f"valid_rank_match_count_{definition}"], errors="coerce").fillna(0)
        unranked_count = pd.to_numeric(
            memberships[f"unranked_match_count_{definition}"], errors="coerce").fillna(0)
        rank1_count = pd.to_numeric(
            memberships[f"rank1_match_count_{definition}"], errors="coerce").fillna(0)
        matches = pd.to_numeric(memberships[f"match_count_{definition}"], errors="coerce").fillna(0)
        memberships[position] = pd.to_numeric(memberships[position], errors="coerce").where(
            valid_count.gt(0))
        memberships[inclusion] = matches.gt(0).astype("Int8")
        resolved_group = pd.Series(pd.NA, index=memberships.index, dtype="Int8")
        resolved_group.loc[rank1_count.gt(0)] = 0
        resolved_group.loc[valid_count.gt(0) & unranked_count.eq(0)
                           & rank1_count.eq(0)] = 1
        memberships[group] = resolved_group
    memberships["pos"] = memberships["pos_broad"]
    memberships["grp_broad"] = memberships["grp"]
    return memberships, audit


def _audit_small_dictionaries(zip_path: Path, private_dir: Path) -> dict:
    items = common._csv_member(zip_path, MEMBERS["d_items"],
                               usecols=["ITEMID", "LABEL", "CATEGORY", "UNITNAME", "LINKSTO"])
    items.columns = items.columns.str.lower()
    chart_audit = items[items["itemid"].isin(CHART_IDS)].copy()
    chart_audit.to_csv(private_dir / "mimic_iii_v2_chart_dictionary_audit.csv", index=False)
    labs = common._csv_member(zip_path, MEMBERS["d_labitems"],
                              usecols=["ITEMID", "LABEL", "FLUID", "CATEGORY"])
    labs.columns = labs.columns.str.lower()
    lab_audit = labs[labs["itemid"].isin(LAB_IDS)
                     | labs["label"].fillna("").astype("string").str.contains(
                         r"band|pco2|carbon dioxide", case=False, regex=True)].copy()
    lab_audit.to_csv(private_dir / "mimic_iii_v2_lab_dictionary_audit.csv", index=False)
    return {
        "chart_dictionary_rows_audited": int(len(chart_audit)),
        "lab_dictionary_rows_audited": int(len(lab_audit)),
        "bands_itemid_51144_present": bool(labs["itemid"].eq(51144).any()),
        "unused_pco2_candidate_itemids": [int(x) for x in labs.loc[
            labs["label"].fillna("").astype("string").str.contains(r"pco2|carbon dioxide", case=False, regex=True),
            "itemid"].dropna().unique()],
    }


def _copy_dictionary_audits(private_dir: Path, out_dir: Path) -> None:
    import shutil
    for name in ("mimic_iii_v2_chart_dictionary_audit.csv", "mimic_iii_v2_lab_dictionary_audit.csv"):
        src = private_dir / name
        if src.exists():
            shutil.copy2(src, out_dir / name)


def build_index(zip_path: Path, private_dir: Path) -> tuple[pd.DataFrame, dict, dict]:
    """Build adult first-ICU rows from the small MIMIC-III tables."""
    dx = common._csv_member(zip_path, MEMBERS["diagnoses"],
                            dtype={"ICD9_CODE": "string"},
                            usecols=["SUBJECT_ID", "HADM_ID", "SEQ_NUM", "ICD9_CODE"])
    dx.columns = dx.columns.str.lower()
    dx = dx.rename(columns={"icd9_code": "icd_code"})
    dx["icd_version"] = 9
    diagnosis_seq_audit = common._diagnosis_sequence_position_audit(dx)
    memberships, diagnosis_match_audit = _memberships_with_sequence_quality(dx)
    del dx

    admissions = common._csv_member(zip_path, MEMBERS["admissions"],
                                    dtype={"HOSPITAL_EXPIRE_FLAG": "Float64"},
                                    usecols=["SUBJECT_ID", "HADM_ID", "ADMITTIME", "DISCHTIME",
                                             "DEATHTIME", "HOSPITAL_EXPIRE_FLAG"])
    admissions.columns = admissions.columns.str.lower()
    patients = common._csv_member(zip_path, MEMBERS["patients"],
                                  usecols=["SUBJECT_ID", "GENDER", "DOB"])
    patients.columns = patients.columns.str.lower()
    icu = common._csv_member(zip_path, MEMBERS["icustays"],
                             usecols=["SUBJECT_ID", "HADM_ID", "ICUSTAY_ID", "INTIME", "OUTTIME"])
    icu.columns = icu.columns.str.lower()
    icu = icu.rename(columns={"icustay_id": "stay_id"})

    for col in ("admittime", "dischtime", "deathtime"):
        admissions[col] = pd.to_datetime(admissions[col], errors="coerce")
    for col in ("intime", "outtime"):
        icu[col] = pd.to_datetime(icu[col], errors="coerce")
    icu["hadm_id"] = pd.to_numeric(icu["hadm_id"], errors="coerce")
    icu["stay_id"] = pd.to_numeric(icu["stay_id"], errors="coerce")
    icu = icu.dropna(subset=["subject_id", "hadm_id", "stay_id", "intime"])
    icu = (icu.sort_values(["hadm_id", "intime", "stay_id"], kind="mergesort")
           .drop_duplicates("hadm_id", keep="first"))
    admissions["hospital_expire_flag"] = pd.to_numeric(admissions["hospital_expire_flag"], errors="coerce")
    base = (memberships.merge(icu, on=["subject_id", "hadm_id"], how="inner", validate="many_to_one")
            .merge(admissions, on=["subject_id", "hadm_id"], how="left", validate="many_to_one")
            .merge(patients, on="subject_id", how="left", validate="many_to_one"))
    base["died"] = pd.to_numeric(base["hospital_expire_flag"], errors="coerce")
    base["age_at_admit"], base["age_topcoded_90"], base["age_exact"] = _age_from_dob(base["dob"], base["intime"])
    base = base[base["age_at_admit"].ge(18)].copy()
    base["pid"] = base["subject_id"]
    base["admission_id"] = base["hadm_id"]
    base = common.add_observation_windows(base)
    eligible = base[["subject_id", "hadm_id", "admittime", "disease"]].drop_duplicates()
    first_any = (eligible.sort_values(["subject_id", "admittime", "hadm_id"], kind="mergesort")
                 .drop_duplicates("subject_id").set_index("hadm_id").index)
    base["first_eligible_admission_any_disease"] = base["hadm_id"].isin(first_any)
    first_disease = (eligible.sort_values(["subject_id", "disease", "admittime", "hadm_id"], kind="mergesort")
                     .drop_duplicates(["subject_id", "disease"]).set_index(["hadm_id", "disease"]).index)
    base["first_eligible_admission_disease"] = pd.MultiIndex.from_frame(
        base[["hadm_id", "disease"]]).isin(first_disease)
    diagnosis_group_quality = {}
    for definition, inclusion, group in (
        ("broad", "broad_inclusion", "grp"),
        ("narrow", "narrow_inclusion", "grp_narrow"),
        ("legacy", "legacy_broad_inclusion", "grp_legacy_broad"),
    ):
        unranked = f"unranked_match_count_{definition}"
        rank1 = f"rank1_match_count_{definition}"
        for disease in common.DISEASES:
            selected = base.loc[base["disease"].eq(disease)
                                & base[inclusion].eq(1).fillna(False)]
            diagnosis_group_quality[f"{disease}:{definition}"] = {
                "adult_first_icu_index_rows": int(len(selected)),
                "rows_with_unranked_matching_diagnosis": int(
                    pd.to_numeric(selected[unranked], errors="coerce").fillna(0).gt(0).sum()),
                "rows_with_unknown_primary_status": int(selected[group].isna().sum()),
                "rows_with_unranked_match_but_confirmed_primary": int(
                    (pd.to_numeric(selected[unranked], errors="coerce").fillna(0).gt(0)
                     & pd.to_numeric(selected[rank1], errors="coerce").fillna(0).gt(0)).sum()),
            }
    base = base.drop(columns=["dob", "hospital_expire_flag"])
    base = base.sort_values(["disease", "hadm_id"], kind="mergesort").reset_index(drop=True)
    stats = {
        "diagnosis_rows": diagnosis_seq_audit["diagnosis_rows"],
        "diagnosis_seq_num_quality": diagnosis_seq_audit,
        "diagnosis_group_quality": {
            "source_definition_matches": diagnosis_match_audit,
            "adult_first_icu_index_rows": diagnosis_group_quality,
            "grouping_source": "all DIAGNOSES_ICD rows in the hospital admission; primary status is unknown if an unranked matching code exists and no matching seq_num=1 is documented",
        },
        "adult_disease_admissions": int(base["hadm_id"].nunique()),
        "admission_disease_rows": int(len(base)),
        "diseases": {str(k): int(v) for k, v in base.groupby("disease").size().items()},
        "age_topcoded_90_rows": int(base["age_topcoded_90"].sum()),
        "age_exact_rows": int(base["age_exact"].sum()),
        "missing_hospital_expire_flag": int(base["died"].isna().sum()),
        "chart_window_truncated_by_discharge": int(base["chart_window_truncated_by_discharge"].sum()),
        "chart_window_truncated_by_death": int(base["chart_window_truncated_by_death"].sum()),
        "window_anchor_inconsistent": int(base["window_anchor_inconsistent"].sum()),
        "death_within_24h_observed": int(base["death_within_24h_of_index_icu"].notna().sum()),
    }
    private_dir.mkdir(parents=True, exist_ok=True)
    dict_stats = _audit_small_dictionaries(zip_path, private_dir)
    return base, stats, dict_stats


def _atomic_filtered_cache(zip_path: Path, member: str, cache: Path, *, table: str,
                           index: pd.DataFrame, chunksize: int) -> int:
    cache.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_name(cache.name + ".partial")
    tmp.unlink(missing_ok=True)
    unique = index.drop_duplicates("hadm_id")
    if table == "chartevents":
        columns = ["stay_id", "hadm_id", "charttime", "itemid", "valuenum", "value"]
        usecols = ["ICUSTAY_ID", "HADM_ID", "CHARTTIME", "ITEMID", "VALUENUM", "VALUE"]
        dtype = {"ICUSTAY_ID": "Int64", "HADM_ID": "Int64", "ITEMID": "int32", "VALUE": "string"}
        start_map = dict(zip(unique["stay_id"].astype("int64"), unique["intime"]))
        end_map = dict(zip(unique["stay_id"].astype("int64"), unique["chart_window_end"]))
        valid_ids = set(unique["stay_id"].astype("int64"))
        id_col = "stay_id"
        before = pd.Timedelta(0)
        itemids = CHART_IDS
    elif table == "labevents":
        columns = ["hadm_id", "charttime", "itemid", "valuenum", "valueuom"]
        usecols = ["HADM_ID", "CHARTTIME", "ITEMID", "VALUENUM", "VALUEUOM"]
        dtype = {"HADM_ID": "Int64", "ITEMID": "int32"}
        start_map = dict(zip(unique["hadm_id"].astype("int64"), unique["intime"]))
        end_map = dict(zip(unique["hadm_id"].astype("int64"), unique["lab_window_end"]))
        valid_ids = set(unique["hadm_id"].astype("int64"))
        id_col = "hadm_id"
        before = pd.Timedelta(hours=-6)
        itemids = LAB_IDS
    else:
        raise ValueError(f"Unsupported event table: {table}")

    count = 0
    started = time.monotonic()
    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as writer:
        wrote_header = False
        for i, chunk in enumerate(common._member_chunks(
                zip_path, member, chunksize=chunksize, usecols=usecols, dtype=dtype), 1):
            chunk = chunk[chunk["ITEMID"].isin(itemids)]
            if chunk.empty:
                continue
            if table == "labevents":
                pct = chunk["ITEMID"].eq(51144) & common._percent_unit_mask(chunk["VALUEUOM"])
                chunk = chunk[~chunk["ITEMID"].eq(51144) | pct]
                if chunk.empty:
                    continue
            source_id = "stay_id" if table == "chartevents" else "hadm_id"
            source_id_col = "ICUSTAY_ID" if table == "chartevents" else "HADM_ID"
            chunk[source_id] = pd.to_numeric(chunk[source_id_col], errors="coerce")
            chunk = chunk[chunk[source_id].isin(valid_ids)]
            if chunk.empty:
                continue
            chunk["charttime"] = pd.to_datetime(chunk["CHARTTIME"], errors="coerce")
            chunk["t0"] = chunk[source_id].map(start_map)
            chunk["window_end"] = chunk[source_id].map(end_map)
            chunk = chunk[(chunk["charttime"] >= chunk["t0"] + before)
                          & (chunk["charttime"] <= chunk["window_end"])]
            if chunk.empty:
                continue
            if table == "chartevents":
                chunk["hadm_id"] = pd.to_numeric(chunk["HADM_ID"], errors="coerce")
                chunk["itemid"] = pd.to_numeric(chunk["ITEMID"], errors="coerce").map(CHART_MAP)
                chunk = chunk.rename(columns={"VALUENUM": "valuenum", "VALUE": "value"})
            else:
                chunk["itemid"] = pd.to_numeric(chunk["ITEMID"], errors="coerce")
                chunk = chunk.rename(columns={"VALUENUM": "valuenum", "VALUEUOM": "valueuom"})
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
    _write_cache_manifest(cache, zip_path, member, common._index_hash(index), count)
    return count


def _aggregate_carevue_gcs(cache: Path) -> tuple[pd.DataFrame, dict]:
    """Reduce CareVue's direct GCS total (item 198) without summing components."""
    best: dict[int, tuple[float, pd.Timestamp]] = {}
    invalid = 0
    valid_count = 0
    for chunk in common._read_cache_chunks(cache, chunksize=1_000_000,
                                           dtype={"stay_id": "Int64", "itemid": "int32"}):
        x = chunk[chunk["itemid"].eq(GCS_TOTAL_ID)].copy()
        if x.empty:
            continue
        x["stay_id"] = pd.to_numeric(x["stay_id"], errors="coerce")
        x["charttime"] = pd.to_datetime(x["charttime"], errors="coerce")
        value = pd.to_numeric(x["valuenum"], errors="coerce")
        fallback = pd.to_numeric(x["value"].astype("string").str.extract(r"(-?\d+(?:\.\d+)?)")[0],
                                  errors="coerce")
        value = value.where(value.notna(), fallback)
        valid = value.between(3, 15) & np.isclose(value.fillna(0) % 1, 0)
        invalid += int((value.notna() & ~valid).sum())
        x["gcs_total"] = value.where(valid)
        x = x.dropna(subset=["stay_id", "charttime", "gcs_total"])
        valid_count += int(len(x))
        x = x.sort_values(["stay_id", "gcs_total", "charttime"], kind="mergesort")
        x = x.drop_duplicates("stay_id", keep="first")
        for row in x[["stay_id", "gcs_total", "charttime"]].itertuples(index=False, name=None):
            stay_id, score, charttime = int(row[0]), float(row[1]), row[2]
            previous = best.get(stay_id)
            if previous is None or score < previous[0] or (score == previous[0] and charttime < previous[1]):
                best[stay_id] = (score, charttime)
    out = pd.DataFrame([{"stay_id": k, "gcs_total_worst": v[0],
                         "gcs_total_worst_charttime": v[1]} for k, v in best.items()])
    if out.empty:
        out = pd.DataFrame({"stay_id": pd.Series(dtype="int64"),
                            "gcs_total_worst": pd.Series(dtype="float64"),
                            "gcs_total_worst_charttime": pd.Series(dtype="datetime64[ns]")})
    return out, {"valid_carevue_total_rows": valid_count,
                 "invalid_carevue_total_values": invalid,
                 "stays_with_carevue_total": int(len(out))}


def _combine_gcs(chart: pd.DataFrame, carevue: pd.DataFrame) -> pd.DataFrame:
    out = chart.merge(carevue, on="stay_id", how="outer", validate="one_to_one")
    if "gcs_worst_ett_as1" not in out:
        out["gcs_worst_ett_as1"] = np.nan
        out["gcs_worst_ett_as1_charttime"] = pd.NaT
    component = pd.to_numeric(out["gcs_worst"], errors="coerce")
    direct = pd.to_numeric(out["gcs_total_worst"], errors="coerce")
    direct_lower = direct.notna() & (component.isna() | direct.lt(component))
    out.loc[direct_lower, "gcs_worst"] = direct.loc[direct_lower]
    out.loc[direct_lower, "gcs_worst_charttime"] = out.loc[direct_lower, "gcs_total_worst_charttime"]
    component_ett = pd.to_numeric(out["gcs_worst_ett_as1"], errors="coerce")
    direct_lower_ett = direct.notna() & (component_ett.isna() | direct.lt(component_ett))
    out.loc[direct_lower_ett, "gcs_worst_ett_as1"] = direct.loc[direct_lower_ett]
    out.loc[direct_lower_ett, "gcs_worst_ett_as1_charttime"] = out.loc[
        direct_lower_ett, "gcs_total_worst_charttime"]
    out["gcs_worst_source"] = pd.Series(pd.NA, index=out.index, dtype="string")
    out.loc[component.notna(), "gcs_worst_source"] = "metavision_complete_components"
    out.loc[direct_lower, "gcs_worst_source"] = "carevue_total_item_198"
    out["gcs_worst_ett_as1_source"] = pd.Series(pd.NA, index=out.index, dtype="string")
    out.loc[component_ett.notna(), "gcs_worst_ett_as1_source"] = "metavision_components_ett_as1"
    out.loc[direct_lower_ett, "gcs_worst_ett_as1_source"] = "carevue_total_item_198"
    return out.drop(columns=["gcs_total_worst", "gcs_total_worst_charttime"])


def _merge_aggregate(index: pd.DataFrame, chart: pd.DataFrame, labs: pd.DataFrame) -> pd.DataFrame:
    panel = index.merge(chart, on="stay_id", how="left", validate="many_to_one")
    panel = panel.merge(labs, on="hadm_id", how="left", validate="many_to_one")
    return common.score_panel(panel)


def _definition_summary(panel: pd.DataFrame) -> pd.DataFrame:
    return common._definition_summary(panel)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, default=ZIP_DEFAULT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--private-dir", type=Path, default=PRIVATE_DEFAULT)
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--index-only", action="store_true", help="build/reuse the small admission index only")
    parser.add_argument("--allow-event-scan", action="store_true",
                        help="required to read the large CHARTEVENTS/LABEVENTS members")
    parser.add_argument("--force-rescan", action="store_true", help="ignore index and filtered event caches")
    parser.add_argument("--chart-chunksize", type=int, default=CHART_CHUNK_SIZE)
    parser.add_argument("--lab-chunksize", type=int, default=LAB_CHUNK_SIZE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if not args.index_only and not args.allow_event_scan:
        raise SystemExit("Refusing large MIMIC-III event-table scans without --allow-event-scan")
    zip_path = args.zip.resolve()
    if not zip_path.is_file():
        raise FileNotFoundError(zip_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.private_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.cache_dir or (args.private_dir / "cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{VERSION}] source={zip_path} ({zip_path.stat().st_size:,} bytes)", flush=True)

    if not args.force_rescan and _index_cache_valid(args.private_dir, zip_path):
        print("[index] reuse verified private admission index", flush=True)
        index, index_stats, dict_stats = _read_index_cache(args.private_dir)
        index_manifest = json.loads(_manifest_path(args.private_dir).read_text(encoding="utf-8"))
    else:
        print("[index] cache miss; building adult first-ICU admission index", flush=True)
        index, index_stats, dict_stats = build_index(zip_path, args.private_dir)
        index_manifest = _write_index_cache(index, index_stats, dict_stats, args.private_dir, zip_path)
    _copy_dictionary_audits(args.private_dir, args.out_dir)
    common._write_json(args.out_dir / "mimic_iii_v2_index_manifest.json", index_manifest)
    print(f"   index rows={len(index):,}; admissions={index['hadm_id'].nunique():,}; "
          f"sequence unranked rows={index_stats['diagnosis_seq_num_quality']['seq_num_unranked_rows']:,}", flush=True)
    if args.index_only:
        print(f"[index-only] wrote private index under {args.private_dir}", flush=True)
        return 0

    index_hash = index_manifest["index_filter_sha256"]
    chart_cache = cache_dir / "mimic_iii_chartevents_filtered.csv.gz"
    lab_cache = cache_dir / "mimic_iii_labevents_filtered.csv.gz"
    if args.force_rescan or not _cache_is_valid(chart_cache, zip_path, MEMBERS["chartevents"], index_hash):
        print("[chart] streaming selected MIMIC-III itemids/stays", flush=True)
        chart_rows = _atomic_filtered_cache(zip_path, MEMBERS["chartevents"], chart_cache,
                                            table="chartevents", index=index,
                                            chunksize=args.chart_chunksize)
    else:
        chart_rows = int(json.loads(_cache_manifest_path(chart_cache).read_text()).get("rows", 0))
        print(f"[chart] reuse verified filtered cache rows={chart_rows:,}", flush=True)
    if args.force_rescan or not _cache_is_valid(lab_cache, zip_path, MEMBERS["labevents"], index_hash):
        print("[labs] streaming selected MIMIC-III itemids/admissions", flush=True)
        lab_rows = _atomic_filtered_cache(zip_path, MEMBERS["labevents"], lab_cache,
                                          table="labevents", index=index,
                                          chunksize=args.lab_chunksize)
    else:
        lab_rows = int(json.loads(_cache_manifest_path(lab_cache).read_text()).get("rows", 0))
        print(f"[labs] reuse verified filtered cache rows={lab_rows:,}", flush=True)

    print("[aggregate] reducing filtered MIMIC-III caches", flush=True)
    chart, chart_stats = common.aggregate_chart_cache(chart_cache)
    carevue_gcs, carevue_gcs_stats = _aggregate_carevue_gcs(chart_cache)
    chart = _combine_gcs(chart, carevue_gcs)
    labs, lab_stats = common.aggregate_lab_cache(lab_cache)
    panel = _merge_aggregate(index, chart, labs)
    panel_path = args.private_dir / "mimic_iii_v2_score_panel.csv.gz"
    tmp_panel = panel_path.with_name(panel_path.name + ".partial")
    panel.to_csv(tmp_panel, index=False, compression="gzip")
    os.replace(tmp_panel, panel_path)
    summary = _definition_summary(panel)
    summary_path = args.out_dir / "mimic_iii_v2_score_coverage.csv"
    tmp_summary = summary_path.with_name(summary_path.name + ".partial")
    summary.to_csv(tmp_summary, index=False)
    os.replace(tmp_summary, summary_path)
    run_manifest = {
        "version": VERSION, "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "source_zip": str(zip_path), "source_zip_size": zip_path.stat().st_size,
        "source_zip_mtime_ns": zip_path.stat().st_mtime_ns,
        "archive_fingerprint": common._archive_fingerprint(zip_path),
        "members": {name: _source_fingerprint(zip_path, member) for name, member in MEMBERS.items()},
        "index_stats": index_stats, "diagnosis_seq_num_quality": index_stats.get("diagnosis_seq_num_quality"),
        "diagnosis_group_quality": index_stats.get("diagnosis_group_quality"),
        "dictionary_audit": dict_stats, "filtered_chart_rows": chart_rows, "filtered_lab_rows": lab_rows,
        "chart_aggregation": chart_stats, "carevue_gcs_total": carevue_gcs_stats,
        "lab_aggregation": lab_stats, "panel_rows": int(len(panel)),
        "unique_admissions": int(panel["hadm_id"].nunique()),
        "unique_patients": int(panel["pid"].nunique()),
        "missing_outcome_rows": int(panel["died"].isna().sum()),
        "gcs_ett_as1_sensitivity": "No Response-ETT/unassessable primary GCS values are missing; alternate score fields map No Response-ETT to 1.",
        "score_complete_counts": {s: int(panel[s].notna().sum()) for s in common.SCORE_NAMES},
        "private_directory": str(args.private_dir), "filtered_cache_directory": str(cache_dir),
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": common._sha256(p)}
                  for p in (panel_path, summary_path)},
    }
    common._write_json(args.out_dir / "mimic_iii_v2_run_manifest.json", run_manifest)
    print(f"[done] rows={len(panel):,}; admissions={panel['hadm_id'].nunique():,}; "
          f"patients={panel['pid'].nunique():,}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

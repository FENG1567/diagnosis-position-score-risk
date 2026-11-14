#!/usr/bin/env python3
"""Aggregate-only QA for MIMIC-III GCS handling; never opens source events."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import m58_mimic3_rebuild as m3

COMMON = m3.common
WORKSPACE = m3.WORKSPACE
PRIVATE = m3.PRIVATE_DEFAULT
OUTPUT = m3.OUT_DEFAULT


def _sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    cache = PRIVATE / "cache" / "mimic_iii_chartevents_filtered.csv.gz"
    index_manifest_path = PRIVATE / "mimic_iii_v2_index_manifest.json"
    panel_path = PRIVATE / "mimic_iii_v2_score_panel.csv.gz"
    run_manifest_path = OUTPUT / "mimic_iii_v2_run_manifest.json"
    index_manifest = json.loads(index_manifest_path.read_text(encoding="utf-8"))
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    index_hash = index_manifest["index_filter_sha256"]
    cache_valid = m3._cache_is_valid(cache, Path(run_manifest["source_zip"]),
                                      m3.MEMBERS["chartevents"], index_hash)
    if not cache_valid:
        raise SystemExit("Refusing GCS QA: filtered MIMIC-III chart cache failed provenance validation")

    counts = {
        "gcs_component_rows": 0,
        "carevue_gcs_total_rows": 0,
        "explicit_unassessable_rows": 0,
        "explicit_unassessable_primary_missing_rows": 0,
        "unassessable_numeric_fallback_suppressed_rows": 0,
        "no_response_ett_rows": 0,
        "no_response_ett_primary_missing_rows": 0,
        "no_response_ett_ett_as1_mapped_to_one_rows": 0,
    }
    by_itemid: dict[str, dict[str, int]] = {}
    unassessable_pattern = re.compile(COMMON.GCS_UNASSESSABLE_PATTERN, re.IGNORECASE)
    for chunk in COMMON._read_cache_chunks(
            cache, chunksize=1_000_000,
            dtype={"stay_id": "Int64", "itemid": "int32"}):
        chunk["itemid"] = pd.to_numeric(chunk["itemid"], errors="coerce")
        counts["carevue_gcs_total_rows"] += int(chunk["itemid"].eq(m3.GCS_TOTAL_ID).sum())
        gcs = chunk[chunk["itemid"].isin(COMMON.GCS_IDS)].copy()
        if gcs.empty:
            continue
        raw = (gcs["value"].astype("string").str.strip().str.lower()
               .str.replace(r"\s*[-–]\s*", "-", regex=True))
        unassessable = raw.str.contains(unassessable_pattern, na=False)
        no_response_ett = raw.str.contains(r"\bno response-ett\b", regex=True, na=False)
        primary = COMMON._map_gcs_values(gcs)
        ett_as1 = COMMON._map_gcs_values(gcs, ett_as_one=True)
        fallback_numeric = pd.Series(False, index=gcs.index)
        for itemid, maximum in ((220739, 4), (223900, 5), (223901, 6)):
            selected = gcs["itemid"].eq(itemid)
            num = pd.to_numeric(gcs.loc[selected, "valuenum"], errors="coerce")
            fallback_numeric.loc[selected] = num.between(1, maximum) & (num % 1).eq(0)
        counts["gcs_component_rows"] += int(len(gcs))
        counts["explicit_unassessable_rows"] += int(unassessable.sum())
        counts["explicit_unassessable_primary_missing_rows"] += int(
            (unassessable & primary.isna()).sum())
        counts["unassessable_numeric_fallback_suppressed_rows"] += int(
            (unassessable & fallback_numeric & primary.isna()).sum())
        counts["no_response_ett_rows"] += int(no_response_ett.sum())
        counts["no_response_ett_primary_missing_rows"] += int(
            (no_response_ett & primary.isna()).sum())
        counts["no_response_ett_ett_as1_mapped_to_one_rows"] += int(
            (no_response_ett & ett_as1.eq(1)).sum())
        for itemid in COMMON.GCS_IDS:
            key = str(int(itemid))
            selected = gcs["itemid"].eq(itemid)
            by_itemid.setdefault(key, {"component_rows": 0, "unassessable_rows": 0,
                                      "no_response_ett_rows": 0,
                                      "no_response_ett_ett_as1_mapped_to_one_rows": 0})
            by_itemid[key]["component_rows"] += int(selected.sum())
            by_itemid[key]["unassessable_rows"] += int((selected & unassessable).sum())
            by_itemid[key]["no_response_ett_rows"] += int((selected & no_response_ett).sum())
            by_itemid[key]["no_response_ett_ett_as1_mapped_to_one_rows"] += int(
                (selected & no_response_ett & ett_as1.eq(1)).sum())

    usecols = ["gcs_worst", "gcs_worst_ett_as1", "gcs_worst_source",
               "gcs_worst_ett_as1_source", "qsofa", "qsofa_ett_as1",
               "qsofa_gcs15", "qsofa_gcs15_ett_as1", "curb65", "curb65_ett_as1",
               "bisap4", "bisap4_ett_as1"]
    panel = pd.read_csv(panel_path, compression="gzip", low_memory=False, usecols=usecols)
    score_pairs = {
        "qsofa": "qsofa_ett_as1", "qsofa_gcs15": "qsofa_gcs15_ett_as1",
        "curb65": "curb65_ett_as1", "bisap4": "bisap4_ett_as1",
    }
    score_counts = {}
    for primary_score, sensitivity_score in score_pairs.items():
        paired = panel[primary_score].notna() & panel[sensitivity_score].notna()
        score_counts[primary_score] = {
            "primary_complete": int(panel[primary_score].notna().sum()),
            "ett_as1_complete": int(panel[sensitivity_score].notna().sum()),
            "primary_missing_but_ett_as1_complete": int(
                (panel[primary_score].isna() & panel[sensitivity_score].notna()).sum()),
            "paired_rows_with_different_score": int(
                (paired & panel[primary_score].ne(panel[sensitivity_score])).sum()),
        }
    panel_counts = {
        "panel_rows": int(len(panel)),
        "rows_primary_gcs_missing_but_ett_as1_observed": int(
            (panel["gcs_worst"].isna() & panel["gcs_worst_ett_as1"].notna()).sum()),
        "gcs_worst_source_rows": {
            str(key): int(value) for key, value in
            panel["gcs_worst_source"].value_counts(dropna=False).items()
        },
        "gcs_worst_ett_as1_source_rows": {
            str(key): int(value) for key, value in
            panel["gcs_worst_ett_as1_source"].value_counts(dropna=False).items()
        },
        "scores": score_counts,
    }
    if counts["explicit_unassessable_primary_missing_rows"] != counts["explicit_unassessable_rows"]:
        raise SystemExit("Unexpected primary GCS mapping for an explicit unassessable value")

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "verified filtered MIMIC-III chart cache only; no source event-table reads",
        "cache_validation_passed": cache_valid,
        "cache_name": cache.name,
        "cache_bytes": cache.stat().st_size,
        "cache_sha256": _sha256(cache),
        "panel_name": panel_path.name,
        "panel_bytes": panel_path.stat().st_size,
        "panel_sha256": _sha256(panel_path),
        "gcs_event_mapping": counts,
        "gcs_event_mapping_by_itemid": by_itemid,
        "score_panel": panel_counts,
        "policy": "All explicit unassessable/intubated GCS components are missing in primary mapping; No Response-ETT maps to 1 only in the labeled ETT-as-1 sensitivity where specified by component item mapping. CareVue total GCS remains a separate direct total source.",
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT / "mimic_iii_v2_gcs_ett_cache_qa.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run_manifest["gcs_ett_cache_qa"] = {
        "file": report_path.name,
        "bytes": report_path.stat().st_size,
        "sha256": _sha256(report_path),
        "gcs_event_mapping": counts,
        "score_panel": panel_counts,
    }
    run_manifest.setdefault("files", {})[report_path.name] = {
        "bytes": report_path.stat().st_size,
        "sha256": _sha256(report_path),
    }
    run_manifest["final_qa_utc"] = report["generated_utc"]
    run_manifest_path.write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    print(json.dumps({"report": str(report_path), "gcs_event_mapping": counts,
                      "score_panel": panel_counts}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

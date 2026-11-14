#!/usr/bin/env python3
"""Validate MIMIC-III rebuilt panel/cache manifests without source-table scans."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import m58_mimic3_rebuild as m3


def _sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _group_counts(frame: pd.DataFrame, inclusion: str, group_col: str) -> dict:
    included = frame[frame[inclusion].eq(1).fillna(False)]
    return {
        "included_rows": int(len(included)),
        "grp_0": int(included[group_col].eq(0).fillna(False).sum()),
        "grp_1": int(included[group_col].eq(1).fillna(False).sum()),
        "grp_unknown": int(included[group_col].isna().sum()),
    }


def main() -> int:
    private = m3.PRIVATE_DEFAULT
    output = m3.OUT_DEFAULT
    run_path = output / "mimic_iii_v2_run_manifest.json"
    index_path = private / "mimic_iii_v2_index.csv.gz"
    panel_path = private / "mimic_iii_v2_score_panel.csv.gz"
    summary_path = output / "mimic_iii_v2_score_coverage.csv"
    index_manifest_path = private / "mimic_iii_v2_index_manifest.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    index_manifest = json.loads(index_manifest_path.read_text(encoding="utf-8"))
    index_hash = index_manifest["index_filter_sha256"]
    cache_results = {}
    for table in ("chartevents", "labevents"):
        cache = private / "cache" / f"mimic_iii_{table}_filtered.csv.gz"
        cache_results[table] = {
            "valid": bool(m3._cache_is_valid(cache, Path(run["source_zip"]),
                                              m3.MEMBERS[table], index_hash)),
            "bytes": int(cache.stat().st_size),
            "sha256": _sha256(cache),
        }
    if not all(row["valid"] for row in cache_results.values()):
        raise SystemExit("One or more MIMIC-III filtered caches failed provenance validation")

    panel = pd.read_csv(panel_path, compression="gzip", low_memory=False)
    duplicate_key_rows = int(panel.duplicated(["hadm_id", "disease"]).sum())
    multi_stay_admissions = int((panel.groupby("hadm_id")["stay_id"].nunique() > 1).sum())
    score_complete = {score: int(panel[score].notna().sum()) for score in m3.common.SCORE_NAMES}
    by_disease = {}
    for disease in m3.common.DISEASES:
        source = panel.loc[panel["disease"].eq(disease)]
        by_disease[disease] = {
            "panel_rows": int(len(source)),
            "unique_admissions": int(source["hadm_id"].nunique()),
            "outcomes_observed": int(source["died"].notna().sum()),
            "grp": _group_counts(source, "broad_inclusion", "grp"),
        }
        if disease in {"sepsis", "pneumonia"}:
            by_disease[disease]["narrow_grp"] = _group_counts(
                source, "narrow_inclusion", "grp_narrow")
        if disease not in {"sepsis", "pneumonia"}:
            by_disease[disease]["legacy_grp"] = _group_counts(
                source, "legacy_broad_inclusion", "grp_legacy_broad")

    file_checks = {}
    for name, record in run.get("files", {}).items():
        path = (private if name.endswith(".csv.gz") and "score_panel" in name
                else output) / name
        if not path.exists():
            raise SystemExit(f"Manifest file is missing: {name}")
        actual = {"bytes": int(path.stat().st_size), "sha256": _sha256(path)}
        file_checks[name] = {"matches_manifest": actual == record, **actual}
        if actual != record:
            raise SystemExit(f"Manifest hash/size mismatch for {name}")

    qa = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "validation_scope": "private rebuilt panel and verified filtered caches; no source event-table reads",
        "version": run["version"],
        "index_rows": int(len(pd.read_csv(index_path, compression="gzip", usecols=["hadm_id", "disease"]))),
        "panel_rows": int(len(panel)),
        "unique_admissions": int(panel["hadm_id"].nunique()),
        "unique_patients": int(panel["pid"].nunique()),
        "duplicate_admission_disease_rows": duplicate_key_rows,
        "admissions_with_multiple_index_stays": multi_stay_admissions,
        "missing_outcomes": int(panel["died"].isna().sum()),
        "score_complete_counts_match_manifest": score_complete == run["score_complete_counts"],
        "score_complete_counts": score_complete,
        "cache_validation": cache_results,
        "manifest_file_checks": file_checks,
        "diagnosis_group_quality": index_manifest.get("diagnosis_group_quality"),
        "by_disease": by_disease,
    }
    if duplicate_key_rows or multi_stay_admissions:
        raise SystemExit("Admission-level row uniqueness check failed")
    if len(panel) != run["panel_rows"] or score_complete != run["score_complete_counts"]:
        raise SystemExit("Panel counts do not match the run manifest")
    if qa["missing_outcomes"] != run["missing_outcome_rows"]:
        raise SystemExit("Outcome-missingness count does not match the run manifest")

    qa_path = output / "mimic_iii_v2_panel_qa.json"
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run["panel_qa"] = {
        "file": qa_path.name,
        "bytes": int(qa_path.stat().st_size),
        "sha256": _sha256(qa_path),
        "panel_rows": len(panel),
        "duplicate_admission_disease_rows": duplicate_key_rows,
        "admissions_with_multiple_index_stays": multi_stay_admissions,
        "score_complete_counts_match_manifest": qa["score_complete_counts_match_manifest"],
    }
    run.setdefault("files", {})[qa_path.name] = {
        "bytes": int(qa_path.stat().st_size),
        "sha256": _sha256(qa_path),
    }
    run["final_qa_utc"] = qa["generated_utc"]
    run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(qa_path), "panel_rows": len(panel),
                      "unique_admissions": int(panel["hadm_id"].nunique()),
                      "unique_patients": int(panel["pid"].nunique()),
                      "duplicate_admission_disease_rows": duplicate_key_rows,
                      "admissions_with_multiple_index_stays": multi_stay_admissions,
                      "missing_outcomes": qa["missing_outcomes"],
                      "score_complete_counts_match_manifest": qa["score_complete_counts_match_manifest"],
                      "cache_validation": cache_results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

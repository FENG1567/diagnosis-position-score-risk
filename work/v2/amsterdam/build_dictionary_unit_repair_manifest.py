"""Bind Amsterdam dictionary-unit repair inputs, code, private cache and results."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "work" / "v2" / "amsterdam"
OUT = ROOT / "outputs" / "v2" / "amsterdam" / "dictionary_unit_repair"
STRICT_OUT = ROOT / "outputs" / "v2" / "amsterdam" / "strict_row_units"
PRIVATE = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\private")
ORIGINAL_MANIFEST = ROOT / "outputs" / "v2" / "amsterdam" / "strict_row_units" / "amsterdam_source_manifest.json"
LOCK = ROOT / "outputs" / "v2" / "amsterdam" / "mapping_lock.json"
DICTIONARY = ROOT / "work" / "v2" / "sources" / "amsterdam_metadata" / "dictionary.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(label: str, path: Path, private: bool = False) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return {"label": label, "file_name": path.name,
            "storage": "private F: drive" if private else "workspace",
            "bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> int:
    validation_path = OUT / "preoutcome_repair_validation.json"
    summary_path = OUT / "amsterdam_dictionary_unit_repair_outcome_summary.json"
    outcome_marker_path = OUT / "outcome_run_marker.json"
    progress_path = WORK / "dictionary_unit_repair_progress.json"
    if not summary_path.is_file() or not validation_path.is_file() or not outcome_marker_path.is_file():
        raise RuntimeError("Completed outcome marker, repaired outcome and pre-outcome validation are required")
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    outcome_marker = json.loads(outcome_marker_path.read_text(encoding="utf-8"))
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    strict_source = json.loads(ORIGINAL_MANIFEST.read_text(encoding="utf-8"))
    strict_snapshot = json.loads((STRICT_OUT / "snapshot_manifest.json").read_text(encoding="utf-8"))

    if progress.get("status") != "complete" or progress.get("member_crc32_verified") != "475539f6":
        raise RuntimeError("Full numeric-member EOF/CRC verification is absent")
    if not validation.get("numeric_validation", {}).get("zip_member_crc_checked"):
        raise RuntimeError("Pre-outcome validation does not attest a full-member CRC check")
    if not validation.get("strict_panel_reconstruction", {}).get("pass"):
        raise RuntimeError("Strict-row-unit reconstruction did not pass")
    if lock.get("lock_status") != "locked_before_outcome_join":
        raise RuntimeError("The original mapping lock is not in its pre-outcome frozen state")
    if sha256(DICTIONARY) != lock["source"].get("dictionary_sha256"):
        raise RuntimeError("The unit dictionary differs from the source locked before outcomes")

    raw_cache = PRIVATE / "numeric_qsofa_target_raw_before_unit_window.csv.gz"
    repaired_pre = PRIVATE / "qsofa_sepsis_icu_dictionary_unit_repair_preoutcome.csv.gz"
    repaired_outcome = PRIVATE / "qsofa_sepsis_icu_dictionary_unit_repair_outcome.csv.gz"
    outcome_comparison = OUT / "amsterdam_unit_repair_interval_comparison.csv"
    outcome_intervals = OUT / "amsterdam_unit_repair_intervals.csv"
    completeness_comparison = OUT / "amsterdam_unit_repair_completeness_comparison.csv"
    mortality_by_score = OUT / "mortality_by_qsofa_score_repaired.csv"
    if (outcome_marker.get("status") != "complete"
            or outcome_marker.get("run_id") != summary.get("outcome_run_id")):
        raise RuntimeError("Outcome panel exists without a completed matching aggregate-analysis run marker")
    if (outcome_marker.get("strict_baseline_reproduction_passed") is not True
            or outcome_marker.get("direct_estimand_crosschecks_passed") is not True):
        raise RuntimeError("Outcome marker does not attest to strict-baseline and direct-estimand checks")
    for key, path in (
        ("summary_sha256", summary_path),
        ("repaired_outcome_panel_sha256", repaired_outcome),
        ("interval_comparison_csv_sha256", outcome_comparison),
        ("intervals_csv_sha256", outcome_intervals),
        ("completeness_comparison_csv_sha256", completeness_comparison),
        ("mortality_by_score_csv_sha256", mortality_by_score),
    ):
        if sha256(path) != outcome_marker.get(key):
            raise RuntimeError(f"Completed outcome marker hash mismatch: {path.name}")
    private_artifacts = [
        artifact("selected numeric events before time/unit filtering", raw_cache, private=True),
        artifact("repaired outcome-blind ICU panel", repaired_pre, private=True),
        artifact("repaired outcome-linked ICU panel", repaired_outcome, private=True),
    ]
    if sha256(raw_cache) != progress.get("cache_sha256"):
        raise RuntimeError("Selected-event cache hash differs from the completed scan progress record")
    original_sources = strict_source["audit_run"]["sources"]
    public_outputs = []
    for path in sorted(OUT.iterdir()):
        if (path.is_file() and path.name != "dictionary_unit_repair_source_manifest.json"
                and not path.name.endswith(".partial")):
            public_outputs.append(artifact("repaired aggregate output", path))
    code = [
        artifact("dictionary-unit repair scan and analysis", WORK / "run_amsterdam_dictionary_unit_repair.py"),
        artifact("dictionary-unit repair tests", WORK / "test_unit_mapping_repair.py"),
        artifact("dictionary-unit repair manifest builder", WORK / "build_dictionary_unit_repair_manifest.py"),
        artifact("strict-row-unit analysis implementation", STRICT_OUT / "run_amsterdam_audit.py"),
        artifact("shared audit_v2 implementation", ROOT / "work/v2/audit/cohort_definition_audit.py"),
        artifact("root direct estimand implementation", ROOT / "work/v2/estimands.py"),
    ]
    manifest = {
        "manifest_version": 2,
        "analysis_version": "amsterdam_dictionary_unit_repair_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "repair_timing_and_independence": validation["repair_timing"],
        "unchanged_mapping_lock": {
            "path": "outputs/v2/amsterdam/mapping_lock.json",
            "sha256": sha256(LOCK),
            "frozen_preoutcome": True,
        },
        "official_unit_dictionary": {
            "path": "work/v2/sources/amsterdam_metadata/dictionary.csv",
            "sha256": sha256(DICTIONARY),
            "expected_sha256_from_lock": lock["source"]["dictionary_sha256"],
            "row_8874": validation["unit_policy"]["dictionary_unit_map"].get("8874"),
            "numeric_measurement_concept": validation["unit_policy"]["dictionary_mapped_measurement_concept"].get("8874"),
            "blank_event_unit_only": True,
            "explicit_conflicts_overridden": False,
        },
        "source_data": {
            "dataset": "AmsterdamUMCdb 1.0.2",
            "source_repository_commit": lock["source"]["commit"],
            "original_locked_source_hashes_reused": original_sources,
            "numeric_member": {
                "name": progress["member"],
                "uncompressed_bytes": progress["member_uncompressed_bytes"],
                "rows_scanned_to_eof": progress["rows_scanned"],
                "matched_rows_cached_before_unit_and_window_filter": progress["cache_rows_written"],
                "crc32_expected_and_verified": progress["member_crc32_verified"],
                "crc_verification_method": progress["crc_verified_by"],
            },
            "strict_baseline_snapshot_manifest_sha256": sha256(STRICT_OUT / "snapshot_manifest.json"),
            "strict_snapshot_entries_verified_pre_scan": validation["strict_snapshot_verification"],
        },
        "method": {
            "dictionary_unit_resolution": validation["unit_policy"],
            "first_24h_and_stay_filter": "0 to 86,400,000 ms inclusive from ICU admission episode; reject measurements after discharge",
            "strict_reconstruction": validation["strict_panel_reconstruction"],
            "score_completion_and_allocation_change": validation["score_completeness_and_allocation_change"],
            "canonical_interval_for_root_tables": "Normal patient-cluster influence-function interval",
            "bootstrap_interval_label": "Patient-cluster percentile bootstrap sensitivity interval",
            "clinical_unit": "ICU admission episode; patientid clusters inference",
        },
        "audit": {
            "config": summary["audit_config"],
            "outcome_run_marker": outcome_marker,
            "strict_results_reproduced": summary["strict_baseline_reproduction"],
            "unit_repair_outcome_flow": summary["outcome_flow_by_group_dictionary_unit_repair"],
            "audit_verdicts": {
                version: {score: result.get("verdict") for score, result in scores.items()}
                for version, scores in summary["audit"].items()
            },
            "direct_estimand_crosschecks": summary["direct_estimand_crosscheck"],
        },
        "runtime": {"python": sys.version, "platform": platform.platform(),
                    "pandas": pd.__version__, "numpy": np.__version__},
        "privacy": {
            "record_level_data_retained_only_on_private_F_drive": True,
            "workspace_outputs_contain_no_record_level_rows_or_patient_identifiers": True,
            "private_data_location": "F:/分析专用/meta_measurement_20261103/work/paperB_v2/amsterdam",
        },
        "private_derived_artifacts": private_artifacts,
        "code_artifacts": code,
        "public_aggregate_outputs": public_outputs,
    }
    outpath = OUT / "dictionary_unit_repair_source_manifest.json"
    temporary = outpath.with_name(outpath.name + ".partial")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(outpath)
    print(json.dumps({"manifest": str(outpath.relative_to(ROOT)),
                      "numeric_rows_scanned": progress["rows_scanned"],
                      "cached_event_rows": progress["cache_rows_written"],
                      "crc32": progress["member_crc32_verified"],
                      "public_outputs_hashed": len(public_outputs),
                      "code_files_hashed": len(code)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

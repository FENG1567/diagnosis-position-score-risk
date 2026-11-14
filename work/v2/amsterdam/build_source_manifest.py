"""Create a privacy-preserving source and code manifest after the Amsterdam audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PRIVATE = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\private")
ARCHIVE = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\archive\numericitems.zip")
OUT = ROOT / "outputs" / "v2" / "amsterdam"
WORK = ROOT / "work" / "v2" / "amsterdam"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def entry(label: str, path: Path, *, private: bool = False) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "label": label,
        "storage": "private F: drive" if private else "workspace",
        "file_name": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after-outcome", action="store_true",
                        help="Require and bind the completed ICU discharge outcome summary.")
    args = parser.parse_args()

    lock = OUT / "mapping_lock.json"
    preoutcome = OUT / "preoutcome_field_validation.json"
    progress = WORK / "numeric_scan_progress.json"
    if not preoutcome.is_file() or not progress.is_file():
        raise RuntimeError("Pre-outcome validation and numeric scan progress are required")
    lock_data = json.loads(lock.read_text(encoding="utf-8"))
    pre = json.loads(preoutcome.read_text(encoding="utf-8"))
    scan = json.loads(progress.read_text(encoding="utf-8"))
    if lock_data.get("lock_status") != "locked_before_outcome_join":
        raise RuntimeError("Mapping lock is not frozen")
    if pre.get("outcome_field_loaded") is not False:
        raise RuntimeError("Pre-outcome artifact was not outcome-blind")
    numeric = pre.get("numeric_validation", {})
    if not numeric.get("zip_member_crc_checked") or scan.get("status") != "complete":
        raise RuntimeError("Numeric ZIP member was not fully read and CRC-verified")
    if scan.get("member_crc32_verified") != numeric.get("numeric_member_crc32"):
        raise RuntimeError("Numeric ZIP CRC in progress record differs from field validation")

    sources = [
        entry("admissions source table", PRIVATE / "admissions.csv", private=True),
        entry("listitems source table", PRIVATE / "listitems.csv", private=True),
        entry("numericitems source archive", ARCHIVE, private=True),
    ]
    source_code = [
        entry("official source dictionary", ROOT / "work/v2/sources/amsterdam_metadata/dictionary.csv"),
        entry("official GCS definition SQL", WORK / "references/gcs.sql"),
        entry("official diagnosis SQL", WORK / "references/reason_for_admission.sql"),
        entry("frozen mapping lock", lock),
        entry("mapping lock builder", WORK / "lock_amsterdam_mapping.py"),
        entry("Amsterdam audit implementation", WORK / "run_amsterdam_audit.py"),
        entry("source manifest builder", WORK / "build_source_manifest.py"),
        entry("shared audit_v2 implementation", ROOT / "work/v2/audit/cohort_definition_audit.py"),
        entry("root direct estimator implementation", ROOT / "work/v2/estimands.py"),
    ]
    derived = [
        entry("selected listitems cache", PRIVATE / "listitems_qsofa_nice.csv.gz", private=True),
        entry("outcome-blind ICU panel", PRIVATE / "qsofa_sepsis_icu_preoutcome.csv.gz", private=True),
        entry("outcome-blind field validation", preoutcome),
    ]
    if args.after_outcome:
        outcome = OUT / "amsterdam_qsofa_outcome_summary.json"
        private_outcome_panel = PRIVATE / "qsofa_sepsis_icu_outcome.csv.gz"
        if not outcome.is_file() or not private_outcome_panel.is_file():
            raise RuntimeError("Outcome summary and private joined panel are required")
        derived.extend([
            entry("outcome-linked private ICU panel", private_outcome_panel, private=True),
            entry("supplementary outcome audit", outcome),
            entry("primary qSOFA audit JSON", OUT / "audit_gcs_le_13.json"),
            entry("primary qSOFA audit report", OUT / "audit_gcs_le_13.md"),
            entry("primary qSOFA per-level table", OUT / "audit_gcs_le_13_per_level.csv"),
            entry("GCS<15 sensitivity audit JSON", OUT / "audit_gcs_lt_15_sensitivity.json"),
            entry("GCS<15 sensitivity audit report", OUT / "audit_gcs_lt_15_sensitivity.md"),
            entry("GCS<15 sensitivity per-level table", OUT / "audit_gcs_lt_15_sensitivity_per_level.csv"),
            entry("mortality by qSOFA score table", OUT / "mortality_by_qsofa_score.csv"),
        ])

    manifest = {
        "manifest_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "dataset": {
            "name": "AmsterdamUMCdb",
            "release": "1.0.2",
            "official_repository": "https://github.com/AmsterdamUMC/AmsterdamUMCdb",
            "source_commit": lock_data["source"]["commit"],
            "admissions_schema_url": "https://github.com/AmsterdamUMC/AmsterdamUMCdb/wiki/admissions",
            "destination_semantics": "Discharge department, or Overleden when death occurred during the ICU/MCU admission.",
            "official_outcome_example_url": "https://github.com/AmsterdamUMC/AmsterdamUMCdb/blob/master/tables/numericitems.ipynb",
            "outcome_interpretation": "Official example maps destination == Overleden to death and all other department destinations to alive at discharge.",
        },
        "privacy": {
            "record_level_data_retained_only_on_private_F_drive": True,
            "workspace_outputs_contain_no_record_level_rows_or_patient_identifiers": True,
            "private_data_location": "F:/分析专用/meta_measurement_20261103/work/paperB_v2/amsterdam",
        },
        "mapping_lock": {
            "status": lock_data["lock_status"],
            "sha256": sha256(lock),
            "outcome_accessed_at_lock_time": lock_data["reporting"]["outcome_accessed_at_lock_time"],
            "primary_and_secondary_diagnosis_itemids": [
                lock_data["analysis_target"]["primary_diagnosis_itemid"],
                lock_data["analysis_target"]["secondary_diagnosis_itemid"],
            ],
        },
        "numeric_member_integrity": {
            "member": numeric.get("numeric_member"),
            "uncompressed_bytes": numeric.get("numeric_member_uncompressed_bytes"),
            "rows_scanned_to_eof": numeric.get("numeric_rows_scanned"),
            "crc32_expected_and_verified": numeric.get("numeric_member_crc32"),
            "full_member_crc_check_passed": numeric.get("zip_member_crc_checked"),
            "verification_method": scan.get("crc_verified_by"),
        },
        "preoutcome_validation": {
            "outcome_field_loaded": pre["outcome_field_loaded"],
            "icu_admissions": pre["admissions_validation"]["icu_admissions"],
            "target_admissions": pre["private_panel_rows"],
            "diagnosis_group_counts": {
                "primary": pre["diagnosis_validation"]["primary_group_n"],
                "secondary_only": pre["diagnosis_validation"]["secondary_only_group_n"],
            },
            "same_timestamp_complete_gcs_admissions": pre["gcs_validation"].get("complete_gcs_admissions", 0),
            "gcs_observed_min_max": [numeric_value for numeric_value in [
                pre["gcs_validation"].get("gcs_score_min_observed"),
                pre["gcs_validation"].get("gcs_score_max_observed"),
            ]],
            "numeric_unit_counts_by_itemid": numeric.get("unit_counts_by_itemid", {}),
            "unexpected_unit_rows_by_itemid": numeric.get("unexpected_unit_by_itemid", {}),
            "non_numeric_rows_by_itemid": numeric.get("non_numeric_by_itemid", {}),
            "observed_numeric_extrema_by_itemid": numeric.get("observed_extrema_by_itemid", {}),
        },
        "audit_run": {
            "python": sys.version,
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "bootstrap_replicates": 60,
            "random_seed": 20261112,
            "shared_audit_gates": {
                "min_events": 10, "min_records_per_arm": 10,
                "min_records_per_level": 20, "min_distinct_patients": 20,
                "min_usable_bootstrap_replicates": 20,
            },
            "estimand": "Observed pooled ICU-admission record-weighted qSOFA mortality contrast on common score support; patients are inference clusters.",
            "sources": sources,
            "analysis_code": source_code,
            "derived_artifacts": derived,
        },
    }
    if args.after_outcome:
        manifest["audit_run"]["outcome_join_completed"] = True
    outpath = OUT / "amsterdam_source_manifest.json"
    temporary = outpath.with_name(outpath.name + ".partial")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(outpath)
    print(json.dumps({"manifest": str(outpath.relative_to(ROOT)),
                      "source_files_hashed": len(sources),
                      "code_files_hashed": len(source_code),
                      "numeric_rows_scanned": numeric["numeric_rows_scanned"],
                      "numeric_crc32": numeric["numeric_member_crc32"],
                      "outcome_join_completed": bool(args.after_outcome)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

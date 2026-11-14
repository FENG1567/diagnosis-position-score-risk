#!/usr/bin/env python3
"""Apply the supplementary conditional interval to available standardized panels."""
from __future__ import annotations

import hashlib
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from analyse_panels import SCORES, analysis_frame, normalize_panel  # noqa: E402
from conditional_interval import conditional_design_interval  # noqa: E402
from estimands import direct_contrast  # noqa: E402


OUTPUT_ROOT = ROOT / "outputs" / "v2" / "conditional_validation" / "clinical"
VALIDATION_MANIFEST = ROOT / "outputs" / "v2" / "conditional_validation" / "conditional_run_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def registry() -> list[dict]:
    return [
        {
            "database": "eICU-CRD",
            "path": ROOT / "work" / "v2" / "eicu" / "eicu_disease_panel.csv.gz",
            "panel_type": "standard_disease_panel",
            "application_ready": True,
            "diseases": list(SCORES),
        },
        {
            "database": "MIMIC-IV",
            "path": Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\mimic\mimic_iv_v2_score_panel.csv.gz"),
            "panel_type": "standard_disease_panel",
            "application_ready": True,
            "diseases": list(SCORES),
        },
        {
            "database": "MIMIC-III",
            "path": Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\mimic3\mimic_iii_v2_score_panel.csv.gz"),
            "panel_type": "standard_disease_panel",
            "application_ready": True,
            "diseases": list(SCORES),
        },
        {
            "database": "Zigong",
            "path": Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\zigong\zigong_admission_panel.csv.gz"),
            "panel_type": "standard_disease_panel",
            "application_ready": True,
            "diseases": list(SCORES),
        },
        {
            "database": "AmsterdamUMCdb",
            "path": Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\amsterdam\qsofa_sepsis_icu_outcome.csv.gz"),
            "panel_type": "amsterdam_qsofa_outcome_panel",
            "application_ready": False,
            "pending_reason": "Awaiting official numeric-unit repair and final Amsterdam panel; prior strict panel remains separate.",
            "diseases": ["sepsis"],
            "score_column": "qsofa_main",
            "outcome_column": "icu_death",
            "patient_column": "patientid",
            "admission_column": "admissionid",
        },
        {
            "database": "PEER-adapted-eICU",
            "path": Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2\published_application\adapted_peer_population.csv.gz"),
            "panel_type": "standard_disease_panel",
            "application_ready": True,
            "diseases": ["pneumonia"],
            "interpretation": "Adapted published PEER population; original PEER model results are not reproduced.",
        },
    ]


def freeze_application_config(validation_manifest: dict, config_path: Path,
                              application_id: str) -> dict:
    sources = []
    for item in registry():
        path = Path(item["path"])
        exists = path.is_file()
        source = {
            **{key: value for key, value in item.items() if key != "path"},
            "path": str(path.resolve(strict=False)),
            "available_before_application": exists,
            "sha256_before_application": sha256(path) if exists else None,
        }
        if item["panel_type"] == "standard_disease_panel":
            source["score_columns"] = {
                disease: SCORES[disease][0] for disease in item["diseases"]
            }
        else:
            source["score_columns"] = {"sepsis": item["score_column"]}
        sources.append(source)
    config = {
        "record_type": "conditional_interval_clinical_application_config",
        "application_id": application_id,
        "config_status": "frozen_before_clinical_application",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "validation_benchmark_id": validation_manifest["benchmark_id"],
        "validation_manifest_sha256": sha256(VALIDATION_MANIFEST),
        "sources": sources,
        "analysis_rules": {
            "primary_panel_handling": "Use analyse_panels.normalize_panel and analyse_panels.analysis_frame for standardized panels.",
            "conditional_target": "theta_D = E(sum_i a_i Y_i | observed complete-case design), on actual observed common support and observed pooled-record weights.",
            "interval_method": "conditional_interval.conditional_design_interval at alpha=0.05.",
            "primary_C": "This supplementary analysis does not modify, fill, or replace any primary C status or interval.",
            "missing_inputs": "Missing source panels are listed as pending; no outcomes, scores, or confidence intervals are imputed.",
            "independence_assumption": "Mutually independent patient clusters conditional on the observed design; this is assumed, not verified, for clinical panels.",
            "population_target": "No population-target coverage claim is made from this conditional interval.",
        },
    }
    if config_path.exists():
        raise FileExistsError("Clinical application config already exists; preserve it and start a new application version.")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return config


def adapt_amsterdam(path: Path, item: dict) -> pd.DataFrame:
    panel = pd.read_csv(path, low_memory=False)
    required = [item["patient_column"], item["admission_column"], "grp",
                item["outcome_column"], item["score_column"]]
    missing = [column for column in required if column not in panel]
    if missing:
        raise ValueError(f"Amsterdam panel is missing columns: {missing}")
    adapted = pd.DataFrame({
        "pid": panel[item["patient_column"]],
        "admission_id": panel[item["admission_column"]],
        "disease": "sepsis",
        "grp": panel["grp"],
        "died": panel[item["outcome_column"]],
        "qsofa": panel[item["score_column"]],
    })
    return normalize_panel(adapted)


def _application_record(database: str, disease: str, instrument: str, frame: pd.DataFrame,
                        panel_path: Path, panel_hash: str, peer_note: str | None = None) -> dict:
    required = frame[["pid", "score", "grp", "y"]].copy()
    interval = conditional_design_interval(required, alpha=0.05)
    direct = direct_contrast(required)
    point_difference = (
        abs(float(interval["point"]) - float(direct.estimate))
        if np.isfinite(direct.estimate) and np.isfinite(interval["point"]) else None
    )
    if point_difference is not None and point_difference > 1e-12:
        raise AssertionError("conditional interval point differs from independent supported-record direct contrast")
    emitted = interval["state"] == "conditional interval computed"
    return {
        "database": database,
        "disease": disease,
        "instrument": instrument,
        "conditional_estimand": "theta_D: conditional-design mean contrast on actual observed common support",
        "interval_method": "patient-cluster conditional Hoeffding interval",
        "confidence_level": 0.95,
        "n_records": int(len(required)),
        "n_patients": int(required.pid.nunique()),
        "n_supported_records": int(interval["n_supported_records"]),
        "n_supported_patients": int(interval["n_supported_patients"]),
        "n_common_support_levels": int(interval["levels"]),
        "state": interval["state"],
        "conditional_interval_emitted": bool(emitted),
        "point_pp": 100 * float(interval["point"]) if emitted else None,
        "lower_pp": 100 * float(interval["lower"]) if emitted else None,
        "upper_pp": 100 * float(interval["upper"]) if emitted else None,
        "halfwidth_pp": 100 * float(interval["halfwidth"]) if emitted else None,
        "actual_width_pp": 100 * float(interval["width"]) if emitted else None,
        "full_range_interval": bool(interval["full_range"]) if emitted else None,
        "halfwidth_ge_one": bool(interval["halfwidth_ge_one"]) if emitted else None,
        "sum_squared_cluster_ranges": float(interval["sum_squared_cluster_ranges"]) if emitted else None,
        "direct_contrast_point_difference_abs": point_difference,
        "patient_cluster_independence_assumed_not_verified": True,
        "does_not_modify_or_replace_primary_C": True,
        "source_panel_path": str(panel_path.resolve()),
        "source_panel_sha256": panel_hash,
        "interpretation_note": peer_note,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--application-id", default="run_01",
                        help="Immutable output version, for example run_01 or run_02 after pending panels arrive.")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.application_id):
        raise ValueError("application-id may contain only letters, numbers, underscores, and hyphens")
    output_dir = OUTPUT_ROOT / args.application_id
    output_dir.mkdir(parents=True, exist_ok=True)
    app_config_path = output_dir / "clinical_application_config.json"
    if not VALIDATION_MANIFEST.is_file():
        raise FileNotFoundError("Synthetic conditional validation has not completed; clinical output is gated.")
    validation_manifest = json.loads(VALIDATION_MANIFEST.read_text(encoding="utf-8"))
    if validation_manifest.get("status") != "complete":
        raise RuntimeError("Synthetic conditional validation is incomplete; clinical output is gated.")
    config = freeze_application_config(validation_manifest, app_config_path, args.application_id)

    availability = []
    results = []
    source_hashes = {}
    for item in registry():
        panel_path = Path(item["path"])
        if not item.get("application_ready", True):
            availability.append({
                "database": item["database"],
                "path": str(panel_path.resolve(strict=False)),
                "status": "pending_input_repair",
                "reason": item.get("pending_reason"),
                "diseases_expected": "|".join(item["diseases"]),
                "confidence_intervals_imputed": False,
            })
            continue
        if not panel_path.is_file():
            availability.append({
                "database": item["database"],
                "path": str(panel_path.resolve(strict=False)),
                "status": "pending_panel_missing",
                "diseases_expected": "|".join(item["diseases"]),
                "confidence_intervals_imputed": False,
            })
            continue
        panel_hash = sha256(panel_path)
        source_hashes[item["database"]] = panel_hash
        if item["panel_type"] == "amsterdam_qsofa_outcome_panel":
            normalized = adapt_amsterdam(panel_path, item)
            score_columns = {"sepsis": "qsofa"}
        else:
            normalized = normalize_panel(panel_path)
            score_columns = {disease: SCORES[disease][0] for disease in item["diseases"]}

        available_diseases = []
        for disease in item["diseases"]:
            source = normalized.loc[normalized.disease.eq(disease)].copy()
            if source.empty:
                continue
            instrument = score_columns[disease]
            frame = analysis_frame(source, instrument)
            if frame.empty:
                continue
            available_diseases.append(disease)
            results.append(_application_record(
                item["database"], disease, instrument, frame,
                panel_path, panel_hash, item.get("interpretation")
            ))
        availability.append({
            "database": item["database"],
            "path": str(panel_path.resolve()),
            "status": "applied" if available_diseases else "panel_has_no_analyzable_rows",
            "diseases_expected": "|".join(item["diseases"]),
            "diseases_applied": "|".join(available_diseases),
            "sha256": panel_hash,
            "confidence_intervals_imputed": False,
        })

    pd.DataFrame.from_records(results).to_csv(
        output_dir / "conditional_clinical_application.csv", index=False, encoding="utf-8"
    )
    pd.DataFrame.from_records(availability).to_csv(
        output_dir / "clinical_input_availability.csv", index=False, encoding="utf-8"
    )
    config_hash = sha256(app_config_path)
    (output_dir / "clinical_application_provenance.json").write_text(json.dumps({
        "record_type": "conditional_clinical_application_provenance",
        "status": "complete_available_panels_only",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "application_script_sha256": sha256(Path(__file__).resolve()),
        "config_path": str(app_config_path.resolve()),
        "config_sha256": config_hash,
        "validation_manifest_sha256": sha256(VALIDATION_MANIFEST),
        "conditional_interval_helper_sha256": sha256(HERE.parent / "conditional_interval.py"),
        "source_panel_hashes": source_hashes,
        "available_analysis_count": len(results),
        "pending_source_count": sum(row["status"].startswith("pending_") for row in availability),
        "primary_C_modified": False,
        "raw_patient_records_written": False,
        "interpretation": (
            "Supplementary conditional-design intervals are reported on the observed complete-case design. "
            "Missing panels remain pending. These results do not alter the primary C rule, do not impute intervals, "
            "and do not establish population-target coverage."
        ),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"available_analyses": len(results), "pending_sources": [
        row["database"] for row in availability if row["status"].startswith("pending_")
    ], "output_dir": str(output_dir.resolve())}, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

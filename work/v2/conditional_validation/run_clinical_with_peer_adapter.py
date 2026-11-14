#!/usr/bin/env python3
"""Run the frozen clinical application with a verified in-memory PEER adapter.

The adapted PEER panel contains equivalent ``y`` and ``died`` outcome columns.
The unchanged clinical driver renames ``died`` to ``y``; this wrapper verifies
both columns row by row, then removes only the redundant ``y`` alias in memory
while the driver's existing normalizer reads that source panel.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import analyse_panels  # noqa: E402
import apply_conditional_clinical as application  # noqa: E402


APPLICATION_ID = "run_02"
OUTPUT_DIR = ROOT / "outputs" / "v2" / "conditional_validation" / "clinical" / APPLICATION_ID
BASELINE_CONFIG = ROOT / "outputs" / "v2" / "conditional_validation" / "clinical" / "run_01" / "clinical_application_config.json"
CHECK_PATH = OUTPUT_DIR / "peer_outcome_alias_validation.json"
EXECUTION_PATH = OUTPUT_DIR / "clinical_adapter_execution.json"
PEER_DATABASE = "PEER-adapted-eICU"
ORIGINAL_READ_CSV = pd.read_csv


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _normalized_path(value: object) -> str | None:
    try:
        return os.path.normcase(str(Path(value).resolve()))
    except (TypeError, OSError, ValueError):
        return None


def validate_peer_outcome_aliases(peer_path: Path) -> dict:
    if not BASELINE_CONFIG.is_file():
        raise FileNotFoundError(f"Baseline frozen application config is missing: {BASELINE_CONFIG}")
    baseline = json.loads(BASELINE_CONFIG.read_text(encoding="utf-8"))
    baseline_source = next(
        (item for item in baseline.get("sources", []) if item.get("database") == PEER_DATABASE),
        None,
    )
    if baseline_source is None:
        raise ValueError(f"Baseline config has no {PEER_DATABASE} source entry")

    expected_hash = baseline_source.get("sha256_before_application")
    source_hash = file_sha256(peer_path)
    if not expected_hash or source_hash != expected_hash:
        raise ValueError(
            "PEER source hash differs from the preserved run_01 config; refusing adaptation "
            f"(expected={expected_hash}, observed={source_hash})"
        )

    raw = ORIGINAL_READ_CSV(peer_path, low_memory=False)
    if "y" not in raw.columns or "died" not in raw.columns:
        raise ValueError("PEER source must contain both y and died columns for alias verification")

    y = pd.to_numeric(raw["y"], errors="raise")
    died = pd.to_numeric(raw["died"], errors="raise")
    y_missing = y.isna().to_numpy()
    died_missing = died.isna().to_numpy()
    masks_equal = bool(np.array_equal(y_missing, died_missing))
    jointly_observed = ~y_missing & ~died_missing
    unequal = jointly_observed & ~np.equal(y.to_numpy(), died.to_numpy())
    mismatch = (not masks_equal) or bool(unequal.any())
    mismatch_rows = np.flatnonzero(unequal).tolist()
    if not masks_equal:
        mismatch_rows.extend(np.flatnonzero(y_missing != died_missing).tolist())

    report = {
        "record_type": "peer_duplicate_outcome_alias_validation",
        "application_id": APPLICATION_ID,
        "status": "conflict" if mismatch else "passed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_panel_path": str(peer_path.resolve()),
        "source_panel_sha256": source_hash,
        "run_01_frozen_source_sha256": expected_hash,
        "source_hash_matches_preserved_config": source_hash == expected_hash,
        "n_rows": int(len(raw)),
        "outcome_columns": ["y", "died"],
        "missingness_masks_equal_row_by_row": masks_equal,
        "n_both_missing": int((y_missing & died_missing).sum()),
        "n_y_missing_died_observed": int((y_missing & ~died_missing).sum()),
        "n_died_missing_y_observed": int((~y_missing & died_missing).sum()),
        "n_both_observed": int(jointly_observed.sum()),
        "observed_values_equal_row_by_row": not bool(unequal.any()),
        "n_observed_value_mismatches": int(unequal.sum()),
        "mismatch_row_indices_preview": mismatch_rows[:20],
        "adapter": {
            "scope": PEER_DATABASE,
            "operation": "drop the verified redundant y column in memory before the unchanged panel normalizer runs",
            "outcome_retained": "died",
            "source_panel_modified": False,
            "raw_patient_records_written": False,
            "clinical_application_driver_sha256": file_sha256(Path(application.__file__).resolve()),
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHECK_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if mismatch:
        raise ValueError(
            "PEER y and died outcome aliases disagree; see "
            f"{CHECK_PATH} and do not run the clinical application"
        )
    return report


def main() -> None:
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise FileExistsError(
            f"Application output already contains files; preserve it and choose a new ID: {OUTPUT_DIR}"
        )

    peer_item = next(
        (item for item in application.registry() if item.get("database") == PEER_DATABASE),
        None,
    )
    if peer_item is None:
        raise ValueError(f"Clinical driver registry has no {PEER_DATABASE} entry")
    peer_path = Path(peer_item["path"])
    validation = validate_peer_outcome_aliases(peer_path)
    peer_normalized_path = _normalized_path(peer_path)
    source_hash = validation["source_panel_sha256"]

    def guarded_read_csv(filepath_or_buffer, *args, **kwargs):
        frame = ORIGINAL_READ_CSV(filepath_or_buffer, *args, **kwargs)
        if _normalized_path(filepath_or_buffer) == peer_normalized_path:
            observed_hash = file_sha256(peer_path)
            if observed_hash != source_hash:
                raise RuntimeError("PEER source changed after alias validation; refusing to apply")
            if "y" not in frame.columns or "died" not in frame.columns:
                raise ValueError("PEER columns changed after alias validation; refusing to apply")
            current_y = pd.to_numeric(frame["y"], errors="raise")
            current_died = pd.to_numeric(frame["died"], errors="raise")
            current_y_missing = current_y.isna().to_numpy()
            current_died_missing = current_died.isna().to_numpy()
            if not np.array_equal(current_y_missing, current_died_missing):
                raise ValueError("PEER outcome missingness changed after alias validation")
            observed = ~current_y_missing
            if not np.array_equal(current_y.to_numpy()[observed], current_died.to_numpy()[observed]):
                raise ValueError("PEER outcome values changed after alias validation")
            return frame.drop(columns=["y"])
        return frame

    driver_hash_before = file_sha256(Path(application.__file__).resolve())
    execution = {
        "record_type": "clinical_adapter_execution",
        "application_id": APPLICATION_ID,
        "status": "started",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "peer_outcome_alias_validation_path": str(CHECK_PATH.resolve()),
        "peer_source_panel_sha256": source_hash,
        "clinical_application_driver_sha256_before": driver_hash_before,
    }
    EXECUTION_PATH.write_text(json.dumps(execution, indent=2, ensure_ascii=False), encoding="utf-8")

    try:
        with __import__("unittest.mock", fromlist=["patch"]).patch.object(
            analyse_panels.pd, "read_csv", new=guarded_read_csv
        ):
            sys.argv = [str(Path(application.__file__).resolve()), "--application-id", APPLICATION_ID]
            application.main()
    except BaseException as exc:
        execution.update({
            "status": "failed",
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "error": str(exc),
        })
        EXECUTION_PATH.write_text(json.dumps(execution, indent=2, ensure_ascii=False), encoding="utf-8")
        raise

    driver_hash_after = file_sha256(Path(application.__file__).resolve())
    execution.update({
        "status": "complete",
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "clinical_application_driver_sha256_after": driver_hash_after,
        "clinical_application_driver_unchanged": driver_hash_before == driver_hash_after,
        "peer_duplicate_y_dropped_in_memory": True,
        "source_panel_modified": False,
        "primary_C_modified": False,
    })
    EXECUTION_PATH.write_text(json.dumps(execution, indent=2, ensure_ascii=False), encoding="utf-8")
    if driver_hash_before != driver_hash_after:
        raise RuntimeError("Clinical application driver changed during the adapter run")


if __name__ == "__main__":
    main()

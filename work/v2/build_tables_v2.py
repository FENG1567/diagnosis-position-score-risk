#!/usr/bin/env python3
"""Freeze v2 aggregate outputs and build the six JCE tables.

The builder only reads structured aggregate outputs (CSV/JSON/Markdown) under
outputs/v2. It does not open patient panels, source data, raw rare text, logs, or
replicate-level simulation files. Every copied aggregate is hash-bound before
it is read. A preview can be built from currently available sources; final mode
requires the complete four-database analysis, including MIMIC-III.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "outputs" / "v2"
ANALYSIS = V2 / "analysis"
DB_DIRS = {
    "eICU-CRD": "eicu",
    "MIMIC-IV": "mimic_iv",
    "MIMIC-III": "mimic_iii",
    "Zigong": "zigong",
}
DB_ORDER = ["eICU-CRD", "MIMIC-IV", "MIMIC-III", "Zigong"]
PRIMARY_GROUPS = [
    ("eICU-CRD", "sepsis"), ("eICU-CRD", "pneumonia"),
    ("MIMIC-IV", "sepsis"), ("MIMIC-IV", "pneumonia"),
]
US_CONDITIONS = ["sepsis", "pneumonia", "pancreatitis", "heart failure", "COPD"]
ZIGONG_MAIN_CONDITIONS = ["sepsis", "pneumonia", "pancreatitis", "COPD"]
SCORES = {
    "sepsis": "qSOFA",
    "pneumonia": "CURB-65",
    "pancreatitis": "BISAP-4",
    "heart failure": "qSOFA",
    "COPD": "qSOFA",
}
TABLE5_DESIGNS = [
    "null_balanced_iid",
    "repeated_admissions_cross_group",
    "rare_common_support_holdout",
    "near_boundary_risks",
    "few_large_clusters",
]
TABLE5_POLICIES = ["A", "B", "C"]
SIM_POLICY_ORDER = ["A", "B", "C", "D", "A_legacy_fixed_weight_IF", "A_fixed_true_weights"]
AGGREGATE_SUFFIXES = {".csv", ".json", ".md"}
EXCLUDED_RELATIVE_PARTS = {
    "superseded_rounding_pilot_20261112_2049",
    "replicate_checkpoints",
    "delivery",
    "delivery_preview",
    "mimic3_repair_stage_20261113",
    "mimic_iii_before_mv_bp_repair",
    "strict_row_units",
    "adapter_attempts",
}
EXCLUDED_FILE_PATTERNS = [
    re.compile(r"^benchmark_replicate_metrics\.csv$", re.I),
    re.compile(r"^benchmark_replicates_.*\.csv$", re.I),
    re.compile(r"^replicate_results\.csv$", re.I),
    re.compile(r"^per_level_replicate_results\.csv$", re.I),
    re.compile(r"^conditional_replicate_results\.csv$", re.I),
    re.compile(r"^checkpoint_.*\.(csv|json)$", re.I),
]
EXCLUDED_FINAL_SOURCE_FILES = {
    'eicu/eicu_v2_pilot_summary.json',
    'amsterdam/dictionary_unit_repair/strict_reconstruction_failure.json',
    'level_validation/first_attempt_provenance.json',
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hashes(path: Path) -> tuple[str, str, int]:
    raw = path.read_bytes()
    return hashlib.md5(raw).hexdigest(), sha256_bytes(raw), len(raw)


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def csv_write(path: Path, headers: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def is_numeric_text(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if text == "":
        return False
    try:
        number = float(text)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number)


def number(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def count_text(value: Any) -> str:
    value_num = number(value)
    if value_num is None:
        return "—"
    if not math.isclose(value_num, round(value_num), abs_tol=1e-9):
        raise ValueError(f"Expected an integer count, got {value!r}")
    return f"{int(round(value_num)):,}"


def score_text(value: Any) -> str:
    value_num = number(value)
    if value_num is None:
        return "—"
    return str(int(value_num)) if math.isclose(value_num, round(value_num), abs_tol=1e-9) else f"{value_num:g}"


def decimal_text(value: Any, places: int = 2) -> str:
    value_num = number(value)
    return "—" if value_num is None else f"{value_num:.{places}f}"


def pct_text(value: Any, places: int = 2) -> str:
    value_num = number(value)
    return "—" if value_num is None else f"{value_num:.{places}f}%"


def fraction_pct_text(value: Any, places: int = 2) -> str:
    value_num = number(value)
    return "—" if value_num is None else f"{100 * value_num:.{places}f}%"


def interval_text(lo: Any, hi: Any, places: int = 2) -> str:
    low, high = number(lo), number(hi)
    if low is None and high is None:
        return "not computed"
    if low is None or high is None:
        raise ValueError(f"Only one CI endpoint is available: {lo!r}, {hi!r}")
    return f"[{low:.{places}f}, {high:.{places}f}]"


def md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


@dataclass(frozen=True)
class CellRef:
    source_file: str
    physical_row: int
    source_column: str
    raw_value: str


class CSVSource:
    def __init__(self, original_path: Path, snapshot_path: Path, relative_path: str):
        self.original_path = original_path
        self.snapshot_path = snapshot_path
        self.relative_path = relative_path
        self.rows: list[dict[str, str | int]] = []
        with snapshot_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            self.headers = list(reader.fieldnames or [])
            for physical_row, row in enumerate(reader, start=2):
                self.rows.append({"_physical_row": physical_row, **row})

    def ref(self, row: dict[str, Any], column: str) -> CellRef:
        if column not in row:
            raise KeyError(f"Missing {column!r} in {self.relative_path}, physical row {row.get('_physical_row')}")
        return CellRef(self.relative_path, int(row["_physical_row"]), column, str(row[column]))


class Table:
    def __init__(self, table_id: str, title: str, headers: list[str], notes: list[str] | None = None):
        self.table_id = table_id
        self.title = title
        self.headers = headers
        self.notes = notes or []
        self.rows: list[dict[str, Any]] = []

    def add(self, row_id: str, values: list[Any], refs: dict[str, list[CellRef]] | None = None,
            *, bold: bool = False, section: bool = False) -> None:
        if len(values) != len(self.headers):
            raise ValueError(f"{self.table_id}/{row_id}: expected {len(self.headers)} fields, got {len(values)}")
        refs = refs or {}
        row = dict(zip(self.headers, ["" if value is None else str(value) for value in values]))
        row["_row_id"] = row_id
        row["_bold"] = bold
        row["_section"] = section
        self.rows.append(row)
        for column, value in zip(self.headers, values):
            column_refs = refs.get(column, [])
            if is_numeric_text(value) and not column_refs:
                raise ValueError(f"Numeric cell lacks provenance: {self.table_id}/{row_id}/{column}={value}")
            for ref in column_refs:
                PROVENANCE.append({
                    "output_table": self.table_id,
                    "output_row": row_id,
                    "output_column": column,
                    "displayed_value": str(value),
                    "source_file": ref.source_file,
                    "source_physical_row_header_1": ref.physical_row,
                    "source_column": ref.source_column,
                    "raw_value": ref.raw_value,
                    "formatting_or_derivation": DERIVATION.get((self.table_id, row_id, column), "Copied/formatted from the hash-frozen aggregate source cell."),
                })

    def section(self, row_id: str, label: str) -> None:
        self.add(row_id, [label] + [""] * (len(self.headers) - 1), section=True)


PROVENANCE: list[dict[str, Any]] = []
DERIVATION: dict[tuple[str, str, str], str] = {}


def set_derivation(table_id: str, row_id: str, column: str, text: str) -> None:
    DERIVATION[(table_id, row_id, column)] = text


def source_ref(source: CSVSource, row: dict[str, Any], *columns: str) -> list[CellRef]:
    return [source.ref(row, column) for column in columns]


def read_json_snapshot(relative_path: str, snapshot_map: dict[str, Path]) -> Any:
    path = snapshot_map.get(relative_path)
    if path is None:
        raise FileNotFoundError(f"Aggregate JSON missing from snapshot: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def aggregate_output_files() -> list[Path]:
    files: list[Path] = []
    if not V2.exists():
        return files
    for path in sorted(V2.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in AGGREGATE_SUFFIXES:
            continue
        rel = path.relative_to(V2)
        if rel.as_posix() in EXCLUDED_FINAL_SOURCE_FILES:
            continue
        if any(part in EXCLUDED_RELATIVE_PARTS or part.startswith("delivery_preview") or part.startswith("pilot_seed_") for part in rel.parts):
            continue
        # Only final immutable applications are eligible for the new freeze.
        # Older source interpretations and failed runs remain in the workspace.
        if rel.parts[0] == "bootstrap_precision" and (len(rel.parts) < 2 or rel.parts[1] != "run02_final_sources"):
            continue
        if rel.parts[0] == "conditional_validation" and len(rel.parts) > 1 and rel.parts[1] == "clinical" and (len(rel.parts) < 3 or rel.parts[2] != "run_03_final"):
            continue
        if rel.parts[0] == "amsterdam" and (len(rel.parts) < 2 or rel.parts[1] != "dictionary_unit_repair"):
            continue
        if any(pattern.match(path.name) for pattern in EXCLUDED_FILE_PATTERNS):
            continue
        if path.name == "SUPERSEDED.txt":
            continue
        files.append(path)
    return files


def inspect_csv(path: Path) -> tuple[int, list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader, [])
        row_count = sum(1 for _ in reader)
    return row_count, headers


def source_code_dependencies() -> list[Path]:
    candidates = [
        ROOT / "work/v2/build_tables_v2.py",
        ROOT / "work/v2/analyse_panels.py",
        ROOT / "work/v2/estimands.py",
        ROOT / "work/v2/robustness.py",
        ROOT / "work/v2/audit/cohort_definition_audit.py",
        ROOT / "work/v2/audit/benchmark.py",
        ROOT / "work/v2/summarize_target_coverage.py",
        ROOT / "work/v2/sparse_boundary_validation.py",
        ROOT / "work/v2/conditional_interval.py",
        ROOT / "work/v2/conditional_validation/run_final_clinical.py",
        ROOT / "work/v2/conditional_validation/apply_conditional_clinical.py",
        ROOT / "work/v2/primary_multiplicity_sensitivity.py",
        ROOT / "work/v2/hospital_cluster_sensitivity.py",
        ROOT / "work/v2/eicu_measurement_sensitivity.py",
    ]
    return [path for path in candidates if path.is_file()]


def freeze_aggregate_outputs(stage: Path) -> tuple[dict[str, Path], list[dict[str, Any]], list[str]]:
    files = aggregate_output_files()
    if not files:
        raise RuntimeError(f"No aggregate CSV/JSON/Markdown outputs found under {V2}")
    snapshot_root = stage / "source_snapshot"
    snapshot_map: dict[str, Path] = {}
    manifest_rows: list[dict[str, Any]] = []
    copied: list[str] = []
    for original in files:
        rel = relative(ROOT, original)
        md5_before, sha_before, size_before = file_hashes(original)
        destination = snapshot_root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, destination)
        md5_copy, sha_copy, size_copy = file_hashes(destination)
        md5_after, sha_after, size_after = file_hashes(original)
        if (md5_before, sha_before, size_before) != (md5_copy, sha_copy, size_copy):
            raise RuntimeError(f"Source snapshot copy hash mismatch: {rel}")
        if (md5_before, sha_before, size_before) != (md5_after, sha_after, size_after):
            raise RuntimeError(f"Aggregate changed while being frozen: {rel}")
        row_count: int | str = ""
        columns: list[str] = []
        if original.suffix.lower() == ".csv":
            row_count, columns = inspect_csv(destination)
        manifest_rows.append({
            "record_type": "aggregate_output",
            "source_file": rel,
            "snapshot_file": relative(stage, destination),
            "bytes": size_before,
            "physical_csv_rows_including_header": row_count if row_count == "" else row_count + 1,
            "data_rows": row_count,
            "column_count": len(columns),
            "columns": json.dumps(columns, ensure_ascii=False),
            "md5": md5_before,
            "sha256": sha_before,
        })
        snapshot_map[rel] = destination
        copied.append(rel)

    config_dependency = ROOT / "work/v2/audit/benchmark_config.json"
    if config_dependency.is_file():
        rel = relative(ROOT, config_dependency)
        destination = snapshot_root / "dependencies" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        md5_before, sha_before, size_before = file_hashes(config_dependency)
        shutil.copyfile(config_dependency, destination)
        md5_copy, sha_copy, size_copy = file_hashes(destination)
        md5_after, sha_after, size_after = file_hashes(config_dependency)
        if (md5_before, sha_before, size_before) != (md5_copy, sha_copy, size_copy) or (md5_before, sha_before, size_before) != (md5_after, sha_after, size_after):
            raise RuntimeError(f"Configuration changed while being frozen: {rel}")
        manifest_rows.append({
            "record_type": "analysis_config_dependency",
            "source_file": rel,
            "snapshot_file": relative(stage, destination),
            "bytes": size_before,
            "physical_csv_rows_including_header": "",
            "data_rows": "",
            "column_count": "",
            "columns": "",
            "md5": md5_before,
            "sha256": sha_before,
        })
        snapshot_map[rel] = destination
        copied.append(rel)

    for dependency in source_code_dependencies():
        md5, sha, size = file_hashes(dependency)
        manifest_rows.append({
            "record_type": "code_dependency",
            "source_file": relative(ROOT, dependency),
            "snapshot_file": "",
            "bytes": size,
            "physical_csv_rows_including_header": "",
            "data_rows": "",
            "column_count": "",
            "columns": "",
            "md5": md5,
            "sha256": sha,
        })
    return snapshot_map, manifest_rows, copied


def load_sources(snapshot_map: dict[str, Path], mode: str) -> tuple[dict[str, dict[str, CSVSource]], dict[str, Any]]:
    data: dict[str, dict[str, CSVSource]] = {}
    json_data: dict[str, Any] = {}
    required_dbs = ["eICU-CRD", "MIMIC-IV", "Zigong"]
    if mode == "final":
        required_dbs = DB_ORDER
    for database in required_dbs:
        folder = DB_DIRS[database]
        key = database
        data[key] = {}
        required_files = ["summary.csv", "levels.csv", "robustness.csv", "timing.csv",
                          "sensitivity.csv", "selection.csv", "missing_bounds.csv",
                          "sparse_level_sensitivity.csv", "fine_cell_counts.csv"]
        for name in required_files:
            rel = f"outputs/v2/analysis/{folder}/{name}"
            path = snapshot_map.get(rel)
            if path is None:
                # Empty timing/robustness exports are required to make the output contract explicit.
                if name in {"timing.csv", "robustness.csv"}:
                    continue
                raise FileNotFoundError(f"Required aggregate input missing: {rel}")
            data[key][name[:-4]] = CSVSource(ROOT / rel, path, rel)
        expected_summary = 5
        if "summary" not in data[key] or len(data[key]["summary"].rows) != expected_summary:
            found = len(data[key]["summary"].rows) if "summary" in data[key] else 0
            raise RuntimeError(f"{database} needs {expected_summary} aggregate condition rows; found {found}")
        prov_rel = f"outputs/v2/analysis/{folder}/analysis_provenance.json"
        if prov_rel in snapshot_map:
            json_data[f"analysis_provenance:{database}"] = read_json_snapshot(prov_rel, snapshot_map)

    if mode == "preview" and DB_DIRS["MIMIC-III"] in {p.name for p in (ANALYSIS.iterdir() if ANALYSIS.exists() else [])}:
        pass

    for rel, label in [
        ("outputs/v2/audit/confirmatory_v2/benchmark_summary.csv", "benchmark_summary"),
        ("outputs/v2/audit/confirmatory_v2/benchmark_target_and_coverage_denominators.csv", "benchmark_denominators"),
        ("outputs/v2/audit/confirmatory_v2/benchmark_paired_comparisons.csv", "benchmark_pairs"),
        ("outputs/v2/sparse_boundary_validation/strategy_summary.csv", "sparse_summary"),
    ]:
        if rel not in snapshot_map:
            raise FileNotFoundError(f"Required simulation aggregate missing: {rel}")
        data[label] = {"table": CSVSource(ROOT / rel, snapshot_map[rel], rel)}
    for rel, label in [
        ("outputs/v2/audit/confirmatory_v2/benchmark_run_manifest.json", "benchmark_manifest"),
        ("outputs/v2/audit/confirmatory_v2/benchmark_run_state.json", "benchmark_state"),
        ("outputs/v2/sparse_boundary_validation/frozen_config.json", "sparse_config"),
        ("outputs/v2/sparse_boundary_validation/provenance.json", "sparse_provenance"),
    ]:
        if rel in snapshot_map:
            json_data[label] = read_json_snapshot(rel, snapshot_map)
    config_rel = "work/v2/audit/benchmark_config.json"
    if config_rel in snapshot_map:
        json_data["benchmark_config"] = read_json_snapshot(config_rel, snapshot_map)
    return data, json_data


def get_source(data: dict[str, dict[str, CSVSource]], database: str, name: str) -> CSVSource:
    try:
        return data[database][name]
    except KeyError as exc:
        raise FileNotFoundError(f"Missing aggregate table {database}/{name}.csv") from exc


def row_index(source: CSVSource, keys: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]:
    index: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in source.rows:
        key = tuple(str(row[column]) for column in keys)
        if key in index:
            raise RuntimeError(f"Duplicate key {key!r} in {source.relative_path}")
        index[key] = row
    return index


def assert_ci_fields(source: CSVSource, row: dict[str, Any], status_column: str,
                     low_column: str, high_column: str, label: str) -> None:
    status = str(row.get(status_column, "")).strip().lower()
    low, high = number(row.get(low_column)), number(row.get(high_column))
    if status == "computed":
        if low is None or high is None:
            raise RuntimeError(f"{label}: computed CI lacks both endpoints in {source.relative_path} row {row['_physical_row']}")
        if low > high:
            raise RuntimeError(f"{label}: reversed CI endpoints in {source.relative_path} row {row['_physical_row']}")
    elif low is not None or high is not None:
        raise RuntimeError(f"{label}: noncomputed CI has numeric endpoint in {source.relative_path} row {row['_physical_row']}")


def run_data_checks(data: dict[str, dict[str, CSVSource]], json_data: dict[str, Any], mode: str) -> dict[str, Any]:
    results: dict[str, Any] = {"mode": mode, "datasets": {}, "simulation": {}, "expected_table_shapes": {}}
    for database in [db for db in DB_ORDER if db in data]:
        summary_source = get_source(data, database, "summary")
        levels_source = get_source(data, database, "levels")
        summaries = row_index(summary_source, ("database", "disease"))
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in levels_source.rows:
            key = (str(row["database"]), str(row["disease"]))
            grouped.setdefault(key, []).append(row)
            n = number(row["n"])
            never, primary = number(row["n_never"]), number(row["n_primary"])
            if None in (n, never, primary) or not math.isclose(n or 0, (never or 0) + (primary or 0), abs_tol=1e-8):
                raise RuntimeError(f"Per-level record reconciliation failed: {database}/{row['disease']} level {row['level']}")
            for count_column, event_column in [("n_never", "events_never"), ("n_primary", "events_primary")]:
                count, events = number(row[count_column]), number(row[event_column])
                if count is None or events is None or events < 0 or events > count:
                    raise RuntimeError(f"Invalid event count in {levels_source.relative_path} row {row['_physical_row']}")
            for status, lo, hi, label in [
                ("risk_never_ci_status", "risk_never_ci_pp_lo", "risk_never_ci_pp_hi", "never risk"),
                ("risk_primary_ci_status", "risk_primary_ci_pp_lo", "risk_primary_ci_pp_hi", "primary risk"),
                ("delta_ci_status", "delta_ci_pp_lo", "delta_ci_pp_hi", "delta_s"),
            ]:
                if lo in row and hi in row:
                    assert_ci_fields(levels_source, row, status, lo, hi, f"{database}/{row['disease']}/{label}")
            weight = number(row.get("weight"))
            if weight is None or weight < 0 or weight > 1 + 1e-8:
                raise RuntimeError(f"Invalid record weight at {levels_source.relative_path}:{row['_physical_row']}")
            for risk_column, events_column, records_column in [
                ("risk_never", "events_never", "n_never"), ("risk_primary", "events_primary", "n_primary")
            ]:
                risk = number(row.get(risk_column))
                records = number(row.get(records_column))
                events = number(row.get(events_column))
                if risk is not None and records and events is not None:
                    exact = 100 * events / records
                    if abs(exact - risk) > 0.02:
                        raise RuntimeError(f"Risk/count reconciliation failed at {levels_source.relative_path}:{row['_physical_row']}")
            risk_n, risk_p, diff = number(row.get("risk_never")), number(row.get("risk_primary")), number(row.get("diff_pp"))
            if None not in (risk_n, risk_p, diff) and abs((risk_n - risk_p) - diff) > 0.03:
                raise RuntimeError(f"Per-level risk difference reconciliation failed at {levels_source.relative_path}:{row['_physical_row']}")

        db_checks: dict[str, Any] = {"summary_rows": len(summary_source.rows), "level_rows": len(levels_source.rows), "cells": {}}
        for key, summary in summaries.items():
            levels = grouped.get(key, [])
            def val(column: str) -> float:
                result = number(summary.get(column))
                if result is None:
                    raise RuntimeError(f"Missing numeric summary field {column} in {summary_source.relative_path}:{summary['_physical_row']}")
                return result
            n = sum(number(row["n"]) or 0 for row in levels)
            n_never = sum(number(row["n_never"]) or 0 for row in levels)
            n_primary = sum(number(row["n_primary"]) or 0 for row in levels)
            if not levels:
                if val("n_shared_primary") or val("n_shared_never") or val("n"):
                    raise RuntimeError(f"Summary has supported records but no level rows for {key}")
            for column, total in [("n", n), ("n_shared_never", n_never), ("n_shared_primary", n_primary)]:
                if not math.isclose(val(column), total, abs_tol=1e-8):
                    raise RuntimeError(f"Summary/level count mismatch for {key} field {column}: {val(column)} vs {total}")
            if levels:
                weights = [number(row["weight"]) or 0 for row in levels]
                if not math.isclose(sum(weights), 1.0, abs_tol=2e-7):
                    raise RuntimeError(f"Record weights do not sum to 1 for {key}: {sum(weights)}")
                level_estimate = sum((number(row.get("weight")) or 0) * (number(row.get("diff_pp")) or 0) for row in levels)
                if abs(level_estimate - val("delta_w_pp")) > 0.03:
                    raise RuntimeError(f"Weighted point estimate does not reconcile for {key}: {level_estimate} vs {val('delta_w_pp')}")
            for arm in ("primary", "never"):
                eligible = val(f"n_eligible_{arm}")
                complete = val(f"n_complete_{arm}")
                shared = val(f"n_shared_{arm}")
                if not (eligible >= complete >= shared >= 0):
                    raise RuntimeError(f"Eligibility/completeness/support counts not nested for {key}/{arm}")
            if int(round(val("levels"))) != len(levels):
                raise RuntimeError(f"Summary supported level count mismatch for {key}: {val('levels')} vs {len(levels)}")
            summary_status = str(summary.get("interval_status", "")).strip().lower()
            lo, hi = number(summary.get("lo_pp")), number(summary.get("hi_pp"))
            if summary_status == "computed":
                if lo is None or hi is None or lo > hi:
                    raise RuntimeError(f"Summary computed CI not aligned with endpoints for {key}")
            elif lo is not None or hi is not None:
                raise RuntimeError(f"Summary noncomputed CI has endpoint for {key}")
            db_checks["cells"]["|".join(key)] = {
                "levels": len(levels),
                "shared_records": int(round(n)),
                "weight_sum": sum(number(row["weight"]) or 0 for row in levels),
                "summary_interval_status": summary.get("interval_status"),
            }
        results["datasets"][database] = db_checks

    expected_main_cells = {db: (5 if db in {"eICU-CRD", "MIMIC-IV", "MIMIC-III"} else 4)
                           for db in results["datasets"]}
    results["expected_table_shapes"] = {
        "table1_primary_cells": sum(1 for db, disease in PRIMARY_GROUPS if db in data),
        "table1_level_rows": sum(len([r for r in get_source(data, db, "levels").rows if r.get("disease") == disease])
                                 for db, disease in PRIMARY_GROUPS if db in data),
        "table2_database_condition_cells": sum(expected_main_cells.values()),
        "table2_final_expected_cells": 19,
        "table4_eicu_comparison_rows": 6,
        "table5_selected_benchmark_rows": 15,
        "table5_sparse_rows": 6,
        "table6_all_benchmark_c_rows": 11,
        "table6_sparse_c_rows": 2,
    }
    if mode == "final":
        if results["expected_table_shapes"]["table1_primary_cells"] != 4:
            raise RuntimeError("Final mode requires all four primary Table 1 cells")
        if results["expected_table_shapes"]["table2_database_condition_cells"] != 19:
            raise RuntimeError("Final mode requires the original 19 Table 2 cells")
        for db in DB_ORDER:
            if db not in data:
                raise RuntimeError(f"Final mode missing {db} aggregate analysis")

    bench = data["benchmark_summary"]["table"]
    denom = data["benchmark_denominators"]["table"]
    bench_idx = row_index(bench, ("design", "policy"))
    denom_idx = row_index(denom, ("design", "policy"))
    if set(bench_idx) != set(denom_idx):
        raise RuntimeError("Benchmark summary and target/coverage denominator keys differ")
    for key, row in bench_idx.items():
        drow = denom_idx[key]
        check_pairs = [("interval_emission_pct", "interval_output_pct"),
                       ("off_target_interval_pct", "off_target_output_pct")]
        for left, right in check_pairs:
            a, b = number(row.get(left)), number(drow.get(right))
            if a is not None and b is not None and abs(a - b) > 0.011:
                raise RuntimeError(f"Benchmark metric mismatch for {key}: {left}={a}, {right}={b}")
    config = json_data.get("benchmark_config", {})
    design_names = [item.get("name") for item in config.get("designs", []) if isinstance(item, dict)]
    if design_names and len(design_names) != 11:
        raise RuntimeError(f"Confirmatory benchmark expected 11 DGPs; found {len(design_names)}")
    for design in TABLE5_DESIGNS:
        for policy in TABLE5_POLICIES:
            if (design, policy) not in bench_idx:
                raise RuntimeError(f"Table 5 required benchmark row is absent: {design}/{policy}")
    for design in design_names:
        if (design, "C") not in bench_idx:
            raise RuntimeError(f"Table 6 required C row is absent: {design}")
    sparse_rows = row_index(data["sparse_summary"]["table"], ("design", "strategy"))
    for design in ("fine_cells", "tiny_arm"):
        for strategy in ("A", "B", "C", "D"):
            if (design, strategy) not in sparse_rows:
                raise RuntimeError(f"Sparse validation row missing: {design}/{strategy}")
    results["simulation"] = {
        "benchmark_summary_rows": len(bench.rows),
        "benchmark_dgp_count": len(design_names),
        "benchmark_designs": design_names,
        "benchmark_replicates_per_design": (json_data.get("benchmark_manifest", {}).get("outer_replicates_per_design")),
        "sparse_summary_rows": len(data["sparse_summary"]["table"].rows),
        "selected_table5_designs": TABLE5_DESIGNS,
    }
    return results


def ci_display(row: dict[str, Any], source: CSVSource, lo: str, hi: str, status: str,
                table_id: str, row_id: str, column: str, places: int = 2) -> tuple[str, list[CellRef]]:
    state = str(row.get(status, "")).strip()
    low, high = row.get(lo), row.get(hi)
    refs: list[CellRef] = []
    if number(low) is not None and number(high) is not None:
        refs = source_ref(source, row, lo, hi)
        display = interval_text(low, high, places)
        set_derivation(table_id, row_id, column, "Displayed source confidence-interval endpoints with fixed decimal formatting.")
    else:
        display = "not computed"
        if status in row:
            refs = source_ref(source, row, status)
        set_derivation(table_id, row_id, column, "No interval was added; the source interval status is shown separately.")
    return display, refs


def build_table1(data: dict[str, dict[str, CSVSource]]) -> Table:
    table = Table("T1", "Table 1. Score-level mortality differences in the four primary analysis groups",
                  ["Database", "Condition", "Instrument", "Score level", "Total supported records",
                   "Never-primary records / patients", "Never-primary deaths / risk (95% CI; status)",
                   "Primary records / patients", "Primary deaths / risk (95% CI; status)",
                   "δ_s (percentage points; 95% CI; status)", "Pooled observed record weight", "CI method"],
                  [
                      "At each score level, δ_s is observed mortality among never-primary records minus observed mortality among primary records. Repeated admission records remain separate in the record-weighted target; patient clustering handles dependence.",
                      "Risk intervals are the source-issued patient-cluster sandwich intervals transformed on the logit scale. δ_s intervals are patient-cluster sandwich Wald intervals. Each interval is separately gated; withheld intervals remain withheld and retain their source status.",
                      "The displayed weight is the pooled observed admission-record share for that supported score level. It is not a patient share or an external population weight.",
                  ])
    for database, disease in PRIMARY_GROUPS:
        if database not in data:
            continue
        source = get_source(data, database, "levels")
        matching = [r for r in source.rows if r["disease"] == disease]
        table.section(f"section-{database}-{disease}", f"{database} — {disease}")
        for row in matching:
            row_id = f"{database}|{disease}|{score_text(row['level'])}"
            score = score_text(row["level"])
            total = count_text(row["n"])
            n_never = f"{count_text(row['n_never'])} / {count_text(row['patients_never'])}"
            n_primary = f"{count_text(row['n_primary'])} / {count_text(row['patients_primary'])}"
            ci_never = interval_text(row.get("risk_never_ci_pp_lo"), row.get("risk_never_ci_pp_hi"))
            ci_primary = interval_text(row.get("risk_primary_ci_pp_lo"), row.get("risk_primary_ci_pp_hi"))
            ci_delta = interval_text(row.get("delta_ci_pp_lo"), row.get("delta_ci_pp_hi"))
            risk_never = (f"{count_text(row['events_never'])}/{count_text(row['n_never'])}; "
                          f"{decimal_text(row['risk_never'])}% {ci_never}; {row['risk_never_ci_status']}")
            risk_primary = (f"{count_text(row['events_primary'])}/{count_text(row['n_primary'])}; "
                            f"{decimal_text(row['risk_primary'])}% {ci_primary}; {row['risk_primary_ci_status']}")
            delta = f"{decimal_text(row['diff_pp'])} {ci_delta}; {row['delta_ci_status']}"
            weight = decimal_text(row["weight"], 6)
            refs = {
                "Score level": source_ref(source, row, "level"),
                "Total supported records": source_ref(source, row, "n"),
                "Never-primary records / patients": source_ref(source, row, "n_never", "patients_never"),
                "Never-primary deaths / risk (95% CI; status)": source_ref(source, row, "events_never", "n_never", "risk_never", "risk_never_ci_pp_lo", "risk_never_ci_pp_hi", "risk_never_ci_status"),
                "Primary records / patients": source_ref(source, row, "n_primary", "patients_primary"),
                "Primary deaths / risk (95% CI; status)": source_ref(source, row, "events_primary", "n_primary", "risk_primary", "risk_primary_ci_pp_lo", "risk_primary_ci_pp_hi", "risk_primary_ci_status"),
                "δ_s (percentage points; 95% CI; status)": source_ref(source, row, "diff_pp", "delta_ci_pp_lo", "delta_ci_pp_hi", "delta_ci_status"),
                "Pooled observed record weight": source_ref(source, row, "weight"),
            }
            for col in ["Never-primary deaths / risk (95% CI; status)", "Primary deaths / risk (95% CI; status)", "δ_s (percentage points; 95% CI; status)"]:
                set_derivation("T1", row_id, col, "Composite cell combines source counts/risks, source CI endpoints when computed, and the source CI status; risk and δ_s intervals are not imputed.")
            set_derivation("T1", row_id, "Pooled observed record weight", "Rounded to six decimal places for display; source weight retained in provenance.")
            table.add(row_id, [database, disease, SCORES[disease], score, total, n_never, risk_never,
                               n_primary, risk_primary, delta, weight,
                               "Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI"], refs)
    return table


def main_table2_cells(mode: str, data: dict[str, dict[str, CSVSource]]) -> list[tuple[str, str]]:
    cells: list[tuple[str, str]] = []
    for db in [d for d in DB_ORDER if d in data]:
        diseases = ZIGONG_MAIN_CONDITIONS if db == "Zigong" else US_CONDITIONS
        summary = get_source(data, db, "summary")
        available = {str(row["disease"]) for row in summary.rows}
        for disease in diseases:
            if disease in available:
                cells.append((db, disease))
            elif mode == "final":
                raise RuntimeError(f"Final Table 2 cell missing: {db}/{disease}")
    if mode == "final" and len(cells) != 19:
        raise RuntimeError(f"Final Table 2 requires 19 source-condition cells; found {len(cells)}")
    return cells


def build_table2(data: dict[str, dict[str, CSVSource]], mode: str) -> Table:
    table = Table("T2", "Table 2. Database-condition eligible cohorts and weighted summaries",
                  ["Database", "Condition / instrument", "Primary eligible → complete (incomplete excluded) → shared; complete outside support",
                   "Never-primary eligible → complete (incomplete excluded) → shared; complete outside support",
                   "Common-support score levels", "Computed δ_s CIs excluding zero / computed δ_s CIs",
                   "Δ_w weighted summary (percentage points)", "95% patient-cluster CI for Δ_w weighted summary", "Summary interval status"],
                  [
                      "Eligible records are source-classified records; complete records have complete score components and a known outcome. Shared counts are the records retained on observed common score support. The counts in parentheses are calculated as eligible minus complete, then complete minus shared.",
                      "Δ_w is a weighted summary over common score levels using pooled observed admission-record shares. It is not a score-level δ_s. Summary intervals and per-level intervals have separate gates; a point estimate is retained when an interval is withheld.",
                      "The per-level interval count uses only source-issued δ_s CIs; the denominator is the number of levels with computed δ_s CIs. The aggregate inputs report the number of common-support score levels, not the count of unsupported score values by arm; complete records outside common support are shown explicitly.",
                      "Pancreatitis rows are bold. The instrument is BISAP-4 and omits pleural effusion; it should not be interpreted as full BISAP. qSOFA applications to heart failure and COPD are outside the instrument's intended use. Zigong heart failure is supplemental and is not part of the original 19-cell table.",
                      "Zigong uses the source-defined hospital-mortality classification based on discharge status. The endpoint definition and discharge-status combination checks are included in the frozen aggregate source snapshot.",
                  ])
    for database, disease in main_table2_cells(mode, data):
        summary_source = get_source(data, database, "summary")
        level_source = get_source(data, database, "levels")
        summary = row_index(summary_source, ("database", "disease"))[(database, disease)]
        level_rows = [r for r in level_source.rows if r["database"] == database and r["disease"] == disease]
        row_id = f"{database}|{disease}"
        primary_counts = (f"{count_text(summary['n_eligible_primary'])} → {count_text(summary['n_complete_primary'])} "
                          f"({count_text((number(summary['n_eligible_primary']) or 0) - (number(summary['n_complete_primary']) or 0))} excluded) → "
                          f"{count_text(summary['n_shared_primary'])} ({count_text((number(summary['n_complete_primary']) or 0) - (number(summary['n_shared_primary']) or 0))} outside support)")
        never_counts = (f"{count_text(summary['n_eligible_never'])} → {count_text(summary['n_complete_never'])} "
                        f"({count_text((number(summary['n_eligible_never']) or 0) - (number(summary['n_complete_never']) or 0))} excluded) → "
                        f"{count_text(summary['n_shared_never'])} ({count_text((number(summary['n_complete_never']) or 0) - (number(summary['n_shared_never']) or 0))} outside support)")
        ci_rows = [r for r in level_rows if str(r.get("delta_ci_status", "")).lower() == "computed"]
        excludes_rows = [r for r in ci_rows if (number(r.get("delta_ci_pp_lo")) or 0) > 0 or (number(r.get("delta_ci_pp_hi")) or 0) < 0]
        excludes = f"{len(excludes_rows)} / {len(ci_rows)}"
        delta = decimal_text(summary["delta_w_pp"])
        summary_ci = interval_text(summary.get("lo_pp"), summary.get("hi_pp"))
        if summary_ci == "not computed":
            summary_ci = "not computed"
        refs = {
            "Primary eligible → complete (incomplete excluded) → shared; complete outside support": source_ref(
                summary_source, summary, "n_eligible_primary", "n_complete_primary", "n_shared_primary"),
            "Never-primary eligible → complete (incomplete excluded) → shared; complete outside support": source_ref(
                summary_source, summary, "n_eligible_never", "n_complete_never", "n_shared_never"),
            "Common-support score levels": source_ref(summary_source, summary, "levels"),
            "Computed δ_s CIs excluding zero / computed δ_s CIs": [ref for r in level_rows for ref in source_ref(level_source, r, "delta_ci_pp_lo", "delta_ci_pp_hi", "delta_ci_status")],
            "Δ_w weighted summary (percentage points)": source_ref(summary_source, summary, "delta_w_pp"),
            "95% patient-cluster CI for Δ_w weighted summary": source_ref(summary_source, summary, "lo_pp", "hi_pp", "interval_status"),
            "Summary interval status": source_ref(summary_source, summary, "interval_status"),
        }
        for col in ["Primary eligible → complete (incomplete excluded) → shared; complete outside support",
                    "Never-primary eligible → complete (incomplete excluded) → shared; complete outside support"]:
            set_derivation("T2", row_id, col, "Eligible, complete, and shared counts are copied from the source summary; excluded values are derived by subtraction and retain both source count references.")
        set_derivation("T2", row_id, "Computed δ_s CIs excluding zero / computed δ_s CIs", "Counted source-computed level intervals whose lower endpoint is above zero or upper endpoint below zero; denominator includes only computed level intervals.")
        set_derivation("T2", row_id, "95% patient-cluster CI for Δ_w weighted summary", "Source CI endpoints are copied only when the separately gated summary interval status is computed.")
        table.add(row_id, [database, f"{disease} / {SCORES[disease]}", primary_counts, never_counts,
                           count_text(summary["levels"]), excludes, delta, summary_ci,
                           summary["interval_status"]], refs, bold=(disease == "pancreatitis"))
    return table


def get_robustness_rows(data: dict[str, dict[str, CSVSource]], database: str, starts: str) -> list[dict[str, Any]]:
    source = get_source(data, database, "robustness")
    return [row for row in source.rows if str(row.get("analysis", "")).startswith(starts)]


def add_table3_numeric_cell(table: Table, source: CSVSource, row_id: str, column: str, value: Any,
                            refs: list[CellRef], derivation: str | None = None) -> None:
    if derivation:
        set_derivation(table.table_id, row_id, column, derivation)
    # Helper retained for clarity at composite-derived table cells.


def build_table3(data: dict[str, dict[str, CSVSource]]) -> Table:
    table = Table("T3", "Table 3. Paired code-breadth and refinement comparisons",
                  ["Analysis block", "Database", "Condition", "Records (patients)", "Narrow / score-only Δ_w weighted summary",
                   "Broad / refined Δ_w weighted summary", "Paired difference (percentage points; numerical interval)",
                   "Cell inventory / reconstruction", "Interval status"],
                  [
                      "Code-breadth differences compare narrow and broad definitions on identical records and common score support. The paired point estimate and interval are descriptive numerical influence summaries; they do not inherit the audit tool's interval gate.",
                      "For hospital-by-score and component-pattern refinements, the coarse and refined summaries use the same records. Refinement splits individual pooled record-count weights across subcells, changing the weighting target; the difference is not a causal or instrument-validity test.",
                      "Hospital-by-score intervals are descriptive because calibration for this refined target has not been established. Cell counts at or below five in either group are shown as an inventory. Component-pattern agreement describes score reconstruction and does not resolve unmeasured severity.",
                  ])
    # Paired code breadth.
    for database in [db for db in DB_ORDER if db in data]:
        source = get_source(data, database, "robustness")
        by_disease: dict[str, dict[str, dict[str, Any]]] = {}
        for row in source.rows:
            analysis = str(row.get("analysis", ""))
            if analysis in {"broad minus narrow on common records and common score support"}:
                by_disease.setdefault(str(row["disease"]), {})["paired"] = row
            elif analysis.startswith("narrow "):
                by_disease.setdefault(str(row["disease"]), {})["narrow"] = row
            elif analysis.startswith("broad "):
                by_disease.setdefault(str(row["disease"]), {})["broad"] = row
        paired_diseases = [d for d, rows in by_disease.items() if "paired" in rows]
        if paired_diseases:
            table.section(f"section-code-{database}", f"Paired code breadth — {database}")
        for disease in sorted(paired_diseases, key=lambda d: US_CONDITIONS.index(d) if d in US_CONDITIONS else 99):
            rows = by_disease[disease]
            pair = rows["paired"]
            narrow_point = float(pair["narrow_delta_w_pp"])
            broad_point = float(pair["broad_delta_w_pp"])
            if not math.isclose(broad_point - narrow_point, float(pair["difference_pp"]),
                                rel_tol=1e-9, abs_tol=1e-10):
                raise ValueError(f"Paired code-breadth points disagree with their difference: {database}, {disease}")
            rid = f"code|{database}|{disease}"
            ci = interval_text(pair.get("numerical_lo_pp"), pair.get("numerical_hi_pp"))
            refs = {
                "Records (patients)": source_ref(source, pair, "n", "n_patients"),
                "Narrow / score-only Δ_w weighted summary": source_ref(source, pair, "narrow_delta_w_pp"),
                "Broad / refined Δ_w weighted summary": source_ref(source, pair, "broad_delta_w_pp"),
                "Paired difference (percentage points; numerical interval)": source_ref(source, pair, "difference_pp", "numerical_lo_pp", "numerical_hi_pp"),
                "Interval status": source_ref(source, pair, "interval_status"),
            }
            set_derivation("T3", rid, "Records (patients)", "Counts come from the paired common-record comparison; values are records and distinct patients.")
            set_derivation("T3", rid, "Paired difference (percentage points; numerical interval)", "Displayed paired broad-minus-narrow difference and its descriptive numerical interval from common records and common score support.")
            table.add(rid, ["Paired code breadth", database, disease,
                            f"{count_text(pair['n'])} ({count_text(pair['n_patients'])})",
                            decimal_text(narrow_point), decimal_text(broad_point),
                            f"{decimal_text(pair.get('difference_pp'))} {ci}", "Same records; common score support",
                            pair.get("interval_status", "")], refs)

    # Hospital-by-score refinement (eICU only in the current execution path).
    for database in [db for db in DB_ORDER if db in data]:
        source = get_source(data, database, "robustness")
        indexes: dict[str, dict[str, dict[str, Any]]] = {}
        for row in source.rows:
            label = str(row.get("analysis", ""))
            if label in {"hospital x score score-only on matched records", "hospital x score fine-cell contrast",
                         "hospital x score fine minus score-only", "hospital x score sparsity inventory"}:
                indexes.setdefault(str(row.get("disease", "")), {})[label] = row
        diseases = [d for d, rows in indexes.items() if "hospital x score fine minus score-only" in rows]
        if diseases:
            table.section(f"section-hospital-{database}", f"Hospital × score refinement — {database}")
        for disease in sorted(diseases, key=lambda d: US_CONDITIONS.index(d) if d in US_CONDITIONS else 99):
            rows = indexes[disease]
            coarse = rows["hospital x score score-only on matched records"]
            fine = rows["hospital x score fine-cell contrast"]
            diff = rows["hospital x score fine minus score-only"]
            inventory = rows.get("hospital x score sparsity inventory", {})
            rid = f"hospital|{database}|{disease}"
            ci = interval_text(diff.get("numerical_lo_pp"), diff.get("numerical_hi_pp"))
            inventory_display = ""
            invrefs: list[CellRef] = []
            if inventory:
                inventory_display = (f"{count_text(inventory.get('n_observed_hospital_score_cells'))} hospital-score cells; "
                                     f"{count_text(inventory.get('n_cells_any_arm_le5'))} with either arm ≤5; "
                                     f"{fraction_pct_text(inventory.get('proportion_any_arm_le5'), 2)}")
                invrefs = source_ref(source, inventory, "n_observed_hospital_score_cells", "n_cells_any_arm_le5", "proportion_any_arm_le5")
            refs = {
                "Records (patients)": source_ref(source, diff, "n", "n_patients"),
                "Narrow / score-only Δ_w weighted summary": source_ref(source, coarse, "delta_w_pp"),
                "Broad / refined Δ_w weighted summary": source_ref(source, fine, "delta_w_pp"),
                "Paired difference (percentage points; numerical interval)": source_ref(source, diff, "difference_pp", "numerical_lo_pp", "numerical_hi_pp"),
                "Cell inventory / reconstruction": invrefs,
                "Interval status": source_ref(source, diff, "interval_status"),
            }
            table.add(rid, ["Hospital × score", database, disease,
                            f"{count_text(diff['n'])} ({count_text(diff['n_patients'])})",
                            decimal_text(coarse.get("delta_w_pp")), decimal_text(fine.get("delta_w_pp")),
                            f"{decimal_text(diff.get('difference_pp'))} {ci}", inventory_display,
                            diff.get("interval_status", "")], refs)

    # Component-pattern refinement; the analysis is only defined for sepsis/qSOFA.
    for database in [db for db in DB_ORDER if db in data]:
        source = get_source(data, database, "robustness")
        indexes: dict[str, dict[str, dict[str, Any]]] = {}
        for row in source.rows:
            label = str(row.get("analysis", ""))
            if label in {"component pattern score-only on matched records", "component pattern fine-cell contrast",
                         "component pattern fine minus score-only"}:
                indexes.setdefault(str(row.get("disease", "")), {})[label] = row
        diseases = [d for d, rows in indexes.items() if "component pattern fine minus score-only" in rows]
        if diseases:
            table.section(f"section-component-{database}", f"Component-pattern refinement — {database}")
        for disease in sorted(diseases, key=lambda d: US_CONDITIONS.index(d) if d in US_CONDITIONS else 99):
            rows = indexes[disease]
            coarse = rows["component pattern score-only on matched records"]
            fine = rows["component pattern fine-cell contrast"]
            diff = rows["component pattern fine minus score-only"]
            agreement = coarse.get("component_reconstruction_agreement", "")
            agreement_display = fraction_pct_text(agreement, 2) if number(agreement) is not None else "not reported"
            rid = f"component|{database}|{disease}"
            ci = interval_text(diff.get("numerical_lo_pp"), diff.get("numerical_hi_pp"))
            refs = {
                "Records (patients)": source_ref(source, diff, "n", "n_patients"),
                "Narrow / score-only Δ_w weighted summary": source_ref(source, coarse, "delta_w_pp"),
                "Broad / refined Δ_w weighted summary": source_ref(source, fine, "delta_w_pp"),
                "Paired difference (percentage points; numerical interval)": source_ref(source, diff, "difference_pp", "numerical_lo_pp", "numerical_hi_pp"),
                "Cell inventory / reconstruction": source_ref(source, coarse, "component_reconstruction_agreement") if number(agreement) is not None else [],
                "Interval status": source_ref(source, diff, "interval_status"),
            }
            set_derivation("T3", rid, "Cell inventory / reconstruction", "Component-pattern reconstruction agreement copied and formatted as a percentage.")
            table.add(rid, ["Component pattern", database, disease,
                            f"{count_text(diff['n'])} ({count_text(diff['n_patients'])})",
                            decimal_text(coarse.get("delta_w_pp")), decimal_text(fine.get("delta_w_pp")),
                            f"{decimal_text(diff.get('difference_pp'))} {ci}", agreement_display,
                            diff.get("interval_status", "")], refs)
    return table


def build_table4(data: dict[str, dict[str, CSVSource]]) -> Table:
    source = get_source(data, "eICU-CRD", "timing")
    table = Table("T4", "Table 4. Full-course and documentation-by-24-hours weighted summaries in eICU",
                  ["Condition", "Grouping", "Records", "Patients", "Landmark-classifiable / reclassified records",
                   "Δ_w weighted summary (percentage points)", "95% patient-cluster CI", "Interval status"],
                  [
                      "The 24-hour exposure label is never-primary-by-24-hours. It describes diagnosis documentation by the landmark, not disease onset. Diagnosis grouping uses full-course documentation in the main comparison.",
                      "For each condition, the three rows compare the full sample with full-course grouping, the same classifiable subset with full-course grouping, and that same subset grouped by never-primary-by-24-hours. Point estimates and intervals are copied from the aggregate output; withheld intervals are not reconstructed.",
                      "The 24-hour hospital-survivor sensitivity is supplied separately in the supplement. Patient-cluster summary intervals use the separately gated v2 audit method.",
                  ])
    expected_labels = ["full sample, full-course diagnosis", "same classifiable subset, full-course diagnosis",
                       "same classifiable subset, never-primary-by-24-hours"]
    for disease in ("sepsis", "pneumonia"):
        condition_rows = [r for r in source.rows if r.get("database") == "eICU-CRD" and r.get("disease") == disease]
        indexed = {str(r["analysis"]): r for r in condition_rows}
        for label in expected_labels:
            if label not in indexed:
                raise RuntimeError(f"Table 4 timing comparison missing: {disease}/{label}")
        flow = next((r for r in condition_rows if r.get("analysis") == "classification flow"), None)
        if flow is None:
            raise RuntimeError(f"Table 4 classification flow missing: {disease}")
        for label in expected_labels:
            row = indexed[label]
            row_id = f"eicu|{disease}|{label}"
            lo, hi = row.get("lo_pp"), row.get("hi_pp")
            ci = interval_text(lo, hi)
            classifiable = f"{count_text(flow.get('classifiable_n'))} / {count_text(flow.get('reclassified_n'))}"
            refs = {
                "Records": source_ref(source, row, "n"),
                "Patients": source_ref(source, row, "n_patients"),
                "Landmark-classifiable / reclassified records": source_ref(source, flow, "classifiable_n", "reclassified_n"),
                "Δ_w weighted summary (percentage points)": source_ref(source, row, "delta_w_pp"),
                "95% patient-cluster CI": source_ref(source, row, "lo_pp", "hi_pp", "interval_status"),
                "Interval status": source_ref(source, row, "interval_status"),
            }
            table.add(row_id, [disease, label, count_text(row.get("n")), count_text(row.get("n_patients")),
                               classifiable, decimal_text(row.get("delta_w_pp")), ci,
                               row.get("interval_status", "")], refs)
    return table


def refusal_state(row: dict[str, Any], source: CSVSource) -> str:
    refusal_raw = str(row.get("refusal_counts", "{}"))
    try:
        refusal = json.loads(refusal_raw) if refusal_raw else {}
    except json.JSONDecodeError:
        refusal = {"source": refusal_raw}
    point = number(row.get("point_estimate_pct"))
    interval = number(row.get("interval_emission_pct"))
    if point is not None and point <= 0:
        state = "no point estimate; no interval"
    elif interval is not None and interval <= 0:
        state = "point only; no interval emitted"
    elif interval is not None and interval < 100:
        state = "point output; interval emitted in a subset of replicates"
    else:
        state = "point and interval emitted in all replicates"
    if refusal:
        state += "; refusals: " + ", ".join(f"{k}={v}" for k, v in sorted(refusal.items()))
    return state


def benchmark_maps(data: dict[str, dict[str, CSVSource]]) -> tuple[CSVSource, CSVSource, dict, dict]:
    summary = data["benchmark_summary"]["table"]
    denoms = data["benchmark_denominators"]["table"]
    return summary, denoms, row_index(summary, ("design", "policy")), row_index(denoms, ("design", "policy"))


def build_table5(data: dict[str, dict[str, CSVSource]]) -> Table:
    summary_source, denom_source, summary_idx, denom_idx = benchmark_maps(data)
    sparse_source = data["sparse_summary"]["table"]
    sparse_idx = row_index(sparse_source, ("design", "strategy"))
    table = Table("T5", "Table 5. Selected audit-strategy and sparse-boundary results for Δ_w weighted-summary intervals",
                  ["Design", "Strategy", "Point output (% of replicates)", "Interval output (% of replicates)", "Target support matched (% of replicates)",
                   "Off-target interval output (% of replicates)", "Population-truth coverage on target (n; MCSE, pp)",
                   "Valid-target coverage among emitted intervals (n; MCSE, pp)",
                   "Emitted-interval population-truth noncoverage / all replicates", "Output / refusal state"],
                  [
                      "Five representative confirmatory designs are shown with the two separate sparse-boundary structures. The selected designs cover a baseline, cross-group repeated admissions, rare common support with off-target emission, near-boundary outcomes, and few large clusters. Table 6 reports strategy C for all 11 confirmatory designs; the full A/B/C/D results and supplementary policies are in the supplement.",
                      "Conditional population-truth coverage is calculated only when an interval is emitted on the declared support. Valid-target coverage among emitted intervals counts off-target intervals as failures; its denominator is the number of emitted intervals. Both denominators and off-target output are displayed so coverage cannot hide target mismatch.",
                      "The source's unconditional noncoverage count includes emitted off-target or truth-missing intervals; refused intervals are reported in the output state and are not counted as noncoverage events. Sparse-boundary coverage is reported only when an interval exists; the sparse source does not provide target-support matching or a comparable valid-target denominator.",
                  ])
    for design in TABLE5_DESIGNS:
        for policy in TABLE5_POLICIES:
            row = summary_idx[(design, policy)]
            denom = denom_idx[(design, policy)]
            row_id = f"{design}|{policy}"
            n_on_target = denom.get("n_emitted_on_declared_target")
            n_emitted = denom.get("n_emitted")
            coverage = row.get("conditional_coverage_pct")
            coverage_mcse = row.get("conditional_coverage_mcse_pct")
            target_cov = denom.get("valid_target_coverage_all_emitted_pct")
            target_mcse = denom.get("valid_target_coverage_mcse_pp")
            if number(n_on_target) == 0 or number(coverage) is None:
                pop_cov_display = f"— (0 on-target intervals)"
            else:
                pop_cov_display = f"{decimal_text(coverage)}% (n={count_text(n_on_target)}; {decimal_text(coverage_mcse, 3)} pp)"
            if number(n_emitted) == 0 or number(target_cov) is None:
                valid_display = "— (no emitted intervals)"
            else:
                valid_display = f"{decimal_text(target_cov)}% (n={count_text(n_emitted)}; {decimal_text(target_mcse, 3)} pp)"
            missed = f"{count_text(row.get('unconditional_missed_intervals'))} / {count_text(row.get('replicates'))} ({pct_text(row.get('unconditional_missed_pct'))}; {decimal_text(row.get('unconditional_missed_mcse_pct'), 3)} pp)"
            state = refusal_state(row, summary_source)
            refs = {
                "Point output (% of replicates)": source_ref(summary_source, row, "point_estimate_pct"),
                "Interval output (% of replicates)": source_ref(summary_source, row, "interval_emission_pct"),
                "Target support matched (% of replicates)": source_ref(summary_source, row, "target_support_match_pct"),
                "Off-target interval output (% of replicates)": source_ref(summary_source, row, "off_target_interval_pct"),
                "Population-truth coverage on target (n; MCSE, pp)": source_ref(summary_source, row, "conditional_coverage_pct", "conditional_coverage_n", "conditional_coverage_mcse_pct") + source_ref(denom_source, denom, "n_emitted_on_declared_target"),
                "Valid-target coverage among emitted intervals (n; MCSE, pp)": source_ref(denom_source, denom, "valid_target_coverage_all_emitted_pct", "n_emitted", "valid_target_coverage_mcse_pp"),
                "Emitted-interval population-truth noncoverage / all replicates": source_ref(summary_source, row, "unconditional_missed_intervals", "replicates", "unconditional_missed_pct", "unconditional_missed_mcse_pct"),
                "Output / refusal state": source_ref(summary_source, row, "point_estimate_pct", "interval_emission_pct", "refusal_counts"),
            }
            set_derivation("T5", row_id, "Population-truth coverage on target (n; MCSE, pp)", "Conditional coverage and its denominator/MCSE are copied from the benchmark summary; denominator is verified against emitted intervals on declared support.")
            set_derivation("T5", row_id, "Valid-target coverage among emitted intervals (n; MCSE, pp)", "Copied from the denominator audit; wrong-support intervals count as failures, and denominator is the number of emitted intervals.")
            set_derivation("T5", row_id, "Emitted-interval population-truth noncoverage / all replicates", "Copied source count/rate/MCSE; refused intervals are not counted in this source noncoverage metric and are listed in output state.")
            table.add(row_id, [design, policy, pct_text(row.get("point_estimate_pct")), pct_text(row.get("interval_emission_pct")),
                               pct_text(row.get("target_support_match_pct")), pct_text(row.get("off_target_interval_pct")),
                               pop_cov_display, valid_display, missed, state], refs)
    for design in ("fine_cells", "tiny_arm"):
        for strategy in TABLE5_POLICIES:
            row = sparse_idx[(design, strategy)]
            row_id = f"sparse|{design}|{strategy}"
            coverage = row.get("conditional_coverage")
            mcse = row.get("coverage_mcse")
            if number(row.get("n_intervals")) and number(coverage) is not None:
                coverage_display = f"{fraction_pct_text(coverage)} (n={count_text(row['n_intervals'])}; {decimal_text((number(mcse) or 0) * 100, 3)} pp)"
            else:
                coverage_display = "— (no emitted intervals)"
            refs = {
                "Point output (% of replicates)": source_ref(sparse_source, row, "point_output_rate"),
                "Interval output (% of replicates)": source_ref(sparse_source, row, "interval_output_rate"),
                "Population-truth coverage on target (n; MCSE, pp)": source_ref(sparse_source, row, "conditional_coverage", "n_intervals", "coverage_mcse") if number(row.get("n_intervals")) else source_ref(sparse_source, row, "n_intervals"),
                "Emitted-interval population-truth noncoverage / all replicates": source_ref(sparse_source, row, "unconditional_missed_intervals", "replicates"),
                "Output / refusal state": source_ref(sparse_source, row, "point_output_rate", "interval_output_rate", "refusal_evaluation"),
            }
            state = "A emits a point/interval; B/C apply deterministic count rules" if strategy == "A" else "point output; interval refused by sparse-cell count rule"
            table.add(row_id, [design, strategy, fraction_pct_text(row.get("point_output_rate")), fraction_pct_text(row.get("interval_output_rate")),
                               "not separately summarized", "not separately summarized", coverage_display,
                               "not separately summarized", f"{count_text(row.get('unconditional_missed_intervals'))} / {count_text(row.get('replicates'))}", state], refs)
    return table


def build_table6(data: dict[str, dict[str, CSVSource]], json_data: dict[str, Any]) -> Table:
    summary_source, denom_source, summary_idx, denom_idx = benchmark_maps(data)
    sparse_source = data["sparse_summary"]["table"]
    sparse_idx = row_index(sparse_source, ("design", "strategy"))
    designs = json_data.get("benchmark_config", {}).get("designs", [])
    design_order = [item["name"] for item in designs if isinstance(item, dict) and "name" in item]
    table = Table("T6", "Table 6. Bias, coverage and output states for the Δ_w weighted summary under strategy C",
                  ["Design", "Observed-weight truth defined (n)", "C point / interval output (% of replicates)", "Target support matched (% of replicates)",
                   "Off-target interval output (% of replicates)", "Population-truth coverage on target (n; MCSE, pp)",
                   "Valid-target coverage among emitted intervals (n; MCSE, pp)",
                   "Mean bias of Δ_w weighted summary (pp)",
                   "Population-truth noncoverage events / all replicates", "Tool state"],
                  [
                      "Population-truth coverage conditions on an emitted interval with the declared support. Mean bias compares points on that support with population truth and is reported in percentage points. Conditional observed-weight coverage addresses a distinct target and is retained in Supplementary Table 7.",
                      "Valid-target coverage among emitted intervals counts wrong-support intervals as failures. The rare-common-support design therefore reports target-support match, off-target output and the valid-target coverage denominator alongside on-target conditional coverage.",
                      "Population-truth noncoverage events use the source definition: emitted off-target or truth-missing intervals are counted; refused intervals are separately described in the tool state and are not counted as noncoverage events. These results do not establish generic strategy superiority.",
                      "The first denominator column is the number of replicates with an observed-weight truth defined. The two sparse structures are additional deterministic boundary checks; their sparse summary does not carry separate population- and observed-weight coverage columns, so unavailable target-specific coverage is shown as not reported.",
                  ])
    for design in design_order:
        row = summary_idx[(design, "C")]
        denom = denom_idx[(design, "C")]
        row_id = f"{design}|C"
        n_target = denom.get("n_emitted_on_declared_target")
        n_emit = denom.get("n_emitted")
        pop_cov = row.get("conditional_coverage_pct")
        pop_mcse = row.get("conditional_coverage_mcse_pct")
        if number(n_target) == 0 or number(pop_cov) is None:
            pop_display = "— (0 on-target intervals)"
        else:
            pop_display = f"{decimal_text(pop_cov)}% (n={count_text(n_target)}; {decimal_text(pop_mcse, 3)} pp)"
        valid_cov = denom.get("valid_target_coverage_all_emitted_pct")
        valid_mcse = denom.get("valid_target_coverage_mcse_pp")
        valid_display = "— (no emitted intervals)" if number(n_emit) == 0 or number(valid_cov) is None else f"{decimal_text(valid_cov)}% (n={count_text(n_emit)}; {decimal_text(valid_mcse, 3)} pp)"
        obs_cov = row.get("conditional_observed_weight_coverage_pct")
        obs_n = row.get("conditional_observed_weight_coverage_n")
        obs_mcse = row.get("conditional_observed_weight_coverage_mcse_pct")
        obs_display = "— (truth unavailable or no eligible intervals)" if number(obs_n) == 0 or number(obs_cov) is None else f"{decimal_text(obs_cov)}% (n={count_text(obs_n)}; {decimal_text(obs_mcse, 3)} pp)"
        missed = f"{count_text(row.get('unconditional_missed_intervals'))} / {count_text(row.get('replicates'))} ({pct_text(row.get('unconditional_missed_pct'))}; {decimal_text(row.get('unconditional_missed_mcse_pct'), 3)} pp)"
        refs = {
            "Observed-weight truth defined (n)": source_ref(summary_source, row, "conditional_truth_complete_n"),
            "C point / interval output (% of replicates)": source_ref(summary_source, row, "point_estimate_pct", "interval_emission_pct"),
            "Target support matched (% of replicates)": source_ref(summary_source, row, "target_support_match_pct"),
            "Off-target interval output (% of replicates)": source_ref(summary_source, row, "off_target_interval_pct"),
            "Population-truth coverage on target (n; MCSE, pp)": source_ref(summary_source, row, "conditional_coverage_pct", "conditional_coverage_n", "conditional_coverage_mcse_pct") + source_ref(denom_source, denom, "n_emitted_on_declared_target"),
            "Valid-target coverage among emitted intervals (n; MCSE, pp)": source_ref(denom_source, denom, "valid_target_coverage_all_emitted_pct", "n_emitted", "valid_target_coverage_mcse_pp"),
            "Mean bias of Δ_w weighted summary (pp)": source_ref(summary_source, row, "mean_point_bias_on_target"),
            "Population-truth noncoverage events / all replicates": source_ref(summary_source, row, "unconditional_missed_intervals", "replicates", "unconditional_missed_pct", "unconditional_missed_mcse_pct"),
            "Tool state": source_ref(summary_source, row, "point_estimate_pct", "interval_emission_pct", "refusal_counts"),
        }
        for col in ["Population-truth coverage on target (n; MCSE, pp)", "Conditional observed-weight coverage (n; MCSE, pp)"]:
            set_derivation("T6", row_id, col, "Coverage estimate, denominator, and Monte Carlo SE are copied from their target-specific benchmark fields; denominators are not merged across targets.")
        set_derivation("T6", row_id, "Valid-target coverage among emitted intervals (n; MCSE, pp)", "Copied from the denominator audit; wrong-support intervals count as failures, denominator is emitted intervals.")
        set_derivation("T6", row_id, "Mean bias of Δ_w weighted summary (pp)", "100 times the source mean_point_bias_on_target, converted from probability to percentage points.")
        bias = number(row.get("mean_point_bias_on_target"))
        table.add(row_id, [design, count_text(row.get("conditional_truth_complete_n")),
                           f"{pct_text(row.get('point_estimate_pct'))} / {pct_text(row.get('interval_emission_pct'))}",
                           pct_text(row.get("target_support_match_pct")), pct_text(row.get("off_target_interval_pct")),
                           pop_display, valid_display, decimal_text(None if bias is None else 100*bias, 3), missed, refusal_state(row, summary_source)], refs)
    for design in ("fine_cells", "tiny_arm"):
        row = sparse_idx[(design, "C")]
        row_id = f"{design}|C-sparse-validation"
        refs = {
            "C point / interval output (% of replicates)": source_ref(sparse_source, row, "point_output_rate", "interval_output_rate"),
            "Population-truth noncoverage events / all replicates": source_ref(sparse_source, row, "unconditional_missed_intervals", "replicates"),
            "Tool state": source_ref(sparse_source, row, "point_output_rate", "interval_output_rate", "refusal_evaluation"),
            "Mean bias of Δ_w weighted summary (pp)": source_ref(sparse_source, row, "bias"),
        }
        state = "point output; no CI emitted under the sparse-cell count rule"
        table.add(row_id, [f"{design} (sparse boundary)", "—", f"{fraction_pct_text(row.get('point_output_rate'))} / {fraction_pct_text(row.get('interval_output_rate'))}",
                           "not separately summarized", "not separately summarized", "not reported",
                           "not reported", decimal_text(100*float(row['bias']), 3), "not reported", state], refs)
    if len(design_order) != 11:
        raise RuntimeError(f"Table 6 requires 11 confirmatory DGPs; found {len(design_order)}")
    return table


def add_source_table(table_id: str, title: str, source: CSVSource, selected_columns: list[str],
                     notes: list[str] | None = None, row_prefix: str = "") -> Table:
    missing = [column for column in selected_columns if column not in source.headers]
    if missing:
        raise KeyError(f"Missing selected columns in {source.relative_path}: {missing}")
    table = Table(table_id, title, selected_columns, notes)
    for row in source.rows:
        row_id = f"{row_prefix}{row['_physical_row']}"
        values = [row.get(column, "") for column in selected_columns]
        refs: dict[str, list[CellRef]] = {}
        for column, value in zip(selected_columns, values):
            if is_numeric_text(value):
                refs[column] = source_ref(source, row, column)
        table.add(row_id, values, refs)
    return table


def make_supplementary_tables(data: dict[str, dict[str, CSVSource]], snapshot_map: dict[str, Path],
                              json_data: dict[str, Any], mode: str) -> list[Table]:
    tables: list[Table] = []
    # S1: one nonprimary database-condition cell omitted from the historical 19-cell contract.
    if "Zigong" in data:
        summary = get_source(data, "Zigong", "summary")
        hf = [r for r in summary.rows if r.get("disease") == "heart failure"]
        if hf:
            table = Table("S1", "Supplementary Table 1. Zigong heart-failure application",
                          ["Database", "Condition / instrument", "Eligible primary / never-primary", "Complete primary / never-primary",
                           "Shared primary / never-primary", "Supported score levels", "Δ_w weighted summary (percentage points)",
                           "95% patient-cluster CI", "Interval status"],
                          ["This cell is supplemental and does not change the original 19-cell Table 2 contract. qSOFA is outside intended use for heart failure; interpret as a source-specific application."])
            for row in hf:
                rid = f"Zigong|heart failure"
                refs = {
                    "Eligible primary / never-primary": source_ref(summary, row, "n_eligible_primary", "n_eligible_never"),
                    "Complete primary / never-primary": source_ref(summary, row, "n_complete_primary", "n_complete_never"),
                    "Shared primary / never-primary": source_ref(summary, row, "n_shared_primary", "n_shared_never"),
                    "Supported score levels": source_ref(summary, row, "levels"),
                    "Δ_w weighted summary (percentage points)": source_ref(summary, row, "delta_w_pp"),
                    "95% patient-cluster CI": source_ref(summary, row, "lo_pp", "hi_pp", "interval_status"),
                    "Interval status": source_ref(summary, row, "interval_status"),
                }
                table.add(rid, ["Zigong", f"heart failure / {SCORES['heart failure']}",
                                f"{count_text(row['n_eligible_primary'])} / {count_text(row['n_eligible_never'])}",
                                f"{count_text(row['n_complete_primary'])} / {count_text(row['n_complete_never'])}",
                                f"{count_text(row['n_shared_primary'])} / {count_text(row['n_shared_never'])}",
                                count_text(row["levels"]), decimal_text(row["delta_w_pp"]),
                                interval_text(row.get("lo_pp"), row.get("hi_pp")), row["interval_status"]], refs)
            tables.append(table)

    # S2: selection flow and analysis sensitivities, preserving source rows and columns.
    flow_headers = ["Database", "Condition", "Row type", "Group / analysis", "Records / source n",
                    "Patients", "Score complete", "Outcome known", "Analyzed", "Δ_w (pp)", "CI lower (pp)",
                    "CI upper (pp)", "Interval status", "Selection rule / estimand"]
    flow_table = Table("S2", "Supplementary Table 2. Source flow and patient-level sensitivities", flow_headers,
                       ["One-record-per-patient analyses use the prespecified chronological first admission where dates are available; eICU uses the prespecified hash selection because full admission dates are unavailable. Patient-weighted supported-admission results are separate estimands."])
    for database in [db for db in DB_ORDER if db in data]:
        selection = data[database].get("selection")
        if selection:
            for row in selection.rows:
                rid = f"flow|{database}|{row.get('disease')}|{row.get('group')}"
                refs = {
                    "Records / source n": source_ref(selection, row, "n_source"),
                    "Patients": source_ref(selection, row, "n_patients"),
                    "Score complete": source_ref(selection, row, "n_score_complete"),
                    "Outcome known": source_ref(selection, row, "n_outcome_known"),
                    "Analyzed": source_ref(selection, row, "n_analyzed"),
                }
                flow_table.add(rid, [database, row["disease"], "Eligibility flow", row["group"],
                                     count_text(row["n_source"]), count_text(row["n_patients"]),
                                     count_text(row["n_score_complete"]), count_text(row["n_outcome_known"]),
                                     count_text(row["n_analyzed"]), "", "", "", "", ""], refs)
        sensitivity = data[database].get("sensitivity")
        if sensitivity:
            for row in sensitivity.rows:
                rid = f"sensitivity|{database}|{row.get('disease')}|{row.get('analysis')}"
                refs = {
                    "Records / source n": source_ref(sensitivity, row, "n"),
                    "Patients": source_ref(sensitivity, row, "n_patients"),
                    "Δ_w (pp)": source_ref(sensitivity, row, "delta_w_pp"),
                    "CI lower (pp)": source_ref(sensitivity, row, "lo_pp"),
                    "CI upper (pp)": source_ref(sensitivity, row, "hi_pp"),
                    "Interval status": source_ref(sensitivity, row, "interval_status"),
                    "Selection rule / estimand": source_ref(sensitivity, row, "selection_rule", "estimand"),
                }
                flow_table.add(rid, [database, row["disease"], "Sensitivity", row["analysis"],
                                     count_text(row["n"]), count_text(row["n_patients"]), "", "", "",
                                     decimal_text(row.get("delta_w_pp")), decimal_text(row.get("lo_pp")),
                                     decimal_text(row.get("hi_pp")), row.get("interval_status", ""),
                                     row.get("selection_rule") or row.get("estimand", "")], refs)
    tables.append(flow_table)

    # S3: score missingness bounds and intervals-withheld perturbation ranges.
    for table_id, filename, label in [
        ("S3", "missing_bounds", "Supplementary Table 3. Separate score-level missingness identification bounds"),
        ("S4", "sparse_level_sensitivity", "Supplementary Table 4. Perturbation ranges when score-level intervals are withheld"),
    ]:
        headers = ["Database", "Disease", "Score level", "Estimand"]
        if filename == "missing_bounds":
            headers += ["Fixed primary n", "Optional primary n", "Primary risk lower", "Primary risk upper",
                        "Fixed never-primary n", "Optional never-primary n", "Never-primary risk lower",
                        "Never-primary risk upper", "δ_s lower bound", "δ_s upper bound"]
        else:
            headers += ["Δ_w point (pp)", "Record weight on levels without δ_s CI", "Unsupported interval levels",
                        "Good-level contribution (pp)", "Perturbation lower (pp)", "Perturbation upper (pp)", "Interpretation"]
        source_key = filename
        generic_rows: list[dict[str, Any]] = []
        refs_by: list[dict[str, list[CellRef]]] = []
        for database in [db for db in DB_ORDER if db in data]:
            src = data[database].get(source_key)
            if not src:
                continue
            for row in src.rows:
                row_id = f"{database}|{row.get('disease')}|{row.get('level','weighted')}"
                vals: dict[str, Any] = {"Database": database, "Disease": row.get("disease", ""),
                                        "Score level": score_text(row.get("level")) if row.get("level") not in (None, "") else "weighted",
                                        "Estimand": row.get("estimand", "")}
                source_cols: dict[str, str] = {}
                if filename == "missing_bounds":
                    for outcol, srccol in zip(headers[4:], ["n_fixed_primary", "n_optional_primary", "risk_lower_primary", "risk_upper_primary",
                                                            "n_fixed_never", "n_optional_never", "risk_lower_never", "risk_upper_never",
                                                            "delta_lower", "delta_upper"]):
                        vals[outcol] = row.get(srccol, "")
                        source_cols[outcol] = srccol
                else:
                    for outcol, srccol in zip(headers[4:], ["delta_w_pp", "bad_record_weight", "n_unsupported_interval_levels",
                                                            "empirical_good_level_contribution_pp", "perturbation_lower_pp",
                                                            "perturbation_upper_pp", "interpretation"]):
                        vals[outcol] = row.get(srccol, "")
                        source_cols[outcol] = srccol
                generic_rows.append({"_id": row_id, "_vals": vals, "_source": src, "_row": row, "_source_cols": source_cols})
        table = Table(table_id, label, headers,
                      ["Missingness bounds are identification bounds from incomplete component scores, not confidence intervals. Perturbation ranges are not confidence intervals and hold observed good-level risks and record weights fixed."])
        for entry in generic_rows:
            refs = {outcol: source_ref(entry["_source"], entry["_row"], srccol) for outcol, srccol in entry["_source_cols"].items() if is_numeric_text(entry["_vals"].get(outcol))}
            if entry["_row"].get("level") not in (None, ""):
                refs["Score level"] = source_ref(entry["_source"], entry["_row"], "level")
            values = [entry["_vals"].get(col, "") for col in headers]
            table.add(entry["_id"], values, refs)
        tables.append(table)

    # S5: paired eICU documentation-timing comparison on identical records.
    eicu_timing = get_source(data, "eICU-CRD", "timing")
    paired_timing_rows = [r for r in eicu_timing.rows if str(r.get("analysis", "")).startswith("by-24-hours minus full-course grouping")]
    paired_timing = Table("S5", "Supplementary Table 5. Paired eICU documentation-timing contrasts",
                          ["Condition", "Comparison", "Records", "Patients", "Difference in Δ_w (pp)",
                           "Descriptive paired interval (pp)", "Interval status"],
                          ["These contrasts use identical classifiable records and pooled observed score weights. The intervals are descriptive paired influence intervals, not audit-gated summary CIs."])
    for row in paired_timing_rows:
        rid = f"eicu-timing-paired|{row.get('disease')}"
        refs = {"Records": source_ref(eicu_timing, row, "n"), "Patients": source_ref(eicu_timing, row, "n_patients"),
                "Difference in Δ_w (pp)": source_ref(eicu_timing, row, "difference_pp"),
                "Descriptive paired interval (pp)": source_ref(eicu_timing, row, "numerical_lo_pp", "numerical_hi_pp"),
                "Interval status": source_ref(eicu_timing, row, "interval_status")}
        paired_timing.add(rid, [row.get("disease", ""), row.get("analysis", ""), count_text(row.get("n")),
                                count_text(row.get("n_patients")), decimal_text(row.get("difference_pp")),
                                interval_text(row.get("numerical_lo_pp"), row.get("numerical_hi_pp")),
                                row.get("interval_status", "")], refs)
    tables.append(paired_timing)

    # S6: eICU survivor-only documentation timing sensitivity.
    survivor_rows = [r for r in eicu_timing.rows if str(r.get("analysis", "")).startswith("24-hour hospital survivors")]
    survivor_table = Table("S6", "Supplementary Table 6. eICU 24-hour hospital-survivor sensitivity",
                           ["Condition", "Analysis", "Risk set", "Records", "Patients", "Δ_w / paired difference (pp)",
                            "Numerical interval (pp)", "Interval status"],
                           ["This survivor sensitivity conditions on remaining hospitalized 24 hours after index ICU admission and is separate from the primary three-way documentation comparison."])
    for row in survivor_rows:
        rid = f"eicu-survivor|{row.get('disease')}|{row.get('analysis')}"
        point_col = "difference_pp" if number(row.get("difference_pp")) is not None else "delta_w_pp"
        refs = {"Records": source_ref(eicu_timing, row, "n"), "Patients": source_ref(eicu_timing, row, "n_patients"),
                "Δ_w / paired difference (pp)": source_ref(eicu_timing, row, point_col),
                "Numerical interval (pp)": source_ref(eicu_timing, row, "numerical_lo_pp", "numerical_hi_pp") if point_col == "difference_pp" else source_ref(eicu_timing, row, "lo_pp", "hi_pp"),
                "Interval status": source_ref(eicu_timing, row, "interval_status")}
        if "risk_set" in row:
            refs["Risk set"] = source_ref(eicu_timing, row, "risk_set")
        low, high = ((row.get("numerical_lo_pp"), row.get("numerical_hi_pp")) if point_col == "difference_pp" else (row.get("lo_pp"), row.get("hi_pp")))
        survivor_table.add(rid, [row.get("disease", ""), row.get("analysis", ""), row.get("risk_set", ""),
                                 count_text(row.get("n")), count_text(row.get("n_patients")), decimal_text(row.get(point_col)),
                                 interval_text(low, high), row.get("interval_status", "")], refs)
    tables.append(survivor_table)

    # S6: full confirmatory benchmark and paired strategy summaries, with all policies retained.
    bench = data["benchmark_summary"]["table"]
    denom = data["benchmark_denominators"]["table"]
    denidx = row_index(denom, ("design", "policy"))
    headers = ["Design", "Policy", "Weight mode", "Replicates", "Point output (%)", "Interval output (%)",
               "Target support match (%)", "Off-target interval output (%)", "On-target population coverage (%)",
               "On-target denominator", "Population coverage MCSE (pp)", "Valid-target coverage among emitted (%)",
               "Emitted interval denominator", "Valid-target coverage MCSE (pp)", "Observed-weight coverage (%)",
               "Observed-weight denominator", "Observed-weight MCSE (pp)", "Unconditional noncoverage events",
               "Unconditional noncoverage (%)", "Unconditional noncoverage MCSE (pp)", "Mean point bias on target", "Refusal counts"]
    full = Table("S7", "Supplementary Table 7. Full confirmatory simulation policy results",
                 headers, ["All eleven confirmatory designs and every reported policy are retained. Population-truth coverage, conditional observed-weight coverage, and valid-target coverage among emitted intervals are separate fields. Off-target output is not folded into conditional on-target coverage."])
    for row in bench.rows:
        design, policy = str(row["design"]), str(row["policy"])
        drow = denidx[(design, policy)]
        rid = f"{design}|{policy}"
        refs = {
            "Replicates": source_ref(bench, row, "replicates"),
            "Point output (%)": source_ref(bench, row, "point_estimate_pct"),
            "Interval output (%)": source_ref(bench, row, "interval_emission_pct"),
            "Target support match (%)": source_ref(bench, row, "target_support_match_pct"),
            "Off-target interval output (%)": source_ref(bench, row, "off_target_interval_pct"),
            "On-target population coverage (%)": source_ref(bench, row, "conditional_coverage_pct"),
            "On-target denominator": source_ref(bench, row, "conditional_coverage_n"),
            "Population coverage MCSE (pp)": source_ref(bench, row, "conditional_coverage_mcse_pct"),
            "Valid-target coverage among emitted (%)": source_ref(denom, drow, "valid_target_coverage_all_emitted_pct"),
            "Emitted interval denominator": source_ref(denom, drow, "n_emitted"),
            "Valid-target coverage MCSE (pp)": source_ref(denom, drow, "valid_target_coverage_mcse_pp"),
            "Observed-weight coverage (%)": source_ref(bench, row, "conditional_observed_weight_coverage_pct"),
            "Observed-weight denominator": source_ref(bench, row, "conditional_observed_weight_coverage_n"),
            "Observed-weight MCSE (pp)": source_ref(bench, row, "conditional_observed_weight_coverage_mcse_pct"),
            "Unconditional noncoverage events": source_ref(bench, row, "unconditional_missed_intervals"),
            "Unconditional noncoverage (%)": source_ref(bench, row, "unconditional_missed_pct"),
            "Unconditional noncoverage MCSE (pp)": source_ref(bench, row, "unconditional_missed_mcse_pct"),
            "Mean point bias on target": source_ref(bench, row, "mean_point_bias_on_target"),
            "Refusal counts": source_ref(bench, row, "refusal_counts"),
        }
        full.add(rid, [design, policy, row.get("weight_mode", ""), count_text(row.get("replicates")),
                       row.get("point_estimate_pct", ""), row.get("interval_emission_pct", ""), row.get("target_support_match_pct", ""), row.get("off_target_interval_pct", ""),
                       row.get("conditional_coverage_pct", ""), row.get("conditional_coverage_n", ""), row.get("conditional_coverage_mcse_pct", ""),
                       drow.get("valid_target_coverage_all_emitted_pct", ""), drow.get("n_emitted", ""), drow.get("valid_target_coverage_mcse_pp", ""),
                       row.get("conditional_observed_weight_coverage_pct", ""), row.get("conditional_observed_weight_coverage_n", ""), row.get("conditional_observed_weight_coverage_mcse_pct", ""),
                       row.get("unconditional_missed_intervals", ""), row.get("unconditional_missed_pct", ""), row.get("unconditional_missed_mcse_pct", ""),
                       row.get("mean_point_bias_on_target", ""), row.get("refusal_counts", "")], refs)
    tables.append(full)
    paired = data["benchmark_pairs"]["table"]
    if paired.rows:
        tables.append(add_source_table("S8", "Supplementary Table 8. Paired confirmatory strategy comparisons", paired,
                                       ["design", "first_policy", "second_policy", "contrast", "paired_replicates", "emission_difference",
                                        "emission_difference_mcse", "unconditional_miss_difference", "unconditional_miss_difference_mcse",
                                        "conditional_coverage_difference", "conditional_coverage_difference_mcse", "paired_coverage_n_min",
                                        "conditional_observed_weight_coverage_difference", "conditional_observed_weight_coverage_difference_mcse",
                                        "paired_conditional_observed_weight_n_min", "mean_width_difference_on_jointly_emitted",
                                        "mean_width_difference_mcse", "width_joint_n"],
                                       ["Paired differences are descriptive simulation contrasts over the recorded paired replicate sets."]))
    sparse = data["sparse_summary"]["table"]
    tables.append(add_source_table("S9", "Supplementary Table 9. Full sparse-boundary strategy results", sparse,
                                   ["design", "strategy", "replicates", "point_output_rate", "interval_output_rate", "n_intervals",
                                    "conditional_coverage", "coverage_mcse", "unconditional_missed_intervals", "median_width",
                                    "bias", "bias_mcse", "refusal_evaluation"],
                                   ["The sparse validation holds the score-specific risk difference constant, so the population and observed record-weight targets coincide. B/C/D emit no interval for these structures; conditional coverage is undefined when no interval is emitted."]))

    # S9: all stagewise version comparisons currently available.
    version_sources: list[tuple[str, CSVSource, list[str]]] = []
    for folder in ["eicu_versions", "mimic_iv_versions", "mimic_iii_versions", "zigong_versions"]:
        for filename in ["version_comparison.csv", "paired_version_changes.csv", "version_flow.csv", "endpoint_score_selection_comparison.csv"]:
            rel = f"outputs/v2/reconciliation/{folder}/{filename}"
            if rel in snapshot_map:
                src = CSVSource(ROOT / rel, snapshot_map[rel], rel)
                # Keep all source aggregate columns; provenance is cell-level.
                version_sources.append((f"{folder}/{filename}", src, src.headers))
    for i, (label, source, cols) in enumerate(version_sources, start=1):
        tables.append(add_source_table(f"S{9+i}", f"Supplementary Table {9+i}. Stagewise comparison: {label}", source, cols,
                                       ["Stagewise comparisons are aggregate, source-specific decompositions. Their labels describe the revised stages and should not be interpreted as independent replications."]))

    # S13+: existing aggregate sensitivity and application outputs; no patient rows.
    next_supplement_number = 10 + len(version_sources)
    extra_prefixes = [
        "outputs/v2/measurement_sensitivity/",
        "outputs/v2/published_application/",
        "outputs/v2/amsterdam/",
        "outputs/v2/level_validation/",
        "outputs/v2/zigong/",
        "outputs/v2/sources/",
        "outputs/v2/eicu/",
        "outputs/v2/mimic/",
        "outputs/v2/mimic3/",
        "outputs/v2/reconciliation/",
        "outputs/v2/ed_timing/run_r02/",
        "outputs/v2/conditional_validation/",
        "outputs/v2/bootstrap_precision/run02_final_sources/",
    ]
    version_folders = ("eicu_versions/", "mimic_iv_versions/", "mimic_iii_versions/", "zigong_versions/")
    for path in sorted(V2.rglob("*.csv")):
        rel = relative(ROOT, path)
        if not any(rel.startswith(prefix) for prefix in extra_prefixes):
            continue
        if rel.startswith("outputs/v2/reconciliation/") and any(folder in rel for folder in version_folders):
            continue
        snapshot = snapshot_map.get(rel)
        if snapshot is None:
            continue
        src = CSVSource(ROOT / rel, snapshot, rel)
        if not src.rows:
            continue
        table_id = f"S{next_supplement_number}"
        title = f"Supplementary Table {next_supplement_number}. Aggregate snapshot: {rel}"
        tables.append(add_source_table(table_id, title, src, src.headers,
                                       ["Aggregate source table copied without recomputing estimates."]))
        next_supplement_number += 1
    return tables


def render_markdown(tables: list[Table], mode: str, checks: dict[str, Any]) -> str:
    status = "FINAL" if mode == "final" else "PREVIEW — incomplete database set"
    chunks = [f"# V2 table package ({status})\n\n",
              "Generated from hash-frozen aggregate CSV/JSON/Markdown inputs. Numeric cell provenance is in `table_numeric_provenance_v2.csv`; copied input hashes and row/column counts are in `source_freeze_manifest.csv`.\n\n"]
    if mode == "preview":
        present = ", ".join(checks.get("datasets", {}).keys())
        chunks.append(f"**Preview status:** available analysis inputs: {present}. MIMIC-III is pending and is omitted from this preview; no pending MIMIC-III values are inserted. Final mode requires all 19 Table 2 cells.\n\n")
    for table in tables:
        chunks.append(f"## {table.title}\n\n")
        chunks.append("| " + " | ".join(md_cell(h) for h in table.headers) + " |\n")
        chunks.append("| " + " | ".join("---" for _ in table.headers) + " |\n")
        for row in table.rows:
            values = [md_cell(row[h]) for h in table.headers]
            if row["_section"]:
                values = [f"**{values[0]}**"] + [""] * (len(values) - 1)
            elif row["_bold"]:
                values = [f"**{v}**" if v else "" for v in values]
            chunks.append("| " + " | ".join(values) + " |\n")
        if table.notes:
            chunks.append("\n**Notes.**\n\n")
            chunks.extend(f"- {note}\n" for note in table.notes)
        chunks.append("\n")
    return "".join(chunks)


def render_html(tables: list[Table], mode: str, checks: dict[str, Any]) -> str:
    status = "FINAL" if mode == "final" else "PREVIEW — incomplete database set"
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
           "<title>V2 JCE tables</title>",
           "<style>body{font-family:Arial,sans-serif;font-size:9.5pt;margin:1.4em}h1{font-size:18pt}h2{font-size:13pt;margin-top:2em}table{border-collapse:collapse;width:100%;margin:.5em 0 1.1em;font-size:8.5pt}th,td{border:1px solid #555;padding:4px 5px;vertical-align:top}thead th{background:#e8edf3}.section td{font-weight:bold;background:#dce4ed}.bold td,.bold th{font-weight:bold}.notes{font-size:9pt}li{margin:.3em 0}</style>",
           "</head><body>", f"<h1>V2 JCE tables — {html.escape(status)}</h1>",
           "<p>Generated from hash-frozen aggregate outputs. Numeric cell provenance is in <em>table_numeric_provenance_v2.csv</em>; source hashes are in <em>source_freeze_manifest.csv</em>.</p>"]
    if mode == "preview":
        present = ", ".join(checks.get("datasets", {}).keys())
        out.append(f"<p><strong>Preview:</strong> available aggregate analyses: {html.escape(present)}. MIMIC-III is pending and is omitted from this preview; no pending values are inserted.</p>")
    for table in tables:
        out.append(f"<h2>{html.escape(table.title)}</h2><table><thead><tr>")
        out.extend(f"<th scope=\"col\">{html.escape(h)}</th>" for h in table.headers)
        out.append("</tr></thead><tbody>")
        for row in table.rows:
            klass = "section" if row["_section"] else ("bold" if row["_bold"] else "")
            out.append(f"<tr class=\"{klass}\">")
            for i, header in enumerate(table.headers):
                value = html.escape(row[header]).replace("\n", "<br>")
                if i == 0:
                    out.append(f"<th scope=\"row\">{value}</th>")
                else:
                    out.append(f"<td>{value}</td>")
            out.append("</tr>")
        out.append("</tbody></table>")
        if table.notes:
            out.append("<div class=\"notes\"><strong>Notes.</strong><ul>")
            out.extend(f"<li>{html.escape(note)}</li>" for note in table.notes)
            out.append("</ul></div>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def write_table_csv(stage: Path, table: Table) -> None:
    rows = [{header: row[header] for header in table.headers} for row in table.rows if not row["_section"]]
    csv_write(stage / f"{table.table_id.lower()}.csv", table.headers, rows)


def write_provenance(stage: Path) -> None:
    headers = ["output_table", "output_row", "output_column", "displayed_value", "source_file",
               "source_physical_row_header_1", "source_column", "raw_value", "formatting_or_derivation"]
    ordered = sorted(PROVENANCE, key=lambda r: (r["output_table"], r["output_row"], r["output_column"],
                                                 r["source_file"], int(r["source_physical_row_header_1"]), r["source_column"]))
    csv_write(stage / "table_numeric_provenance_v2.csv", headers, ordered)


def write_manifest(stage: Path, snapshot_rows: list[dict[str, Any]]) -> None:
    source_headers = ["record_type", "source_file", "snapshot_file", "bytes", "physical_csv_rows_including_header",
                      "data_rows", "column_count", "columns", "md5", "sha256"]
    csv_write(stage / "source_freeze_manifest.csv", source_headers, snapshot_rows)


def table_shape_summary(main_tables: list[Table], supplement: list[Table], checks: dict[str, Any]) -> dict[str, Any]:
    shapes = {table.table_id: sum(1 for row in table.rows if not row["_section"]) for table in main_tables}
    supplement_shapes = {table.table_id: len(table.rows) for table in supplement}
    expected = {"T1": 20, "T2": 19, "T3": None, "T4": 6, "T5": 21, "T6": 13}
    if checks["mode"] == "preview":
        expected["T1"] = checks["expected_table_shapes"]["table1_level_rows"]
        expected["T2"] = checks["expected_table_shapes"]["table2_database_condition_cells"]
    for table_id, shape in expected.items():
        if shape is not None and shapes.get(table_id) != shape:
            raise RuntimeError(f"Unexpected {table_id} data row count: {shapes.get(table_id)}; expected {shape}")
    return {"main_table_rows": shapes, "supplementary_table_rows": supplement_shapes,
            "numeric_provenance_rows": len(PROVENANCE)}


def write_outputs(stage: Path, main_tables: list[Table], supplement: list[Table], mode: str,
                  checks: dict[str, Any], snapshot_rows: list[dict[str, Any]], copied: list[str], json_data: dict[str, Any]) -> None:
    all_tables = main_tables + supplement
    (stage / "tables_v2.md").write_text(render_markdown(main_tables, mode, checks), encoding="utf-8")
    (stage / "tables_v2.html").write_text(render_html(main_tables, mode, checks), encoding="utf-8")
    (stage / "supplementary_tables_v2.md").write_text(render_markdown(supplement, mode, checks).replace("# V2 table package", "# V2 supplementary tables", 1), encoding="utf-8")
    (stage / "supplementary_tables_v2.html").write_text(render_html(supplement, mode, checks).replace("<title>V2 JCE tables</title>", "<title>V2 JCE supplementary tables</title>", 1), encoding="utf-8")
    for table in all_tables:
        write_table_csv(stage, table)
    write_provenance(stage)
    write_manifest(stage, snapshot_rows)
    shapes = table_shape_summary(main_tables, supplement, checks)
    checks["delivery_shapes"] = shapes
    checks["aggregate_snapshot"] = {
        "frozen_files": len(copied),
        "snapshot_relative_root": "source_snapshot/outputs/v2",
        "excluded_categories": ["log files", "binary figures", "replicate-level simulation CSVs", "superseded simulation outputs", "patient panels"],
        "snapshotted_source_files": copied,
    }
    json_write(stage / "table_build_checks.json", checks)
    manifest = {
        "mode": mode,
        "status": "final tables generated" if mode == "final" else "partial preview; MIMIC-III omitted pending analysis",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "workspace": ROOT.as_posix(),
        "input_snapshots": "source_snapshot/outputs/v2",
        "source_freeze_manifest": "source_freeze_manifest.csv",
        "table_count_main": len(main_tables),
        "table_count_supplementary": len(supplement),
        "row_level_numeric_provenance": "table_numeric_provenance_v2.csv",
        "primary_databases_available": list(checks["datasets"].keys()),
        "benchmark": json_data.get("benchmark_manifest", {}),
        "notes": ["All input aggregates were hash-verified at freeze time and tables were read from the frozen copies.",
                  "No patient-level panel, source data, replicate-level simulation CSV, superseded simulation output, or log was copied.",
                  "The figure deliverables are maintained by the figure build and are not generated by this table builder."],
    }
    json_write(stage / "table_build_manifest_v2.json", manifest)
    readme = [
        f"# V2 table package ({mode})", "",
        "Main tables are in `tables_v2.md`, `tables_v2.html`, and `t1.csv` through `t6.csv`. Supplementary aggregate tables are in `supplementary_tables_v2.md` and `.html`, with one CSV per table.",
        "", "## Provenance and integrity", "",
        "`table_numeric_provenance_v2.csv` maps every numeric result cell in the tables to its source aggregate file, physical CSV row (header is row 1), source column, raw value, and formatting/derivation.",
        "`source_freeze_manifest.csv` records MD5 and SHA-256 hashes, byte sizes, row/column counts, and the frozen snapshot path for each structured aggregate source. All table values were read from the copied snapshot.",
        "`delivery_hash_manifest.csv` contains MD5 and SHA-256 for package files other than itself and its sidecar. `delivery_hash_manifest.sha256.txt` binds the manifests.",
        "`table_build_checks.json` records numeric consistency and expected row-count checks.",
        "", "## Scope", "",
        "The snapshot includes aggregate CSV, JSON, and Markdown outputs under `outputs/v2`; logs, binary figures, patient-level panels, replicate-level simulation CSVs, and the archived superseded simulation are excluded. No raw rare text is copied.",
        "The final mode requires eICU-CRD, MIMIC-IV, MIMIC-III, and Zigong analysis aggregates and exactly 19 main Table 2 cells. Preview mode never inserts pending MIMIC-III values.",
        "",
    ]
    (stage / "README.md").write_text("\n".join(readme), encoding="utf-8")
    # Hash all package outputs except the hash manifest and its sidecar, then bind those manifests separately.
    hash_rows: list[dict[str, Any]] = []
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name in {"delivery_hash_manifest.csv", "delivery_hash_manifest.sha256.txt"}:
            continue
        md5, sha, size = file_hashes(path)
        hash_rows.append({"file": relative(stage, path), "bytes": size, "md5": md5, "sha256": sha})
    csv_write(stage / "delivery_hash_manifest.csv", ["file", "bytes", "md5", "sha256"], hash_rows)
    manifest_hash = file_hashes(stage / "delivery_hash_manifest.csv")
    source_manifest_hash = file_hashes(stage / "source_freeze_manifest.csv")
    sidecar = (f"delivery_hash_manifest.csv md5={manifest_hash[0]} sha256={manifest_hash[1]}\n"
               f"source_freeze_manifest.csv md5={source_manifest_hash[0]} sha256={source_manifest_hash[1]}\n")
    (stage / "delivery_hash_manifest.sha256.txt").write_text(sidecar, encoding="ascii")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["preview", "final"], default="preview",
                        help="preview uses completed analysis inputs; final requires all four databases")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output directory (defaults to outputs/v2/delivery_preview or delivery). Existing nonempty directories are never overwritten.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mode = args.mode
    pending_repairs = list(ANALYSIS.glob('*/PENDING_SOURCE_REPAIR.json'))
    if pending_repairs:
        raise RuntimeError(f'Analysis inputs require source repair before table generation: {pending_repairs}')
    if mode == "final":
        for rel in ["conditional_validation/clinical/run_03_final/clinical_application_provenance.json",
                    "bootstrap_precision/run02_final_sources/run_status.json"]:
            manifest_path = V2 / rel
            if not manifest_path.is_file() or json.loads(manifest_path.read_text(encoding="utf-8-sig")).get("status") != "complete":
                raise RuntimeError(f'Final supplementary analysis is not complete: {manifest_path}')
    output = args.output or (V2 / ("delivery_preview_3" if mode == "preview" else "delivery"))
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite nonempty delivery directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=output.name + ".build-", dir=output.parent) as temp_name:
        stage = Path(temp_name)
        snapshot_map, snapshot_rows, copied = freeze_aggregate_outputs(stage)
        data, json_data = load_sources(snapshot_map, mode)
        checks = run_data_checks(data, json_data, mode)
        main_tables = [build_table1(data), build_table2(data, mode), build_table3(data),
                       build_table4(data), build_table5(data), build_table6(data, json_data)]
        supplement = make_supplementary_tables(data, snapshot_map, json_data, mode)
        write_outputs(stage, main_tables, supplement, mode, checks, snapshot_rows, copied, json_data)
        if output.exists() and any(output.iterdir()):
            raise FileExistsError(f"Refusing to overwrite nonempty delivery directory: {output}")
        if output.exists():
            output.rmdir()
        stage.rename(output)
    print(json.dumps({"status": "complete", "mode": mode, "output": str(output),
                      "main_tables": 6, "supplementary_tables": len(supplement),
                      "numeric_provenance_rows": len(PROVENANCE),
                      "databases": list(checks["datasets"].keys()),
                      "table_rows": checks["delivery_shapes"]["main_table_rows"]}, indent=2))


if __name__ == "__main__":
    main()

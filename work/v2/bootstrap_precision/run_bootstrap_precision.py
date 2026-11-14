"""Locked 5,000-draw patient-cluster bootstrap precision diagnostic.

This diagnostic reproduces the observed-common-support, pooled-record-weight
Delta_w estimand and the C-policy draw-level bootstrap gates. It does not alter
the shared audit tool or any primary C output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import binom


ROOT = Path(__file__).resolve().parents[3]
V2 = ROOT / "work" / "v2"
sys.path.insert(0, str(V2))

from analyse_panels import SCORES, analysis_frame, audit_module, normalize_panel  # noqa: E402
from estimands import direct_contrast  # noqa: E402


PRIVATE_BASE = Path(r"F:\分析专用\meta_measurement_20261103\work\paperB_v2")
OUT_ROOT = ROOT / "outputs" / "v2" / "bootstrap_precision"
PENDING_MIII = ROOT / "outputs" / "v2" / "analysis" / "mimic_iii" / "PENDING_SOURCE_REPAIR.json"
RUN01_MANIFEST = OUT_ROOT / "run01_available_sources" / "config_frozen.json"
MASTER_SEED = 27112030
REQUESTED_DRAWS = 5000
C_BOOTSTRAP_SEED = 20261112
C_REPS = 60
C_MIN_EVENTS = 10
C_MIN_USABLE = 20
C_MIN_LEVEL_RECORDS = 20
C_MIN_ARM_RECORDS = 10
C_MIN_PATIENTS = 20
MC_ALPHA = 0.05
MIMIC_III_CORRECTED_SHA256 = "ee935d72baea239d5b1e4dfdedb2abea5684abf17c2363ea86ade41d456f3538"
MIMIC_III_REVIEW = ROOT / "work" / "v2" / "mimic3" / "final_bp_independent_review.md"
MIMIC_III_RESOLVED_MARKER = ROOT / "work" / "v2" / "mimic3" / "repair_logs" / "RESOLVED_PENDING_SOURCE_REPAIR.json"

SOURCES = {
    "eicu": {
        "database": "eICU-CRD",
        "panel": ROOT / "work" / "v2" / "eicu" / "eicu_disease_panel.csv.gz",
        "analysis_key": "eicu",
        "kind": "standard",
        "diseases": tuple(SCORES),
    },
    "mimic_iv": {
        "database": "MIMIC-IV",
        "panel": PRIVATE_BASE / "mimic" / "mimic_iv_v2_score_panel.csv.gz",
        "analysis_key": "mimic_iv",
        "kind": "standard",
        "diseases": tuple(SCORES),
    },
    "mimic_iii": {
        "database": "MIMIC-III",
        "panel": PRIVATE_BASE / "mimic3" / "mimic_iii_v2_score_panel.csv.gz",
        "analysis_key": "mimic_iii",
        "kind": "standard",
        "diseases": tuple(SCORES),
    },
    "zigong": {
        "database": "Zigong",
        "panel": PRIVATE_BASE / "zigong" / "zigong_admission_panel.csv.gz",
        "analysis_key": "zigong",
        "kind": "standard",
        "diseases": tuple(SCORES),
    },
    "peer": {
        "database": "PEER-adapted-eICU",
        "panel": PRIVATE_BASE / "published_application" / "adapted_peer_population.csv.gz",
        "kind": "peer",
        "diseases": ("pneumonia",),
    },
    "amsterdam": {
        "database": "AmsterdamUMCdb 1.0.2",
        "panel": PRIVATE_BASE / "amsterdam" / "private" / "qsofa_sepsis_icu_dictionary_unit_repair_outcome.csv.gz",
        "kind": "amsterdam",
        "diseases": ("sepsis",),
    },
}

HELPER_PATHS = [
    Path(__file__).resolve(),
    Path(__file__).resolve().with_name("test_bootstrap_precision.py"),
    V2 / "audit" / "cohort_definition_audit.py",
    V2 / "estimands.py",
    V2 / "analyse_panels.py",
    V2 / "amsterdam" / "run_amsterdam_dictionary_unit_repair.py",
    V2 / "conditional_validation" / "run_clinical_with_peer_adapter.py",
    V2 / "published_application.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_frozen_hash(config: dict[str, Any], item_key: str, path: Path) -> str:
    expected = config.get("frozen_inputs", {}).get(item_key, {}).get("sha256")
    if not expected:
        raise KeyError(f"Frozen manifest lacks {item_key}.")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(f"Input changed after the run configuration was frozen: {item_key}")
    return observed


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def safe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def nested_values(payload: Any, field_name: str) -> list[Any]:
    """Return every exact-key value found in nested manifest JSON."""
    found: list[Any] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == field_name:
                found.append(value)
            found.extend(nested_values(value, field_name))
    elif isinstance(payload, list):
        for value in payload:
            found.extend(nested_values(value, field_name))
    return found


def data_artifact_hashes() -> dict[str, Any]:
    """Hash all source panels and existing eligibility/audit artifacts before analysis."""
    items: dict[str, Any] = {}
    for key, spec in SOURCES.items():
        panel = Path(spec["panel"])
        items[f"panel:{key}"] = {
            "path": str(panel.resolve(strict=False)),
            "exists": panel.is_file(),
            "sha256": sha256_file(panel) if panel.is_file() else None,
            "byte_size": panel.stat().st_size if panel.is_file() else None,
        }
    for key in ("eicu", "mimic_iv", "mimic_iii", "zigong"):
        folder = ROOT / "outputs" / "v2" / "analysis" / key
        for name in ("summary.csv", "audit_details.json", "analysis_provenance.json"):
            path = folder / name
            # MIMIC-III is source-repair-gated; hashing its marker and panel is enough
            # for run01. Do not read/hash its superseded aggregates into that run.
            if key == "mimic_iii":
                continue
            items[f"artifact:{key}:{name}"] = {
                "path": str(path.resolve(strict=False)), "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
    pending_path = PENDING_MIII
    items["gate:mimic_iii_pending_source_repair"] = {
        "path": str(pending_path.resolve(strict=False)), "exists": pending_path.is_file(),
        "sha256": sha256_file(pending_path) if pending_path.is_file() else None,
    }
    peer_config = ROOT / "outputs" / "v2" / "conditional_validation" / "clinical" / "run_02" / "clinical_application_config.json"
    peer_alias = ROOT / "outputs" / "v2" / "conditional_validation" / "clinical" / "run_02" / "peer_outcome_alias_validation.json"
    for name, path in (("peer_application_config", peer_config), ("peer_alias_validation", peer_alias)):
        items[f"artifact:{name}"] = {
            "path": str(path.resolve(strict=False)), "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
    amsterdam_dir = ROOT / "outputs" / "v2" / "amsterdam" / "dictionary_unit_repair"
    for name in ("dictionary_unit_repair_source_manifest.json", "audit_gcs_le_13.json",
                 "audit_gcs_lt_15_sensitivity.json", "amsterdam_unit_repair_interval_comparison.csv"):
        path = amsterdam_dir / name
        items[f"artifact:amsterdam:{name}"] = {
            "path": str(path.resolve(strict=False)), "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
    if PENDING_MIII.is_file():
        # Capture only the gate file hash for run01; do not consume its superseded outputs.
        items["mimic_iii_pending_gate"] = {"status": "source repair pending"}
    return items


def freeze_config(run_id: str, final: bool, outdir: Path) -> dict[str, Any]:
    launcher_files = {"launcher.json", "stdout.log", "stderr.log"}
    if outdir.exists() and any(path.name not in launcher_files for path in outdir.iterdir()):
        raise FileExistsError(f"Run output folder already contains files; preserve it: {outdir}")
    outdir.mkdir(parents=True, exist_ok=True)
    source_hashes = data_artifact_hashes()
    if not source_hashes["panel:eicu"]["exists"]:
        raise FileNotFoundError("The eICU primary panel is unavailable.")
    if final:
        if PENDING_MIII.exists():
            raise RuntimeError(f"MIMIC-III remains source-repair-gated: {PENDING_MIII}")
        miii = source_hashes["panel:mimic_iii"]
        if not miii["exists"] or not miii["sha256"]:
            raise FileNotFoundError("Corrected MIMIC-III panel is unavailable.")
        if miii["sha256"] != MIMIC_III_CORRECTED_SHA256:
            raise RuntimeError("MIMIC-III panel hash differs from the independently reviewed corrected source hash.")
        if not RUN01_MANIFEST.is_file():
            raise FileNotFoundError("run01 manifest is required to verify the MIMIC-III source changed.")
        old = json.loads(RUN01_MANIFEST.read_text(encoding="utf-8"))
        old_hash = old["frozen_inputs"]["panel:mimic_iii"]["sha256"]
        if miii["sha256"] == old_hash:
            raise RuntimeError("MIMIC-III panel hash is unchanged from the pending superseded input.")
        if not MIMIC_III_RESOLVED_MARKER.is_file() or not MIMIC_III_REVIEW.is_file():
            raise FileNotFoundError("Resolved marker and independent BP review are required before the final run.")
        resolved = json.loads(MIMIC_III_RESOLVED_MARKER.read_text(encoding="utf-8"))
        if resolved.get("status") != "withdrawn_pending_source_repair":
            raise RuntimeError("Resolved source-repair marker has an unexpected prior state.")
        review_text = MIMIC_III_REVIEW.read_text(encoding="utf-8")
        required_review_text = [
            MIMIC_III_CORRECTED_SHA256,
            "独立运行全部 7 项测试，通过",
            "主分析依赖代码哈希与当前文件一致",
            "全部一致",
        ]
        if any(token not in review_text for token in required_review_text):
            raise RuntimeError("Independent MIMIC-III BP review lacks its required PASS evidence.")
        source_hashes["artifact:mimic_iii:resolved_pending_marker"] = {
            "path": str(MIMIC_III_RESOLVED_MARKER.resolve()), "exists": True,
            "sha256": sha256_file(MIMIC_III_RESOLVED_MARKER)}
        source_hashes["artifact:mimic_iii:independent_review"] = {
            "path": str(MIMIC_III_REVIEW.resolve()), "exists": True,
            "sha256": sha256_file(MIMIC_III_REVIEW)}
        # Require the current C provenance to have been rebuilt against the corrected panel.
        prov_path = ROOT / "outputs" / "v2" / "analysis" / "mimic_iii" / "analysis_provenance.json"
        summary_path = ROOT / "outputs" / "v2" / "analysis" / "mimic_iii" / "summary.csv"
        audit_path = ROOT / "outputs" / "v2" / "analysis" / "mimic_iii" / "audit_details.json"
        if not all(p.is_file() for p in (prov_path, summary_path, audit_path)):
            raise FileNotFoundError("Corrected MIMIC-III provenance, C summary, and audit details must exist.")
        provenance = json.loads(prov_path.read_text(encoding="utf-8"))
        if provenance.get("panel_sha256") != miii["sha256"]:
            raise RuntimeError("Corrected MIMIC-III C outputs are not provenance-matched to the current panel hash.")
        analysis_script = V2 / "analyse_panels.py"
        if provenance.get("script_sha256") != sha256_file(analysis_script):
            raise RuntimeError("MIMIC-III analysis provenance uses a stale analysis-driver hash.")
        provenance_dependencies = {Path(item.get("path", "")).resolve(): item.get("sha256")
                                  for item in provenance.get("dependencies", [])}
        for dependency in (V2 / "audit" / "cohort_definition_audit.py", V2 / "estimands.py", V2 / "robustness.py"):
            resolved_dependency = dependency.resolve()
            if provenance_dependencies.get(resolved_dependency) != sha256_file(dependency):
                raise RuntimeError(f"MIMIC-III analysis provenance dependency is stale: {dependency.name}")
        source_hashes["artifact:mimic_iii:summary.csv"] = {
            "path": str(summary_path.resolve()), "exists": True, "sha256": sha256_file(summary_path)}
        source_hashes["artifact:mimic_iii:audit_details.json"] = {
            "path": str(audit_path.resolve()), "exists": True, "sha256": sha256_file(audit_path)}
        source_hashes["artifact:mimic_iii:analysis_provenance.json"] = {
            "path": str(prov_path.resolve()), "exists": True, "sha256": sha256_file(prov_path)}
    for key, item in source_hashes.items():
        if key.startswith("panel:") and key != "panel:mimic_iii" and not item["exists"]:
            raise FileNotFoundError(f"Source panel is unavailable: {item['path']}")
    code_hashes = {str(path.resolve()): sha256_file(path) for path in HELPER_PATHS if path.is_file()}
    config = {
        "record_type": "delta_w_patient_cluster_bootstrap_precision_config",
        "run_id": run_id,
        "status": "frozen_before_diagnostic_bootstrap_outcomes",
        "created_utc": utc_now(),
        "requested_draws": REQUESTED_DRAWS,
        "master_seed": MASTER_SEED,
        "rng": "numpy Generator / PCG64; per-row SeedSequence spawn key is stable SHA-256-derived row identifier",
        "row_seed_derivation": "SeedSequence(entropy=27112030, spawn_key=(first_32_bits_SHA256(source|disease|variant),))",
        "draw_batch_memory_limit": "at most 2,000,000 integer cluster draws per generation batch, capped at 64 replicates",
        "estimand": "Delta_w: never-primary minus primary mortality risk difference in percentage points, pooled observed record shares across fixed observed common-support score levels",
        "primary_C_eligibility": {
            "source_of_status": "existing frozen C summary/audit outputs for the four primary databases and Amsterdam; for PEER, audit_v2 with the shared frozen C rules",
            "bootstrap_eligibility": "every observed score-by-group support cell retained; at least 10 events in each definition in each usable draw; at least 20 usable draws for primary C status",
            "deterministic_rules": {"min_records_per_score_level": C_MIN_LEVEL_RECORDS,
                                    "min_records_per_score_definition_cell": C_MIN_ARM_RECORDS,
                                    "min_distinct_patients_total_and_per_cell": C_MIN_PATIENTS,
                                    "nondegenerate_outcome_per_score_definition_cell": True},
            "primary_c_existing_bootstrap": {"draws": C_REPS, "seed": C_BOOTSTRAP_SEED,
                                             "min_events_per_definition": C_MIN_EVENTS,
                                             "min_usable_draws": C_MIN_USABLE},
        },
        "precision_bootstrap": {
            "cluster_unit": "patient; all complete-case rows of each selected patient are resampled together",
            "input_universe": "all complete-case patients, including patients with no rows on observed common support; those patients have zero supported-cell counts but remain in the resampling population",
            "draw_count": REQUESTED_DRAWS,
            "draw_validity": "fixed observed common support retained and at least 10 events in each definition; all other draws are refused and counted",
            "weights": "re-estimated pooled record shares within each draw; never held fixed",
            "point_estimate": "unrounded direct Delta_w; no rounding enters resampling or quantiles",
            "percentiles": [2.5, 97.5],
            "quantile_method": "numpy linear percentile, matching the shared C reducer",
            "monte_carlo_ranges": "separate exact binomial order-statistic 95% ranges for each bootstrap-distribution percentile endpoint, conditional on IID usable draws; not clinical confidence intervals",
        },
        "run_scope": "all available C-estimable primary disease rows, plus PEER pneumonia and both repaired Amsterdam score variants; skipped rows and reasons retained",
        "run_kind": "final_all_sources_after_mimic_iii_repair" if final else "run01_available_sources_with_mimic_iii_gated",
        "mimic_iii_final_gate": ({
            "expected_corrected_panel_sha256": MIMIC_III_CORRECTED_SHA256,
            "observed_panel_sha256": source_hashes["panel:mimic_iii"]["sha256"],
            "source_repair_marker_absent_at_original_path": not PENDING_MIII.exists(),
            "resolved_marker_sha256": source_hashes.get("artifact:mimic_iii:resolved_pending_marker", {}).get("sha256"),
            "independent_review_sha256": source_hashes.get("artifact:mimic_iii:independent_review", {}).get("sha256"),
            "provenance_bound_to_current_panel": True,
        } if final else {"status": "pending; MIMIC-III excluded"}),
        "frozen_inputs": source_hashes,
        "code_sha256": code_hashes,
        "environment": {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__},
        "seed_and_draw_count_fixed_before_outcomes": True,
        "patient_level_records_written": False,
        "primary_c_modified": False,
    }
    config_path = outdir / "config_frozen.json"
    with config_path.open("x", encoding="utf-8") as stream:
        json.dump(config, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return config


def stable_child_seed(key: str) -> np.random.SeedSequence:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    spawn_key = int.from_bytes(digest[:4], "big", signed=False)
    return np.random.SeedSequence(MASTER_SEED, spawn_key=(spawn_key,))


def common_support_levels(frame: pd.DataFrame) -> np.ndarray:
    groups = set(pd.to_numeric(frame["grp"], errors="coerce").dropna().astype(int).unique())
    if not {0, 1}.issubset(groups):
        return np.asarray([], dtype=float)
    g = pd.to_numeric(frame["grp"], errors="coerce").to_numpy(int)
    score = pd.to_numeric(frame["score"], errors="coerce").to_numpy(float)
    return np.intersect1d(np.unique(score[g == 0]), np.unique(score[g == 1])).astype(float)


class CellLedger:
    """Compact per-patient score-by-definition record/event counts."""

    def __init__(self, patient_ids: np.ndarray, levels: np.ndarray,
                 record_counts: np.ndarray, event_counts: np.ndarray):
        self.patient_ids = patient_ids
        self.levels = levels.astype(float)
        self.record_counts = record_counts
        self.event_counts = event_counts
        self.n_patients = len(patient_ids)


def build_cell_ledger(frame: pd.DataFrame, levels: np.ndarray) -> CellLedger:
    required = ["pid", "grp", "y", "score"]
    if frame[required].isna().any().any():
        raise ValueError("Cell ledger requires complete patient, score, group, and binary outcome fields.")
    if not frame["grp"].isin([0, 1]).all() or not frame["y"].isin([0, 1]).all():
        raise ValueError("Cell ledger requires binary group (0/1) and outcome (0/1).")
    if len(levels) == 0:
        return CellLedger(np.asarray([], dtype=object), levels, np.zeros((0, 0), dtype=np.int64),
                          np.zeros((0, 0), dtype=np.int64))
    patient_codes, patient_ids = pd.factorize(frame["pid"], sort=True)
    score = frame["score"].to_numpy(float)
    group = frame["grp"].to_numpy(int)
    outcome = frame["y"].to_numpy(int)
    score_idx = np.searchsorted(levels, score)
    inside = ((score_idx < len(levels)) &
              (levels[np.clip(score_idx, 0, len(levels) - 1)] == score))
    k = len(levels)
    cell = group[inside] * k + score_idx[inside]
    n = np.zeros((len(patient_ids), 2 * k), dtype=np.int64)
    e = np.zeros_like(n)
    np.add.at(n, (patient_codes[inside], cell), 1)
    np.add.at(e, (patient_codes[inside], cell), outcome[inside])
    return CellLedger(np.asarray(patient_ids), levels, n, e)


def value_for_multiplicities(ledger: CellLedger, multiplicities: np.ndarray,
                             min_events: int = C_MIN_EVENTS) -> tuple[float | None, str]:
    """Evaluate exact Delta_w from a patient-multiplicity vector, with C draw gates."""
    if len(ledger.levels) == 0:
        return None, "no_support"
    n_cell = multiplicities @ ledger.record_counts
    e_cell = multiplicities @ ledger.event_counts
    k = len(ledger.levels)
    n0, n1 = n_cell[:k], n_cell[k:]
    e0, e1 = e_cell[:k], e_cell[k:]
    if not np.all((n0 > 0) & (n1 > 0)):
        return None, "lost_levels"
    if min(float(e0.sum()), float(e1.sum())) < min_events:
        return None, "few_events"
    ns = n0 + n1
    p1 = e1 / n1
    p0 = e0 / n0
    value = float(np.sum(ns * (p1 - p0)) / np.sum(ns))
    return value, "ok"


def numeric_bootstrap(frame: pd.DataFrame, reps: int, seed_sequence: np.random.SeedSequence,
                      min_events: int = C_MIN_EVENTS) -> dict[str, Any]:
    levels = common_support_levels(frame)
    ledger = build_cell_ledger(frame, levels)
    n_clusters = ledger.n_patients
    failures = {"no_support": 0, "few_events": 0, "lost_levels": 0, "ok": 0}
    if not len(levels) or n_clusters == 0:
        failures["no_support"] = reps
        return {"values": np.asarray([], dtype=float), "failures": failures,
                "n_usable": 0, "n_requested": int(reps), "n_input_patients": n_clusters,
                "n_support_levels": len(levels), "batch_size": 0}
    # Bound the temporary patient-index draw matrix. This is in addition to the
    # small patient-by-cell sufficient-statistic matrices held by the ledger.
    batch_size = max(1, min(64, 2_000_000 // max(1, n_clusters)))
    rng = np.random.default_rng(seed_sequence)
    all_values: list[np.ndarray] = []
    done = 0
    while done < reps:
        batch = min(batch_size, reps - done)
        draws = rng.integers(0, n_clusters, size=(batch, n_clusters), dtype=np.int32)
        offsets = np.arange(batch, dtype=np.int64)[:, None] * n_clusters
        multiplicities = np.bincount((draws.astype(np.int64, copy=False) + offsets).ravel(),
                                     minlength=batch * n_clusters).reshape(batch, n_clusters)
        sampled_n = multiplicities @ ledger.record_counts
        sampled_e = multiplicities @ ledger.event_counts
        k = len(levels)
        n0, n1 = sampled_n[:, :k], sampled_n[:, k:]
        e0, e1 = sampled_e[:, :k], sampled_e[:, k:]
        has_levels = np.all((n0 > 0) & (n1 > 0), axis=1)
        few_events = (np.minimum(e0.sum(axis=1), e1.sum(axis=1)) < min_events) & has_levels
        valid = has_levels & ~few_events
        failures["lost_levels"] += int((~has_levels).sum())
        failures["few_events"] += int(few_events.sum())
        if valid.any():
            n0v, n1v = n0[valid], n1[valid]
            e0v, e1v = e0[valid], e1[valid]
            ns = n0v + n1v
            d = e1v / n1v - e0v / n0v
            values = (ns * d).sum(axis=1) / ns.sum(axis=1)
            values = values[np.isfinite(values)]
            all_values.append(values.astype(float, copy=False))
            failures["ok"] += int(len(values))
        done += batch
    values = np.concatenate(all_values) if all_values else np.asarray([], dtype=float)
    return {"values": values, "failures": failures, "n_usable": int(len(values)),
            "n_requested": int(reps), "n_input_patients": n_clusters,
            "n_support_levels": len(levels), "batch_size": batch_size,
            "patients_without_support_cells": int((ledger.record_counts.sum(axis=1) == 0).sum())}


def mc_order_statistic_range(values: np.ndarray, probability: float,
                             alpha: float = MC_ALPHA) -> dict[str, Any]:
    """Equal-tail binomial order-statistic range for a bootstrap percentile endpoint."""
    values = np.sort(np.asarray(values, dtype=float))
    n = len(values)
    if n == 0:
        return {"lower_pp": None, "upper_pp": None, "lower_rank_1based": None,
                "upper_rank_1based": None, "nominal_coverage": 1 - alpha,
                "achieved_binomial_coverage": None, "n_usable_draws": 0}
    # For K~Binomial(n,p), Q_p lies between X_(lo) and X_(hi) when lo<=K<hi.
    lo_rank = int(binom.ppf(alpha / 2, n, probability))
    hi_rank = int(binom.ppf(1 - alpha / 2, n, probability)) + 1
    lo_rank = max(0, lo_rank)
    hi_rank = min(n + 1, hi_rank)
    lower = None if lo_rank == 0 else float(values[lo_rank - 1])
    upper = None if hi_rank == n + 1 else float(values[hi_rank - 1])
    coverage = float(binom.cdf(hi_rank - 1, n, probability)
                     - (binom.cdf(lo_rank - 1, n, probability) if lo_rank > 0 else 0.0))
    return {"lower_pp": None if lower is None else lower * 100,
            "upper_pp": None if upper is None else upper * 100,
            "lower_rank_1based": lo_rank if lo_rank else None,
            "upper_rank_1based": hi_rank if hi_rank <= n else None,
            "nominal_coverage": 1 - alpha,
            "achieved_binomial_coverage": coverage,
            "n_usable_draws": n}


def run_precision(frame: pd.DataFrame, key: str, reps: int = REQUESTED_DRAWS) -> dict[str, Any]:
    levels = common_support_levels(frame)
    if len(levels) == 0:
        raise ValueError(f"C-estimable row has no observed common support: {key}")
    direct = direct_contrast(frame)
    audit = audit_module()
    numeric_point, _, _, _ = audit.stratified_rd(
        frame.score.to_numpy(float), frame.y.to_numpy(float), frame.grp.to_numpy(int),
        support_levels=levels)
    if not np.isclose(numeric_point, direct.estimate, atol=1e-12):
        raise AssertionError(f"shared and independent direct point estimates disagree for {key}")
    result = numeric_bootstrap(frame, reps, stable_child_seed(key), C_MIN_EVENTS)
    values = result.pop("values")
    if result["n_usable"] >= C_MIN_USABLE:
        pct = np.percentile(values, [2.5, 97.5], method="linear")
        lo_pp, hi_pp = float(pct[0] * 100), float(pct[1] * 100)
        lower_mc = mc_order_statistic_range(values, 0.025)
        upper_mc = mc_order_statistic_range(values, 0.975)
        status = "computed"
    else:
        lo_pp = hi_pp = None
        lower_mc = mc_order_statistic_range(values, 0.025)
        upper_mc = mc_order_statistic_range(values, 0.975)
        status = "withheld: fewer than 20 usable precision-bootstrap draws"
    normal_lo = 100 * (direct.estimate - 1.96 * direct.se)
    normal_hi = 100 * (direct.estimate + 1.96 * direct.se)
    return {
        "precision_bootstrap_status": status,
        "precision_requested_draws": reps,
        "precision_usable_draws": result["n_usable"],
        "precision_refused_no_support": result["failures"]["no_support"],
        "precision_refused_lost_levels": result["failures"]["lost_levels"],
        "precision_refused_few_events": result["failures"]["few_events"],
        "precision_valid_draws": result["failures"]["ok"],
        "precision_C_percentile_ci_lower_pp": lo_pp,
        "precision_C_percentile_ci_upper_pp": hi_pp,
        "precision_C_percentile_ci_width_pp": (hi_pp - lo_pp if lo_pp is not None and hi_pp is not None else None),
        "normal_if_ci_exact_lower_pp": float(normal_lo),
        "normal_if_ci_exact_upper_pp": float(normal_hi),
        "normal_if_ci_exact_width_pp": float(normal_hi - normal_lo),
        "precision_lower_endpoint_mc95_lower_pp": lower_mc["lower_pp"],
        "precision_lower_endpoint_mc95_upper_pp": lower_mc["upper_pp"],
        "precision_lower_endpoint_mc95_rank_low": lower_mc["lower_rank_1based"],
        "precision_lower_endpoint_mc95_rank_high": lower_mc["upper_rank_1based"],
        "precision_lower_endpoint_mc95_binomial_coverage": lower_mc["achieved_binomial_coverage"],
        "precision_upper_endpoint_mc95_lower_pp": upper_mc["lower_pp"],
        "precision_upper_endpoint_mc95_upper_pp": upper_mc["upper_pp"],
        "precision_upper_endpoint_mc95_rank_low": upper_mc["lower_rank_1based"],
        "precision_upper_endpoint_mc95_rank_high": upper_mc["upper_rank_1based"],
        "precision_upper_endpoint_mc95_binomial_coverage": upper_mc["achieved_binomial_coverage"],
        "direct_point_unrounded_pp": float(100 * direct.estimate),
        "direct_numerical_se_pp": float(100 * direct.se),
        "n_complete_case_records": int(len(frame)),
        "n_patient_clusters_in_resampling_universe": int(result["n_input_patients"]),
        "n_patients_with_supported_records": int(direct.n_patients),
        "n_records_on_common_support": int(direct.n_records),
        "n_support_levels": int(len(levels)),
        "observed_support_levels": "|".join(str(float(x)) for x in levels),
        "patients_without_support_cells_in_universe": int(result["patients_without_support_cells"]),
        "bootstrap_batch_size": int(result["batch_size"]),
        "direct_estimator_agreement": True,
    }


def load_primary_baseline(source_key: str, config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any], Path, Path]:
    spec = SOURCES[source_key]
    folder = ROOT / "outputs" / "v2" / "analysis" / spec["analysis_key"]
    summary_path, audits_path, provenance_path = (folder / "summary.csv", folder / "audit_details.json",
                                                   folder / "analysis_provenance.json")
    source_hash = assert_frozen_hash(config, f"panel:{source_key}", Path(spec["panel"]))
    assert_frozen_hash(config, f"artifact:{source_key}:summary.csv", summary_path)
    assert_frozen_hash(config, f"artifact:{source_key}:audit_details.json", audits_path)
    assert_frozen_hash(config, f"artifact:{source_key}:analysis_provenance.json", provenance_path)
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("panel_sha256") != source_hash:
        raise RuntimeError(f"C provenance source hash mismatch for {source_key}: {source_hash}")
    summary = pd.read_csv(summary_path)
    audits = json.loads(audits_path.read_text(encoding="utf-8"))
    return summary, audits, provenance, summary_path, audits_path


def baseline_record(summary: pd.DataFrame, audits: dict[str, Any], disease: str,
                    score_col: str, source_hash: str, summary_path: Path,
                    audits_path: Path, source_key: str) -> dict[str, Any]:
    rows = summary.loc[summary["disease"].astype(str).eq(disease)]
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one primary C summary row for {source_key}/{disease}; found {len(rows)}")
    row = rows.iloc[0].to_dict()
    if str(row.get("instrument")) != score_col:
        raise ValueError(f"Primary score mismatch for {source_key}/{disease}: {row.get('instrument')} != {score_col}")
    if disease not in audits:
        raise KeyError(f"C audit details lack {source_key}/{disease}")
    detail = audits[disease].get("primary", audits[disease])
    status = str(row.get("state", detail.get("verdict", "unspecified")))
    detail_status = str(detail.get("verdict", "unspecified"))
    eligible = status == "estimable" and detail_status == "estimable" and detail.get("interval_status") == "computed"
    return {
        "source_key": source_key, "database": str(SOURCES[source_key]["database"]),
        "disease": disease, "score_variant": score_col, "source_panel_sha256": source_hash,
        "primary_C_state": status, "primary_C_interval_status": str(row.get("interval_status", detail.get("interval_status"))),
        "primary_C_refusal_reasons": ";".join(map(str, detail.get("refusal_reasons", []))),
        "primary_C_estimable": bool(eligible),
        "primary_C_point_pp_reported": safe_float(row.get("delta_w_pp")),
        "primary_C_normal_if_ci_lower_pp": safe_float((detail.get("delta_ci_pp") or [None, None])[0]),
        "primary_C_normal_if_ci_upper_pp": safe_float((detail.get("delta_ci_pp") or [None, None])[1]),
        "primary_C_old60_percentile_ci_lower_pp": safe_float((detail.get("stratified_rd_ci_pp") or [None, None])[0]),
        "primary_C_old60_percentile_ci_upper_pp": safe_float((detail.get("stratified_rd_ci_pp") or [None, None])[1]),
        "primary_C_old60_usable_draws": detail.get("bootstrap", {}).get("usable"),
        "primary_C_old60_requested_draws": detail.get("bootstrap", {}).get("reps"),
        # The primary summary's Delta_w is taken directly from the unrounded
        # independent direct_contrast; the audit JSON's reported point is rounded.
        "audit_point_pp_unrounded": safe_float(row.get("delta_w_pp", detail.get("stratified_rd_pp"))),
        "audit_numerical_se_pp": safe_float(detail.get("root_estimand_crosscheck", {}).get("numerical_cluster_se_pp", detail.get("delta_se_pp"))),
        "primary_summary_sha256": sha256_file(summary_path),
        "primary_audit_details_sha256": sha256_file(audits_path),
    }


def load_standard_panel(source_key: str) -> pd.DataFrame:
    """Use the existing shared normalizer's path-based API without altering it."""
    return normalize_panel(Path(SOURCES[source_key]["panel"]))


def canonicalize_peer_after_normalization(peer: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, bool]]:
    """Verify PEER duplicate aliases rowwise, then retain canonical source columns."""
    if "y" not in peer or "died" not in peer:
        raise ValueError("PEER source must contain y and died aliases for rowwise validation.")
    y, died = pd.to_numeric(peer["y"], errors="coerce"), pd.to_numeric(peer["died"], errors="coerce")
    same_missing = np.array_equal(y.isna().to_numpy(), died.isna().to_numpy())
    observed = y.notna() & died.notna()
    aliases_equal = bool(same_missing and np.array_equal(y.loc[observed].to_numpy(), died.loc[observed].to_numpy()))
    if not aliases_equal:
        raise ValueError("PEER y/died aliases disagree; no row is analyzed until aliases reconcile.")
    if "score" not in peer or "curb65" not in peer:
        raise ValueError("PEER adapter must have its standardized score and CURB-65 source column.")
    peer_score = pd.to_numeric(peer["score"], errors="coerce")
    curb65 = pd.to_numeric(peer["curb65"], errors="coerce")
    same_score_missing = np.array_equal(peer_score.isna().to_numpy(), curb65.isna().to_numpy())
    scores_equal = bool(same_score_missing and np.array_equal(
        peer_score.fillna(-1).to_numpy(), curb65.fillna(-1).to_numpy()))
    if not scores_equal:
        raise ValueError("PEER standardized score differs from its adapted CURB-65 score.")
    return peer.drop(columns=["y"]), {
        "peer_y_died_aliases_validated_equal": True,
        "peer_standard_score_equals_curb65": True,
    }


def c_audit(frame: pd.DataFrame, database: str, disease: str, label: str) -> dict[str, Any]:
    module = audit_module()
    return module.audit_v2(
        frame, score_col="score", outcome_col="y", group_col="grp", pid_col="pid",
        metadata={"database": database, "disease": disease,
                  "analysis_label": label, "record_unit": "hospital admission",
                  "weight_unit": "records", "cluster_unit": "patient",
                  "missing_handling": "complete required score, outcome, group, and patient identifier",
                  "target": "pooled observed record shares in common support"},
        config={"reps": C_REPS, "seed": C_BOOTSTRAP_SEED, "min_events": C_MIN_EVENTS,
                "min_level_n": C_MIN_LEVEL_RECORDS, "min_arm_n": C_MIN_ARM_RECORDS,
                "min_clusters": C_MIN_PATIENTS, "min_usable_bootstrap": C_MIN_USABLE,
                "model_check": False})


def get_standard_rows(source_key: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    summary, audits, _, summary_path, audits_path = load_primary_baseline(source_key, config)
    panel_path = Path(SOURCES[source_key]["panel"])
    panel_hash = assert_frozen_hash(config, f"panel:{source_key}", panel_path)
    disease_status = []
    for disease, (score, _max_score) in SCORES.items():
        disease_status.append(baseline_record(summary, audits, disease, score, panel_hash,
                                              summary_path, audits_path, source_key))
    eligible_diseases = [r["disease"] for r in disease_status if r["primary_C_estimable"]]
    panel = load_standard_panel(source_key) if eligible_diseases else None
    output = []
    for row in disease_status:
        if not row["primary_C_estimable"]:
            row.update(skipped_under_primary_C=True, skip_reason=row["primary_C_interval_status"],
                       diagnostic_run_status="skipped_under_primary_C")
            output.append(row)
            continue
        source = panel.loc[panel.disease.eq(row["disease"])].copy()
        frame = analysis_frame(source, row["score_variant"])
        if frame.empty:
            raise ValueError(f"C-estimable source row has no complete cases: {source_key}/{row['disease']}")
        result = run_precision(frame, f"{source_key}|{row['disease']}|primary")
        primary_c_point = row["primary_C_point_pp_reported"]
        if primary_c_point is not None:
            difference = result["direct_point_unrounded_pp"] - primary_c_point
            if not np.isclose(difference, 0.0, atol=0.011):
                raise AssertionError(f"direct point disagrees with primary C audit by {difference} pp")
            result["direct_point_vs_primary_C_difference_pp"] = float(difference)
        else:
            result["direct_point_vs_primary_C_difference_pp"] = None
        old_lo, old_hi = row["primary_C_old60_percentile_ci_lower_pp"], row["primary_C_old60_percentile_ci_upper_pp"]
        row.update(result,
                   primary_C_normal_if_ci_width_pp=(row["primary_C_normal_if_ci_upper_pp"] - row["primary_C_normal_if_ci_lower_pp"]
                       if row["primary_C_normal_if_ci_lower_pp"] is not None and row["primary_C_normal_if_ci_upper_pp"] is not None else None),
                   primary_C_old60_percentile_ci_width_pp=(old_hi - old_lo if old_lo is not None and old_hi is not None else None),
                   precision_minus_old60_lower_endpoint_pp=(result["precision_C_percentile_ci_lower_pp"] - old_lo
                       if result["precision_C_percentile_ci_lower_pp"] is not None and old_lo is not None else None),
                   precision_minus_old60_upper_endpoint_pp=(result["precision_C_percentile_ci_upper_pp"] - old_hi
                       if result["precision_C_percentile_ci_upper_pp"] is not None and old_hi is not None else None),
                   precision_minus_old60_width_pp=(result["precision_C_percentile_ci_width_pp"] - (old_hi - old_lo)
                       if result["precision_C_percentile_ci_width_pp"] is not None and old_lo is not None and old_hi is not None else None),
                   skipped_under_primary_C=False, skip_reason="", diagnostic_run_status="computed")
        output.append(row)
        del source, frame
    del panel
    return output


def peer_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(SOURCES["peer"]["panel"])
    peer_app_dir = ROOT / "outputs" / "v2" / "conditional_validation" / "clinical" / "run_02"
    peer_config_path = peer_app_dir / "clinical_application_config.json"
    peer_alias_path = peer_app_dir / "peer_outcome_alias_validation.json"
    peer_config = json.loads(peer_config_path.read_text(encoding="utf-8"))
    peer_source = next((item for item in peer_config.get("sources", [])
                        if item.get("database") == SOURCES["peer"]["database"]), None)
    if peer_source is None:
        raise KeyError("Frozen clinical application config lacks the PEER-adapted input.")
    source_hash = assert_frozen_hash(config, "panel:peer", path)
    assert_frozen_hash(config, "artifact:peer_application_config", peer_config_path)
    assert_frozen_hash(config, "artifact:peer_alias_validation", peer_alias_path)
    if peer_source.get("sha256_before_application") != source_hash:
        raise RuntimeError("PEER panel hash differs from its frozen source manifest.")
    alias_report = json.loads(peer_alias_path.read_text(encoding="utf-8"))
    if alias_report.get("status") != "passed" or alias_report.get("source_panel_sha256") != source_hash:
        raise RuntimeError("PEER y/died alias validation is not passed for the current panel hash.")
    # Match the path-based adapter contract exactly: normalize the complete source
    # first, then validate and drop only the redundant outcome alias in memory.
    peer = normalize_panel(path)
    # Retain the source's canonical `died` column; analysis_frame performs its
    # standard single rename to `y` after this redundant source alias is dropped.
    peer, peer_validation = canonicalize_peer_after_normalization(peer)
    disease = "pneumonia"
    source = peer.loc[peer.disease.eq(disease)].copy()
    frame = analysis_frame(source, "score")
    if frame.empty:
        raise ValueError("PEER adapted pneumonia panel has no complete-case rows.")
    audit = c_audit(frame, SOURCES["peer"]["database"], disease, "adapted published PEER population").copy()
    row = {
        "source_key": "peer", "database": SOURCES["peer"]["database"], "disease": disease,
        "score_variant": "adapted CURB-65 (`score`, validated equal to `curb65`)",
        "source_panel_sha256": source_hash,
        "primary_C_state": str(audit.get("verdict")),
        "primary_C_interval_status": str(audit.get("interval_status")),
        "primary_C_refusal_reasons": ";".join(map(str, audit.get("refusal_reasons", []))),
        "primary_C_estimable": audit.get("verdict") == "estimable" and audit.get("interval_status") == "computed",
        "primary_C_point_pp_reported": safe_float(audit.get("stratified_rd_pp")),
        "primary_C_normal_if_ci_lower_pp": safe_float((audit.get("delta_ci_pp") or [None, None])[0]),
        "primary_C_normal_if_ci_upper_pp": safe_float((audit.get("delta_ci_pp") or [None, None])[1]),
        "primary_C_old60_percentile_ci_lower_pp": safe_float((audit.get("stratified_rd_ci_pp") or [None, None])[0]),
        "primary_C_old60_percentile_ci_upper_pp": safe_float((audit.get("stratified_rd_ci_pp") or [None, None])[1]),
        "primary_C_old60_usable_draws": audit.get("bootstrap", {}).get("usable"),
        "primary_C_old60_requested_draws": audit.get("bootstrap", {}).get("reps"),
        "audit_point_pp_unrounded": 100 * float(direct_contrast(frame).estimate),
        "audit_numerical_se_pp": 100 * float(direct_contrast(frame).se),
        **peer_validation,
        "peer_frozen_config_sha256": sha256_file(peer_config_path),
        "peer_alias_validation_sha256": sha256_file(peer_alias_path),
    }
    row["primary_C_normal_if_ci_width_pp"] = (
        row["primary_C_normal_if_ci_upper_pp"] - row["primary_C_normal_if_ci_lower_pp"]
        if row["primary_C_normal_if_ci_lower_pp"] is not None and row["primary_C_normal_if_ci_upper_pp"] is not None else None)
    old_lo, old_hi = row["primary_C_old60_percentile_ci_lower_pp"], row["primary_C_old60_percentile_ci_upper_pp"]
    row["primary_C_old60_percentile_ci_width_pp"] = old_hi - old_lo if old_lo is not None and old_hi is not None else None
    if not row["primary_C_estimable"]:
        row.update(skipped_under_primary_C=True, skip_reason=row["primary_C_interval_status"],
                   diagnostic_run_status="skipped_under_primary_C")
        return [row]
    result = run_precision(frame, "peer|pneumonia|primary")
    diff = result["direct_point_unrounded_pp"] - row["audit_point_pp_unrounded"]
    if not np.isclose(diff, 0.0, atol=1e-12):
        raise AssertionError(f"PEER direct point cross-check differs by {diff} pp")
    lo60, hi60 = old_lo, old_hi
    row.update(result,
               direct_point_vs_primary_C_difference_pp=diff,
               precision_minus_old60_lower_endpoint_pp=(result["precision_C_percentile_ci_lower_pp"] - lo60
                   if result["precision_C_percentile_ci_lower_pp"] is not None and lo60 is not None else None),
               precision_minus_old60_upper_endpoint_pp=(result["precision_C_percentile_ci_upper_pp"] - hi60
                   if result["precision_C_percentile_ci_upper_pp"] is not None and hi60 is not None else None),
               precision_minus_old60_width_pp=(result["precision_C_percentile_ci_width_pp"] - (hi60 - lo60)
                   if result["precision_C_percentile_ci_width_pp"] is not None and lo60 is not None and hi60 is not None else None),
               skipped_under_primary_C=False, skip_reason="", diagnostic_run_status="computed")
    return [row]


def amsterdam_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(SOURCES["amsterdam"]["panel"])
    outdir = ROOT / "outputs" / "v2" / "amsterdam" / "dictionary_unit_repair"
    manifest_path = outdir / "dictionary_unit_repair_source_manifest.json"
    assert_frozen_hash(config, "artifact:amsterdam:dictionary_unit_repair_source_manifest.json", manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_hashes = nested_values(manifest, "repaired_outcome_panel_sha256")
    if len(expected_hashes) != 1:
        raise KeyError("Amsterdam manifest does not expose the repaired outcome panel SHA-256.")
    expected_hash = expected_hashes[0]
    source_hash = assert_frozen_hash(config, "panel:amsterdam", path)
    if source_hash != expected_hash:
        raise RuntimeError(f"Repaired Amsterdam panel hash mismatch: {source_hash} != {expected_hash}")
    panel = pd.read_csv(path, compression="gzip", low_memory=False)
    variants = [
        ("gcs_le_13", "qsofa_main", "audit_gcs_le_13.json"),
        ("gcs_lt_15_sensitivity", "qsofa_gcs_lt15", "audit_gcs_lt_15_sensitivity.json"),
    ]
    output = []
    for label, score, audit_name in variants:
        detail_path = outdir / audit_name
        assert_frozen_hash(config, f"artifact:amsterdam:{audit_name}", detail_path)
        audit = json.loads(detail_path.read_text(encoding="utf-8"))
        frame = panel[["patientid", "grp", "icu_death", score]].rename(
            columns={"patientid": "pid", "icu_death": "y", score: "score"})
        frame["grp"] = pd.to_numeric(frame["grp"], errors="coerce")
        frame["y"] = pd.to_numeric(frame["y"], errors="coerce")
        frame["score"] = pd.to_numeric(frame["score"], errors="coerce")
        frame = frame.dropna(subset=["pid", "grp", "y", "score"]).copy()
        direct = direct_contrast(frame)
        cstate = str(audit.get("verdict", "unspecified"))
        eligible = cstate == "estimable" and audit.get("interval_status") == "computed"
        ci = audit.get("delta_ci_pp") or [None, None]
        boot = audit.get("stratified_rd_ci_pp") or [None, None]
        row = {
            "source_key": "amsterdam", "database": SOURCES["amsterdam"]["database"],
            "disease": "sepsis", "score_variant": label,
            "score_column": score, "source_panel_sha256": source_hash,
            "primary_C_state": cstate, "primary_C_interval_status": str(audit.get("interval_status")),
            "primary_C_refusal_reasons": ";".join(map(str, audit.get("refusal_reasons", []))),
            "primary_C_estimable": bool(eligible),
            "primary_C_point_pp_reported": safe_float(audit.get("stratified_rd_pp")),
            "primary_C_normal_if_ci_lower_pp": safe_float(ci[0]),
            "primary_C_normal_if_ci_upper_pp": safe_float(ci[1]),
            "primary_C_old60_percentile_ci_lower_pp": safe_float(boot[0]),
            "primary_C_old60_percentile_ci_upper_pp": safe_float(boot[1]),
            "primary_C_old60_usable_draws": audit.get("bootstrap", {}).get("usable"),
            "primary_C_old60_requested_draws": audit.get("bootstrap", {}).get("reps"),
            "audit_point_pp_unrounded": safe_float(audit.get("root_estimand_crosscheck", {}).get("estimate_pp", 100 * direct.estimate)),
            "audit_numerical_se_pp": safe_float(audit.get("root_estimand_crosscheck", {}).get("numerical_cluster_se_pp", 100 * direct.se)),
            "primary_C_normal_if_ci_width_pp": safe_float(ci[1] - ci[0]) if ci[0] is not None and ci[1] is not None else None,
            "primary_C_old60_percentile_ci_width_pp": safe_float(boot[1] - boot[0]) if boot[0] is not None and boot[1] is not None else None,
            "primary_C_audit_sha256": sha256_file(detail_path),
        }
        if not eligible:
            row.update(skipped_under_primary_C=True, skip_reason=row["primary_C_interval_status"],
                       diagnostic_run_status="skipped_under_primary_C")
            output.append(row)
            continue
        exact = 100 * direct.estimate
        if row["audit_point_pp_unrounded"] is not None and not np.isclose(exact, row["audit_point_pp_unrounded"], atol=0.011):
            raise AssertionError(f"Amsterdam direct point disagrees with frozen audit for {label}")
        result = run_precision(frame, f"amsterdam|sepsis|{label}")
        old_lo, old_hi = row["primary_C_old60_percentile_ci_lower_pp"], row["primary_C_old60_percentile_ci_upper_pp"]
        row.update(result,
                   direct_point_vs_primary_C_difference_pp=exact - row["audit_point_pp_unrounded"],
                   precision_minus_old60_lower_endpoint_pp=(result["precision_C_percentile_ci_lower_pp"] - old_lo
                       if result["precision_C_percentile_ci_lower_pp"] is not None and old_lo is not None else None),
                   precision_minus_old60_upper_endpoint_pp=(result["precision_C_percentile_ci_upper_pp"] - old_hi
                       if result["precision_C_percentile_ci_upper_pp"] is not None and old_hi is not None else None),
                   precision_minus_old60_width_pp=(result["precision_C_percentile_ci_width_pp"] - (old_hi - old_lo)
                       if result["precision_C_percentile_ci_width_pp"] is not None and old_lo is not None and old_hi is not None else None),
                   skipped_under_primary_C=False, skip_reason="", diagnostic_run_status="computed")
        output.append(row)
    del panel
    return output


def skipped_pending_miii(config: dict[str, Any]) -> list[dict[str, Any]]:
    miii_panel_hash = assert_frozen_hash(config, "panel:mimic_iii", Path(SOURCES["mimic_iii"]["panel"]))
    return [{
        "source_key": "mimic_iii", "database": SOURCES["mimic_iii"]["database"],
        "disease": disease, "score_variant": score,
        "source_panel_sha256": miii_panel_hash,
        "primary_C_state": "not evaluated: MIMIC-III source repair pending",
        "primary_C_interval_status": "superseded; not consumed",
        "primary_C_refusal_reasons": "PENDING_SOURCE_REPAIR.json present; four MVBP IDs absent from source filter",
        "primary_C_estimable": False,
        "skipped_under_primary_C": True,
        "skip_reason": "pending source repair; current MIMIC-III aggregates are superseded",
        "diagnostic_run_status": "skipped_pending_source_repair",
    } for disease, (score, _max_score) in SCORES.items()]


def write_results(outdir: Path, rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    results_path = outdir / "precision_results.csv"
    pd.DataFrame(rows).to_csv(results_path, index=False, encoding="utf-8-sig", float_format="%.12g")
    skipped_path = outdir / "primary_C_skipped.csv"
    skipped = [row for row in rows if row.get("skipped_under_primary_C")]
    pd.DataFrame(skipped).to_csv(skipped_path, index=False, encoding="utf-8-sig", float_format="%.12g")
    completed = [row for row in rows if row.get("diagnostic_run_status") == "computed"]
    discrepancies = []
    for row in completed:
        old_lo, old_hi = row.get("primary_C_old60_percentile_ci_lower_pp"), row.get("primary_C_old60_percentile_ci_upper_pp")
        new_lo, new_hi = row.get("precision_C_percentile_ci_lower_pp"), row.get("precision_C_percentile_ci_upper_pp")
        if old_lo is not None and old_hi is not None and new_lo is not None and new_hi is not None:
            discrepancies.append({
                "source_key": row["source_key"], "disease": row["disease"],
                "score_variant": row["score_variant"], "point_pp": row.get("direct_point_unrounded_pp"),
                "normal_if_ci": [row.get("primary_C_normal_if_ci_lower_pp"), row.get("primary_C_normal_if_ci_upper_pp")],
                "old60_percentile_ci": [old_lo, old_hi],
                "precision5000_percentile_ci": [new_lo, new_hi],
                "endpoint_differences_5000_minus_60_pp": [new_lo - old_lo, new_hi - old_hi],
                "widths_pp": {"normal_if": row.get("primary_C_normal_if_ci_width_pp"),
                              "old60_percentile": row.get("primary_C_old60_percentile_ci_width_pp"),
                              "precision5000_percentile": row.get("precision_C_percentile_ci_width_pp")},
            })
    report = {
        "record_type": "delta_w_bootstrap_precision_diagnostic_results",
        "run_id": config["run_id"], "status": "complete", "completed_utc": utc_now(),
        "requested_draws_per_C_estimable_summary": int(config.get("requested_draws", REQUESTED_DRAWS)),
        "master_seed": MASTER_SEED,
        "candidate_rows": len(rows), "precision_computed_rows": len(completed),
        "primary_C_skipped_rows": len(skipped),
        "skip_counts": pd.Series([row.get("skip_reason", "") for row in skipped], dtype="string").value_counts(dropna=False).to_dict(),
        "favorable_or_adverse_endpoint_differences": discrepancies,
        "interpretation": "Bootstrap percentile endpoints are finite-simulation quantiles under the locked resampling procedure. Their Monte Carlo order-statistic ranges quantify endpoint simulation uncertainty only; they are not clinical confidence intervals and do not select or replace primary C.",
        "primary_c_modified": False,
        "patient_level_rows_written": False,
        "precision_results_sha256": sha256_file(results_path),
        "primary_C_skipped_sha256": sha256_file(skipped_path),
    }
    atomic_json(outdir / "run_report.json", report)
    atomic_json(outdir / "run_status.json", {"status": "complete", "completed_utc": utc_now(),
                                              "results_sha256": report["precision_results_sha256"]})
    return report


def write_source_checkpoint(outdir: Path, source_key: str, rows: list[dict[str, Any]]) -> None:
    """Persist only aggregate results after each source so later failure loses no completed work."""
    outdir.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"checkpoint_{source_key}.csv"
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig", float_format="%.12g")
    atomic_json(outdir / f"checkpoint_{source_key}.json", {
        "source_key": source_key, "status": "complete", "completed_utc": utc_now(),
        "candidate_rows": len(rows),
        "precision_rows": sum(row.get("diagnostic_run_status") == "computed" for row in rows),
        "patient_level_rows_written": False,
        "sha256": sha256_file(path),
    })


def run(run_id: str, final: bool = False) -> dict[str, Any]:
    outdir = OUT_ROOT / run_id
    config = freeze_config(run_id, final, outdir)
    atomic_json(outdir / "run_status.json", {"status": "in_progress", "started_utc": utc_now(),
                                              "config_sha256": sha256_file(outdir / "config_frozen.json")})
    # Shared arithmetic validation runs before reading any clinical outcomes.
    from test_bootstrap_precision import validate_numeric_reducer
    validation = validate_numeric_reducer()
    atomic_json(outdir / "numeric_reducer_validation.json", validation)
    rows: list[dict[str, Any]] = []
    source_order = ["eicu", "mimic_iv", "mimic_iii", "zigong", "peer", "amsterdam"]
    for source_key in source_order:
        before = len(rows)
        if source_key == "mimic_iii" and not final:
            rows.extend(skipped_pending_miii(config))
        elif source_key in {"eicu", "mimic_iv", "mimic_iii", "zigong"}:
            rows.extend(get_standard_rows(source_key, config))
        elif source_key == "peer":
            rows.extend(peer_rows(config))
        elif source_key == "amsterdam":
            rows.extend(amsterdam_rows(config))
        progress = {
            "status": "in_progress", "updated_utc": utc_now(), "source_completed": source_key,
            "rows_so_far": len(rows), "precision_rows_so_far": sum(r.get("diagnostic_run_status") == "computed" for r in rows),
        }
        write_source_checkpoint(outdir, source_key, rows[before:])
        atomic_json(outdir / "progress.json", progress)
        print(json.dumps(progress, ensure_ascii=False), flush=True)
    return write_results(outdir, rows, config)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--final-after-mimic3-repair", action="store_true")
    args = parser.parse_args()
    try:
        report = run(args.run_id, final=args.final_after_mimic3_repair)
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    except BaseException as exc:
        outdir = OUT_ROOT / args.run_id
        if outdir.exists():
            atomic_json(outdir / "run_status.json", {"status": "failed", "failed_utc": utc_now(),
                                                      "error_type": type(exc).__name__, "error": str(exc)})
        raise


if __name__ == "__main__":
    main()

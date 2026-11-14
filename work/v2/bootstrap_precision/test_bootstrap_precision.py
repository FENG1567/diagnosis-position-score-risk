"""Deterministic equivalence checks for the bootstrap sufficient-statistic reducer."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "work" / "v2"))

from run_bootstrap_precision import (  # noqa: E402
    audit_module,
    build_cell_ledger,
    canonicalize_peer_after_normalization,
    c_audit,
    common_support_levels,
    nested_values,
    run_precision,
    SOURCES,
    sha256_file,
    value_for_multiplicities,
    write_source_checkpoint,
    write_results,
)
from analyse_panels import analysis_frame, normalize_panel  # noqa: E402


def fixture() -> pd.DataFrame:
    """Cross-group patients, unequal clusters, and patients entirely off-support."""
    rows = [
        # p1 contributes to both groups and score levels (clustered dependence).
        ("p1", 0, 0, 0), ("p1", 1, 1, 1),
        # p2 has unequal cluster size and group-1 score-0 records.
        ("p2", 1, 0, 0), ("p2", 1, 0, 0),
        # p3 spans groups and levels, with a second supported record.
        ("p3", 0, 1, 0), ("p3", 1, 0, 0), ("p3", 1, 1, 1),
        # p4 / p5 ensure both score-1 definition cells remain populated.
        ("p4", 0, 0, 1), ("p4", 1, 0, 1),
        ("p5", 0, 1, 1),
        # Unequal multi-record patient at score 1.
        ("p6", 0, 1, 1), ("p6", 1, 1, 0), ("p6", 1, 1, 1),
        # These patients have no rows on the observed common support {0,1}.
        ("p7", 0, 0, 3), ("p8", 1, 1, 4),
    ]
    return pd.DataFrame(rows, columns=["pid", "grp", "y", "score"])


def explicit_duplicate_value(frame: pd.DataFrame, multiplicities: np.ndarray,
                             levels: np.ndarray) -> tuple[float | None, str]:
    copies = []
    patient_ids = list(pd.unique(frame.pid))
    for pid, count in zip(patient_ids, multiplicities):
        if count:
            selected = frame.loc[frame.pid.eq(pid)]
            copies.extend([selected] * int(count))
    if not copies:
        return None, "no_support"
    sampled = pd.concat(copies, ignore_index=True)
    selected = sampled.loc[sampled.score.isin(levels)]
    if not np.all([((selected.score == level) & (selected.grp == group)).any()
                   for level in levels for group in (0, 1)]):
        return None, "lost_levels"
    events = {group: int(selected.loc[selected.grp.eq(group), "y"].sum()) for group in (0, 1)}
    if min(events.values()) < 0:
        return None, "few_events"
    audit = audit_module()
    estimate, _, _, _ = audit.stratified_rd(
        selected.score.to_numpy(float), selected.y.to_numpy(float), selected.grp.to_numpy(int),
        support_levels=levels)
    if not np.isfinite(estimate):
        return None, "lost_levels"
    return float(estimate), "ok"


def validate_numeric_reducer() -> dict:
    frame = fixture()
    levels = common_support_levels(frame)
    if not np.array_equal(levels, np.asarray([0.0, 1.0])):
        raise AssertionError(f"Expected common support {{0,1}}, observed {levels}")
    ledger = build_cell_ledger(frame, levels)
    if ledger.n_patients != 8:
        raise AssertionError("All patients must remain in the cluster resampling universe.")
    if int((ledger.record_counts.sum(axis=1) == 0).sum()) != 2:
        raise AssertionError("Patients outside common support must remain with zero supported counts.")
    p1_index = list(ledger.patient_ids).index("p1")
    if ledger.record_counts[p1_index].sum() != 2:
        raise AssertionError("Cross-group patient records were not kept in one cluster ledger.")

    resamples = {
        "identity": np.asarray([1, 1, 1, 1, 1, 1, 1, 1]),
        "duplicate_cross_group_cluster": np.asarray([2, 1, 1, 1, 1, 1, 0, 1]),
        "duplicate_unequal_cluster": np.asarray([1, 2, 1, 1, 1, 0, 1, 1]),
        "partial_support_with_offsupport_cluster": np.asarray([0, 1, 1, 2, 1, 1, 1, 1]),
    }
    checked = {}
    for label, multiplicities in resamples.items():
        if int(multiplicities.sum()) != ledger.n_patients:
            raise AssertionError(f"{label} is not a fixed-size patient bootstrap draw.")
        numeric, numeric_status = value_for_multiplicities(ledger, multiplicities, min_events=0)
        explicit, explicit_status = explicit_duplicate_value(frame, multiplicities, levels)
        if numeric_status != explicit_status:
            raise AssertionError(f"{label}: statuses differ ({numeric_status} vs {explicit_status})")
        if numeric is not None and not np.isclose(numeric, explicit, atol=1e-14):
            raise AssertionError(f"{label}: numeric reducer {numeric} != explicit duplicate rows {explicit}")
        checked[label] = {"status": numeric_status, "estimate_pp": None if numeric is None else 100 * numeric}

    # A draw that omits the supported group-1 score-0 sources loses fixed support.
    lost = np.asarray([1, 0, 0, 2, 1, 0, 2, 2])
    value, status = value_for_multiplicities(ledger, lost, min_events=0)
    if status != "lost_levels" or value is not None:
        raise AssertionError("Fixed-support loss was not refused.")
    # A high event threshold tests draw-level event refusal after support is retained.
    value, status = value_for_multiplicities(ledger, resamples["identity"], min_events=100)
    if status != "few_events" or value is not None:
        raise AssertionError("Few-event draw was not refused.")
    return {
        "status": "passed",
        "n_patients_in_universe": ledger.n_patients,
        "n_patients_without_supported_records": int((ledger.record_counts.sum(axis=1) == 0).sum()),
        "observed_common_support": levels.tolist(),
        "checked_deterministic_resamples": checked,
        "explicit_duplicate_row_equivalence": "all checked point estimates matched within 1e-14 risk-difference units",
        "fixed_support_refusal": "validated separately (lost_levels)",
        "few_event_refusal": "validated separately (few_events)",
    }


def smoke_real_adapter_and_report() -> dict:
    """Exercise path normalizers, source adapters, C gates and aggregate report output."""
    rows = []
    for group, event_count in ((0, 100), (1, 120)):
        for i in range(200):
            event = int(i < event_count)
            rows.append({
                "pid": f"patient-{group}-{i:03d}",
                "admission_id": f"admission-{group}-{i:03d}",
                "disease": "pneumonia", "grp": group, "died": event,
                "curb65": 0, "score": 0, "y": event,
            })
    source = pd.DataFrame(rows)
    with tempfile.TemporaryDirectory(prefix="bootstrap_precision_smoke_") as scratch:
        scratch_path = Path(scratch)
        standard_path = scratch_path / "tiny_standard_panel.csv.gz"
        peer_path = scratch_path / "tiny_peer_panel.csv.gz"
        source[["pid", "admission_id", "disease", "grp", "died", "curb65"]].to_csv(
            standard_path, index=False, compression="gzip")
        source.to_csv(peer_path, index=False, compression="gzip")

        # Shared normalizer is intentionally path-based; the source adapter then
        # passes the normalized `died` plus named score column to analysis_frame.
        standard = normalize_panel(standard_path)
        standard_frame = analysis_frame(standard.loc[standard.disease.eq("pneumonia")], "curb65")
        peer_normalized = normalize_panel(peer_path)
        peer_canonical, alias_validation = canonicalize_peer_after_normalization(peer_normalized)
        peer_frame = analysis_frame(peer_canonical.loc[peer_canonical.disease.eq("pneumonia")], "score")
        if len(standard_frame) != 400 or len(peer_frame) != 400:
            raise AssertionError("Real path adapter smoke did not preserve the expected complete-case records.")
        if not np.array_equal(standard_frame[["pid", "grp", "y", "score"]].to_numpy(),
                              peer_frame[["pid", "grp", "y", "score"]].to_numpy()):
            raise AssertionError("Standard and PEER adapters disagree on canonical analysis fields.")

        bad_value = peer_normalized.copy()
        bad_value.loc[0, "y"] = 1 - int(bad_value.loc[0, "died"])
        with unittest.TestCase().assertRaises(ValueError):
            canonicalize_peer_after_normalization(bad_value)
        bad_missing = peer_normalized.copy()
        bad_missing.loc[0, "y"] = np.nan
        with unittest.TestCase().assertRaises(ValueError):
            canonicalize_peer_after_normalization(bad_missing)

        audit = c_audit(standard_frame, "synthetic-smoke", "pneumonia", "path adapter smoke")
        if audit.get("verdict") != "estimable" or audit.get("interval_status") != "computed":
            raise AssertionError(f"Smoke panel failed the unchanged C gates: {audit.get('verdict')}")
        precision = run_precision(standard_frame, "synthetic-smoke|pneumonia", reps=64)
        row = {
            "source_key": "synthetic-smoke", "database": "synthetic smoke only",
            "disease": "pneumonia", "score_variant": "curb65",
            "primary_C_state": audit["verdict"], "primary_C_interval_status": audit["interval_status"],
            "primary_C_refusal_reasons": ";".join(audit.get("refusal_reasons", [])),
            "primary_C_estimable": True, "primary_C_point_pp_reported": audit["stratified_rd_pp"],
            "primary_C_normal_if_ci_lower_pp": audit["delta_ci_pp"][0],
            "primary_C_normal_if_ci_upper_pp": audit["delta_ci_pp"][1],
            "primary_C_old60_percentile_ci_lower_pp": audit["stratified_rd_ci_pp"][0],
            "primary_C_old60_percentile_ci_upper_pp": audit["stratified_rd_ci_pp"][1],
            "primary_C_old60_usable_draws": audit["bootstrap"]["usable"],
            "primary_C_old60_requested_draws": audit["bootstrap"]["reps"],
            "skipped_under_primary_C": False, "skip_reason": "", "diagnostic_run_status": "computed",
            **precision,
        }
        output_dir = scratch_path / "aggregate_output"
        report = write_results(output_dir, [row], {"run_id": "synthetic_smoke", "requested_draws": 64})
        result_table = pd.read_csv(output_dir / "precision_results.csv")
        if report["precision_computed_rows"] != 1 or report["requested_draws_per_C_estimable_summary"] != 64:
            raise AssertionError("Smoke report constructor omitted or misreported its diagnostic row.")
        if any(column in result_table.columns for column in ("pid", "patient_id", "admission_id")):
            raise AssertionError("Smoke aggregate report unexpectedly contains record identifiers.")

        # Also exercise the real nested Amsterdam manifest schema and the
        # aggregate-only per-source checkpoint writer without rerunning outcomes.
        manifest_path = ROOT / "outputs" / "v2" / "amsterdam" / "dictionary_unit_repair" / "dictionary_unit_repair_source_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        panel_hashes = nested_values(manifest, "repaired_outcome_panel_sha256")
        amsterdam_hash = sha256_file(Path(SOURCES["amsterdam"]["panel"]))
        if panel_hashes != [amsterdam_hash]:
            raise AssertionError("Nested Amsterdam panel hash does not match the repaired source panel.")
        checkpoint_dir = scratch_path / "source_checkpoint"
        write_source_checkpoint(checkpoint_dir, "synthetic-smoke", [row])
        checkpoint_meta = json.loads(
            (checkpoint_dir / "checkpoint_synthetic-smoke.json").read_text(encoding="utf-8"))
        checkpoint_table = pd.read_csv(checkpoint_dir / "checkpoint_synthetic-smoke.csv")
        if checkpoint_meta["status"] != "complete" or checkpoint_meta["sha256"] != sha256_file(
                checkpoint_dir / "checkpoint_synthetic-smoke.csv"):
            raise AssertionError("Per-source aggregate checkpoint metadata/hash failed.")
        if any(column in checkpoint_table.columns for column in ("pid", "patient_id", "admission_id")):
            raise AssertionError("Per-source checkpoint unexpectedly contains record identifiers.")
        return {
            "status": "passed",
            "normalizer_api": "shared normalize_panel(path)",
            "analysis_frame_api": "source retains died; named score column passed to shared analysis_frame",
            "peer_alias_adapter": alias_validation,
            "peer_value_mismatch_refusal": True,
            "peer_missingness_mismatch_refusal": True,
            "standard_vs_peer_canonical_frames_equal": True,
            "primary_C_gates": audit["verdict"],
            "numeric_precision_draws": precision["precision_usable_draws"],
            "aggregate_report_rows": report["precision_computed_rows"],
            "amsterdam_nested_manifest_hash_matches": True,
            "aggregate_source_checkpoint_hash_matches": True,
            "patient_level_output_written": False,
        }
class NumericReducerValidation(unittest.TestCase):
    def test_reducer_equals_explicit_patient_cluster_duplication(self):
        result = validate_numeric_reducer()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["n_patients_without_supported_records"], 2)

    def test_refusal_gates(self):
        frame = fixture()
        levels = common_support_levels(frame)
        ledger = build_cell_ledger(frame, levels)
        lost = np.asarray([1, 0, 0, 2, 1, 0, 2, 2])
        self.assertEqual(value_for_multiplicities(ledger, lost, min_events=0)[1], "lost_levels")
        self.assertEqual(value_for_multiplicities(ledger, np.ones(8, dtype=int), min_events=100)[1], "few_events")

    def test_real_adapter_and_report_smoke(self):
        result = smoke_real_adapter_and_report()
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["peer_value_mismatch_refusal"])
        self.assertTrue(result["peer_missingness_mismatch_refusal"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

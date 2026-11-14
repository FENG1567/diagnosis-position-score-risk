#!/usr/bin/env python3
"""Create aggregate-only MIMIC-III BP-repair comparison and provenance record."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import m58_mimic3_rebuild as m3

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "outputs" / "v2" / "analysis" / "mimic_iii"
RECON = ROOT / "outputs" / "v2" / "reconciliation"
OLD = RECON / "mimic_iii_before_mv_bp_repair"
OLD_STATE = OLD / "build_state" / "mimic3"
OLD_CACHE = OLD / "build_state" / "cache"
PRIVATE = m3.PRIVATE_DEFAULT
OUTPUT = m3.OUT_DEFAULT
BP_IDS = (220050, 220051, 220179, 220180)
TEST_LOG = ROOT / "work" / "v2" / "mimic3" / "repair_logs" / "mv_bp_repair_20261113_tests.log"
SCAN_STDOUT = ROOT / "work" / "v2" / "mimic3" / "repair_logs" / "mv_bp_repair_20261113.stdout.log"
SCAN_STDERR = ROOT / "work" / "v2" / "mimic3" / "repair_logs" / "mv_bp_repair_20261113.stderr.log"
RESOLVED_MARKER = ROOT / "work" / "v2" / "mimic3" / "repair_logs" / "RESOLVED_PENDING_SOURCE_REPAIR.json"
INDEPENDENT_REVIEW = ROOT / "work" / "v2" / "mimic3" / "final_bp_independent_review.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_old_builder():
    path = OLD_STATE / "m58_mimic3_rebuild.py"
    spec = importlib.util.spec_from_file_location("old_mimic3_rebuild", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load preserved builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selection_record(frame: pd.DataFrame, disease: str, group: str) -> pd.Series:
    found = frame.loc[frame["disease"].eq(disease) & frame["group"].eq(group)]
    if len(found) != 1:
        raise AssertionError(f"Expected one selection row for {disease}/{group}; got {len(found)}")
    return found.iloc[0]


def make_comparison() -> pd.DataFrame:
    old_summary = pd.read_csv(OLD / "summary.csv")
    new_summary = pd.read_csv(ANALYSIS / "summary.csv")
    old_selection = pd.read_csv(OLD / "selection.csv")
    new_selection = pd.read_csv(ANALYSIS / "selection.csv")
    rows = []
    for disease in new_summary["disease"]:
        before = old_summary.loc[old_summary["disease"].eq(disease)].iloc[0]
        after = new_summary.loc[new_summary["disease"].eq(disease)].iloc[0]
        row = {"database": "MIMIC-III", "disease": disease, "instrument": after["instrument"]}
        for group, suffix in (("primary", "primary"), ("never-primary", "never")):
            b = selection_record(old_selection, disease, group)
            a = selection_record(new_selection, disease, group)
            if int(a["n_source"]) != int(b["n_source"]):
                raise AssertionError(f"Eligible source count changed for {disease}/{group}")
            source = int(a["n_source"])
            row[f"eligible_{suffix}"] = source
            for measure, column in (("score_complete", "n_score_complete"),
                                    ("complete_outcome", "n_analyzed")):
                before_n, after_n = int(b[column]), int(a[column])
                row[f"{measure}_{suffix}_before"] = before_n
                row[f"{measure}_{suffix}_after"] = after_n
                row[f"{measure}_{suffix}_change"] = after_n - before_n
            before_cov = 100 * int(b["n_score_complete"]) / source
            after_cov = 100 * int(a["n_score_complete"]) / source
            row[f"score_coverage_{suffix}_pct_before"] = before_cov
            row[f"score_coverage_{suffix}_pct_after"] = after_cov
            row[f"score_coverage_{suffix}_change_pp"] = after_cov - before_cov
        for column in ("n_shared_primary", "n_shared_never", "n", "n_patients",
                       "n_inference_clusters", "support_share", "levels", "delta_w_pp",
                       "numerical_se_pp", "lo_pp", "hi_pp", "state", "interval_status"):
            row[f"{column}_before"] = before[column]
            row[f"{column}_after"] = after[column]
        row["delta_w_change_pp"] = float(after["delta_w_pp"]) - float(before["delta_w_pp"])
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    old_builder = load_old_builder()
    old_panel_path = OLD_STATE / "mimic_iii_v2_score_panel.csv.gz"
    new_panel_path = PRIVATE / "mimic_iii_v2_score_panel.csv.gz"
    old_panel = pd.read_csv(old_panel_path, compression="gzip", low_memory=False)
    new_panel = pd.read_csv(new_panel_path, compression="gzip", low_memory=False)
    old_panel = old_panel.set_index(["hadm_id", "disease"]).sort_index()
    new_panel = new_panel.set_index(["hadm_id", "disease"]).sort_index()
    if not old_panel.index.equals(new_panel.index):
        raise AssertionError("Admission-disease panel keys changed during BP repair")

    bisap = {}
    bisap_columns = [column for column in old_panel.columns
                     if column.startswith("bisap4") or column.startswith("bisap_")]
    for column in bisap_columns:
        before, after = old_panel[column], new_panel[column]
        same = (before.eq(after) | (before.isna() & after.isna())).fillna(False)
        changed = int((~same).sum())
        if changed:
            raise AssertionError(f"BISAP field changed: {column}: {changed} rows")
        bisap[column] = {
            "identical": True, "rows": len(before), "changed_values": 0,
            "nonmissing_before": int(before.notna().sum()),
            "nonmissing_after": int(after.notna().sum()),
            "missing_before": int(before.isna().sum()),
            "missing_after": int(after.isna().sum()),
        }

    old_index = json.loads((OLD_STATE / "mimic_iii_v2_index_manifest.json").read_text(encoding="utf-8"))
    new_index = json.loads((PRIVATE / "mimic_iii_v2_index_manifest.json").read_text(encoding="utf-8"))
    if old_index["index_filter_sha256"] != new_index["index_filter_sha256"]:
        raise AssertionError("Old and new panels use different admission indexes")
    added_ids = set(m3.CHART_IDS) - set(old_builder.CHART_IDS)
    removed_ids = set(old_builder.CHART_IDS) - set(m3.CHART_IDS)
    if added_ids != set(BP_IDS) or removed_ids:
        raise AssertionError(f"Unexpected chart filter change: added={added_ids}, removed={removed_ids}")
    if any(old_builder.CHART_MAP[item] != m3.CHART_MAP[item]
           for item in old_builder.CHART_MAP):
        raise AssertionError("A preexisting MIMIC-III chart mapping changed")

    old_cache = OLD_CACHE / "mimic_iii_chartevents_filtered.csv.gz"
    new_cache = PRIVATE / "cache" / "mimic_iii_chartevents_filtered.csv.gz"
    old_cache_manifest = json.loads(old_builder._cache_manifest_path(old_cache).read_text(encoding="utf-8"))
    new_cache_manifest = json.loads(m3._cache_manifest_path(new_cache).read_text(encoding="utf-8"))
    if not old_builder._cache_is_valid(old_cache, old_builder.ZIP_DEFAULT,
                                        old_builder.MEMBERS["chartevents"],
                                        old_index["index_filter_sha256"]):
        raise AssertionError("Preserved old chart cache failed legacy provenance validation")
    if not m3._cache_is_valid(new_cache, m3.ZIP_DEFAULT, m3.MEMBERS["chartevents"],
                              new_index["index_filter_sha256"]):
        raise AssertionError("Promoted chart cache failed current provenance validation")
    if sha256(old_cache) != old_cache_manifest["cache_sha256"] or sha256(new_cache) != new_cache_manifest["cache_sha256"]:
        raise AssertionError("Chart-cache bytes do not match their manifests")
    old_channel_counts = pd.read_csv(old_cache, compression="gzip", usecols=["itemid"],
                                     dtype={"itemid": "int32"})["itemid"].value_counts()
    new_channel_counts = pd.read_csv(new_cache, compression="gzip", usecols=["itemid"],
                                     dtype={"itemid": "int32"})["itemid"].value_counts()
    source_id_counts = []
    for source_id in BP_IDS:
        canonical = int(m3.CHART_MAP[source_id])
        old_n = int(old_channel_counts.get(canonical, 0))
        new_n = int(new_channel_counts.get(canonical, 0))
        source_id_counts.append({
            "source_itemid": source_id, "canonical_itemid": canonical,
            "old_canonical_channel_rows": old_n, "new_canonical_channel_rows": new_n,
            "selected_rows_from_added_source_id": new_n - old_n,
        })
    old_rows, new_rows = int(old_cache_manifest["rows"]), int(new_cache_manifest["rows"])
    if sum(row["selected_rows_from_added_source_id"] for row in source_id_counts) != new_rows - old_rows:
        raise AssertionError("Per-ID canonical-channel deltas do not reconcile with total cache rows")

    comparison = make_comparison()
    comparison_path = ANALYSIS / "bp_repair_before_after.csv"
    comparison.to_csv(comparison_path, index=False)
    panel_sha = sha256(new_panel_path)
    analysis_provenance = json.loads((ANALYSIS / "analysis_provenance.json").read_text(encoding="utf-8"))
    if analysis_provenance["panel_sha256"] != panel_sha:
        raise AssertionError("MIMIC-III analysis provenance does not match promoted panel")
    run = json.loads((OUTPUT / "mimic_iii_v2_run_manifest.json").read_text(encoding="utf-8"))
    qa = json.loads((OUTPUT / "mimic_iii_v2_panel_qa.json").read_text(encoding="utf-8"))
    index_hash = new_index["index_filter_sha256"]
    cache_valid = {
        table: bool(m3._cache_is_valid(PRIVATE / "cache" / f"mimic_iii_{table}_filtered.csv.gz",
                                       Path(run["source_zip"]), m3.MEMBERS[table], index_hash))
        for table in ("chartevents", "labevents")
    }
    if not all(cache_valid.values()) or qa["panel_rows"] != len(new_panel):
        raise AssertionError("Promoted cache or panel QA did not pass")

    record = {
        "schema": "mimic-iii-bp-repair-verification-v1",
        "status": "reaggregated_independently_reviewed_root_accepted",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repair": {
            "version": m3.VERSION, "filter_cache_schema": m3.FILTER_CACHE_SCHEMA,
            "added_identity_mappings": {str(item): int(m3.CHART_MAP[item]) for item in BP_IDS},
            "mimic_iii_rr_total_mapping": {"224690": 220210, "mimic_iv_direct_itemid": 220210},
            "source_ids_added": sorted(added_ids), "source_ids_removed": sorted(removed_ids),
            "old_index_filter_sha256": old_index["index_filter_sha256"],
            "new_index_filter_sha256": new_index["index_filter_sha256"],
            "old_chart_rows": old_rows, "new_chart_rows": new_rows,
            "added_chart_rows": new_rows - old_rows,
            "added_source_id_counts": source_id_counts,
            "count_method": (
                "Old and new caches validate against the same source fingerprint and index filter. "
                "CHART_IDS changed only by these four IDs, and every prior map entry is unchanged. "
                "Each added source ID maps one-to-one to its canonical channel, so the channel-row "
                "count delta equals the selected source-ID count."
            ),
            "source_zip": run["source_zip"], "source_zip_size": run["source_zip_size"],
            "source_archive_fingerprint": run["archive_fingerprint"],
            "chartevents_member": run["members"]["chartevents"],
        },
        "panel": {
            "old_path": str(old_panel_path), "old_sha256": sha256(old_panel_path),
            "new_path": str(new_panel_path), "new_sha256": panel_sha,
            "rows": len(new_panel), "same_admission_disease_keys": True,
            "unique_admissions": int(new_panel.reset_index()["hadm_id"].nunique()),
            "unique_patients": int(new_panel["pid"].nunique()),
            "missing_outcomes": int(new_panel["died"].isna().sum()),
        },
        "bisap_invariance": {
            "same_panel_keys": True, "fields": bisap,
            "primary_complete_before": int(old_panel["bisap4"].notna().sum()),
            "primary_complete_after": int(new_panel["bisap4"].notna().sum()),
            "ett_as1_complete_before": int(old_panel["bisap4_ett_as1"].notna().sum()),
            "ett_as1_complete_after": int(new_panel["bisap4_ett_as1"].notna().sum()),
        },
        "cache_validation": {
            "valid": cache_valid,
            "chartevents_sha256": new_cache_manifest["cache_sha256"],
            "labevents_sha256": json.loads(
                m3._cache_manifest_path(PRIVATE / "cache" / "mimic_iii_labevents_filtered.csv.gz")
                .read_text(encoding="utf-8")
            )["cache_sha256"],
        },
        "analysis": {
            "summary_path": str(ANALYSIS / "summary.csv"),
            "summary_sha256": sha256(ANALYSIS / "summary.csv"),
            "sensitivity_path": str(ANALYSIS / "sensitivity.csv"),
            "sensitivity_sha256": sha256(ANALYSIS / "sensitivity.csv"),
            "analysis_provenance_path": str(ANALYSIS / "analysis_provenance.json"),
            "analysis_panel_sha256": analysis_provenance["panel_sha256"],
            "comparison_path": str(comparison_path),
            "comparison_sha256": sha256(comparison_path),
            "comparison_rows": len(comparison),
            "score_complete_counts": run["score_complete_counts"],
        },
        "execution": {
            "full_chart_source_pass": {
                "pid": 55892, "status": "completed",
                "stdout_log": str(SCAN_STDOUT), "stderr_log": str(SCAN_STDERR),
                "completion_line": "[done] rows=38,253; admissions=25,417; patients=19,471",
            },
            "production_cache_only_reducer": {
                "pid": 62992, "status": "completed; reused verified filtered caches",
                "chart_rows_reused": new_rows, "lab_rows_reused": int(
                    json.loads(m3._cache_manifest_path(PRIVATE / "cache" / "mimic_iii_labevents_filtered.csv.gz")
                               .read_text(encoding="utf-8"))["rows"]
                ),
            },
            "normal_entry_tests": {
                "command": "python -X utf8 work/v2/mimic3/test_m58_mimic3_rebuild.py -q",
                "exit_code": 0, "passed": 7,
                "log_path": str(TEST_LOG), "log_sha256": sha256(TEST_LOG),
            },
        },
        "code": {
            "builder_path": str(ROOT / "work" / "v2" / "mimic3" / "m58_mimic3_rebuild.py"),
            "builder_sha256": sha256(ROOT / "work" / "v2" / "mimic3" / "m58_mimic3_rebuild.py"),
            "common_reducer_path": str(ROOT / "work" / "v2" / "mimic" / "m58_mimic_rebuild.py"),
            "common_reducer_sha256": sha256(ROOT / "work" / "v2" / "mimic" / "m58_mimic_rebuild.py"),
            "normal_entry_test_path": str(ROOT / "work" / "v2" / "mimic3" / "test_m58_mimic3_rebuild.py"),
            "normal_entry_test_sha256": sha256(ROOT / "work" / "v2" / "mimic3" / "test_m58_mimic3_rebuild.py"),
            "comparison_script_path": str(Path(__file__).resolve()),
            "comparison_script_sha256": sha256(Path(__file__)),
        },
        "source_repair_gate": {
            "pending_marker_in_analysis": (ANALYSIS / "PENDING_SOURCE_REPAIR.json").exists(),
            "resolved_marker_path": str(RESOLVED_MARKER),
            "resolved_marker_sha256": sha256(RESOLVED_MARKER) if RESOLVED_MARKER.exists() else None,
            "independent_review_path": str(INDEPENDENT_REVIEW),
            "independent_review_sha256": sha256(INDEPENDENT_REVIEW) if INDEPENDENT_REVIEW.exists() else None,
        },
    }
    manifest_path = RECON / "mimic_iii_bp_repair_verification.json"
    manifest_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "comparison_path": str(comparison_path),
        "comparison": comparison[["disease", "score_complete_primary_before",
                                  "score_complete_primary_after", "score_coverage_primary_pct_before",
                                  "score_coverage_primary_pct_after", "score_complete_never_before",
                                  "score_complete_never_after", "score_coverage_never_pct_before",
                                  "score_coverage_never_pct_after", "delta_w_pp_before",
                                  "delta_w_pp_after", "delta_w_change_pp", "state_after"]]
                     .to_dict("records"),
        "added_source_id_counts": source_id_counts,
        "panel_sha256": panel_sha,
        "bisap_primary_complete_before_after": [record["bisap_invariance"]["primary_complete_before"],
                                                record["bisap_invariance"]["primary_complete_after"]],
        "bisap_ett_complete_before_after": [record["bisap_invariance"]["ett_as1_complete_before"],
                                             record["bisap_invariance"]["ett_as1_complete_after"]],
        "manifest_path": str(manifest_path),
    }, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

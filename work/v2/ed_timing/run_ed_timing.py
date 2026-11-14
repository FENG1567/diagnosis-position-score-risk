"""Run the frozen MIMIC-IV ED episode-linkage/code-cohort sensitivity.

All public outputs are aggregate. Row-level linkage flags are retained only in
the assigned private derivative directory. The script refuses to run if any
frozen input, analysis source, or this script differs from the pre-outcome
manifest.
"""
from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
V2 = ROOT / "work" / "v2"
SCRIPT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(V2))
sys.path.insert(0, str(V2 / "mimic"))

from analyse_panels import (analysis_frame, audit_module, audited, clean_json,
                            normalize_panel, status_of, summarize)
from estimands import direct_contrast
from m58_mimic_rebuild import DISEASES, _normalized_codes


DISEASE_SCORE = {"sepsis": "qsofa", "pneumonia": "curb65"}
ROW_SPECS = [
    ("row1_full_main", "Full main ICU-indexed complete-score hospital cohort", None),
    ("row2_linked_ed_episode", "Linked ED episode, any ED diagnosis", "row2_eligible"),
    ("row3_ed_coded", "Linked ED episode with MAIN-matching ED code", "row3_code"),
    ("row4_ed_code_ends_by_icu", "MAIN-matching ED episode ends by index ICU", "row4_code_preicu"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_freeze(revision_dir: Path) -> dict:
    config_path = revision_dir / "analysis_config.json"
    freeze_path = revision_dir / "freeze_manifest.json"
    if not config_path.is_file() or not freeze_path.is_file():
        raise RuntimeError("Pre-outcome config/freeze manifest is missing.")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    manifest = json.loads(freeze_path.read_text(encoding="utf-8"))
    expected_config = manifest.get("analysis_config_sha256")
    observed_config = sha256(config_path)
    if observed_config != expected_config:
        raise RuntimeError("Frozen analysis_config.json hash mismatch.")
    protocol_path = revision_dir / "protocol.md"
    if sha256(protocol_path) != config.get("protocol_sha256") or \
            manifest.get("protocol_sha256") != config.get("protocol_sha256"):
        raise RuntimeError("Frozen protocol hash mismatch.")
    expected_script = config["code_hashes"][str(Path(__file__).resolve())]
    if sha256(Path(__file__).resolve()) != expected_script:
        raise RuntimeError("Frozen ED timing script hash mismatch.")
    for path_text, expected in {**config["input_hashes"], **config["code_hashes"]}.items():
        path = Path(path_text)
        if not path.is_file():
            raise FileNotFoundError(f"Frozen file is absent: {path}")
        if sha256(path) != expected:
            raise RuntimeError(f"Frozen file hash mismatch: {path}")
    for path_text, expected in config.get("validation_artifact_hashes", {}).items():
        path = Path(path_text)
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"Frozen validation artifact hash mismatch: {path}")
    return config


def normalize_id_columns(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = data.copy()
    for column in columns:
        out[column] = pd.to_numeric(out[column], errors="coerce").astype("Int64")
    return out


def load_sources(panel_path: Path, ed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    panel = normalize_panel(panel_path)
    panel = normalize_id_columns(panel, ["subject_id", "hadm_id", "stay_id"])
    for column in ("admittime", "intime"):
        panel[column] = pd.to_datetime(panel[column], errors="coerce")

    edstays = pd.read_csv(
        ed_dir / "edstays.csv.gz",
        dtype={"subject_id": "Int64", "hadm_id": "Int64", "stay_id": "Int64"},
        low_memory=False,
    )
    for column in ("intime", "outtime"):
        edstays[column] = pd.to_datetime(edstays[column], errors="coerce")
    if edstays["stay_id"].duplicated().any():
        raise ValueError("ED edstays stay_id is not unique; stop before cohort linking.")

    diagnosis = pd.read_csv(
        ed_dir / "diagnosis.csv.gz",
        usecols=["subject_id", "stay_id", "icd_code", "icd_version"],
        dtype={"subject_id": "Int64", "stay_id": "Int64", "icd_code": "string",
               "icd_version": "Int8"},
        low_memory=False,
    )
    return panel, edstays, diagnosis


def diagnosis_linkage_and_hits(
    edstays: pd.DataFrame, diagnosis: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    stay_keys = edstays[["stay_id", "subject_id"]].rename(columns={"subject_id": "ed_subject_id"})
    dx = diagnosis.merge(stay_keys, on="stay_id", how="left", validate="many_to_one", indicator=True)
    dx["stay_linked"] = dx["_merge"].eq("both")
    dx["subject_verified"] = dx["stay_linked"] & dx["subject_id"].eq(dx["ed_subject_id"]).fillna(False)
    dx["code"] = _normalized_codes(dx)
    hits = []
    for disease in DISEASE_SCORE:
        spec = DISEASES[disease]
        v = pd.to_numeric(dx["icd_version"], errors="coerce")
        code = dx["code"]
        hit = (((v == 10) & code.str.startswith(spec["main10"], na=False)) |
               ((v == 9) & code.str.startswith(spec["main9"], na=False)))
        selected = dx.loc[dx["subject_verified"] & hit,
                          ["stay_id", "ed_subject_id"]].drop_duplicates()
        if not selected.empty:
            selected["disease"] = disease
            hits.append(selected)
    hit_table = (pd.concat(hits, ignore_index=True) if hits else
                 pd.DataFrame(columns=["stay_id", "ed_subject_id", "disease"]))
    hit_table["has_main_ed_code"] = True
    diagnostics = {
        "diagnosis_rows": int(len(dx)),
        "diagnosis_rows_without_matching_stay_id": int((~dx["stay_linked"]).sum()),
        "diagnosis_rows_with_stay_subject_mismatch": int((dx["stay_linked"] & ~dx["subject_verified"]).sum()),
        "diagnosis_rows_with_verified_stay_subject": int(dx["subject_verified"].sum()),
        "unique_diagnosis_stays": int(dx.loc[dx["subject_verified"], "stay_id"].nunique()),
    }
    return hit_table, diagnostics


def episode_candidates_for_disease(
    source: pd.DataFrame, edstays: pd.DataFrame, hit_table: pd.DataFrame, disease: str,
) -> tuple[pd.DataFrame, dict]:
    target = source[["hadm_id", "subject_id", "disease", "admittime", "intime", "grp", "pos"]].copy()
    if target["hadm_id"].duplicated().any():
        raise ValueError(f"Main panel has duplicate HADM IDs for {disease}.")
    target = target.rename(columns={"subject_id": "cohort_subject_id", "admittime": "hospital_admittime",
                                    "intime": "icu_intime"})
    ed = edstays[["subject_id", "hadm_id", "stay_id", "intime", "outtime"]].rename(
        columns={"subject_id": "ed_subject_id", "intime": "ed_intime", "outtime": "ed_outtime"})
    ed = ed.loc[ed["hadm_id"].notna()]
    candidates = ed.merge(target, on="hadm_id", how="inner", validate="many_to_one")
    candidates["subject_verified"] = candidates["ed_subject_id"].eq(candidates["cohort_subject_id"]).fillna(False)
    disease_hits = hit_table.loc[hit_table["disease"].eq(disease),
                                 ["stay_id", "ed_subject_id", "has_main_ed_code"]]
    candidates = candidates.merge(disease_hits, on=["stay_id", "ed_subject_id"], how="left",
                                  validate="many_to_one")
    candidates["has_main_ed_code"] = candidates["has_main_ed_code"].astype("boolean").fillna(False).astype(bool)

    ed_hours = lambda delta: delta.dt.total_seconds() / 3600.0
    candidates["icu_from_hospital_admit_h"] = ed_hours(
        candidates["icu_intime"] - candidates["hospital_admittime"])
    candidates["icu_from_ed_start_h"] = ed_hours(candidates["icu_intime"] - candidates["ed_intime"])
    candidates["ed_episode_time_valid"] = (
        candidates["ed_intime"].notna() & candidates["ed_outtime"].notna() &
        candidates["ed_outtime"].ge(candidates["ed_intime"])
    )
    candidates["hospital_icu_0_24h"] = candidates["icu_from_hospital_admit_h"].between(0, 24, inclusive="both")
    candidates["ed_start_before_icu"] = candidates["ed_intime"].lt(candidates["icu_intime"])
    candidates["ed_end_by_icu_plus24h"] = candidates["ed_outtime"].le(
        candidates["icu_intime"] + pd.Timedelta("24h"))
    candidates["ed_end_by_icu"] = candidates["ed_outtime"].le(candidates["icu_intime"])
    candidates["row2_eligible"] = (
        candidates["subject_verified"] & candidates["ed_episode_time_valid"] &
        candidates["hospital_icu_0_24h"] & candidates["ed_start_before_icu"] &
        candidates["ed_end_by_icu_plus24h"]
    )
    candidates["row3_code"] = candidates["row2_eligible"] & candidates["has_main_ed_code"]
    candidates["row4_code_preicu"] = candidates["row3_code"] & candidates["ed_end_by_icu"]

    match_rows = candidates["subject_verified"]
    match = candidates.loc[match_rows]
    target_hadm = set(target["hadm_id"].dropna().astype("int64"))
    verified_hadm = set(match["hadm_id"].dropna().astype("int64"))
    any_hadm = set(candidates["hadm_id"].dropna().astype("int64"))
    gap = source[["hadm_id", "admittime", "intime"]].drop_duplicates("hadm_id").copy()
    gap["icu_from_hospital_admit_h"] = ed_hours(gap["intime"] - gap["admittime"])
    coverage = {
        "disease": disease,
        "hospital31_main_disease_admissions": int(source["hadm_id"].nunique()),
        "hospital31_admissions_with_ed_hadm_match_any_subject": int(len(any_hadm)),
        "hospital31_admissions_with_subject_verified_ed_link": int(len(verified_hadm)),
        "hospital31_admissions_without_subject_verified_ed_link": int(len(target_hadm - verified_hadm)),
        "ed_episode_rows_with_hadm_match_to_hospital_disease": int(len(candidates)),
        "ed_episode_rows_hadm_match_subject_verified": int(candidates["subject_verified"].sum()),
        "ed_episode_rows_hadm_match_subject_mismatch": int((~candidates["subject_verified"]).sum()),
        "subject_mismatch_hadm_count": int(candidates.loc[~candidates["subject_verified"], "hadm_id"].nunique()),
        "verified_episode_rows_with_valid_ed_times": int(match["ed_episode_time_valid"].sum()),
        "verified_episode_rows_with_invalid_or_missing_ed_times": int((~match["ed_episode_time_valid"]).sum()),
        "verified_episode_rows_ed_start_before_index_icu": int(match["ed_start_before_icu"].sum()),
        "verified_episode_rows_ed_end_by_index_icu": int(match["ed_end_by_icu"].sum()),
        "verified_episode_rows_ed_end_by_index_icu_plus24h": int(match["ed_end_by_icu_plus24h"].sum()),
        "main_admissions_with_nonmissing_hospital_to_icu_hours": int(gap["icu_from_hospital_admit_h"].notna().sum()),
        "main_admissions_icu_0_to_24h_after_hospital_admit": int(gap["icu_from_hospital_admit_h"].between(0, 24, inclusive="both").sum()),
        "verified_ed_episode_starts_before_hospital_admittime": int(
            (match["ed_intime"] < match["hospital_admittime"]).sum()),
        "verified_ed_episode_ends_before_hospital_admittime": int(
            (match["ed_outtime"] < match["hospital_admittime"]).sum()),
        "verified_ed_episode_starts_after_hospital_admittime": int(
            (match["ed_intime"] >= match["hospital_admittime"]).sum()),
        "ed_release": "MIMIC-IV-ED 2.2",
        "hospital_release": "MIMIC-IV Hospital 3.1 (repaired main panel)",
        "compatibility_interpretation": "empirical HADM + subject linkage and chronology; no blanket release equivalence assumed",
    }
    return candidates, coverage


def completeness_rows(
    disease: str, row_code: str, row_label: str, selected: pd.DataFrame,
    analytic: pd.DataFrame, score_col: str,
) -> list[dict]:
    rows = []
    for group, label in ((0, "primary hospital billing position"),
                         (1, "never-primary hospital billing position")):
        s = selected.loc[selected["grp"].eq(group)]
        a = analytic.loc[analytic["grp"].eq(group)]
        n = len(s)
        score_complete = int(pd.to_numeric(s[score_col], errors="coerce").notna().sum())
        outcome_complete = int(pd.to_numeric(s["died"], errors="coerce").notna().sum())
        both = int((pd.to_numeric(s[score_col], errors="coerce").notna() &
                    pd.to_numeric(s["died"], errors="coerce").notna()).sum())
        rows.append({
            "disease": disease, "cohort": row_code, "cohort_label": row_label,
            "hospital_group": label, "grp": group,
            "n_main_admission_records": n,
            "n_score_complete": score_complete,
            "score_complete_pct": (100 * score_complete / n) if n else np.nan,
            "n_outcome_complete": outcome_complete,
            "outcome_complete_pct": (100 * outcome_complete / n) if n else np.nan,
            "n_score_and_outcome_complete": both,
            "n_analysis_frame_records": int(len(a)),
            "n_main_patients": int(s["pid"].nunique()),
            "n_analysis_frame_patients": int(a["pid"].nunique()),
        })
    return rows


def summary_and_level_rows(
    audit: dict, direct, frame: pd.DataFrame, disease: str, cohort: str,
    cohort_label: str, score_col: str,
) -> tuple[dict, list[dict]]:
    """Build the standard aggregate tables from the canonical Contrast API."""
    summary = summarize(audit, direct, cohort_label)
    summary.update({
        "disease": disease,
        "cohort": cohort,
        "cohort_label": cohort_label,
        "score": score_col,
        "estimand": "Delta_w record-weighted summary (never-primary minus primary)",
        "n_analysis_frame_records_all_levels": int(len(frame)),
        "n_analysis_frame_primary_records": int(frame["grp"].eq(0).sum()),
        "n_analysis_frame_never_primary_records": int(frame["grp"].eq(1).sum()),
        "n_analysis_frame_primary_patients": int(frame.loc[frame["grp"].eq(0), "pid"].nunique()),
        "n_analysis_frame_never_primary_patients": int(frame.loc[frame["grp"].eq(1), "pid"].nunique()),
        "n_supported_records": int(direct.n_records),
        "n_supported_patients": int(direct.n_patients),
        "n_records_outside_common_support": int(len(frame) - direct.n_records),
        "support_share_pct_of_complete_analysis_records": 100 * direct.support_share,
        "common_support_levels": json.dumps(
            [float(x) for x in direct.levels["level"]] if "level" in direct.levels else []),
        "weight_by_score_level": json.dumps({str(float(r.level)): float(r.weight)
                                               for r in direct.levels.itertuples(index=False)}),
        "C_state": status_of(audit),
        "C_interval_status": audit.get("interval_status"),
        "C_verdict": audit.get("verdict"),
        "normal_IF_delta_ci_pp_gated_by_C": json.dumps(audit.get("delta_ci_pp")),
        "bootstrap_ci_pp_gated_by_C": json.dumps(audit.get("stratified_rd_ci_pp")),
        "difference_from_full_main_delta_w_pp_descriptive": np.nan,
        "difference_interpretation": "different observed cohort/common support/record weights; descriptive only",
    })
    per_level = []
    detail_by_level = {float(r.level): float(r.weight)
                       for r in direct.levels.itertuples(index=False)}
    for item in audit.get("per_level", []):
        out = dict(item)
        out.update({
            "disease": disease, "cohort": cohort, "cohort_label": cohort_label,
            "score": score_col,
            "estimand": "score-level risk difference; contributes to Delta_w record-weighted summary",
            "support_record_weight": detail_by_level.get(float(item["level"])),
            "C_state": status_of(audit),
            "C_interval_status": audit.get("interval_status"),
        })
        per_level.append(out)
    return summary, per_level


def write_analysis_outputs(
    panel: pd.DataFrame, edstays: pd.DataFrame, diagnosis: pd.DataFrame,
    hit_table: pd.DataFrame, dx_diagnostics: dict, config: dict,
    revision_dir: Path, output_dir: Path, private_dir: Path,
    panel_path: Path, ed_dir: Path,
) -> None:
    module = audit_module()
    all_summary: list[dict] = []
    all_levels: list[dict] = []
    all_completeness: list[dict] = []
    all_episode_counts: list[dict] = []
    all_coverage: list[dict] = []
    all_link_failures: list[dict] = []
    private_admissions: list[pd.DataFrame] = []
    private_episodes: list[pd.DataFrame] = []
    audit_details: dict[str, dict] = {}

    for disease, score_col in DISEASE_SCORE.items():
        source = panel.loc[panel["disease"].eq(disease)].copy()
        if "broad_inclusion" in source.columns:
            source = source.loc[source["broad_inclusion"].eq(1)].copy()
        if source.empty:
            raise RuntimeError(f"No main-panel records found for {disease}.")
        if source["hadm_id"].duplicated().any():
            raise ValueError(f"The main panel is not one row per admission for {disease}.")
        expected_group = np.where(source["pos"].eq(1), 0,
                                  np.where(source["pos"].gt(1), 1, np.nan))
        observed_group = pd.to_numeric(source["grp"], errors="coerce").to_numpy(float)
        if not np.allclose(observed_group, expected_group, equal_nan=True):
            raise AssertionError(f"The fixed main hospital group is inconsistent with pos for {disease}.")

        source["disease"] = disease
        candidates, coverage = episode_candidates_for_disease(source, edstays, hit_table, disease)
        coverage.update(dx_diagnostics)
        coverage.update({
            "edstays_rows_total": int(len(edstays)),
            "edstays_unique_stays": int(edstays["stay_id"].nunique()),
            "edstays_rows_with_hadm_id": int(edstays["hadm_id"].notna().sum()),
            "edstays_rows_without_hadm_id": int(edstays["hadm_id"].isna().sum()),
            "edstays_unique_hadm_ids_with_id": int(edstays.loc[edstays["hadm_id"].notna(), "hadm_id"].nunique()),
        })
        all_coverage.append(coverage)
        failures = [
            dict(disease=disease, failure="HADM matched target main disease admission but subject_id mismatched",
                 n_rows=coverage["ed_episode_rows_hadm_match_subject_mismatch"],
                 n_distinct_stays=int(candidates.loc[~candidates["subject_verified"], "stay_id"].nunique()),
                 interpretation="excluded from all ED-linked cohorts"),
            dict(disease=disease, failure="Target main disease admissions without subject-verified ED HADM link",
                 n_rows=coverage["hospital31_admissions_without_subject_verified_ed_link"],
                 n_distinct_stays=np.nan,
                 interpretation="no ED cohort link observed; not classified as a data error"),
            dict(disease=disease, failure="ED diagnosis rows without matching stay_id",
                 n_rows=dx_diagnostics["diagnosis_rows_without_matching_stay_id"],
                 n_distinct_stays=np.nan, interpretation="not used for ED code matching"),
            dict(disease=disease, failure="ED diagnosis rows with stay_id but subject_id mismatch",
                 n_rows=dx_diagnostics["diagnosis_rows_with_stay_subject_mismatch"],
                 n_distinct_stays=np.nan, interpretation="not used for ED code matching"),
        ]
        all_link_failures.extend(failures)

        source = source.merge(
            candidates.loc[candidates["subject_verified"]]
            .groupby(["hadm_id", "disease"], dropna=False)
            .agg(n_verified_ed_episodes=("stay_id", "nunique"),
                 n_row2_ed_episodes=("row2_eligible", "sum"),
                 n_row3_ed_code_episodes=("row3_code", "sum"),
                 n_row4_ed_code_preicu_episodes=("row4_code_preicu", "sum"))
            .reset_index(), on=["hadm_id", "disease"], how="left", validate="one_to_one")
        count_cols = ["n_verified_ed_episodes", "n_row2_ed_episodes", "n_row3_ed_code_episodes",
                      "n_row4_ed_code_preicu_episodes"]
        source[count_cols] = source[count_cols].fillna(0).astype("int64")
        source["row2_eligible"] = source["n_row2_ed_episodes"].gt(0)
        source["row3_code"] = source["n_row3_ed_code_episodes"].gt(0)
        source["row4_code_preicu"] = source["n_row4_ed_code_preicu_episodes"].gt(0)
        if (source["row4_code_preicu"] & ~source["row3_code"]).any() or (
                source["row3_code"] & ~source["row2_eligible"]).any():
            raise AssertionError("Nested ED cohort rules are not nested.")

        private_admissions.append(source[[
            "subject_id", "hadm_id", "disease", "grp", "pos", "admittime", "intime",
            score_col, "died", "n_verified_ed_episodes", "n_row2_ed_episodes",
            "n_row3_ed_code_episodes", "n_row4_ed_code_preicu_episodes",
            "row2_eligible", "row3_code", "row4_code_preicu",
        ]].copy())
        episode_private = candidates[[
            "ed_subject_id", "cohort_subject_id", "hadm_id", "stay_id", "disease", "grp", "pos",
            "ed_intime", "ed_outtime", "hospital_admittime", "icu_intime", "subject_verified",
            "ed_episode_time_valid", "hospital_icu_0_24h", "ed_start_before_icu",
            "ed_end_by_icu_plus24h", "ed_end_by_icu", "has_main_ed_code", "row2_eligible",
            "row3_code", "row4_code_preicu",
        ]].copy()
        private_episodes.append(episode_private)

        complete_main = analysis_frame(source, score_col)
        for row_code, row_label, flag_col in ROW_SPECS:
            if flag_col is None:
                selected_source = source.copy()
            else:
                selected_source = source.loc[source[flag_col]].copy()
            frame = analysis_frame(selected_source, score_col)
            all_completeness.extend(completeness_rows(
                disease, row_code, row_label, selected_source, frame, score_col))

            audit, direct = audited(module, frame, "MIMIC-IV ED2.2 / Hospital3.1",
                                   disease, row_code)
            audit_details[f"{disease}::{row_code}"] = audit
            summary, level_rows = summary_and_level_rows(
                audit, direct, frame, disease, row_code, row_label, score_col)
            all_summary.append(summary)
            all_levels.extend(level_rows)

            # ED episode counts for the analytic denominator, by fixed hospital group.
            complete_keys = set(frame["hadm_id"].dropna().astype("int64"))
            analytic_candidates = candidates.loc[
                candidates["subject_verified"] & candidates["hadm_id"].isin(complete_keys)
            ]
            row_episode_flag = {"row2_linked_ed_episode": "row2_eligible",
                                "row3_ed_coded": "row3_code",
                                "row4_ed_code_ends_by_icu": "row4_code_preicu"}.get(row_code)
            if row_episode_flag is not None:
                qualifying = analytic_candidates.loc[analytic_candidates[row_episode_flag]]
                for group, label in ((0, "primary hospital billing position"),
                                     (1, "never-primary hospital billing position")):
                    q = qualifying.loc[qualifying["grp"].eq(group)]
                    per_admission = q.groupby("hadm_id")["stay_id"].nunique()
                    all_episode_counts.append({
                        "disease": disease, "cohort": row_code, "cohort_label": row_label,
                        "hospital_group": label, "grp": group,
                        "n_qualifying_ed_episodes": int(q["stay_id"].nunique()),
                        "n_analysis_admissions_with_qualifying_episode": int(per_admission.size),
                        "n_analysis_admissions_with_multiple_qualifying_episodes": int(per_admission.ge(2).sum()),
                        "max_qualifying_episodes_per_admission": int(per_admission.max()) if len(per_admission) else 0,
                        "analysis_unit": "one hospital admission per disease",
                    })

        del complete_main

    # The row-1 comparisons are descriptive only because each cohort has its own
    # observed common support and record-share target.
    summary_df = pd.DataFrame(all_summary)
    for disease in DISEASE_SCORE:
        base_rows = summary_df.loc[summary_df["disease"].eq(disease) &
                                   summary_df["cohort"].eq("row1_full_main"), "delta_w_pp"]
        base_delta = base_rows.iloc[0] if len(base_rows) else np.nan
        mask = summary_df["disease"].eq(disease) & summary_df["cohort"].ne("row1_full_main")
        summary_df.loc[mask, "difference_from_full_main_delta_w_pp_descriptive"] = (
            pd.to_numeric(summary_df.loc[mask, "delta_w_pp"], errors="coerce") - base_delta)

    output_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_dir / "cohort_summary.csv", index=False)
    pd.DataFrame(all_levels).to_csv(output_dir / "per_level_risks.csv", index=False)
    pd.DataFrame(all_completeness).to_csv(output_dir / "arm_completeness.csv", index=False)
    pd.DataFrame(all_episode_counts).to_csv(output_dir / "ed_episode_counts.csv", index=False)
    pd.DataFrame(all_coverage).to_csv(output_dir / "release_linkage_coverage.csv", index=False)
    pd.DataFrame(all_link_failures).to_csv(output_dir / "linkage_failures.csv", index=False)
    (output_dir / "audit_details.json").write_text(
        json.dumps(clean_json(audit_details), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    pd.concat(private_admissions, ignore_index=True).to_csv(
        private_dir / "admission_ed_timing_flags_private.csv.gz", index=False, compression="gzip")
    pd.concat(private_episodes, ignore_index=True).to_csv(
        private_dir / "linked_ed_episodes_private.csv.gz", index=False, compression="gzip")

    provenance = {
        "analysis_config_sha256": sha256(revision_dir / "analysis_config.json"),
        "freeze_manifest_sha256": sha256(revision_dir / "freeze_manifest.json"),
        "python": sys.version,
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "main_panel": str(panel_path),
        "ed_directory": str(ed_dir),
        "public_aggregate_outputs_only": True,
        "private_row_derivatives": [
            str(private_dir / "admission_ed_timing_flags_private.csv.gz"),
            str(private_dir / "linked_ed_episodes_private.csv.gz"),
        ],
        "estimand": "Delta_w record-weighted summary with each cohort's observed common-support record weights",
        "interpretation_limit": "ED diagnoses are retrospective billing codes with no entry/onset time; episode timing cannot establish prospective availability or disease onset.",
    }
    (output_dir / "analysis_provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    (output_dir / "README.md").write_text(
        "# MIMIC-IV ED episode-linkage and code-cohort sensitivity\n\n"
        "This is the amended retrospective ED episode-linkage/code-cohort selection analysis. "
        "The original code-timing validity gate failed: MIMIC-IV-ED diagnoses are assigned after "
        "hospital discharge, and the code table has no entry/onset timestamp. No result here "
        "establishes onset, prospective coding, or baseline documentation availability.\n\n"
        "`cohort_summary.csv` reports the four frozen rows per disease. Every `delta_w_pp` is a "
        "record-weighted summary with the cohort's observed common-support record weights; the "
        "support and weights are cohort-specific and define no external target. The normal "
        "influence-function interval and C state come from the existing audit path. The comparison "
        "with row 1 is a descriptive change in selected cohort, support, and target.\n\n"
        "`per_level_risks.csv`, `arm_completeness.csv`, `ed_episode_counts.csv`, "
        "`release_linkage_coverage.csv`, and `linkage_failures.csv` provide aggregate detail. "
        "No row-level data are stored under this output directory. Private linked derivatives "
        "are held only under the configured F: path. See the frozen protocol and config in the "
        "run revision directory.\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision-dir", required=True,
                        help="Immutable run directory containing protocol, config, and freeze manifest")
    args = parser.parse_args()
    revision_dir = Path(args.revision_dir).resolve()
    config = verify_freeze(revision_dir)
    panel_path = Path(config["sources"]["hospital_panel"])
    ed_dir = Path(config["sources"]["edstays_file"]).parent
    output_dir = Path(config["output"]["public_aggregate_directory"])
    private_dir = Path(config["privacy"]["private_derivative_directory"])
    output_dir.mkdir(parents=True, exist_ok=True)
    panel, edstays, diagnosis = load_sources(panel_path, ed_dir)
    hit_table, dx_diagnostics = diagnosis_linkage_and_hits(edstays, diagnosis)
    write_analysis_outputs(panel, edstays, diagnosis, hit_table, dx_diagnostics, config,
                           revision_dir, output_dir, private_dir, panel_path, ed_dir)
    print(f"completed ED linkage sensitivity; aggregate outputs: {output_dir}", flush=True)
    print(f"private row-level derivatives: {private_dir}", flush=True)


if __name__ == "__main__":
    main()

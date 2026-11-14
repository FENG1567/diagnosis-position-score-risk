#!/usr/bin/env python3
"""Aggregate-only eligibility and role-count audit for the proposed v3 study.

This script reads the frozen v2 score panels, assigns deterministic data roles,
and writes aggregate counts only. It does not fit or evaluate any model and never
writes patient, admission, or hospital identifiers to disk.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


SEED = "JCE-v3-20261113"
ROLES = ("train", "recalibration", "test")
DISEASES = ("sepsis", "pneumonia")
SCORE_COLUMNS = {"sepsis": "qsofa", "pneumonia": "curb65"}
MAX_SCORES = {"sepsis": 3, "pneumonia": 5}
ANCHOR_RE = re.compile(r"^\s*(\d{4})\s*-\s*(\d{4})\s*$")
DEFAULT_EICU = Path("work/v2/eicu/eicu_disease_panel.csv.gz")
DEFAULT_MIMIC = Path(
    "F:/\u5206\u6790\u4e13\u7528/meta_measurement_20261103/work/paperB_v2/mimic/mimic_iv_v2_score_panel.csv.gz"
)
DEFAULT_OUT = Path("outputs/v3/validation")


def clean(value: object) -> str | None:
    value = "" if value is None else str(value).strip()
    return value or None


def number(value: object) -> float | None:
    value = clean(value)
    if value is None:
        return None
    try:
        result = float(value)
    except ValueError:
        return None
    return result


def binary(value: object) -> int | None:
    parsed = number(value)
    if parsed in (0.0, 1.0):
        return int(parsed)
    return None


def group_value(value: object) -> int | None:
    parsed = number(value)
    if parsed in (0.0, 1.0):
        return int(parsed)
    return None


def hash_bucket(namespace: str, identifier: str) -> int:
    payload = f"{SEED}|{namespace}|{identifier}".encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest(), 16) % 100


def bucket_role(bucket: int) -> str:
    if bucket < 60:
        return "train"
    if bucket < 80:
        return "recalibration"
    return "test"


def read_panel(path: Path, database: str) -> tuple[list[dict[str, object]], dict[str, int]]:
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or ())
        required = {"pid", "admission_id", "disease", "grp", "died"}
        required.add("hospitalid" if database == "eICU" else "anchor_year_group")
        missing = sorted(required - columns)
        if missing:
            raise ValueError(f"{database} panel missing required columns: {missing}")
        rows: list[dict[str, object]] = []
        invalid_outcome_values = 0
        invalid_group_values = 0
        invalid_score_values = 0
        for raw in reader:
            disease = (clean(raw.get("disease")) or "").lower()
            score_col = SCORE_COLUMNS.get(disease)
            raw_score = clean(raw.get(score_col)) if score_col else None
            score = number(raw_score) if score_col else None
            outcome = binary(raw.get("died"))
            group = group_value(raw.get("grp"))
            invalid_outcome_values += int(clean(raw.get("died")) is not None and outcome is None)
            invalid_group_values += int(clean(raw.get("grp")) is not None and group is None)
            invalid_score_values += int(raw_score is not None and (
                score is None or score < 0 or score > MAX_SCORES.get(disease, -1) or not score.is_integer()
            ))
            if score is not None and (
                score < 0 or score > MAX_SCORES.get(disease, -1) or not score.is_integer()
            ):
                score = None
            rows.append({
                "pid": clean(raw.get("pid")),
                "admission_id": clean(raw.get("admission_id")),
                "disease": disease,
                "group": group,
                "score": int(score) if score is not None else None,
                "outcome": outcome,
                "hospital": clean(raw.get("hospitalid")) if database == "eICU" else None,
                "anchor_group": clean(raw.get("anchor_year_group")) if database == "MIMIC-IV" else None,
                "anchor_year": number(raw.get("anchor_year")) if database == "MIMIC-IV" else None,
                "admit_year": parse_year(raw.get("admittime")) if database == "MIMIC-IV" else None,
                "role": None,
                "role_reason": None,
            })
    admission_counts = Counter(
        (str(row["disease"]), str(row["admission_id"]))
        for row in rows if row["admission_id"] is not None
    )
    duplicate_admission_disease_rows = sum(count - 1 for count in admission_counts.values() if count > 1)
    qa = {
        "duplicate_admission_disease_rows": duplicate_admission_disease_rows,
        "invalid_nonmissing_binary_outcome_values": invalid_outcome_values,
        "invalid_nonmissing_group_values": invalid_group_values,
        "invalid_nonmissing_score_values": invalid_score_values,
    }
    if any(qa.values()):
        failures = ", ".join(f"{key}={value}" for key, value in qa.items() if value)
        raise ValueError(f"{database} aggregate panel assertions failed: {failures}")
    return rows, qa


def parse_year(value: object) -> int | None:
    value = clean(value)
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).year
    except ValueError:
        match = re.match(r"^(\d{4})", value)
        return int(match.group(1)) if match else None


def assign_eicu(rows: list[dict[str, object]]) -> dict[str, object]:
    hospitals = sorted({str(r["hospital"]) for r in rows if r["hospital"] is not None})
    hospital_roles = {
        hospital: bucket_role(hash_bucket("eICU-hospital", hospital))
        for hospital in hospitals
    }
    by_patient: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        hospital = row["hospital"]
        row["role"] = hospital_roles.get(str(hospital)) if hospital is not None and row["pid"] is not None else None
        row["role_reason"] = "assigned_hospital" if row["role"] else ("missing_patient_id" if row["pid"] is None else "missing_hospital")
        if row["pid"] is not None:
            by_patient[str(row["pid"])].append(index)

    cross_role_patients: set[str] = set()
    missing_role_patients: set[str] = set()
    multi_hospital_patients: set[str] = set()
    for pid, indices in by_patient.items():
        roles = {rows[i]["role"] for i in indices if rows[i]["role"] is not None}
        has_unknown = any(rows[i]["role"] is None for i in indices)
        patient_hospitals = {rows[i]["hospital"] for i in indices if rows[i]["hospital"] is not None}
        if len(roles) > 1:
            cross_role_patients.add(pid)
        if has_unknown:
            missing_role_patients.add(pid)
        if len(patient_hospitals) > 1:
            multi_hospital_patients.add(pid)
        if len(roles) > 1 or has_unknown or len(patient_hospitals) > 1:
            for i in indices:
                rows[i]["role"] = None
                if len(roles) > 1:
                    reason = "cross_role_patient"
                elif len(patient_hospitals) > 1:
                    reason = "multi_hospital_patient"
                else:
                    reason = "missing_hospital_patient"
                rows[i]["role_reason"] = reason

    return {
        "split_method": "SHA-256 hospital buckets (60% train / 20% recalibration / 20% test); globally exclude patients with cross-role, multihospital, or missing-hospital records",
        "seed": SEED,
        "hospitals_total": len(hospitals),
        "hospitals_by_role": dict(Counter(hospital_roles.values())),
        "cross_role_patients_excluded": len(cross_role_patients),
        "patients_with_missing_hospital_excluded": len(missing_role_patients),
        "multi_hospital_patients_excluded_globally": len(multi_hospital_patients),
        "multi_hospital_patient_records_excluded_globally": sum(
            row["pid"] in multi_hospital_patients for row in rows
        ),
        "patient_count": len(by_patient),
    }


def interval_group_bounds(label: str | None) -> tuple[int, int] | None:
    match = ANCHOR_RE.match(label or "")
    if not match:
        return None
    low, high = int(match.group(1)), int(match.group(2))
    return (low, high) if low <= high else None


def assign_mimic(rows: list[dict[str, object]]) -> dict[str, object]:
    labels = sorted({str(r["anchor_group"]) for r in rows if r["anchor_group"] is not None})
    bounds_by_label = {label: interval_group_bounds(label) for label in labels}
    ordered = sorted((bounds, label) for label, bounds in bounds_by_label.items() if bounds is not None)
    intervals_valid = len(ordered) == len(labels) and len(ordered) >= 3
    if intervals_valid:
        intervals_valid = all(ordered[i][0][1] < ordered[i + 1][0][0] for i in range(len(ordered) - 1))
    required_columns_available = all(
        any(r[key] is not None for r in rows)
        for key in ("anchor_year", "admit_year", "anchor_group")
    )
    temporal = intervals_valid and required_columns_available

    unresolved_records = 0
    if temporal:
        for row in rows:
            bounds = bounds_by_label.get(str(row["anchor_group"])) if row["anchor_group"] is not None else None
            anchor_year, admit_year = row["anchor_year"], row["admit_year"]
            if bounds is None or anchor_year is None or admit_year is None or not float(anchor_year).is_integer():
                row["role"] = None
                row["role_reason"] = "unresolved_calendar_interval"
                unresolved_records += 1
                continue
            shift = int(admit_year) - int(anchor_year)
            low, high = bounds[0] + shift, bounds[1] + shift
            if high <= 2013:
                row["role"] = "train"
                row["role_reason"] = "calendar_interval"
            elif low >= 2014 and high <= 2016:
                row["role"] = "recalibration"
                row["role_reason"] = "calendar_interval"
            elif low >= 2017 and high <= 2022:
                row["role"] = "test"
                row["role_reason"] = "calendar_interval"
            else:
                row["role"] = None
                row["role_reason"] = "ambiguous_or_outside_calendar_windows"
                unresolved_records += 1
    else:
        for row in rows:
            row["role"] = (
                bucket_role(hash_bucket("MIMIC-IV-patient", str(row["pid"])))
                if row["pid"] is not None else None
            )
            row["role_reason"] = "patient_hash_fallback" if row["role"] else "missing_patient_id"

    for row in rows:
        if row["pid"] is None:
            row["role"] = None
            row["role_reason"] = "missing_patient_id"

    by_patient: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        if row["pid"] is not None:
            by_patient[str(row["pid"])].append(index)
    cross_role_patients: set[str] = set()
    for pid, indices in by_patient.items():
        roles = {rows[i]["role"] for i in indices if rows[i]["role"] is not None}
        if len(roles) > 1:
            cross_role_patients.add(pid)
            for i in indices:
                rows[i]["role"] = None
                rows[i]["role_reason"] = "cross_role_patient"

    return {
        "split_method": (
            "calendar-interval migration split from anchor_year_group plus admission-year shift; "
            "intervals wholly <=2013=train, 2014-2016=recalibration, 2017-2022=test; "
            "ambiguous/out-of-window records excluded"
            if temporal else
            "SHA-256 patient buckets (60% train / 20% recalibration / 20% test); temporal metadata not identifiable"
        ),
        "seed": SEED,
        "temporal_metadata_identifiable": temporal,
        "anchor_year_groups": [label for _, label in ordered] if temporal else labels,
        "calendar_windows": {"train": "entire possible admission interval <= 2013", "recalibration": "2014-2016", "test": "2017-2022"} if temporal else None,
        "unresolved_or_ambiguous_records": unresolved_records,
        "cross_role_patients_excluded": len(cross_role_patients),
        "patient_count": len(by_patient),
    }


def summarize_rows(rows: list[dict[str, object]], database: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for disease in DISEASES:
        score_col = SCORE_COLUMNS[disease]
        for role in ROLES:
            role_rows = [r for r in rows if r["role"] == role and r["disease"] == disease]
            for group_label, group_value_filter in (("all", None), ("primary", 0), ("never_primary", 1)):
                selected = [r for r in role_rows if group_value_filter is None or r["group"] == group_value_filter]
                identified = [r for r in selected if r["pid"] is not None and r["admission_id"] is not None]
                group_outcome = [r for r in identified if r["group"] in (0, 1) and r["outcome"] in (0, 1)]
                complete = [r for r in group_outcome if r["score"] is not None]
                result.append({
                    "database": database,
                    "disease": disease,
                    "score": score_col,
                    "role": role,
                    "diagnosis_group": group_label,
                    "panel_records": len(selected),
                    "identifier_complete_records": len(identified),
                    "missing_patient_id_records": sum(r["pid"] is None for r in selected),
                    "missing_admission_id_records": sum(r["admission_id"] is None for r in selected),
                    "group_and_outcome_known_records": len(group_outcome),
                    "score_complete_records": len(complete),
                    "events": sum(int(r["outcome"]) for r in complete),
                    "nonevents": sum(1 - int(r["outcome"]) for r in complete),
                    "patients": len({r["pid"] for r in complete if r["pid"] is not None}),
                    "event_patients": len({r["pid"] for r in complete if r["outcome"] == 1}),
                    "nonevent_patients": len({r["pid"] for r in complete if r["outcome"] == 0}),
                    "admissions": len({r["admission_id"] for r in complete if r["admission_id"] is not None}),
                    "hospitals": len({r["hospital"] for r in complete if r["hospital"] is not None}),
                })
    return result


def score_support_counts(rows: list[dict[str, object]], database: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for disease in DISEASES:
        disease_rows = [r for r in rows if r["disease"] == disease]
        test = [r for r in disease_rows if r["role"] == "test" and r["group"] in (0, 1)
                and r["outcome"] in (0, 1) and r["score"] is not None
                and r["pid"] is not None and r["admission_id"] is not None]
        for model, train_rows in (
            ("primary_only", [r for r in disease_rows if r["role"] == "train" and r["group"] == 0]),
            ("broad", [r for r in disease_rows if r["role"] == "train" and r["group"] in (0, 1)]),
        ):
            train = [r for r in train_rows if r["outcome"] in (0, 1) and r["score"] is not None
                     and r["pid"] is not None and r["admission_id"] is not None]
            support = {int(r["score"]) for r in train}
            for label, group in (("all", None), ("primary", 0), ("never_primary", 1)):
                target = [r for r in test if group is None or r["group"] == group]
                outside = [r for r in target if int(r["score"]) not in support]
                result.append({
                    "database": database,
                    "disease": disease,
                    "model_training_arm": model,
                    "test_group": label,
                    "train_records": len(train),
                    "train_patients": len({r["pid"] for r in train}),
                    "train_score_levels": ";".join(map(str, sorted(support))),
                    "test_records": len(target),
                    "test_records_outside_train_score_support": len(outside),
                    "test_patients_outside_train_score_support": len({r["pid"] for r in outside}),
                })
    return result


def count_flow(rows: list[dict[str, object]], database: str, split: dict[str, object]) -> dict[str, object]:
    target_rows = [r for r in rows if r["disease"] in DISEASES]
    result = {
        "database": database,
        "panel_rows": len(rows),
        "target_disease_rows": len(target_rows),
        "target_rows_with_patient_id": sum(r["pid"] is not None for r in target_rows),
        "target_rows_excluded_missing_patient_id": sum(r["pid"] is None for r in target_rows),
        "target_rows_with_admission_id": sum(r["admission_id"] is not None for r in target_rows),
        "target_rows_excluded_missing_admission_id": sum(r["admission_id"] is None for r in target_rows),
        "target_rows_with_both_identifiers": sum(r["pid"] is not None and r["admission_id"] is not None for r in target_rows),
        "target_rows_assigned_role": sum(r["role"] in ROLES for r in target_rows),
        "target_rows_excluded_or_unassigned": sum(r["role"] not in ROLES for r in target_rows),
        "target_group_unknown_rows": sum(r["group"] is None for r in target_rows),
        "target_outcome_unknown_rows": sum(r["outcome"] is None for r in target_rows),
        "target_score_incomplete_or_invalid_rows": sum(r["score"] is None for r in target_rows),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eicu-panel", type=Path, default=DEFAULT_EICU)
    parser.add_argument("--mimic-panel", type=Path, default=DEFAULT_MIMIC)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    panels = (("eICU", args.eicu_panel), ("MIMIC-IV", args.mimic_panel))
    all_counts: list[dict[str, object]] = []
    all_support: list[dict[str, object]] = []
    feasibility: dict[str, object] = {
        "seed": SEED,
        "role_hash_buckets": {"train": "0-59", "recalibration": "60-79", "test": "80-99"},
        "no_outcome_guided_split_or_model_choice": True,
        "model_fitting_performed": False,
        "panels": {},
        "flow_counts": [],
        "panel_assertions": {},
    }

    for database, path in panels:
        rows, qa = read_panel(path, database)
        split = assign_eicu(rows) if database == "eICU" else assign_mimic(rows)
        feasibility["panels"][database] = {"input_panel": str(path), **split}
        feasibility["panel_assertions"][database] = qa
        feasibility["flow_counts"].append(count_flow(rows, database, split))
        all_counts.extend(summarize_rows(rows, database))
        all_support.extend(score_support_counts(rows, database))

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / "eligibility_counts.csv"
    fields = list(all_counts[0]) if all_counts else []
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_counts)
    json_path = args.outdir / "split_feasibility.json"
    json_path.write_text(json.dumps(feasibility, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    support_path = args.outdir / "score_support_counts.csv"
    support_fields = list(all_support[0]) if all_support else []
    with support_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=support_fields)
        writer.writeheader()
        writer.writerows(all_support)
    print(f"Wrote aggregate eligibility counts: {csv_path}")
    print(f"Wrote split feasibility metadata: {json_path}")
    print(f"Wrote aggregate train/test score-support counts: {support_path}")
    print("No model was fitted; patient-level identifiers were not written.")


if __name__ == "__main__":
    main()

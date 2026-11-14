"""Freeze AmsterdamUMCdb qSOFA and NICE diagnosis mappings before outcomes."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "work" / "v2" / "sources" / "amsterdam_metadata"
WORK_DIR = ROOT / "work" / "v2" / "amsterdam"
OUT_DIR = ROOT / "outputs" / "v2" / "amsterdam"
LOCKED_AT_UTC = "2026-11-12T13:31:02Z"
SOURCE_COMMIT = "5422b94dbaba6c1d9b7c301f059c425ca1fc13ce"

RR_ITEMIDS = [8874, 12266, 12348, 8873, 16241, 12372, 7726, 8876, 9654, 12577, 13092, 14455, 16613]
SBP_ITEMIDS = [6641, 8841, 14056, 6678]
EXCLUDED_RR_ITEMIDS = [12322, 16248, 12385, 12283, 12287, 12558, 8850, 8853, 12384, 12303]
EXCLUDED_SBP_ITEMIDS = [6644, 8649, 12441]

GCS_MAP = {
    "eyes": {
        "6732": "5 - valueid",
        "13077": "valueid",
        "14470": "valueid - 4",
        "16628": "valueid - 4",
        "19635": "valueid - 4",
        "19638": "valueid - 8",
    },
    "motor": {
        "6734": "7 - valueid",
        "13072": "valueid",
        "14476": "valueid - 6",
        "16634": "valueid - 6",
        "19636": "valueid - 6",
        "19639": "valueid - 12",
    },
    "verbal": {
        "6735": "6 - valueid",
        "13066": "valueid",
        "14482": "valueid - 5",
        "16640": "valueid - 5",
        "19637": "valueid - 9",
        "19640": "valueid - 15",
    },
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dictionary_rows() -> list[dict[str, str]]:
    with (SOURCE_DIR / "dictionary.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def unique_descriptions(rows: list[dict[str, str]], itemids: list[int]) -> list[dict[str, str]]:
    wanted = {str(itemid) for itemid in itemids}
    values: dict[str, dict[str, str]] = {}
    for row in rows:
        if row.get("source_vocabulary_id") != "AUMC Numeric":
            continue
        itemid = row.get("source_code", "")
        if itemid not in wanted:
            continue
        candidate = {
            "itemid": itemid,
            "label": row.get("source_code_description", ""),
            "concept_id": row.get("concept_id", ""),
            "concept_name": row.get("concept_name", ""),
            "concept_code": row.get("concept_code", ""),
            "mapping_status": row.get("mapping_status", ""),
            "equivalence": row.get("equivalence", ""),
        }
        previous = values.get(itemid)
        if previous is not None and previous["label"] != candidate["label"]:
            raise ValueError(f"Conflicting dictionary labels for numeric item {itemid}")
        values[itemid] = candidate
    missing = wanted - values.keys()
    if missing:
        raise ValueError(f"No dictionary mapping for numeric itemids: {sorted(missing)}")
    return [values[itemid] for itemid in sorted(values, key=int)]


def diagnosis_values(rows: list[dict[str, str]], itemid: int) -> list[dict[str, str | int]]:
    prefix = f"{itemid}-"
    values: dict[int, dict[str, str | int]] = {}
    for row in rows:
        source_code = row.get("source_code", "")
        if row.get("source_vocabulary_id") != "AUMC Diagnosis" or not source_code.startswith(prefix):
            continue
        label = row.get("source_code_description", "")
        if "sepsis" not in label.casefold():
            continue
        valueid = int(source_code[len(prefix):])
        record = {"itemid": itemid, "valueid": valueid, "source_code": source_code, "label": label}
        previous = values.get(valueid)
        if previous is not None and previous["label"] != label:
            raise ValueError(f"Conflicting dictionary labels for diagnosis value {source_code}")
        values[valueid] = record
    return [values[key] for key in sorted(values)]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = dictionary_rows()
    primary = diagnosis_values(rows, 18671)
    secondary = diagnosis_values(rows, 18673)
    expected_primary = [34, 35, 36, 37, 38, 39, 40, 269, 270, 272, 274]
    expected_secondary = [486, 487, 489, 490, 491, 492, 721, 722, 724, 725]
    if [row["valueid"] for row in primary] != expected_primary:
        raise ValueError(f"Unexpected primary sepsis valueids: {primary}")
    if [row["valueid"] for row in secondary] != expected_secondary:
        raise ValueError(f"Unexpected secondary sepsis valueids: {secondary}")

    gcs_sql = WORK_DIR / "references" / "gcs.sql"
    reason_sql = WORK_DIR / "references" / "reason_for_admission.sql"
    sql_text = gcs_sql.read_text(encoding="utf-8")
    for itemid in (itemid for part in GCS_MAP.values() for itemid in part):
        if f"WHEN {itemid} THEN" not in sql_text:
            raise ValueError(f"GCS mapping itemid {itemid} not found in pinned SQL")

    numeric_maps = {
        "respiratory_rate": unique_descriptions(rows, RR_ITEMIDS),
        "systolic_blood_pressure": unique_descriptions(rows, SBP_ITEMIDS),
    }
    excluded_maps = {
        "respiratory_rate_excluded": unique_descriptions(rows, EXCLUDED_RR_ITEMIDS),
        "systolic_blood_pressure_excluded": unique_descriptions(rows, EXCLUDED_SBP_ITEMIDS),
    }
    lock = {
        "lock_status": "locked_before_outcome_join",
        "locked_at_utc": LOCKED_AT_UTC,
        "source": {
            "dataset": "AmsterdamUMCdb 1.0.2",
            "repository": "AmsterdamUMC/AmsterdamUMCdb",
            "commit": SOURCE_COMMIT,
            "dictionary_path": "work/v2/sources/amsterdam_metadata/dictionary.csv",
            "dictionary_sha256": sha256(SOURCE_DIR / "dictionary.csv"),
            "gcs_sql_path": "work/v2/amsterdam/references/gcs.sql",
            "gcs_sql_sha256": sha256(gcs_sql),
            "reason_for_admission_sql_path": "work/v2/amsterdam/references/reason_for_admission.sql",
            "reason_for_admission_sql_sha256": sha256(reason_sql),
        },
        "analysis_target": {
            "purpose": "supplementary qSOFA application to Amsterdam ICU records",
            "not_untouched_external_validation": True,
            "prior_aggregate_pilot_examined": True,
            "record_unit": "one ICU admission episode (admissionid)",
            "patient_cluster_field": "patientid",
            "primary_location": "admissions.location.str.contains('IC', na=False), matching the official SOFA notebook ICU stratum",
            "all_location_sensitivity": "If run, report ICU and MCU location groups separately; do not pool location labels silently",
            "target": "direct NICE APACHE IV sepsis diagnosis in primary or secondary diagnosis position",
            "diagnosis_source": "listitems",
            "primary_diagnosis_itemid": 18671,
            "primary_diagnosis_item_label": "NICE APACHEIV diagnosen",
            "secondary_diagnosis_itemid": 18673,
            "secondary_diagnosis_item_label": "NICE SEC APACHEIV diagnosen",
            "primary_sepsis_values": primary,
            "secondary_sepsis_values": secondary,
            "grouping": {
                "primary_sepsis": "primary valueid is in the locked primary set; takes precedence if both positions are sepsis",
                "secondary_only_sepsis": "secondary valueid is in the locked secondary set and primary valueid is not in the locked primary set",
                "both_positions_flag": "record both-position matches separately while assigning the primary group",
            },
        },
        "qsofa": {
            "time_origin": "admissions.admittedat for the ICU admission episode",
            "window_ms": {"lower_inclusive": 0, "upper_inclusive": 86400000},
            "stay_boundary": "exclude measurements after admissions.dischargedat",
            "temporal_summary": "worst observed component within the first 24 hours; component thresholds may occur at different times",
            "respiratory_rate_threshold": ">=22 per minute",
            "systolic_blood_pressure_threshold": "<=100 mmHg",
            "gcs_main_threshold": "<=13",
            "gcs_sensitivity_threshold": "<15",
            "main_score": "sum of three binary criteria using GCS <=13",
            "sensitivity_score": "sum of three binary criteria using GCS <15",
            "component_missingness": "score is missing unless RR, SBP and a complete same-time E/M/V GCS are each observed in-window",
            "gcs_source": "pinned Amsterdam legacy gcs.sql item/value transformations and provider/update priority; require complete E/M/V components at one measuredat",
            "gcs_valueid_to_component_score": GCS_MAP,
            "gcs_same_time_key": ["admissionid", "measuredat"],
            "gcs_same_time_provider_priority": [
                "ICV_Medisch Staflid", "ICV_Medisch", "ANES_Anesthesiologie",
                "ICV_Physician assistant", "ICH_Neurochirurgie",
                "ICV_IC-Verpleegkundig", "ICV_MC-Verpleegkundig", "all other providers",
            ],
            "gcs_tie_break_order": [
                "eyes provider rank", "motor provider rank", "verbal provider rank",
                "eyes updatedat descending", "motor updatedat descending", "verbal updatedat descending",
                "eyes score descending", "motor score descending", "verbal score descending",
            ],
            "gcs_verbal_floor": "as in official SQL, verbal_score values <1 are recoded to 1 before total GCS",
            "numeric_items": numeric_maps,
            "excluded_numeric_items": excluded_maps,
            "expected_units": {"respiratory_rate": "/min", "systolic_blood_pressure": "mmHg"},
            "numeric_value_handling": "require numeric values and expected units; no arbitrary outlier trimming; report observed extrema and invalid-unit/value counts",
            "excluded_rr_rule": "exclude ventilator set or backup rates, triggered-rate counts, and the SBI index; use direct measured total/spontaneous RR items only",
            "excluded_sbp_rule": "exclude pulmonary artery and IABP measurements; retain arterial, PiCCO arterial and non-invasive systemic SBP",
        },
        "outcome": {
            "field": "admissions.destination",
            "event_value": "Overleden",
            "label": "ICU/MCU discharge death",
            "missingness": "unknown or unrecognized destinations remain missing, not survival",
            "hospital_mortality_used": False,
            "pooled_with_hospital_mortality": False,
        },
        "reporting": {
            "primary_endpoint_scope": "ICU/MCU discharge mortality only",
            "no_pooled_main_study_estimate": True,
            "outcome_accessed_at_lock_time": False,
        },
    }
    lock_path = OUT_DIR / "mapping_lock.json"
    lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    codes_path = WORK_DIR / "sepsis_diagnosis_codes.csv"
    with codes_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["position", "itemid", "valueid", "source_code", "label"])
        writer.writeheader()
        writer.writerows([{"position": "primary", **row} for row in primary])
        writer.writerows([{"position": "secondary", **row} for row in secondary])
    print(json.dumps({"lock_path": str(lock_path.relative_to(ROOT)), "primary_codes": len(primary),
                      "secondary_codes": len(secondary), "rr_items": len(RR_ITEMIDS),
                      "sbp_items": len(SBP_ITEMIDS), "gcs_items": 18,
                      "lock_sha256": sha256(lock_path)}, indent=2))


if __name__ == "__main__":
    main()

import csv
import sys
from pathlib import Path

import pandas as pd
import pytest


WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))
import run_amsterdam_dictionary_unit_repair as repair  # noqa: E402


def _row(itemid, unit, *, status="APPROVED", equivalence="EQUAL"):
    return {
        "source_vocabulary_id": "AUMC Numeric Unit",
        "source_code": str(itemid),
        "source_code_description": f"item {itemid}",
        "concept_code": unit,
        "mapping_status": status,
        "equivalence": equivalence,
    }


def _real_dictionary_rows():
    path = WORK.parent / "sources" / "amsterdam_metadata" / "dictionary.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def test_locked_dictionary_maps_8874_to_approved_per_minute():
    rows = _real_dictionary_rows()
    unit_map, diagnostics = repair.build_dictionary_unit_map(rows, {8874})
    assert unit_map == {8874: "/min"}
    assert diagnostics["8874"]["status"] == "approved_equal_unique_unit"


def test_blank_event_unit_recovers_only_from_approved_dictionary():
    result = repair.resolve_unit_label("", 8874, "rr", {8874: "/min"})
    assert result["accepted"] is True
    assert result["unit_source"] == "dictionary"
    assert result["effective_unit"] == "/min"


def test_unknown_item_and_ambiguous_dictionary_do_not_impute():
    unknown = repair.resolve_unit_label(None, 999999, "rr", {})
    assert unknown["accepted"] is False
    assert unknown["reason"] == "missing_or_ambiguous_dictionary_unit"

    mapping, diagnostics = repair.build_dictionary_unit_map(
        [_row(8874, "/min"), _row(8874, "mmHg")], {8874}
    )
    assert mapping == {}
    assert diagnostics["8874"]["status"] == "ambiguous_approved_equal_mappings"


def test_explicit_conflict_is_never_overridden_by_dictionary():
    result = repair.resolve_unit_label("mmHg", 8874, "rr", {8874: "/min"})
    assert result["accepted"] is False
    assert result["reason"] == "explicit_event_unit_conflict"
    assert result["unit_source"] == "event_row"


def test_only_expected_component_units_are_compatible():
    assert repair.resolve_unit_label(None, 8874, "sbp", {8874: "/min"})["accepted"] is False
    assert repair.resolve_unit_label("/min", 8874, "rr", {8874: "/min"})["accepted"] is True
    assert repair.resolve_unit_label("mmHg", 6641, "sbp", {6641: "mmHg"})["accepted"] is True


def test_nonapproved_mapping_is_not_used():
    mapping, diagnostics = repair.build_dictionary_unit_map(
        [_row(8874, "/min", status="UNCHECKED", equivalence="UNREVIEWED")], {8874}
    )
    assert mapping == {}
    assert diagnostics["8874"]["status"] == "no_approved_equal_mapping"


def test_first_24h_window_inclusive_and_stay_bounded():
    admitted = 1_000_000.0
    assert repair.measurement_in_window(admitted, admitted, admitted + 86_400_000)
    assert repair.measurement_in_window(admitted + 86_400_000, admitted, admitted + 86_400_000)
    assert not repair.measurement_in_window(admitted - 1, admitted, admitted + 86_400_000)
    assert not repair.measurement_in_window(admitted + 86_400_001, admitted, admitted + 90_000_000)
    assert not repair.measurement_in_window(admitted + 50, admitted, admitted + 49)


def test_outcome_audit_wrapper_accepts_audit_v2_callable_and_crosschecks_direct_estimand():
    sys.path.insert(0, str(WORK.parent))
    sys.path.insert(0, str(WORK.parent / "audit"))
    from cohort_definition_audit import audit_v2

    rows = []
    for group in (0, 1):
        for score in (0, 1):
            for index in range(20):
                rows.append({
                    "patientid": f"p{group}_{score}_{index}",
                    "grp": group,
                    "icu_death": int(index % (3 if group else 4) == 0),
                    "qsofa_main": score,
                })
    panel = pd.DataFrame(rows)
    result, direct = repair.audit_frame(
        audit_v2, panel, "qsofa_main", "gcs_le_13",
        {"reps": 4, "seed": 42, "min_clusters": 20, "min_events": 10,
         "min_level_n": 20, "min_arm_n": 10, "min_usable_bootstrap": 1,
         "model_check": False},
    )

    assert result["api"] == "audit_v2"
    crosscheck = result["root_estimand_crosscheck"]
    assert crosscheck["crosscheck_passed"] is True
    assert crosscheck["estimate_matches_audit_at_reported_precision"] is True
    assert crosscheck["se_matches_audit_at_reported_precision"] is True
    assert crosscheck["estimate_pp"] == 100 * direct.estimate
    assert crosscheck["numerical_cluster_se_pp"] == 100 * direct.se

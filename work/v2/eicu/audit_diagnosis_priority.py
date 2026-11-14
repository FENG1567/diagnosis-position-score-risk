"""Aggregate QA of eICU diagnosispriority values; never writes row-level data."""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
WORK = Path(__file__).resolve().parent
EICU = Path(os.environ.get("EICU_ROOT", r"D:\数据库集合\eicu数据库"))
KNOWN = {"primary", "major", "other"}


def main() -> int:
    counts: Counter[str] = Counter()
    n_rows = 0
    for chunk in pd.read_csv(
        EICU / "diagnosis.csv.gz",
        compression="gzip",
        usecols=["diagnosispriority"],
        dtype={"diagnosispriority": "string"},
        chunksize=500_000,
    ):
        values = chunk["diagnosispriority"].fillna("").str.strip().str.casefold()
        counts.update(values.value_counts(dropna=False).to_dict())
        n_rows += len(chunk)

    missing = int(counts.get("", 0))
    unrecognized = int(sum(count for value, count in counts.items() if value and value not in KNOWN))
    issues = missing + unrecognized
    definitions = ("narrow", "broad", "legacy_v1")
    matching_issue_counts = {
        disease: {definition: 0 for definition in definitions}
        for disease in ("heart_failure", "pneumonia", "copd", "sepsis", "pancreatitis")
    } if issues == 0 else None

    result = {
        "source_table": str((EICU / "diagnosis.csv.gz").resolve()),
        "source_rows_scanned": int(n_rows),
        "priority_counts_normalized": dict(sorted(counts.items())),
        "recognized_priority_values": sorted(KNOWN),
        "missing_priority_rows": missing,
        "unrecognized_priority_rows": unrecognized,
        "matched_disease_priority_issue_rows": matching_issue_counts,
        "matched_disease_zero_basis": (
            "Exact zero: the full diagnosis table contains no missing or unrecognized priority values; "
            "every matched disease/code-list subset therefore contains zero such rows."
            if issues == 0 else None
        ),
        "by_index_24h_priority_issue_rows": matching_issue_counts if issues == 0 else None,
        "grouping_rule_change_required": bool(issues > 0),
    }

    path = WORK / "cache" / "eicu_diagnosis_priority_qa.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "source_rows_scanned": n_rows,
        "missing_priority_rows": missing,
        "unrecognized_priority_rows": unrecognized,
        "grouping_rule_change_required": bool(issues > 0),
        "aggregate_path": str(path.resolve()),
    }, indent=2))
    return 0 if issues == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

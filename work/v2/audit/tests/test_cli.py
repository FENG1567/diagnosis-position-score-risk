import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cohort_definition_audit import main


def test_cli_writes_structured_units_support_and_rule_metadata(tmp_path):
    rows = []
    for score in (0, 1):
        for definition, grp in (("1", 0), ("2", 1)):
            for j in range(40):
                outcome = int(j % (3 + score + grp) == 0)
                rows.append((f"{score}-{grp}-{j}", score, outcome, definition))
    input_path = tmp_path / "synthetic.csv"
    pd.DataFrame(rows, columns=["pid", "score", "outcome", "definition"]).to_csv(input_path, index=False)
    status = main([
        "--input", str(input_path), "--outdir", str(tmp_path / "out"),
        "--expected-levels", "0,1", "--reps", "20", "--min-usable-bootstrap", "1",
        "--min-events", "1", "--min-level-n", "2", "--min-arm-n", "2", "--min-clusters", "2",
    ])
    assert status == 0
    result = json.loads((tmp_path / "out" / "audit_metrics.json").read_text(encoding="utf-8"))
    assert result["metadata"]["row_unit"] == "admission"
    assert result["metadata"]["cluster_unit"] == "patient"
    assert result["metadata"]["weighting_unit"] == "record"
    assert result["metadata"]["missingness_assumption"] == "unknown"
    assert result["metadata"]["support_definition"] == "prespecified expected levels"
    assert result["rules"]["min_records_per_score_definition_cell"]["unit"] == "records"
    assert result["per_level"][0]["delta_ci_status"] == "computed"
    report = (tmp_path / "out" / "audit_report.md").read_text(encoding="utf-8")
    assert "covered 96.0-97.5% in simulation" not in report
    assert "covered 91.5-93.0% in simulation" not in report


def test_cli_maps_nullable_float_definition_and_preserves_missing_category(tmp_path):
    rows = []
    for definition in (1.0, 2.0):
        for j in range(40):
            outcome = int(j % (4 if definition == 1.0 else 3) == 0)
            rows.append((f"p-{definition}-{j}", 0, outcome, definition))
    rows.append(("missing-definition", 0, 0, np.nan))
    input_path = tmp_path / "nullable_definition.csv"
    pd.DataFrame(rows, columns=["pid", "score", "outcome", "definition"]).to_csv(input_path, index=False)
    outdir = tmp_path / "nullable_out"
    assert main([
        "--input", str(input_path), "--outdir", str(outdir), "--primary", "1", "--never", ">1",
        "--expected-levels", "0", "--reps", "20", "--min-usable-bootstrap", "1",
        "--min-events", "1", "--min-level-n", "2", "--min-arm-n", "2", "--min-clusters", "2",
    ]) == 0
    result = json.loads((outdir / "audit_metrics.json").read_text(encoding="utf-8"))
    assert result["flow"]["principal"] == 40
    assert result["flow"]["never-principal"] == 40
    assert result["flow"]["unclassified_definition_rows"] == 1
    assert any("definition column has missing values" in problem
               for problem in result["input_problems"])

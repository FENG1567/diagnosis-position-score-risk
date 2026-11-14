"""Synthetic smoke check for the frozen analysis and output table path."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
V2 = ROOT / "work" / "v2"
sys.path.insert(0, str(V2))
sys.path.insert(0, str(V2 / "ed_timing"))

from analyse_panels import analysis_frame, audit_module, audited, normalize_panel
from run_ed_timing import summary_and_level_rows


def main() -> None:
    event_counts = {(0, 0): 10, (0, 1): 15, (1, 0): 20, (1, 1): 30}
    rows = []
    admission = 0
    for score in (0, 1):
        for grp in (0, 1):
            for index in range(50):
                admission += 1
                rows.append({
                    "disease": "sepsis", "admission_id": admission, "hadm_id": admission,
                    "subject_id": admission, "pid": admission, "grp": grp,
                    "pos": 1 if grp == 0 else 2,
                    "died": int(index < event_counts[(score, grp)]), "qsofa": score,
                })
    fixture = pd.DataFrame(rows)
    fixture_dir = ROOT / "work" / "v2" / "ed_timing" / "runs"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="synthetic_smoke_", dir=fixture_dir) as temp_dir:
        panel_path = Path(temp_dir) / "synthetic_panel.csv"
        fixture.to_csv(panel_path, index=False)
        normalized = normalize_panel(panel_path)
        frame = analysis_frame(normalized, "qsofa")
        audit, direct = audited(audit_module(), frame, "synthetic fixture", "sepsis", "smoke")
        summary, per_level = summary_and_level_rows(
            audit, direct, frame, "sepsis", "smoke",
            "Synthetic full main cohort", "qsofa")

    assert isinstance(direct.levels, pd.DataFrame)
    assert len(direct.levels) == 2
    assert np.isclose(direct.estimate, 0.15)
    assert np.isclose(float(summary["delta_w_pp"]), 15.0)
    assert summary["estimand"] == "Delta_w record-weighted summary (never-primary minus primary)"
    weights = json.loads(summary["weight_by_score_level"])
    assert np.isclose(sum(weights.values()), 1.0)
    assert len(per_level) == 2
    assert all("delta_ci_status" in row and "risk_never_ci_status" in row for row in per_level)
    assert audit["interval_status"] == "computed"
    assert audit["delta_ci_pp"] is not None
    result = {
        "status": "passed",
        "fixture": "synthetic; no MIMIC row data read",
        "contrast_api_field": "Contrast.levels",
        "direct_delta_w_pp": float(summary["delta_w_pp"]),
        "score_levels": [float(value) for value in direct.levels["level"]],
        "score_level_row_count": len(per_level),
        "support_weights": weights,
        "c_state": summary["C_state"],
        "c_interval_status": audit["interval_status"],
        "normal_if_interval_pp": audit["delta_ci_pp"],
    }
    result_path = fixture_dir / "smoke_check_result.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

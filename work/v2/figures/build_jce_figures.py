"""Build the two JCE figures from revised v2 outputs with source-row traceability.

Figure 2 can be rendered immediately from the shared audit policy. Figure 1
requires finalized eICU and MIMIC-IV score-level inputs; the script refuses to
render it until both inputs and all four requested cells are present.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator, FuncFormatter
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "work" / "v2" / "figures"
OUT = ROOT / "outputs" / "v2" / "figures"
EICU_LEVELS_DEFAULT = ROOT / "outputs" / "v2" / "analysis" / "eicu" / "levels.csv"
EXPECTED_CELLS = (
    ("eICU-CRD", "sepsis"),
    ("eICU-CRD", "pneumonia"),
    ("MIMIC-IV", "sepsis"),
    ("MIMIC-IV", "pneumonia"),
)
BLUE = "#347DA3"
ORANGE = "#C47C39"
INK = "#30343B"
MID = "#68717B"
GRID = "#E6E8EA"
NULL_BAND = "#F0F1F2"
STATE_RED = "#F5E1DE"
STATE_RED_EDGE = "#A9655F"
STATE_AMBER = "#FFF1D1"
STATE_AMBER_EDGE = "#A28442"
STATE_GREEN = "#E0EEE9"
STATE_GREEN_EDGE = "#5E8E80"

mpl.rcParams.update({
    "font.family": "Arial",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "font.size": 7.5,
    "axes.labelsize": 7.5,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7.0,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.65,
    "lines.linewidth": 0.95,
    "legend.frameon": False,
    "savefig.dpi": 300,
})


class SourceConflictError(ValueError):
    """Raised when source interval availability contradicts its status fields."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def relative_label(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def save_pdf_png(fig, stem: str, width_mm: float, height_mm: float) -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / f"{stem}.pdf"
    svg = OUT / f"{stem}.svg"
    png = OUT / f"{stem}.png"
    fig.set_size_inches(width_mm / 25.4, height_mm / 25.4, forward=True)
    fig.savefig(pdf, facecolor="white", metadata={"Title": stem.replace("_", " ")})
    fig.savefig(svg, facecolor="white", metadata={"Title": stem.replace("_", " ")})
    fig.savefig(png, dpi=300, facecolor="white")
    plt.close(fig)
    return [
        {"file": pdf.name, "sha256": sha256_file(pdf), "format": "PDF", "editable_text": True},
        {"file": svg.name, "sha256": sha256_file(svg), "format": "SVG", "editable_text": True},
        {"file": png.name, "sha256": sha256_file(png), "format": "PNG", "dpi": 300},
    ]


def figure2_rows() -> list[dict]:
    shared = "work/v2/audit/cohort_definition_audit.py"
    runner = "work/v2/analyse_panels.py"
    protocol = "work/v2/audit/protocol.md"
    tests = "work/v2/audit/tests/test_regressions.py"
    return [
        {
            "order": 1,
            "stage": "Input contract and complete case",
            "criterion": ("Required fields present; patient identifiers present; binary outcome and 0/1 group. "
                          "Missing score, outcome, or group rows are counted and excluded from complete cases."),
            "pass_route": "Continue with the complete-case admission records.",
            "fail_route": "Invalid required input: not estimable; no point estimate or CI.",
            "source_trace": f"{shared}:validate,audit_v2; {runner}:analysis_frame",
        },
        {
            "order": 2,
            "stage": "Common score support",
            "criterion": "At least one score level is observed in both diagnosis groups.",
            "pass_route": "Continue to the point estimate on observed common support.",
            "fail_route": "No common support: not estimable; no point estimate or CI.",
            "source_trace": f"{shared}:audit,stratified_rd",
        },
        {
            "order": 3,
            "stage": "Observed-support point estimate",
            "criterion": "Compute the weighted summary Δ_w using pooled admission-record weights over the applicable support.",
            "pass_route": "Retain the point estimate while evaluating interval reportability.",
            "fail_route": ("If prespecified target support is lost, retain the observed-support point estimate "
                           "and withhold the population-target interval."),
            "source_trace": f"{shared}:audit,stratified_rd; {protocol}:support rule",
        },
        {
            "order": 4,
            "stage": "Deterministic interval gates",
            "criterion": ("≥20 records per score level; ≥10 records per score-by-definition cell; "
                          "≥20 distinct patients overall and per cell; every target cell has at least "
                          "one event and one non-event, checked from exact counts."),
            "pass_route": "Attempt the patient-cluster bootstrap.",
            "fail_route": "Retain the point estimate; withhold the CI.",
            "source_trace": f"{shared}:audit,per_level_inference; {protocol}:policy C",
        },
        {
            "order": 5,
            "stage": "Patient-cluster bootstrap",
            "criterion": ("Run 60 draws. A usable draw retains every score level and has ≥10 events "
                          "in each diagnosis definition across support; require ≥20 usable draws."),
            "pass_route": "Emit the point estimate and the v2 interval outputs.",
            "fail_route": "Retain the point estimate; withhold the CI.",
            "source_trace": f"{shared}:cluster_bootstrap,audit; {runner}:audited; {protocol}:policy C",
        },
        {
            "order": 6,
            "stage": "Executable regression evidence",
            "criterion": ("Focused cases cover prespecified support loss, exact event-count handling, "
                          "and per-level interval availability under a summary refusal."),
            "pass_route": "These tests support the displayed branch semantics.",
            "fail_route": "Not a separate patient outcome or causal pathway.",
            "source_trace": f"{tests}:test_prespecified_support_loss_*,test_exact_event_counts_*,test_per_level_intervals_*",
        },
    ]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No source rows supplied for {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def draw_box(ax, x, y, w, h, heading, body, face, edge, fontsize=7.0):
    ax.add_patch(Rectangle((x, y - h / 2), w, h, facecolor=face,
                           edgecolor=edge, linewidth=0.8, zorder=2))
    ax.text(x + 0.012, y + h * 0.25, heading, ha="left", va="center",
            fontsize=7.8, fontweight="bold", color=INK, zorder=3)
    ax.text(x + 0.012, y - h * 0.12, body, ha="left", va="center",
            fontsize=fontsize, color=INK, linespacing=1.25, zorder=3)


def draw_terminal(ax, x, y, w, h, heading, body, face, edge):
    ax.add_patch(Rectangle((x, y - h / 2), w, h, facecolor=face,
                           edgecolor=edge, linewidth=0.85, zorder=2))
    ax.text(x + w / 2, y + h * 0.27, heading, ha="center", va="center",
            fontsize=8.1, fontweight="bold", color=INK, zorder=3)
    ax.text(x + w / 2, y - h * 0.10, body, ha="center", va="center",
            fontsize=7.0, color=INK, linespacing=1.25, zorder=3)


def render_figure2() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = figure2_rows()
    source_csv = OUT / "fig2_audit_states_source.csv"
    write_csv(source_csv, rows)

    fig, ax = plt.subplots(figsize=(7.2047, 5.05))
    fig.subplots_adjust(left=0.018, right=0.99, bottom=0.025, top=0.91)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ax.text(0.025, 0.975, r"Audit reportability for weighted summary $\Delta_w$",
            fontsize=9.0, fontweight="bold", ha="left", va="top", color=INK)
    ax.text(0.025, 0.925,
            "Admission records are clustered by patient.",
            fontsize=7.2, ha="left", va="top", color=MID)

    x, w = 0.035, 0.555
    steps = [
        (0.835, 0.135, "1  Input contract and complete case",
         "Required score/outcome/group/ID fields; patient ID present; binary outcome; group 0/1.\nMissing score/outcome/group rows are counted, then excluded."),
        (0.645, 0.135, "2  Common score support",
         "At least one score level must occur in both groups."),
        (0.455, 0.135, "3  Point estimate",
         r"Compute weighted summary $\Delta_w$ on observed common support,"
         "\nusing pooled admission-record weights."),
        (0.255, 0.17, "4  Deterministic interval gates",
         "Records: ≥20 per score; ≥10 per score-by-definition cell.\n"
         "Patients: ≥20 distinct overall and per cell.\n"
         "Outcomes: each target cell has ≥1 event and ≥1 non-event."),
        (0.075, 0.14, "5  Patient-cluster bootstrap",
         "60 draws; usable if every score level remains and each definition has ≥10 events;\nrequire at least 20 usable draws."),
    ]
    for y, h, heading, body in steps:
        draw_box(ax, x, y, w, h, heading, body, "#F3F4F5", "#A9AFB7")

    # Main computation path.
    for y_from, y_to in ((0.7675, 0.7125), (0.5775, 0.5225),
                         (0.3875, 0.34), (0.17, 0.145)):
        ax.annotate("", xy=(x + w / 2, y_to), xytext=(x + w / 2, y_from),
                    arrowprops=dict(arrowstyle="-|>", color=MID, lw=0.8), zorder=4)

    # Three mutually legible terminal states.
    red_x, amber_x, green_x, terminal_w = 0.70, 0.70, 0.70, 0.275
    draw_terminal(ax, red_x, 0.825, terminal_w, 0.19,
                  "Not estimable", "No point estimate or CI\nInvalid required input or no shared score.",
                  STATE_RED, STATE_RED_EDGE)
    draw_terminal(ax, amber_x, 0.485, terminal_w, 0.275,
                  "Point estimate only", "No interval\nLost target support, a gate failure,\nor <20 usable bootstrap draws.\nIf target support is lost, retain the\nobserved-support point estimate.",
                  STATE_AMBER, STATE_AMBER_EDGE)
    draw_terminal(ax, green_x, 0.12, terminal_w, 0.17,
                  "Estimable", "Point estimate and 95% interval\nAll reportability gates pass.",
                  STATE_GREEN, STATE_GREEN_EDGE)

    # Input failure and absent common support lead to no estimate.
    ax.annotate("", xy=(red_x, 0.835), xytext=(x + w, 0.835),
                arrowprops=dict(arrowstyle="-|>", color=STATE_RED_EDGE, lw=0.85), zorder=4)
    ax.text(0.645, 0.856, "invalid", fontsize=7.0, color=STATE_RED_EDGE, ha="center")
    ax.plot([x + w, 0.64], [0.645, 0.645], color=STATE_RED_EDGE, lw=0.8, zorder=3)
    ax.plot([0.64, 0.64], [0.645, 0.825], color=STATE_RED_EDGE, lw=0.8, zorder=3)
    ax.annotate("", xy=(red_x, 0.815), xytext=(0.64, 0.815),
                arrowprops=dict(arrowstyle="-|>", color=STATE_RED_EDGE, lw=0.85), zorder=4)
    ax.text(0.626, 0.73, "no common support", fontsize=7.0, color=STATE_RED_EDGE,
            ha="right", va="center", rotation=90)

    # Any point-preserving refusal routes to the amber state. The vertical bus
    # is outside the terminal boxes, so its branches remain readable.
    amber_bus = 0.655
    for y in (0.455, 0.255, 0.075):
        ax.plot([x + w, amber_bus], [y, y], color=STATE_AMBER_EDGE, lw=0.8, zorder=3)
    ax.plot([amber_bus, amber_bus], [0.075, 0.485], color=STATE_AMBER_EDGE, lw=0.8, zorder=3)
    ax.annotate("", xy=(amber_x, 0.485), xytext=(amber_bus, 0.485),
                arrowprops=dict(arrowstyle="-|>", color=STATE_AMBER_EDGE, lw=0.85), zorder=4)
    ax.text(amber_bus - 0.008, 0.485, "withhold CI", fontsize=7.0,
            color=STATE_AMBER_EDGE, ha="right", va="bottom")

    # Passing every gate leads to the green state.
    ax.annotate("", xy=(green_x, 0.12), xytext=(x + w, 0.075),
                arrowprops=dict(arrowstyle="-|>", color=STATE_GREEN_EDGE, lw=0.9), zorder=4)
    ax.text(0.646, 0.103, "pass", fontsize=7.0, color=STATE_GREEN_EDGE, ha="center")

    outputs = save_pdf_png(fig, "fig2_audit_states", width_mm=183, height_mm=128)
    source_entry = {
        "role": "Figure 2 policy/source table",
        "file": source_csv.name,
        "sha256": sha256_file(source_csv),
        "rows": len(rows),
    }
    return {
        "state": "rendered",
        "claim": "The shared v2 audit separates no-point from point-only interval refusal.",
        "archetype": "process diagram",
        "width_mm": 183,
        "height_mm": 128,
        "outputs": outputs,
        "source_data": source_entry,
        "source_evidence": source_hashes(),
    }


FIG1_REQUIRED = {
    "database", "disease", "level", "n", "n_never", "n_primary",
    "events_never", "events_primary", "risk_never", "risk_primary", "diff_pp",
    "risk_never_ci_pp_lo", "risk_never_ci_pp_hi",
    "risk_primary_ci_pp_lo", "risk_primary_ci_pp_hi",
    "delta_ci_pp_lo", "delta_ci_pp_hi",
    "risk_never_ci_status", "risk_primary_ci_status", "delta_ci_status",
}


def validate_interval(row: pd.Series, estimate_col: str, lo_col: str, hi_col: str,
                      status_col: str, label: str) -> bool:
    status = str(row[status_col]).strip().casefold()
    if status in {"", "nan", "none", "<na>"}:
        raise SourceConflictError(f"{label}: interval status is missing")
    lo, hi = pd.to_numeric(row[lo_col], errors="coerce"), pd.to_numeric(row[hi_col], errors="coerce")
    estimate = pd.to_numeric(row[estimate_col], errors="coerce")
    has_bounds = bool(np.isfinite(lo) and np.isfinite(hi))
    if status == "computed":
        if not has_bounds:
            raise SourceConflictError(f"{label}: status is computed but interval bounds are missing")
        if lo > hi:
            raise SourceConflictError(f"{label}: lower interval bound exceeds upper bound")
        if not np.isfinite(estimate) or estimate < lo - 0.06 or estimate > hi + 0.06:
            raise SourceConflictError(f"{label}: source point estimate lies outside its reported interval")
        return True
    if has_bounds or np.isfinite(lo) != np.isfinite(hi):
        raise SourceConflictError(f"{label}: source bounds conflict with status {row[status_col]!r}")
    return False


def load_level_file(path: Path, role: str, expected_database: str) -> tuple[pd.DataFrame, dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Required finalized levels file not found for {role}: {path}")
    frame = pd.read_csv(path, low_memory=False)
    missing = sorted(FIG1_REQUIRED.difference(frame.columns))
    if missing:
        raise SourceConflictError(f"{role} levels file lacks required v2 interval/source fields: {missing}")
    frame["_source_row"] = np.arange(2, len(frame) + 2, dtype=int)
    frame["_source_role"] = role
    frame["_source_sha256"] = sha256_file(path)
    db = frame.database.astype("string").str.strip().str.casefold()
    disease = frame.disease.astype("string").str.strip().str.casefold()
    selected = frame.loc[db.eq(expected_database.casefold()) & disease.isin(["sepsis", "pneumonia"])].copy()
    if selected.empty:
        raise SourceConflictError(f"{role} file contains no requested {expected_database} sepsis/pneumonia rows")

    numeric = ["level", "n", "n_never", "n_primary", "events_never", "events_primary",
               "risk_never", "risk_primary", "diff_pp", "risk_never_ci_pp_lo",
               "risk_never_ci_pp_hi", "risk_primary_ci_pp_lo", "risk_primary_ci_pp_hi",
               "delta_ci_pp_lo", "delta_ci_pp_hi"]
    for col in numeric:
        selected[col] = pd.to_numeric(selected[col], errors="coerce")
    if selected.level.isna().any() or not np.allclose(selected.level, np.round(selected.level)):
        raise SourceConflictError(f"{role} score levels must be finite integer values")
    for col in ["n", "n_never", "n_primary", "events_never", "events_primary"]:
        if selected[col].isna().any() or (selected[col] < 0).any():
            raise SourceConflictError(f"{role} contains missing or negative source counts in {col}")
        if not np.allclose(selected[col], np.round(selected[col])):
            raise SourceConflictError(f"{role} source count {col} contains non-integer values")
    if not np.array_equal(selected.n.to_numpy(int),
                          (selected.n_never + selected.n_primary).to_numpy(int)):
        raise SourceConflictError(f"{role} total record count disagrees with group counts")
    if ((selected.events_never > selected.n_never) | (selected.events_primary > selected.n_primary)).any():
        raise SourceConflictError(f"{role} event count exceeds its group record count")
    if (selected.n_never.eq(0) | selected.n_primary.eq(0)).any():
        raise SourceConflictError(f"{role} includes a plotted score outside two-group support")
    for col in ("risk_never", "risk_primary", "diff_pp"):
        if selected[col].isna().any() or not np.isfinite(selected[col]).all():
            raise SourceConflictError(f"{role} contains a missing point estimate in {col}")
    if ((selected.risk_never < 0) | (selected.risk_never > 100) |
        (selected.risk_primary < 0) | (selected.risk_primary > 100)).any():
        raise SourceConflictError(f"{role} risk estimates must be on a 0–100 percent scale")
    rate_never = 100 * selected.events_never / selected.n_never
    rate_primary = 100 * selected.events_primary / selected.n_primary
    if (np.abs(rate_never - selected.risk_never) > 0.06).any() or \
       (np.abs(rate_primary - selected.risk_primary) > 0.06).any():
        raise SourceConflictError(f"{role} risk points disagree with source events and counts")
    if (np.abs(selected.diff_pp - (selected.risk_never - selected.risk_primary)) > 0.06).any():
        raise SourceConflictError(f"{role} diff_pp does not equal risk_never minus risk_primary")

    for _, row in selected.iterrows():
        label = f"{role} row {int(row._source_row)} level {row.level:g}"
        validate_interval(row, "risk_never", "risk_never_ci_pp_lo", "risk_never_ci_pp_hi",
                          "risk_never_ci_status", label + " never-primary risk CI")
        validate_interval(row, "risk_primary", "risk_primary_ci_pp_lo", "risk_primary_ci_pp_hi",
                          "risk_primary_ci_status", label + " primary risk CI")
        validate_interval(row, "diff_pp", "delta_ci_pp_lo", "delta_ci_pp_hi",
                          "delta_ci_status", label + " δ_s CI")

    duplicate = selected.duplicated(["database", "disease", "level"])
    if duplicate.any():
        raise SourceConflictError(f"{role} has duplicate database-disease-level rows")
    info = {
        "role": role,
        "display_name": f"{expected_database} score-level output",
        "sha256": sha256_file(path),
        "input_rows": int(len(frame)),
        "selected_rows": int(len(selected)),
        "excluded_rows": int(len(frame) - len(selected)),
        "exclusion_rule": f"Rows outside {expected_database} sepsis/pneumonia; no score-level rows excluded.",
        "path_label": relative_label(path),
    }
    return selected, info


def prepare_fig1_sources(eicu_path: Path, mimic_path: Path) -> tuple[pd.DataFrame, list[dict]]:
    eicu, eicu_info = load_level_file(eicu_path, "eICU source", "eICU-CRD")
    mimic, mimic_info = load_level_file(mimic_path, "MIMIC-IV source", "MIMIC-IV")
    combined = pd.concat([eicu, mimic], ignore_index=True)
    present = set(zip(combined.database.astype(str), combined.disease.astype(str).str.casefold()))
    missing_cells = [cell for cell in EXPECTED_CELLS if (cell[0], cell[1]) not in present]
    if missing_cells:
        raise SourceConflictError(f"Figure 1 needs all four database-condition cells; missing: {missing_cells}")
    source_rows = []
    for letter, (database, disease) in zip("abcd", EXPECTED_CELLS):
        panel = combined.loc[
            combined.database.astype(str).eq(database) &
            combined.disease.astype(str).str.casefold().eq(disease)
        ].sort_values("level")
        if panel.empty:
            raise SourceConflictError(f"Figure 1 panel {letter} has no score levels")
        for _, row in panel.iterrows():
            record = {
                "panel": letter,
                "database": database,
                "disease": disease,
                "source_role": row["_source_role"],
                "source_row": int(row["_source_row"]),
                "source_file_sha256": row["_source_sha256"],
            }
            for col in sorted(FIG1_REQUIRED - {"database", "disease"}):
                record[col] = row[col]
            record["risk_never_mark"] = "circle with source CI" if row.risk_never_ci_status == "computed" else "diamond, point only"
            record["risk_primary_mark"] = "square with source CI" if row.risk_primary_ci_status == "computed" else "diamond, point only"
            if row.delta_ci_status == "computed":
                record["delta_marker"] = "hollow circle; δ_s interval includes zero" if \
                    row.delta_ci_pp_lo <= 0 <= row.delta_ci_pp_hi else "filled circle; δ_s interval excludes zero"
            else:
                record["delta_marker"] = "diamond; point only, no interval"
            record["delta_null_band"] = bool(
                row.delta_ci_status == "computed" and row.delta_ci_pp_lo <= 0 <= row.delta_ci_pp_hi
            )
            source_rows.append(record)
    return combined, [eicu_info, mimic_info, source_rows]


def render_figure1(eicu_path: Path, mimic_path: Path) -> dict:
    combined, source_data = prepare_fig1_sources(eicu_path, mimic_path)
    eicu_info, mimic_info, source_rows = source_data
    source_csv = OUT / "fig1_score_specific_risk_source.csv"
    write_csv(source_csv, source_rows)

    fig = plt.figure(figsize=(7.2047, 6.72))
    outer = fig.add_gridspec(2, 2, left=0.09, right=0.985, top=0.865,
                             bottom=0.125, wspace=0.25, hspace=0.32)
    labels = "abcd"
    all_risk_values = []
    all_delta_values = []
    for _, row in combined.iterrows():
        all_risk_values.extend([float(row.risk_never), float(row.risk_primary)])
        for value_col, status_col in (("risk_never_ci_pp_hi", "risk_never_ci_status"),
                                      ("risk_primary_ci_pp_hi", "risk_primary_ci_status")):
            if str(row[status_col]).strip().casefold() == "computed":
                all_risk_values.append(float(row[value_col]))
        all_delta_values.append(abs(float(row.diff_pp)))
        if str(row.delta_ci_status).strip().casefold() == "computed":
            all_delta_values.extend([abs(float(row.delta_ci_pp_lo)), abs(float(row.delta_ci_pp_hi))])
    risk_ymax = min(100.0, max(10.0, math.ceil(max(all_risk_values) / 5.0) * 5.0 + 5.0))
    delta_lim_global = max(5.0, math.ceil(max(all_delta_values) / 5.0) * 5.0 * 1.12)
    for k, (database, disease) in enumerate(EXPECTED_CELLS):
        panel = combined.loc[
            combined.database.astype(str).eq(database) &
            combined.disease.astype(str).str.casefold().eq(disease)
        ].sort_values("level")
        grid = outer[k // 2, k % 2].subgridspec(
            3, 1, height_ratios=(3.1, 1.45, 1.05), hspace=0.12
        )
        ax_risk = fig.add_subplot(grid[0])
        ax_delta = fig.add_subplot(grid[1], sharex=ax_risk)
        ax_count = fig.add_subplot(grid[2], sharex=ax_risk)
        x = panel.level.to_numpy(float)
        null_levels = panel.loc[
            panel.delta_ci_status.astype(str).eq("computed") &
            panel.delta_ci_pp_lo.le(0) & panel.delta_ci_pp_hi.ge(0), "level"
        ].to_numpy(float)
        for ax in (ax_risk, ax_delta):
            for level in null_levels:
                ax.axvspan(level - 0.43, level + 0.43, color=NULL_BAND, zorder=0)
            ax.set_xlim(float(x.min()) - 0.5, float(x.max()) + 0.5)
            ax.set_xticks(x)

        group_specs = (
            ("risk_never", "risk_never_ci_pp_lo", "risk_never_ci_pp_hi",
             "risk_never_ci_status", BLUE, "o", -0.045, "Never-primary"),
            ("risk_primary", "risk_primary_ci_pp_lo", "risk_primary_ci_pp_hi",
             "risk_primary_ci_status", ORANGE, "s", 0.045, "Primary"),
        )
        for estimate_col, lo_col, hi_col, status_col, color, marker, offset, _label in group_specs:
            y = panel[estimate_col].to_numpy(float)
            ax_risk.plot(x + offset, y, color=color, linewidth=0.95, zorder=2)
            for (_, row), xv in zip(panel.iterrows(), x + offset):
                if str(row[status_col]).strip().casefold() == "computed":
                    lo, hi = float(row[lo_col]), float(row[hi_col])
                    ax_risk.errorbar(
                        [xv], [float(row[estimate_col])],
                        yerr=np.array([[max(0.0, float(row[estimate_col]) - lo)],
                                        [max(0.0, hi - float(row[estimate_col]))]]),
                        fmt="none", ecolor=color, elinewidth=0.75, capsize=1.8, capthick=0.75, zorder=2,
                    )
                    ax_risk.scatter([xv], [float(row[estimate_col])], marker=marker, s=22,
                                    facecolor=color, edgecolor=color, linewidth=0.65, zorder=3)
                else:
                    ax_risk.scatter([xv], [float(row[estimate_col])], marker="D", s=19,
                                    facecolor="white", edgecolor=color, linewidth=0.85, zorder=3)

        ax_risk.set_ylim(0, risk_ymax)
        ax_risk.yaxis.set_major_locator(MaxNLocator(4))
        ax_risk.set_ylabel("Observed risk (%)")
        ax_risk.tick_params(axis="x", labelbottom=False, width=0.6, length=2)
        ax_risk.set_title(f"{database} · {disease.capitalize()}", loc="left", pad=4)
        ax_risk.text(-0.145, 1.06, labels[k], transform=ax_risk.transAxes,
                     fontsize=8.5, fontweight="bold", va="bottom", color=INK)

        delta = panel.diff_pp.to_numpy(float)
        ax_delta.plot(x, delta, color=INK, linewidth=0.85, zorder=2)
        for _, row in panel.iterrows():
            xv, estimate = float(row.level), float(row.diff_pp)
            if str(row.delta_ci_status).strip().casefold() == "computed":
                lo, hi = float(row.delta_ci_pp_lo), float(row.delta_ci_pp_hi)
                ax_delta.errorbar([xv], [estimate],
                                  yerr=np.array([[max(0.0, estimate - lo)],
                                                 [max(0.0, hi - estimate)]]),
                                  fmt="none", ecolor=INK, elinewidth=0.8,
                                  capsize=2, capthick=0.8, zorder=2)
                includes_zero = lo <= 0 <= hi
                ax_delta.scatter([xv], [estimate], marker="o", s=23,
                                 facecolor="white" if includes_zero else INK,
                                 edgecolor=INK, linewidth=0.8, zorder=3)
            else:
                ax_delta.scatter([xv], [estimate], marker="D", s=21,
                                 facecolor=INK, edgecolor=INK, linewidth=0.7, zorder=3)
        ax_delta.axhline(0, color=MID, linestyle=(0, (3, 2)), linewidth=0.6, zorder=1)
        ax_delta.set_ylim(-delta_lim_global, delta_lim_global)
        ax_delta.yaxis.set_major_locator(MaxNLocator(4))
        ax_delta.set_ylabel(r"$\delta_s$ (pp)")
        ax_delta.tick_params(axis="x", labelbottom=False, width=0.6, length=2)

        n_never = panel.n_never.to_numpy(float)
        n_primary = panel.n_primary.to_numpy(float)
        ax_count.bar(x, n_never, width=0.62, color=BLUE, linewidth=0, zorder=2)
        ax_count.bar(x, n_primary, width=0.62, bottom=n_never,
                     color=ORANGE, linewidth=0, zorder=2)
        count_max = float(np.max(n_never + n_primary))
        ax_count.set_ylim(0, max(1.0, count_max * 1.16))
        ax_count.yaxis.set_major_locator(MaxNLocator(3, integer=True))
        ax_count.yaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{int(value):,}"))
        ax_count.set_ylabel("Records")
        ax_count.set_xlabel("Integer score")
        ax_count.tick_params(width=0.6, length=2)
        ax_count.grid(axis="y", color=GRID, linewidth=0.45, zorder=0)

    handles = [
        Line2D([0], [0], color=BLUE, marker="o", markersize=3.8, label="Never-primary"),
        Line2D([0], [0], color=ORANGE, marker="s", markersize=3.8, label="Primary"),
        Line2D([0], [0], color=INK, marker="o", markerfacecolor="white",
               markersize=4, linestyle="none", label=r"$\delta_s$ CI includes zero"),
        Line2D([0], [0], color=MID, marker="D", markerfacecolor="white",
               markersize=3.8, linestyle="none", label="Point estimate only"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.58, 0.967),
               ncol=4, handlelength=1.35, columnspacing=1.0, borderaxespad=0.0)
    fig.text(0.09, 0.975, "Score-specific observed risks and differences",
             fontsize=9.0, fontweight="bold", ha="left", va="top", color=INK)
    fig.text(0.09, 0.035,
             "Whiskers show pointwise 95% patient-cluster intervals. Gray bands and open markers identify score-specific intervals containing zero.\n"
             "Diamonds identify point-only output. The record-weighted summary Δ_w is reported in Table 2.",
             fontsize=7.0, ha="left", va="bottom", color=INK, linespacing=1.35)

    outputs = save_pdf_png(fig, "fig1_score_specific_risk", width_mm=183, height_mm=171)
    return {
        "state": "rendered",
        "claim": "Observed mortality risk and δ_s vary across shared integer score levels.",
        "archetype": "quantitative 2-by-2 grid",
        "panel_order": [f"{db} / {disease}" for db, disease in EXPECTED_CELLS],
        "width_mm": 183,
        "height_mm": 171,
        "outputs": outputs,
        "source_data": {
            "file": source_csv.name,
            "sha256": sha256_file(source_csv),
            "rows": len(source_rows),
            "inputs": [eicu_info, mimic_info],
        },
    }


def source_hashes() -> list[dict]:
    items = [
        ("shared audit implementation", "work/v2/audit/cohort_definition_audit.py"),
        ("analysis wrapper policy values", "work/v2/analyse_panels.py"),
        ("frozen policy protocol", "work/v2/audit/protocol.md"),
        ("frozen policy configuration", "work/v2/audit/benchmark_config.json"),
        ("regression cases", "work/v2/audit/tests/test_regressions.py"),
    ]
    return [
        {"role": role, "file": rel, "sha256": sha256_file(ROOT / rel)}
        for role, rel in items
    ]


def write_captions(figures: dict) -> None:
    lines = ["# Figure captions", ""]
    if figures.get("fig1_score_specific_risk", {}).get("state") == "rendered":
        lines += [
            "**Figure 1 | Score-specific observed risks and differences by diagnosis position.** Rows show eICU-CRD and MIMIC-IV. Columns show sepsis and pneumonia. Top panels show observed in-hospital mortality risk per admission record for never-primary and primary groups, with group-specific 95% patient-cluster intervals where issued. Middle panels show `δ_s = risk_never,s − risk_primary,s` in percentage points with score-specific 95% intervals. Gray score bands and open `δ_s` markers identify intervals containing zero. Diamonds identify point-only output. Bottom panels show stacked admission-record counts by diagnosis position. Each score has separately evaluated group-risk and `δ_s` interval gates. Intervals are pointwise. The record-weighted summary `Δ_w` appears in Table 2. The accompanying source table links every plotted score level to its source CSV row.",
            "",
        ]
    else:
        lines += ["Figure 1 is not rendered until finalized eICU and MIMIC-IV score-level files are both supplied.", ""]
    if figures.get("fig2_audit_states", {}).get("state") == "rendered":
        lines += [
            "**Figure 2 | Reportability flow for the record-weighted summary `Δ_w` under the audit policy.** The audit validates required fields and forms a complete-case analysis set, then checks common score support and computes an observed-support point estimate. Prespecified target-support loss retains that observed-support point and withholds the target interval. Interval gates require at least 20 records per score level, 10 records and 20 distinct patients per score-by-definition cell, 20 distinct patients overall, and nondegenerate outcomes in every target cell. The patient-cluster bootstrap uses 60 draws. A usable draw retains every target score level and has at least 10 events in each definition. At least 20 usable draws are required. Invalid required input or absent common support yields the not-estimable state. Other failed interval gates retain the point estimate and withhold interval output. Arrows describe the software decision sequence. The accompanying source table records the exact rule and source trace for each step.",
            "",
        ]
    lines += ["## Source-row trace", "", "Figure 2 is a policy diagram and has no patient-level source rows. Its rule text is traced in `fig2_audit_states_source.csv`. Figure 1 row references and input hashes are stored in `fig1_score_specific_risk_source.csv` when both inputs are available.", ""]
    (OUT / "figure_captions.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(figures: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "package": "JCE v2 manuscript figures",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "backend": "Python / matplotlib",
        "python": sys.version,
        "matplotlib": mpl.__version__,
        "pandas": pd.__version__,
        "font": "Arial",
        "page_width_mm": 183,
        "pdf_text": "TrueType text, editable",
        "png_dpi": 300,
        "display_cap": {"figures": 2, "tables": 6},
        "figures": figures,
        "generator": {
            "file": "work/v2/figures/build_jce_figures.py",
            "sha256": sha256_file(Path(__file__)),
            "contract_file": "work/v2/figures/figure_contract.md",
            "contract_sha256": sha256_file(WORK / "figure_contract.md"),
            "entrypoints": [
                {"file": "work/v2/figures/figure1_score_specific_risk.py",
                 "sha256": sha256_file(WORK / "figure1_score_specific_risk.py")},
                {"file": "work/v2/figures/figure2_audit_states.py",
                 "sha256": sha256_file(WORK / "figure2_audit_states.py")},
            ],
        },
        "integrity_notes": [
            "No simulated quantitative data are used.",
            "Figure 1 intervals are read from source status and bound fields; the plotting script does not calculate intervals.",
            "Score levels outside the four requested panels are excluded by the stated database-condition filter and counted in source metadata.",
            "Figure 2 branches reproduce the shared v2 code and frozen policy; arrows are computational only.",
        ],
    }
    preflight = OUT / "figure_source_preflight.json"
    if preflight.is_file():
        manifest["source_preflight"] = {"file": preflight.name, "sha256": sha256_file(preflight)}
    qa_notes = OUT / "figure_qa.md"
    if qa_notes.is_file():
        manifest["qa_notes"] = {"file": qa_notes.name, "sha256": sha256_file(qa_notes)}
    path = OUT / "figure_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "figure_manifest.sha256").write_text(f"{sha256_file(path)}  {path.name}\n", encoding="ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure1", action="store_true", help="render Figure 1; requires both finalized level files")
    parser.add_argument("--figure2", action="store_true", help="render Figure 2 from the shared audit policy")
    parser.add_argument("--eicu-levels", type=Path, default=EICU_LEVELS_DEFAULT)
    parser.add_argument("--mimic-levels", type=Path, help="finalized MIMIC-IV levels.csv path supplied by the analysis owner")
    args = parser.parse_args()
    if not args.figure1 and not args.figure2:
        args.figure2 = True

    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "figure_manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    figures = dict(existing.get("figures", {}))
    if args.figure2:
        figures["fig2_audit_states"] = render_figure2()
    if args.figure1:
        if args.mimic_levels is None:
            raise ValueError("Figure 1 requires --mimic-levels with the finalized MIMIC-IV levels file")
        figures["fig1_score_specific_risk"] = render_figure1(args.eicu_levels, args.mimic_levels)
    elif "fig1_score_specific_risk" not in figures:
        figures["fig1_score_specific_risk"] = {
            "state": "awaiting finalized eICU and MIMIC-IV level inputs",
            "required_cells": [f"{db} / {disease}" for db, disease in EXPECTED_CELLS],
            "outputs": [],
        }
    write_captions(figures)
    write_manifest(figures)
    print(json.dumps({
        "figures": {key: value.get("state") for key, value in figures.items()},
        "output_dir": relative_label(OUT),
        "manifest_sha256": sha256_file(OUT / "figure_manifest.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

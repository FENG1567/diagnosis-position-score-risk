from __future__ import annotations

import argparse
import csv
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

GRAY = "#D9D9D9"
HEADER_FILL = "#E7E6E6"
GROUP_FILL = "#F2F2F2"
INK = "#202020"


@dataclass
class Cell:
    text: str
    source_row: str
    source_columns: str
    transformation: str = "copied"
    numeric_check: str = "not_required"


@dataclass
class OutputRow:
    cells: list[Cell]
    is_group: bool = False
    group_sources: list[tuple[int, list[str]]] | None = None


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return reader.fieldnames, list(reader)


def markdown_metadata(path: Path) -> dict[int, tuple[str, list[str]]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    result: dict[int, tuple[str, list[str]]] = {}
    for table_no in range(1, 7):
        heading_match = re.compile(rf"^## Table {table_no}\.\s*(.*?)\s*$")
        start = next((i for i, line in enumerate(lines) if heading_match.match(line)), None)
        if start is None:
            raise ValueError(f"Could not find Table {table_no} heading in {path}")
        title = heading_match.match(lines[start]).group(1)
        stop = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## Table ")), len(lines))
        section = lines[start + 1:stop]
        try:
            notes_at = next(i for i, line in enumerate(section) if line.strip() == "**Notes.**")
        except StopIteration as e:
            raise ValueError(f"Could not find Notes for Table {table_no}") from e
        notes: list[str] = []
        for line in section[notes_at + 1:]:
            if line.startswith("## Table "):
                break
            m = re.match(r"^\s*-\s+(.*)$", line)
            if m:
                notes.append(m.group(1).strip())
        if not notes:
            raise ValueError(f"No note bullets found for Table {table_no}")
        result[table_no] = (title, notes)
    return result


def humanize(text: str) -> str:
    return text.replace("_", " ")


def cell(value: str, row: int, cols: str | Iterable[str], transform: str = "copied", numeric_check: str = "not_required") -> Cell:
    if isinstance(cols, str):
        cols = [cols]
    return Cell(humanize(value), str(row), " | ".join(cols), transform, numeric_check)


def arrow_counts(value: str) -> list[int]:
    # Parse eligible -> complete (excluded) -> shared (outside-support).
    pattern = re.compile(
        r"^\s*([\d,]+)\s*→\s*([\d,]+)\s*\(([\d,]+)\s+excluded\)\s*→\s*([\d,]+)\s*\(([\d,]+)\s+outside support\)\s*$"
    )
    match = pattern.match(value)
    if not match:
        raise ValueError(f"Unexpected Table 2 arm counts: {value!r}")
    values = [int(part.replace(",", "")) for part in match.groups()]
    eligible, complete, incomplete, shared, outside = values
    if eligible - complete != incomplete or complete - shared != outside:
        raise ValueError(f"Table 2 count conservation failed: {value!r}")
    return values


def choose_column(row: dict[str, str], aliases: list[str], table_no: int, label: str) -> str:
    for name in aliases:
        if name in row:
            return name
    raise ValueError(f"Table {table_no} is missing the {label} source column; accepted names: {aliases}")


def make_table_rows(table_no: int, headers: list[str], rows: list[dict[str, str]]) -> tuple[list[str], list[OutputRow]]:
    provenance_columns: dict[str, list[str]] = {}
    output_headers: list[str]
    output: list[OutputRow] = []

    if table_no == 1:
        required = ["Database", "Condition", "Instrument", "Score level", "Total supported records",
                    "Never-primary records / patients", "Never-primary deaths / risk (95% CI; status)",
                    "Primary records / patients", "Primary deaths / risk (95% CI; status)",
                    "δ_s (percentage points; 95% CI; status)", "Pooled observed record weight"]
        for col in required:
            if col not in headers:
                raise ValueError(f"Table 1 missing source field: {col}")
        output_headers = [
            "Database / condition / instrument", "Score level", "Total supported records",
            "Never-primary records / patients", "Never-primary deaths; risk (95% CI; status)",
            "Primary records / patients", "Primary deaths; risk (95% CI; status)",
            "δ_s (percentage points; 95% CI; status)", "Pooled observed record weight",
        ]
        previous = None
        grouped: list[tuple[tuple[str, str, str], list[tuple[int, dict[str, str]]]]] = []
        for i, row in enumerate(rows, start=2):
            key = (row["Database"], row["Condition"], row["Instrument"])
            if key != previous:
                grouped.append((key, []))
                previous = key
            grouped[-1][1].append((i, row))
        for (database, condition, instrument), group_rows in grouped:
            label = f"{database} · {condition} · {instrument}"
            trace_rows = [(i, ["Database", "Condition", "Instrument"]) for i, _ in group_rows]
            output.append(OutputRow([Cell(label, ";".join(str(i) for i, _ in group_rows),
                                                "Database | Condition | Instrument",
                                                "merged table section label from all source rows in group")],
                                    is_group=True, group_sources=trace_rows))
            for i, row in group_rows:
                combined = f"{row['Database']} · {row['Condition']} · {row['Instrument']}"
                values = [
                    cell(combined, i, ["Database", "Condition", "Instrument"], "combined label"),
                    cell(row["Score level"], i, "Score level"),
                    cell(row["Total supported records"], i, "Total supported records"),
                    cell(row["Never-primary records / patients"], i, "Never-primary records / patients"),
                    cell(row["Never-primary deaths / risk (95% CI; status)"], i, "Never-primary deaths / risk (95% CI; status)"),
                    cell(row["Primary records / patients"], i, "Primary records / patients"),
                    cell(row["Primary deaths / risk (95% CI; status)"], i, "Primary deaths / risk (95% CI; status)"),
                    cell(row["δ_s (percentage points; 95% CI; status)"], i, "δ_s (percentage points; 95% CI; status)"),
                    cell(row["Pooled observed record weight"], i, "Pooled observed record weight"),
                ]
                output.append(OutputRow(values))

    elif table_no == 2:
        output_headers = [
            "Source / condition / instrument",
            "Primary: eligible → complete (incomplete excluded) → shared; complete outside support",
            "Never-primary: eligible → complete (incomplete excluded) → shared; complete outside support",
            "Common-support score levels",
            "Computed δ_s CIs excluding zero / computed δ_s CIs",
            "Δ_w weighted summary (percentage points)",
            "95% patient-cluster CI for Δ_w weighted summary",
            "Summary interval status",
        ]
        arm_cols = [
            "Primary eligible → complete (incomplete excluded) → shared; complete outside support",
            "Never-primary eligible → complete (incomplete excluded) → shared; complete outside support",
        ]
        for i, row in enumerate(rows, start=2):
            combined = f"{row['Database']} · {row['Condition / instrument']}"
            out_cells = [cell(combined, i, ["Database", "Condition / instrument"], "combined label")]
            for col in arm_cols:
                raw = row[col]
                values = arrow_counts(raw)
                display_values = [int(part.replace(",", "")) for part in re.findall(r"[\d,]+", raw)]
                if values != display_values:
                    raise ValueError(f"Table 2 numeric equality failed at row {i}, {col}")
                out_cells.append(cell(raw, i, col, "parsed arrow-form counts; copied values; checked count conservation",
                                      "PASS: parsed source and displayed numeric values match"))
            summary_ci_col = choose_column(
                row,
                ["95% patient-cluster CI for Δ_w weighted summary", "95% patient-cluster CI for Δ_w"],
                2,
                "weighted-summary confidence interval",
            )
            other_cols = [
                "Common-support score levels",
                "Computed δ_s CIs excluding zero / computed δ_s CIs",
                "Δ_w weighted summary (percentage points)",
                summary_ci_col,
                "Summary interval status",
            ]
            out_cells.extend(cell(row[col], i, col, "underscore reasons converted to plain-language spaces" if "_" in row[col] else "copied")
                             for col in other_cols)
            output.append(OutputRow(out_cells))

    elif table_no == 3:
        output_headers = [
            "Analysis block / database", "Condition", "Records (patients)",
            "Narrow / score-only Δ_w weighted summary (percentage points)",
            "Broad / refined Δ_w weighted summary (percentage points)",
            "Paired difference (percentage points; numerical interval)",
            "Cell inventory / reconstruction", "Interval status",
        ]
        # Final table builds spell out the estimand; preview CSVs use the shorter legacy headers.
        narrow_col = choose_column(row=rows[0], aliases=[
            "Narrow / score-only Δ_w weighted summary",
            "Narrow / score-only Δ_w",
        ], table_no=3, label="narrow weighted summary") if rows else "Narrow / score-only Δ_w weighted summary"
        broad_col = choose_column(row=rows[0], aliases=[
            "Broad / refined Δ_w weighted summary",
            "Broad / refined Δ_w",
        ], table_no=3, label="broad weighted summary") if rows else "Broad / refined Δ_w weighted summary"
        grouped: list[tuple[tuple[str, str], list[tuple[int, dict[str, str]]]]] = []
        for i, row in enumerate(rows, start=2):
            key = (row["Analysis block"], row["Database"])
            if not grouped or grouped[-1][0] != key:
                grouped.append((key, []))
            grouped[-1][1].append((i, row))
        for (block, database), group_rows in grouped:
            label = f"{block} · {database}"
            output.append(OutputRow([Cell(label, ";".join(str(i) for i, _ in group_rows),
                                               "Analysis block | Database",
                                               "merged table section label from all source rows in group")], is_group=True))
            for i, row in group_rows:
                combined = f"{row['Analysis block']} · {row['Database']}"
                output.append(OutputRow([
                    cell(combined, i, ["Analysis block", "Database"], "combined label"),
                    cell(row["Condition"], i, "Condition"),
                    cell(row["Records (patients)"], i, "Records (patients)"),
                    cell(row[narrow_col], i, narrow_col),
                    cell(row[broad_col], i, broad_col),
                    cell(row["Paired difference (percentage points; numerical interval)"], i,
                         "Paired difference (percentage points; numerical interval)"),
                    cell(row["Cell inventory / reconstruction"], i, "Cell inventory / reconstruction"),
                    cell(row["Interval status"], i, "Interval status"),
                ]))

    elif table_no == 4:
        output_headers = [
            "Condition", "Grouping", "Records", "Patients", "Landmark-classifiable / reclassified records",
            "Δ_w weighted summary (percentage points)", "95% patient-cluster CI for Δ_w weighted summary", "Interval status",
        ]
        output = [OutputRow([cell(v, i, h, "underscore reasons converted to plain-language spaces" if "_" in v else "copied")
                             for h, v in row.items()]) for i, row in enumerate(rows, start=2)]

    elif table_no == 5:
        output_headers = headers
        output = [OutputRow([cell(v, i, h, "software separators changed from underscores to spaces" if "_" in v else "copied")
                             for h, v in row.items()]) for i, row in enumerate(rows, start=2)]

    elif table_no == 6:
        output_headers = headers
        output = [OutputRow([cell(v, i, h, "software separators changed from underscores to spaces" if "_" in v else "copied")
                             for h, v in row.items()]) for i, row in enumerate(rows, start=2)]
    else:
        raise ValueError(f"Unexpected table number {table_no}")

    return output_headers, output


def number_tokens(text: str) -> list[int | float]:
    # Use for the Table 2 parsed cells, where each displayed integer must match the source token.
    return [int(t.replace(",", "")) for t in re.findall(r"\d[\d,]*", text)]


def write_trace(trace_path: Path, table_trace: list[dict[str, str]]) -> None:
    with trace_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["table", "docx_row", "docx_column", "display_value", "source_file",
                                               "source_row", "source_columns", "transformation", "numeric_check"])
        writer.writeheader()
        writer.writerows(table_trace)


def render_table_html(table_no: int, title: str, notes: list[str], headers: list[str], rows: list[OutputRow],
                      widths: list[float], trace: list[dict[str, str]], source_file: str) -> str:
    if len(headers) != len(widths):
        raise ValueError(f"Table {table_no} has {len(headers)} headers but {len(widths)} widths")
    total_width = sum(widths)
    colgroup = "".join(f'<col style="width:{width / total_width * 100:.4f}%">' for width in widths)
    parts = [
        f'<h2 class="caption">Table {table_no}. {html.escape(title)}</h2>',
        f'<table class="main-table table-{table_no}"><colgroup>{colgroup}</colgroup><thead><tr>',
    ]
    for header in headers:
        parts.append(f'<th scope="col">{html.escape(header)}</th>')
    parts.append('</tr></thead><tbody>')

    data_row_index = 2
    for row in rows:
        if row.is_group:
            group = row.cells[0]
            parts.append(f'<tr class="group"><td colspan="{len(headers)}">{html.escape(group.text)}</td></tr>')
            trace.append({
                "table": str(table_no), "docx_row": str(data_row_index), "docx_column": "1",
                "display_value": group.text, "source_file": source_file, "source_row": group.source_row,
                "source_columns": group.source_columns, "transformation": group.transformation,
                "numeric_check": group.numeric_check,
            })
            data_row_index += 1
            continue

        if len(row.cells) != len(headers):
            raise ValueError(f"Table {table_no} row has {len(row.cells)} cells; expected {len(headers)}")
        pancreatitis = table_no == 2 and "pancreatitis" in row.cells[0].text.lower()
        parts.append('<tr>')
        for ci, source_cell in enumerate(row.cells):
            left_align = ci == 0 or (ci == len(headers) - 1 and table_no != 1)
            css_class = "left" if left_align else "center"
            value = html.escape(source_cell.text)
            if pancreatitis:
                value = f"<strong>{value}</strong>"
            parts.append(f'<td class="{css_class}">{value}</td>')
            trace.append({
                "table": str(table_no), "docx_row": str(data_row_index), "docx_column": str(ci + 1),
                "display_value": source_cell.text, "source_file": source_file,
                "source_row": source_cell.source_row, "source_columns": source_cell.source_columns,
                "transformation": source_cell.transformation, "numeric_check": source_cell.numeric_check,
            })
        parts.append('</tr>')
        data_row_index += 1

    parts.append('</tbody></table>')
    for note in notes:
        parts.append(f'<p class="note">• {html.escape(humanize(note))}</p>')
    return "\n".join(parts)


def document_html(tables_html: list[str], preview: bool) -> str:
    warning = (
        '<p class="preview">Preview for layout QA. Table 3 values predate the matched narrow and broad correction; they are not final results.</p>'
        if preview else ""
    )
    joined_tables = []
    for table_html in tables_html:
        if joined_tables:
            joined_tables.append('<div class="page-break"></div>')
        joined_tables.append(table_html)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Journal of Clinical Epidemiology Main Tables</title>
<style>
@page WordSection1 {{ size: 11in 8.5in; margin: 0.30in; mso-page-orientation: landscape; }}
div.WordSection1 {{ page: WordSection1; }}
body {{ margin: 0; padding: 0; color: {INK}; font-family: Arial, sans-serif; font-size: 8pt; }}
p.MsoTitle {{ mso-style-name: "Title"; mso-style-next: Normal; margin: 0 0 4pt 0; padding: 0; border: none; font-family: Arial, sans-serif; font-size: 15pt; font-weight: bold; color: #000000; }}
p.preview {{ margin: 0 0 5pt 0; font-size: 8pt; font-style: italic; }}
h2.caption {{ margin: 1pt 0 4pt 0; padding: 0; border: none; page-break-after: avoid; font-family: Arial, sans-serif; font-size: 10.5pt; font-weight: bold; color: {INK}; }}
table.main-table {{ width: 100%; table-layout: fixed; border-collapse: collapse; margin: 0; page-break-inside: auto; }}
table.main-table thead {{ display: table-header-group; }}
table.main-table tr {{ page-break-inside: avoid; }}
table.main-table th, table.main-table td {{ border: 0.5pt solid {GRAY}; padding: 2pt 3pt; font-family: Arial, sans-serif; font-size: 8pt; line-height: 1.0; vertical-align: middle; word-wrap: break-word; overflow-wrap: anywhere; }}
table.main-table th {{ background: {HEADER_FILL}; font-weight: bold; text-align: center; }}
table.main-table td.left {{ text-align: left; }}
table.main-table td.center {{ text-align: center; }}
table.main-table tr.group td {{ background: {GROUP_FILL}; font-weight: bold; text-align: left; }}
p.note {{ margin: 1pt 0 2pt 0; padding: 0; font-family: Arial, sans-serif; font-size: 8pt; line-height: 1.0; }}
div.page-break {{ page-break-before: always; break-before: page; height: 0; margin: 0; padding: 0; }}
</style>
</head>
<body>
<div class="WordSection1">
<p class="MsoTitle">Journal of Clinical Epidemiology Main Tables</p>
{warning}
{chr(10).join(joined_tables)}
</div>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare validated HTML and provenance for WPS-authored six-table DOCX export.")
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--html-output", required=True, type=Path)
    parser.add_argument("--trace", required=True, type=Path)
    parser.add_argument("--qa-json", required=True, type=Path)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    md_path = input_dir / "tables_v2.md"
    metadata = markdown_metadata(md_path)
    table_sources: dict[int, tuple[Path, list[str], list[dict[str, str]]]] = {}
    built_rows: dict[int, list[OutputRow]] = {}
    built_headers: dict[int, list[str]] = {}
    for table_no in range(1, 7):
        source = input_dir / f"t{table_no}.csv"
        source_headers, source_rows = read_csv(source)
        headers, out_rows = make_table_rows(table_no, source_headers, source_rows)
        table_sources[table_no] = (source, source_headers, source_rows)
        built_headers[table_no] = headers
        built_rows[table_no] = out_rows

    if not args.preview and len(table_sources[2][2]) != 19:
        raise ValueError("Final mode requires exactly 19 Table 2 rows; use --preview for incomplete input.")

    # Check every transformed Table 2 arrow cell before any file is written.
    for row in built_rows[2]:
        for c in row.cells[1:3]:
            if c.numeric_check.startswith("PASS"):
                raw_idx = int(c.source_row) - 2
                source_rows = table_sources[2][2]
                src = source_rows[raw_idx][c.source_columns]
                expected = arrow_counts(src)
                got = number_tokens(c.text)
                if expected != got:
                    raise ValueError(f"Numeric equality mismatch in table 2, source row {c.source_row}, {c.source_columns}: {expected} != {got}")

    widths_by_table = {
        1: [1.65, 0.42, 0.70, 0.98, 1.725, 0.98, 1.725, 1.48, 0.735],
        2: [1.05, 1.62, 1.62, 0.74, 1.02, 0.78, 1.18, 2.39],
        3: [1.45, 0.72, 1.03, 1.07, 1.07, 1.55, 1.60, 1.91],
        4: [0.95, 1.75, 0.72, 0.72, 1.25, 1.47, 1.55, 1.99],
        5: [1.08, 0.48, 0.72, 0.72, 0.78, 0.82, 1.16, 1.16, 1.27, 2.21],
        6: [1.08, 0.65, 0.95, 0.82, 0.82, 1.12, 1.05, 1.12, 1.17, 1.62],
    }
    trace: list[dict[str, str]] = []
    row_counts: dict[str, int] = {}
    tables_html: list[str] = []
    for table_no in range(1, 7):
        title, notes = metadata[table_no]
        source, source_headers, source_rows = table_sources[table_no]
        tables_html.append(render_table_html(table_no, title, notes, built_headers[table_no], built_rows[table_no],
                                             widths_by_table[table_no], trace, source.name))
        row_counts[str(table_no)] = len(source_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.html_output.parent.mkdir(parents=True, exist_ok=True)
    args.trace.parent.mkdir(parents=True, exist_ok=True)
    args.qa_json.parent.mkdir(parents=True, exist_ok=True)
    args.html_output.write_text(document_html(tables_html, bool(args.preview)), encoding="utf-8")
    write_trace(args.trace, trace)
    qa = {
        "input_directory": str(input_dir),
        "output_docx": str(args.output.resolve()),
        "html_source": str(args.html_output.resolve()),
        "authoring_runtime": "WPS Office (Kwps.Application); pending conversion step",
        "preview_mode": bool(args.preview),
        "table_source_row_counts": row_counts,
        "output_table_count": 6,
        "table2_numeric_equality_checks": sum(1 for r in built_rows[2] for c in r.cells if c.numeric_check.startswith("PASS")),
        "table2_numeric_equality_status": "PASS",
        "trace_rows": len(trace),
        "notes_per_table": {str(i): len(metadata[i][1]) for i in range(1, 7)},
        "table3_preview_status": "stale paired points; predates matched narrow/broad correction" if args.preview else "not marked as preview",
    }
    args.qa_json.write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=True))


if __name__ == "__main__":
    main()

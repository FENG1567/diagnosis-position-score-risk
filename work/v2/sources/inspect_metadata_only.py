#!/usr/bin/env python3
"""Read source metadata and CSV headers only; never scan patient rows.

The inventory records local schema evidence for candidate ICU sources. For
compressed tables this script reads only the first line (the column header).
It does not extract files, count records, or inspect clinical observations.
"""
from __future__ import annotations

import gzip
import json
import re
import zipfile
from pathlib import Path


WORKSPACE = Path(
    r"C:\Users\aaa12\Documents\Codex\2026-11-08\codex-journal-of-clinical-epidemiology-8"
)
RAW = Path(r"D:\数据库集合")
OUTPUT = WORKSPACE / "outputs" / "v2" / "sources" / "local_metadata_inventory.json"


def gzip_header(path: Path) -> list[str] | None:
    if not path.exists():
        return None
    with gzip.open(path, "rt", encoding="utf-8-sig", errors="replace") as stream:
        return next(stream, "").rstrip("\r\n").split(",")


def archive_gzip_header(archive: zipfile.ZipFile, member: str) -> list[str] | None:
    try:
        with archive.open(member) as compressed_member:
            with gzip.GzipFile(fileobj=compressed_member, mode="rb") as stream:
                return stream.readline().decode("utf-8-sig", errors="replace").rstrip("\r\n").split(",")
    except KeyError:
        return None


def archive_dictionary_matches(
    archive: zipfile.ZipFile, member: str, pattern: str
) -> list[dict[str, str]] | None:
    """Read named dictionary rows only (not clinical event tables)."""
    import csv

    try:
        with archive.open(member) as compressed_member:
            with gzip.GzipFile(fileobj=compressed_member, mode="rb") as stream:
                rows = csv.DictReader(
                    (line.decode("utf-8-sig", errors="replace") for line in stream)
                )
                return [
                    {k: v for k, v in row.items() if k in {"itemid", "label", "abbreviation", "category", "unitname"}}
                    for row in rows
                    if re.search(pattern, " ".join(str(v) for v in row.values()), re.I)
                ]
    except KeyError:
        return None


def archive_dictionary_preview(
    archive: zipfile.ZipFile, member: str, limit: int = 8
) -> list[dict[str, str]] | None:
    """Return a bounded preview of a named dictionary table only."""
    import csv

    try:
        with archive.open(member) as compressed_member:
            with gzip.GzipFile(fileobj=compressed_member, mode="rb") as stream:
                rows = csv.DictReader(
                    (line.decode("utf-8-sig", errors="replace") for line in stream)
                )
                preview = []
                for row in rows:
                    preview.append({k: str(v) for k, v in row.items()})
                    if len(preview) >= limit:
                        break
                return preview
    except KeyError:
        return None


result: dict[str, object] = {
    "scope": "metadata and first-line CSV headers only; no clinical records read",
    "accessed_utc_date": "2026-11-12",
    "sources": {},
}

# INSPIRE is already locally present. Schema/parameters are dictionaries; the
# diagnosis header is the only data-table content read, and no data rows follow.
inspire = RAW / "INSPIRE1.4.2数据库"
inspire_schema = inspire / "schema.csv"
inspire_parameters = inspire / "parameters.csv"
result["sources"]["INSPIRE 1.4.2"] = {
    "files_present": {
        "schema.csv": inspire_schema.exists(),
        "parameters.csv": inspire_parameters.exists(),
        "diagnosis.csv.gz": (inspire / "diagnosis.csv.gz").exists(),
        "operations.csv.gz": (inspire / "operations.csv.gz").exists(),
    },
    "table_headers": {
        "diagnosis.csv.gz": gzip_header(inspire / "diagnosis.csv.gz"),
        "operations.csv.gz": gzip_header(inspire / "operations.csv.gz"),
    },
}

# NWICU archive listing and table headers only. gzip streams stop after the
# header line; no record values are read.
nwicu_zip = RAW / "NWICU数据库" / "northwestern-icu-nwicu-database-0.1.0.zip"
nwicu_tables = (
    "nw_hosp/admissions.csv.gz",
    "nw_hosp/diagnoses_icd.csv.gz",
    "nw_hosp/patients.csv.gz",
    "nw_hosp/labevents.csv.gz",
    "nw_icu/icustays.csv.gz",
    "nw_icu/d_items.csv.gz",
    "nw_icu/chartevents.csv.gz",
)
nwicu_result: dict[str, object] = {
    "archive_present": nwicu_zip.exists(),
    "archive_bytes": nwicu_zip.stat().st_size if nwicu_zip.exists() else None,
    "table_headers": {},
    "dictionary_matches": {},
    "dictionary_previews": {},
}
if nwicu_zip.exists():
    with zipfile.ZipFile(nwicu_zip) as archive:
        names = archive.namelist()
        nwicu_result["archive_members"] = names
        for suffix in nwicu_tables:
            member = next((name for name in names if name.endswith(suffix)), None)
            nwicu_result["table_headers"][suffix] = (
                archive_gzip_header(archive, member) if member else None
            )
        for suffix, query in (
            ("nw_icu/d_items.csv.gz", r"respiratory rate|systolic blood pressure|glasgow coma|confusion"),
            ("nw_hosp/d_labitems.csv.gz", r"urea nitrogen|blood urea|bun"),
        ):
            member = next((name for name in names if name.endswith(suffix)), None)
            nwicu_result["dictionary_matches"][suffix] = (
                archive_dictionary_matches(archive, member, query) if member else None
            )
            nwicu_result["dictionary_previews"][suffix] = (
                archive_dictionary_preview(archive, member) if member else None
            )
result["sources"]["NWICU 0.1.0"] = nwicu_result

# Other candidates are represented as local-package presence only; their
# schemas were checked from cited official documentation and prior notes.
for label, relative, expected_file in (
    ("AmsterdamUMCdb 1.0.2", "Amsterdam数据库", "AmsterdamUMCdb-1.0.2数据集.7z"),
    ("SICdb 1.0.8", "SICdb数据库", "salzburg-intensive-care-database-sicdb-a-freely-accessible-intensive-care-database-1.0.8.rar"),
    ("HiRID 1.1.1", "HIRDI数据库", "hirid-a-high-time-resolution-icu-dataset-1.1.1.rar"),
):
    path = RAW / relative / expected_file
    result["sources"][label] = {
        "archive_present": path.exists(),
        "archive_bytes": path.stat().st_size if path.exists() else None,
        "archive_name": expected_file,
        "clinical_archive_opened": False,
    }

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\nWrote: {OUTPUT}")

"""Bounded eICU table pilot. Prints/writes aggregate metadata only."""
from __future__ import annotations
import json
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
EICU = Path(r"D:\数据库集合\eicu数据库")
OUT = ROOT / "outputs" / "v2" / "eicu"
WINDOW = (0, 1440)


def main() -> int:
    t0 = time.monotonic()
    p = pd.read_csv(EICU / "patient.csv.gz", compression="gzip", usecols=[
        "patientunitstayid", "patienthealthsystemstayid", "uniquepid", "hospitalid",
        "unitvisitnumber", "hospitaladmitoffset", "hospitaldischargestatus",
    ])
    p = p.dropna(subset=["patientunitstayid", "patienthealthsystemstayid"]).copy()
    p["patientunitstayid"] = pd.to_numeric(p["patientunitstayid"], errors="coerce")
    p["unitvisitnumber"] = pd.to_numeric(p["unitvisitnumber"], errors="coerce")
    p["hospitaladmitoffset"] = pd.to_numeric(p["hospitaladmitoffset"], errors="coerce")
    p = p.sort_values(
        ["patienthealthsystemstayid", "unitvisitnumber", "hospitaladmitoffset", "patientunitstayid"],
        ascending=[True, True, False, True], na_position="last", kind="mergesort"
    )
    idx = p.groupby("patienthealthsystemstayid", sort=False).head(1)
    ids = set(idx.patientunitstayid.astype("int64"))
    patient_summary = {
        "patient_rows": int(len(p)),
        "hospital_admissions": int(idx.patienthealthsystemstayid.nunique()),
        "icu_stays": int(p.patientunitstayid.nunique()),
        "multi_icu_admissions": int((p.groupby("patienthealthsystemstayid").size() > 1).sum()),
        "missing_unitvisitnumber": int(p.unitvisitnumber.isna().sum()),
        "missing_hospitaladmitoffset": int(p.hospitaladmitoffset.isna().sum()),
        "index_unique_pid": int(idx.uniquepid.notna().sum()),
        "index_hospitalid": int(idx.hospitalid.notna().sum()),
        "index_hospital_death_status": int(idx.hospitaldischargestatus.notna().sum()),
    }
    print("[pilot:index] " + json.dumps(patient_summary))
    specs = [
        ("vitalPeriodic.csv.gz", ["patientunitstayid", "observationoffset", "respiration", "temperature", "heartrate"], "vitalPeriodic"),
        ("vitalAperiodic.csv.gz", ["patientunitstayid", "observationoffset", "noninvasivesystolic", "noninvasivediastolic"], "vitalAperiodic"),
        ("nurseCharting.csv.gz", ["patientunitstayid", "nursingchartoffset", "nursingchartcelltypevallabel", "nursingchartcelltypevalname", "nursingchartvalue"], "nurseCharting"),
        ("lab.csv.gz", ["patientunitstayid", "labresultoffset", "labname", "labresult", "labmeasurenamesystem", "labmeasurenameinterface"], "lab"),
    ]
    summary = {"index": patient_summary, "pilot_rows_per_table": 250000, "tables": {}}
    for filename, cols, key in specs:
        rows = target = in_window = 0
        stay_ids = set()
        labels, roles, names, units = Counter(), Counter(), Counter(), Counter()
        for chunk in pd.read_csv(EICU / filename, compression="gzip", usecols=cols, chunksize=100000):
            remaining = 250000 - rows
            if len(chunk) > remaining:
                chunk = chunk.iloc[:remaining].copy()
            rows += len(chunk)
            sid = pd.to_numeric(chunk.patientunitstayid, errors="coerce")
            keep = sid.isin(ids)
            target += int(keep.sum())
            chunk = chunk.loc[keep].copy()
            off = "observationoffset" if key.startswith("vital") else "nursingchartoffset" if key == "nurseCharting" else "labresultoffset"
            chunk[off] = pd.to_numeric(chunk[off], errors="coerce")
            chunk = chunk.loc[chunk[off].between(*WINDOW)]
            in_window += int(len(chunk))
            stay_ids.update(pd.to_numeric(chunk.patientunitstayid, errors="coerce").dropna().astype(int).tolist())
            if key == "nurseCharting":
                lab = chunk.nursingchartcelltypevallabel.fillna("").astype(str)
                name = chunk.nursingchartcelltypevalname.fillna("").astype(str)
                mask = (lab + " " + name).str.contains(r"glasgow|gcs|confus|orientation|oriented|mental status", case=False, regex=True)
                for l, n in zip(lab[mask], name[mask]):
                    labels[(l[:100] + " | " + n[:100])] += 1
                    z = re.sub(r"[^a-z0-9]", "", (l + " " + n).lower())
                    role = "total" if ("gcs" in z or "glasgow" in z) and not any(x in z for x in ("eye", "motor", "verbal")) else next((x for x in ("eye", "motor", "verbal") if x in z), "mental_status")
                    roles[role] += 1
            if key == "lab":
                lab = chunk.labname.fillna("").astype(str)
                mask = lab.str.contains(r"\bbun\b|\burea\b", case=False, regex=True)
                for n in lab[mask]:
                    names[n[:100]] += 1
                for u in chunk.loc[mask, "labmeasurenamesystem"].fillna("").astype(str):
                    units[u[:80]] += 1
                for u in chunk.loc[mask, "labmeasurenameinterface"].fillna("").astype(str):
                    units[u[:80]] += 1
            if rows >= 250000:
                break
        table = {
            "sample_rows_read": rows,
            "sample_rows_matching_index_stays": target,
            "sample_rows_in_first24h": in_window,
            "index_stays_in_window": len(stay_ids),
        }
        if key == "nurseCharting":
            table["GCS_confusion_labels_top40"] = dict(labels.most_common(40))
            table["candidate_roles"] = dict(roles)
        if key == "lab":
            table["candidate_names_top30"] = dict(names.most_common(30))
            table["candidate_unit_names_top30"] = dict(units.most_common(30))
        summary["tables"][key] = table
        print(f"[pilot:{key}] " + json.dumps(table, ensure_ascii=False))
    summary["elapsed_seconds"] = round(time.monotonic() - t0, 2)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "eicu_v2_pilot_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[pilot] aggregate summary written; elapsed={summary['elapsed_seconds']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

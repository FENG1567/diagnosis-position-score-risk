"""Apply the audit to an explicitly adapted published pneumonia cohort.

The public study's diagnosis text and exclusion SQL define the population.
The present admission index and adapted CURB-65 remain those of Paper B.
This application does not reproduce the original model or its performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

from analyse_panels import audit_module, audited, clean_json, normalize_panel, summarize

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'work/v2/sources/public_code/hlzhou__peer-score/src/data_processing/eicu/eicu_extraction.sql'
SOURCE = Path('F:/分析专用/meta_measurement_20261103/incoming/eicu_diagnosis.csv.gz')
PRIVATE = Path('F:/分析专用/meta_measurement_20261103/work/paperB_v2/published_application')
OUT = ROOT / 'outputs/v2/published_application'


def quoted(block):
    return re.findall(r"'((?:[^']|'')*)'", block)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--eicu-panel', required=True)
    args = parser.parse_args()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    sql = CODE.read_text(encoding='utf-8')
    inclusion_block = re.search(r'WHERE diagnosisstring IN \((.*?)\)\s*\);', sql, flags=re.S).group(1)
    exception_block = re.search(r'AND \(diagnosisstring NOT IN \((.*?)\)\)\)', sql, flags=re.S).group(1)
    inclusion, hepatic_exceptions = quoted(inclusion_block), quoted(exception_block)
    if len(inclusion) < 10 or not hepatic_exceptions:
        raise ValueError('Published SQL parsing failed its expected structure.')
    configuration = dict(
        source_repository='https://github.com/hlzhou/peer-score',
        source_commit='bad2996b233cb118302d7453f6bb356e72912176',
        sql_sha256=hashlib.sha256(CODE.read_bytes()).hexdigest(),
        inclusion_diagnosis_strings=inclusion, hepatic_exceptions=hepatic_exceptions,
        age_range=[18, 70], source_diagnosis_scope='index ICU stay',
        adaptations=['first ICU per hospital admission', 'missing age excluded',
                     'complete-component CURB-65 with GCS<15 confusion proxy',
                     'no cohort median imputation', 'hospital death reconciled across linked ICU episodes'],
        comparison='never clinical Primary vs clinical Primary among matching published diagnosis rows',
        interpretation='published-cohort application, original PEER model and validation conclusions unreproduced')
    # Written before diagnosis selection or outcome comparisons in this application.
    (OUT / 'application_config.json').write_text(json.dumps(configuration, indent=2), encoding='utf-8')
    dx = pd.read_csv(SOURCE, usecols=['patientunitstayid', 'diagnosisstring', 'icd9code', 'diagnosispriority'],
                     dtype={'diagnosisstring': 'string', 'icd9code': 'string', 'diagnosispriority': 'string'})
    text = dx.diagnosisstring.fillna('')
    lower = text.str.lower()
    inclusion_mask = text.isin(inclusion)
    exclusion = (lower.str.contains('surgery', regex=False)
                 | lower.str.contains(r'neurologic.*stroke|cranial.*hemorrhage|cancer|tumor|lymphoma', regex=True)
                 | ((lower.str.contains('hepatic|hepatitis', regex=True)) & ~text.isin(hepatic_exceptions))
                 | lower.str.contains('liver disease|congestive heart failure', regex=True)
                 | (lower.str.contains('renal', regex=False) & ~lower.str.contains('adrenal', regex=False)
                    & dx.icd9code.fillna('').str.startswith('40')))
    included_ids = set(dx.loc[inclusion_mask, 'patientunitstayid'])
    excluded_ids = set(dx.loc[exclusion, 'patientunitstayid'])
    priority = dx.loc[inclusion_mask].assign(
        primary=lambda d: d.diagnosispriority.fillna('').str.strip().str.lower().eq('primary'))
    priority = priority.groupby('patientunitstayid').primary.max()
    panel = normalize_panel(args.eicu_panel)
    d = panel.loc[panel.disease.eq('pneumonia')].copy()
    id_column = 'index_patientunitstayid' if 'index_patientunitstayid' in d else 'patientunitstayid'
    d['application_eligible'] = d[id_column].isin(included_ids.difference(excluded_ids)) & d.age.between(18, 70)
    selected = d.loc[d.application_eligible].copy()
    selected['grp'] = selected[id_column].map(priority).map({True: 0, False: 1})
    selected['y'] = selected.died
    selected['score'] = selected.curb65
    analyzed = selected.dropna(subset=['pid', 'grp', 'y', 'score']).copy()
    selected.to_csv(PRIVATE / 'adapted_peer_population.csv.gz', index=False, compression='gzip')
    audit, direct = audited(audit_module(), analyzed, 'eICU-CRD', 'pneumonia', 'adapted published PEER population')
    summary = summarize(audit, direct, 'adapted published PEER population')
    summary.update(n_eligible=len(selected), n_complete=len(analyzed),
                   primary_eligible=int((selected.grp == 0).sum()), never_eligible=int((selected.grp == 1).sum()),
                   instrument='adapted CURB-65, same definition in both position groups')
    pd.DataFrame([summary]).to_csv(OUT / 'application_summary.csv', index=False)
    pd.DataFrame(audit.get('per_level', [])).to_json(OUT / 'application_levels.json', orient='records', indent=2)
    (OUT / 'audit_details.json').write_text(json.dumps(clean_json(audit), indent=2, allow_nan=False), encoding='utf-8')
    (OUT / 'provenance.json').write_text(json.dumps(dict(
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        config_sha256=hashlib.sha256((OUT / 'application_config.json').read_bytes()).hexdigest(),
        diagnosis_sha256=hashlib.file_digest(SOURCE.open('rb'), 'sha256').hexdigest(),
        panel_sha256=hashlib.file_digest(open(args.eicu_panel, 'rb'), 'sha256').hexdigest()), indent=2), encoding='utf-8')
    print(json.dumps(clean_json(summary), indent=2, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()

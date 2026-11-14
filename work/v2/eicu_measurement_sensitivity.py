"""Compare documented GCS sources and medication-unassessable flags."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

from analyse_panels import audit_module, audited, normalize_panel, summarize
from estimands import paired_difference

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / 'work/v2/eicu/eicu_disease_panel.csv.gz'
SOURCE = Path('D:/数据库集合/eicu数据库/apacheApsVar.csv.gz')
OUT = ROOT / 'outputs/v2/measurement_sensitivity'
PRIVATE = Path('F:/分析专用/meta_measurement_20261103/work/paperB_v2/measurement_sensitivity')


def add_score(data, name, components):
    block = data[components]
    data[name + '_lower'] = block.sum(axis=1)
    data[name + '_upper'] = data[name + '_lower'] + block.isna().sum(axis=1)
    data[name] = data[name + '_lower'].where(block.notna().all(axis=1))


def replace_mental_components(panel, gcs):
    data = panel.copy()
    data['gcs_used_for_sensitivity'] = gcs
    data['qsofa_gcs13_point'] = (gcs <= 13).astype(float).where(gcs.notna())
    data['qsofa_gcs15_point'] = (gcs < 15).astype(float).where(gcs.notna())
    data['curb65_confusion_proxy_point'] = data.qsofa_gcs15_point
    data['bisap_gcs_point'] = data.qsofa_gcs15_point
    add_score(data, 'qsofa', ['qsofa_rr_point', 'qsofa_sbp_point', 'qsofa_gcs13_point'])
    add_score(data, 'qsofa_gcs15', ['qsofa_rr_point', 'qsofa_sbp_point', 'qsofa_gcs15_point'])
    add_score(data, 'curb65', ['curb65_confusion_proxy_point', 'curb65_urea_point',
                               'curb65_rr_point', 'curb65_bp_point', 'curb65_age_point'])
    add_score(data, 'bisap4', ['bisap_bun_point', 'bisap_gcs_point',
                              'bisap_sirs_operationalized_point', 'bisap_age_point'])
    for score in ['qsofa', 'qsofa_gcs15', 'curb65', 'bisap4']:
        if score + '_score' in data:
            data[score + '_score'] = data[score]
    return data


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    config = dict(analysis='GCS measurement-source sensitivity after revised eICU primary results',
                  reference='https://eicu.mit.edu/eicutables/apacheapsvar/',
                  main='timed nursing GCS, original revised primary retained',
                  alternatives=['timed nursing GCS with APACHE meds1 made unassessable',
                                'valid APACHE GCS preferred, timed nursing fallback, meds1 unassessable'],
                  apache_gcs='all E/V/M components within documented valid ranges, meds!=1',
                  limitation='APACHE day summary has protocol timing rather than a retained event timestamp',
                  other_components='identical repaired timed physiology, diagnosis groups, admission unit and endpoint')
    (OUT / 'config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    panel = normalize_panel(PANEL)
    raw = pd.read_csv(SOURCE, usecols=['patientunitstayid', 'eyes', 'motor', 'verbal', 'meds'])
    if raw.patientunitstayid.duplicated().any():
        raise ValueError('APACHE summary has multiple records per ICU stay.')
    for column, maximum in [('eyes', 4), ('motor', 6), ('verbal', 5)]:
        raw[column] = pd.to_numeric(raw[column], errors='coerce').where(lambda x: x.between(1, maximum))
    raw['meds'] = pd.to_numeric(raw.meds, errors='coerce')
    raw['apache_gcs'] = raw[['eyes', 'motor', 'verbal']].sum(axis=1, min_count=3).where(raw.meds.ne(1))
    panel = panel.merge(raw[['patientunitstayid', 'meds', 'apache_gcs']].rename(
        columns={'patientunitstayid': 'index_patientunitstayid'}),
                        on='index_patientunitstayid', how='left', validate='many_to_one')
    nurse_gcs = panel.gcs_min
    no_meds_gcs = nurse_gcs.where(panel.meds.ne(1))
    hybrid_gcs = panel.apache_gcs.combine_first(no_meds_gcs).where(panel.meds.ne(1))
    panel['gcs_used_for_sensitivity'] = nurse_gcs
    variants = {'timed nursing GCS': panel,
                'timed GCS excluding meds1': replace_mental_components(panel, no_meds_gcs),
                'APACHE valid GCS with timed fallback': replace_mental_components(panel, hybrid_gcs)}
    rows, paired, flows, levels = [], [], [], []
    module = audit_module()
    for disease, score in [('sepsis', 'qsofa'), ('pneumonia', 'curb65'), ('pancreatitis', 'bisap4')]:
        original = variants['timed nursing GCS'].loc[lambda d: d.disease.eq(disease) & d.grp.notna()].copy()
        main_complete = original.loc[original[score].notna() & original.died.notna()].copy()
        for label, variant in variants.items():
            data = variant.loc[variant.disease.eq(disease) & variant.grp.notna()].copy()
            data['y'], data['score'] = data.died, data[score]
            complete = data.dropna(subset=['pid', 'grp', 'y', 'score']).copy()
            report, contrast = audited(module, complete, 'eICU-CRD', disease, label)
            rows.append(dict(database='eICU-CRD', disease=disease, **summarize(report, contrast, label)))
            flows.append(dict(disease=disease, analysis=label, eligible=len(data), complete=len(complete),
                              meds1=int(data.meds.eq(1).sum()), apache_gcs_valid=int(data.apache_gcs.notna().sum()),
                              original_timed_gcs_valid=int(data.gcs_min.notna().sum())))
            cells = complete.groupby(['score', 'grp']).agg(n=('y', 'size'), deaths=('y', 'sum')).reset_index()
            levels.extend(dict(disease=disease, analysis=label, **row) for row in cells.to_dict('records'))
            if label != 'timed nursing GCS':
                ids = set(main_complete.admission_id).intersection(complete.admission_id)
                a = main_complete.loc[main_complete.admission_id.isin(ids)].assign(
                    score=lambda d: d[score], y=lambda d: d.died)
                b = complete.loc[complete.admission_id.isin(ids)]
                _, ca = audited(module, a, 'eICU-CRD', disease, label + ' matched main')
                _, cb = audited(module, b, 'eICU-CRD', disease, label + ' matched alternative')
                change = paired_difference(ca, cb)
                paired.append(dict(disease=disease, alternative=label, n_matched=len(a),
                                   main_delta_w_pp=100 * ca.estimate, alternative_delta_w_pp=100 * cb.estimate,
                                   difference_pp=100 * change['difference'],
                                   numerical_lo_pp=100 * change['lo'], numerical_hi_pp=100 * change['hi'],
                                   estimand='difference between Delta_w weighted summaries on matched records',
                                   interval_status='descriptive paired influence interval'))
    for label, variant in variants.items():
        variant = variant.assign(gcs_sensitivity_variant=label)
        variant.to_csv(PRIVATE / (label.replace(' ', '_') + '.csv.gz'), index=False, compression='gzip')
    pd.DataFrame(rows).to_csv(OUT / 'weighted_summary_comparison.csv', index=False)
    pd.DataFrame(paired).to_csv(OUT / 'matched_record_comparison.csv', index=False)
    pd.DataFrame(flows).to_csv(OUT / 'measurement_selection.csv', index=False)
    pd.DataFrame(levels).to_csv(OUT / 'score_level_counts.csv', index=False)
    with SOURCE.open('rb') as stream:
        source_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
    provenance = dict(source_sha256=source_hash, panel_sha256=hashlib.sha256(PANEL.read_bytes()).hexdigest(),
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      config_sha256=hashlib.sha256((OUT / 'config.json').read_bytes()).hexdigest(),
                      dependencies=[dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                                    for path in [ROOT / 'work/v2/analyse_panels.py',
                                                 ROOT / 'work/v2/estimands.py',
                                                 ROOT / 'work/v2/audit/cohort_definition_audit.py']])
    (OUT / 'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(pd.DataFrame(rows).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()

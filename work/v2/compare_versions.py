"""Separate record restriction, observed-field completeness and source repair."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analyse_panels import normalize_panel
from estimands import direct_contrast, paired_difference

PROJECT = Path('F:/分析专用/meta_measurement_20261103')


def key(values):
    return values.astype('string').str.replace(r'\.0$', '', regex=True)


def old_panel(database):
    name = 'eicu' if database == 'eICU-CRD' else 'mimic'
    d = pd.read_csv(PROJECT / f'incoming/{name}_score_panel.csv.gz')
    if name == 'eicu':
        ids = pd.read_csv(PROJECT / 'incoming/eicu_patient.csv.gz',
                          usecols=['patientunitstayid', 'patienthealthsystemstayid', 'uniquepid'])
        d = d.merge(ids, on='patientunitstayid', validate='many_to_one')
        d['admission_id'], d['pid'], d['index_stay_id'] = d.patienthealthsystemstayid, d.uniquepid, d.patientunitstayid
        d['grp'] = np.where(d.has_primary == 1, 0, np.where(d.has_primary == 0, 1, np.nan))
        d['rr'] = d.respiratoryrate
    else:
        d['admission_id'], d['pid'], d['index_stay_id'] = d.hadm_id, d.subject_id, d.stay_id
        d['grp'] = np.where(d.pos == 1, 0, np.where(d.pos > 1, 1, np.nan))
    d['admission_id'] = key(d.admission_id)
    d['index_stay_id'] = key(d.index_stay_id)
    d['y'] = d.died
    return d


def complete_fields(data, score):
    if score == 'qsofa':
        return data[['rr', 'sbp_min', 'gcs']].notna().all(axis=1)
    bp_known = ((data.sbp_min < 90) | (data.dbp_min <= 60)
                | data[['sbp_min', 'dbp_min']].notna().all(axis=1))
    return data[['rr', 'bun', 'gcs', 'age']].notna().all(axis=1) & bp_known


def canonical_stored_score(data, score):
    if score == 'qsofa':
        value = (data.rr >= 22).astype(float) + (data.sbp_min <= 100).astype(float) + (data.gcs <= 13).astype(float)
    else:
        value = ((data.gcs < 15).astype(float) + (data.bun / 2.801 > 7).astype(float)
                 + (data.rr >= 30).astype(float)
                 + ((data.sbp_min < 90) | (data.dbp_min <= 60)).astype(float)
                 + (data.age >= 65).astype(float))
    return value.where(complete_fields(data, score))


def record(frame, stage, disease, database, inventories=None):
    d = frame.dropna(subset=['score', 'y', 'grp', 'pid']).copy()
    if inventories is not None:
        distribution = d.groupby(['score', 'grp']).agg(records=('y', 'size'), deaths=('y', 'sum'),
                                                       patients=('pid', 'nunique')).reset_index()
        distribution['risk'] = distribution.deaths / distribution.records
        inventories.extend(dict(database=database, disease=disease, stage=stage, **row)
                           for row in distribution.to_dict('records'))
    result = direct_contrast(d)
    return dict(database=database, disease=disease, stage=stage,
                estimand='Delta_w weighted summary, version-diagnostic point estimate',
                n_input_records=len(d), n_shared_records=result.n_records,
                n_admissions=d.admission_id.nunique(), n_patients=result.n_patients,
                delta_w_pp=100 * result.estimate, support_share=result.support_share), result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--outdir', required=True)
    args = parser.parse_args()
    old = old_panel(args.database)
    revised = normalize_panel(args.panel)
    revised['admission_id'] = key(revised.admission_id)
    revised['index_stay_id'] = key(revised['index_patientunitstayid'] if 'index_patientunitstayid' in revised else revised.stay_id)
    results, changes, flows, inventories = [], [], [], []
    for disease, score in [('sepsis', 'qsofa'), ('pneumonia', 'curb65')]:
        legacy = old.loc[old.disease == disease].copy()
        legacy['score'] = legacy[score]
        new = revised.loc[(revised.disease == disease) & revised.grp.notna()].copy()
        new['score'], new['y'] = new[score], new.died
        stage, _ = record(legacy, 'A v1 original ICU-stay records and original score', disease, args.database, inventories)
        results.append(stage)
        index_only = legacy.loc[legacy.index_stay_id.isin(set(new.index_stay_id))].copy()
        stage, _ = record(index_only, 'B v1 restricted to revised index ICU stays and revised disease eligibility', disease, args.database, inventories)
        results.append(stage)
        complete = index_only.loc[complete_fields(index_only, score)].copy()
        stage, _ = record(complete, 'C B with all required stored fields observed', disease, args.database, inventories)
        results.append(stage)
        canonical = complete.copy()
        canonical['score'] = canonical_stored_score(canonical, score)
        stage, _ = record(canonical, 'D C with canonical threshold and urea conversion on stored fields', disease, args.database, inventories)
        results.append(stage)
        old_columns = canonical[['admission_id', 'score', 'y', 'grp']].rename(
            columns={'score': 'old_score', 'y': 'old_y', 'grp': 'old_grp'})
        matched = new.merge(old_columns, on='admission_id', how='inner', validate='one_to_one')
        known = matched[['score', 'old_score', 'y', 'old_y', 'old_grp', 'pid']].notna().all(axis=1)
        agree = matched.y.eq(matched.old_y)
        flows.append(dict(database=args.database, disease=disease, matched_before_score_selection=len(matched),
                          both_scores_outcomes_known=int(known.sum()), outcome_disagreements=int((known & ~agree).sum()),
                          matched_complete_agreeing_outcomes=int((known & agree).sum())))
        matched = matched.loc[known & agree].copy()
        reference = matched.assign(score=matched.old_score, grp=matched.old_grp)
        fixed_group = matched.assign(grp=matched.old_grp)
        final_group = matched
        paired_results = []
        for label, data in [('E matched records, canonical stored-field score and original group', reference),
                             ('F matched records, revised source score and original group', fixed_group),
                             ('G matched records, revised source score and admission-level group', final_group)]:
            row, contrast = record(data, label, disease, args.database, inventories)
            results.append(row)
            paired_results.append(contrast)
        if len(matched):
            for label, left, right in [('F minus E score-source repair on matched records', paired_results[0], paired_results[1]),
                                       ('G minus F diagnosis-scope change on matched records', paired_results[1], paired_results[2])]:
                difference = paired_difference(left, right)
                changes.append(dict(database=args.database, disease=disease, comparison=label,
                                    estimand='difference between Delta_w weighted summaries',
                                    difference_pp=100 * difference['difference'],
                                    numerical_se_pp=100 * difference['se'],
                                    numerical_lo_pp=100 * difference['lo'], numerical_hi_pp=100 * difference['hi'],
                                    interval_status='descriptive paired version comparison'))
        row, _ = record(new, 'H revised full admission target, complete score and known outcome', disease, args.database, inventories)
        results.append(row)
    output = Path(args.outdir)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output / 'version_comparison.csv', index=False)
    pd.DataFrame(changes).to_csv(output / 'paired_version_changes.csv', index=False)
    pd.DataFrame(flows).to_csv(output / 'matched_version_flow.csv', index=False)
    pd.DataFrame(inventories).to_csv(output / 'version_score_level_inventory.csv', index=False)
    name = 'eicu' if args.database == 'eICU-CRD' else 'mimic'
    inputs = [Path(args.panel), PROJECT / f'incoming/{name}_score_panel.csv.gz']
    if name == 'eicu':
        inputs.append(PROJECT / 'incoming/eicu_patient.csv.gz')
    dependencies = [Path(__file__), Path(__file__).with_name('analyse_panels.py'),
                    Path(__file__).with_name('estimands.py')]
    def fingerprint(path):
        with path.open('rb') as stream:
            return dict(path=str(path.resolve()), sha256=hashlib.file_digest(stream, 'sha256').hexdigest())
    provenance = dict(inputs=[fingerprint(path) for path in inputs],
                      code=[fingerprint(path) for path in dependencies],
                      stage_b='joint index-stay restriction and revised disease eligibility, not a pure deduplication effect')
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(pd.DataFrame(results).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()

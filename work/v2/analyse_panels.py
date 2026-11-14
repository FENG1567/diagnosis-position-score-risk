"""Analyze repaired panels through the same audit entry point used by the CLI."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from estimands import direct_contrast, incomplete_score_bounds, paired_difference
from robustness import analyze_robustness

ROOT = Path(__file__).resolve().parents[2]
SCORES = {'sepsis': ('qsofa', 3), 'pneumonia': ('curb65', 5),
          'pancreatitis': ('bisap4', 4), 'heart failure': ('qsofa', 3), 'COPD': ('qsofa', 3)}


def clean_json(obj):
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_json(v) for v in obj]
    if isinstance(obj, np.generic):
        return clean_json(obj.item())
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def file_hash(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def audit_module():
    path = ROOT / 'work/v2/audit/cohort_definition_audit.py'
    specification = importlib.util.spec_from_file_location('paper_b_audit_v2', path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    if not hasattr(module, 'audit_v2'):
        raise RuntimeError('The reconciled audit_v2 public entry point is not yet available.')
    return module


def normalize_panel(path):
    panel = pd.read_csv(path, low_memory=False)
    flag_suffixes = ('_member', '_inclusion', '_classifiable', '_has_primary',
                     '_primary_all_icu', '_primary_firstunit', '_primary_by24',
                     '_primary_firstunit_by24', '_complete')
    boolean_values = {'true': 1.0, 'false': 0.0, '1': 1.0, '0': 0.0,
                      '1.0': 1.0, '0.0': 0.0}
    for column in panel:
        if column.startswith('cohort_') or column.endswith(flag_suffixes):
            values = panel[column].astype('string').str.strip().str.lower()
            invalid = values.notna() & ~values.isin(boolean_values)
            if invalid.any():
                raise ValueError(f'Unrecognized boolean flag values in {column}')
            panel[column] = values.map(boolean_values).astype(float)
    disease_aliases = {'acute pancreatitis': 'pancreatitis', 'heart_failure': 'heart failure',
                       'heart failure': 'heart failure', 'copd': 'COPD', 'pneumonia': 'pneumonia',
                       'sepsis': 'sepsis', 'pancreatitis': 'pancreatitis'}
    original_names = panel.disease.astype(str).str.strip().str.lower()
    unknown = set(original_names).difference(disease_aliases)
    if unknown:
        raise ValueError(f'Unrecognized disease labels {sorted(unknown)}')
    panel['disease'] = original_names.map(disease_aliases)
    for score in ['qsofa', 'qsofa_gcs15', 'curb65', 'bisap4']:
        if score not in panel and score + '_score' in panel:
            panel[score] = panel[score + '_score']
    if 'age' not in panel and 'age_at_admit' in panel:
        panel['age'] = panel.age_at_admit
    if 'pid' not in panel:
        for candidate in ['subject_id', 'uniquepid', 'PATIENT_ID']:
            if candidate in panel:
                panel['pid'] = panel[candidate]
                break
    if 'admission_id' not in panel:
        for candidate in ['hadm_id', 'patienthealthsystemstayid', 'INP_NO']:
            if candidate in panel:
                panel['admission_id'] = panel[candidate]
                break
    if 'grp' not in panel:
        if 'pos' in panel:
            panel['grp'] = np.where(panel.pos == 1, 0, np.where(panel.pos > 1, 1, np.nan))
        elif 'has_primary' in panel:
            panel['grp'] = np.where(panel.has_primary == 1, 0, np.where(panel.has_primary == 0, 1, np.nan))
    if panel.duplicated(['admission_id', 'disease']).any():
        raise ValueError('Revised panel must have one record per admission and disease.')
    return panel


def analysis_frame(data, score):
    frame = data.rename(columns={'died': 'y'}).copy()
    frame['score'] = pd.to_numeric(frame[score], errors='coerce')
    return frame.dropna(subset=['pid', 'grp', 'y', 'score']).copy()


def audited(module, frame, database, disease, label, seed=20261112):
    result = module.audit_v2(frame, score_col='score', outcome_col='y', group_col='grp', pid_col='pid',
                             metadata=dict(database=database, disease=disease,
                                           analysis_label=label, record_unit='hospital admission',
                                           weight_unit='records', cluster_unit='patient',
                                           missing_handling='complete required binary score components',
                                           target='pooled observed record shares in common support'),
                             config=dict(reps=60, seed=seed, min_events=10, min_level_n=20,
                                         min_arm_n=10, min_clusters=20, min_usable_bootstrap=20,
                                         model_check=False))
    independent = direct_contrast(frame)
    reported = result.get('stratified_rd_pp')
    if reported is not None and np.isfinite(independent.estimate):
        if not np.isclose(float(reported), 100 * independent.estimate, atol=0.011):
            raise AssertionError('Independent direct estimate disagrees with audit entry point.')
    return result, independent


def status_of(audit):
    return audit.get('state', audit.get('verdict', audit.get('interval_status', 'unspecified')))


def summarize(audit, direct, label):
    interval = audit.get('delta_ci_pp')
    return dict(analysis=label, estimand='Delta_w weighted summary',
                n=direct.n_records, n_patients=direct.n_patients,
                n_inference_clusters=direct.n_inference_clusters,
                delta_w_pp=100 * direct.estimate, numerical_se_pp=100 * direct.se,
                lo_pp=interval[0] if interval else np.nan,
                hi_pp=interval[1] if interval else np.nan,
                support_share=direct.support_share,
                levels=len(direct.levels), state=status_of(audit),
                interval_status=audit.get('interval_status'),
                weight_target='observed pooled record shares within common support')


def flatten_level(row):
    flat = {}
    for key, value in row.items():
        if isinstance(value, (list, tuple)) and len(value) == 2:
            flat[key + '_lo'] = value[0]
            flat[key + '_hi'] = value[1]
        elif isinstance(value, (dict, list, tuple)):
            flat[key] = json.dumps(clean_json(value), ensure_ascii=False)
        else:
            flat[key] = value
    return flat


def one_record_per_patient(frame):
    result = frame.copy()
    # Dates shifted within a patient retain ordering in MIMIC. eICU lacks full
    # admission dates, so use prespecified outcome-independent hash selection.
    time_column = next((c for c in ['admittime', 'icu_intime', 'intime'] if c in result), None)
    if time_column:
        result['_date'] = pd.to_datetime(result[time_column], errors='coerce')
        if result._date.notna().all():
            result = result.sort_values(['pid', '_date', 'admission_id'])
            return result.drop_duplicates('pid'), 'chronological first eligible admission'
    result['_selection_hash'] = [hashlib.sha256(f'20261112|{pid}|{admission}'.encode()).hexdigest()
                                 for pid, admission in zip(result.pid, result.admission_id)]
    result = result.sort_values(['pid', '_selection_hash'])
    return result.drop_duplicates('pid'), 'one admission per patient selected by prespecified hash'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--outdir', required=True)
    args = parser.parse_args()
    module = audit_module()
    panel = normalize_panel(args.panel)
    output = Path(args.outdir)
    output.mkdir(parents=True, exist_ok=True)
    tables = {name: [] for name in ['summary', 'levels', 'selection', 'missing_bounds', 'sensitivity',
                                  'robustness', 'fine_cell_counts', 'timing', 'sparse_level_sensitivity']}
    all_audits = {}
    for disease, (score, maximum) in SCORES.items():
        source = panel.loc[panel.disease == disease].copy()
        if not len(source):
            continue
        frame = analysis_frame(source, score)
        for group, label in [(0, 'primary'), (1, 'never-primary')]:
            selected = source.loc[source.grp == group]
            tables['selection'].append(dict(database=args.database, disease=disease, group=label,
                                             n_source=len(selected), n_patients=selected.pid.nunique(),
                                             n_score_complete=int(selected[score].notna().sum()),
                                             n_outcome_known=int(selected.died.notna().sum()),
                                             n_analyzed=int((selected[score].notna() & selected.died.notna()).sum())))
        audit, direct = audited(module, frame, args.database, disease, 'repaired primary')
        all_audits[disease] = dict(primary=audit)
        tables['summary'].append(dict(database=args.database, disease=disease, instrument=score,
                                      n_eligible_primary=int((source.grp == 0).sum()),
                                      n_eligible_never=int((source.grp == 1).sum()),
                                      n_complete_primary=int((frame.grp == 0).sum()),
                                      n_complete_never=int((frame.grp == 1).sum()),
                                      n_shared_primary=int(direct.levels.n_primary.sum()) if len(direct.levels) else 0,
                                      n_shared_never=int(direct.levels.n_never.sum()) if len(direct.levels) else 0,
                                      **summarize(audit, direct, 'repaired primary')))
        tables['levels'].extend(dict(database=args.database, disease=disease, instrument=score,
                                     estimand='delta_s observed mortality difference', **flatten_level(row))
                                for row in audit.get('per_level', []))
        issued_levels = {float(row['level']) for row in audit.get('per_level', [])
                         if row.get('delta_ci_status') == 'computed'}
        if len(direct.levels):
            good = direct.levels.level.astype(float).isin(issued_levels)
            bad_mass = float(direct.levels.loc[~good, 'weight'].sum())
            good_contribution = float((direct.levels.loc[good, 'weight'] * direct.levels.loc[good, 'delta']).sum())
            tables['sparse_level_sensitivity'].append(dict(
                database=args.database, disease=disease, estimand='Delta_w weighted summary perturbation range',
                delta_w_pp=100 * direct.estimate, bad_record_weight=bad_mass,
                n_unsupported_interval_levels=int((~good).sum()),
                empirical_good_level_contribution_pp=100 * good_contribution,
                perturbation_lower_pp=100 * (good_contribution - bad_mass),
                perturbation_upper_pp=100 * (good_contribution + bad_mass),
                interpretation='not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1'))
        lower, upper = score + '_lower', score + '_upper'
        if lower in source and upper in source:
            bounded = source.rename(columns={'died': 'y', lower: 'score_lower', upper: 'score_upper'})
            bounds = incomplete_score_bounds(bounded, maximum)
            tables['missing_bounds'].extend(dict(database=args.database, disease=disease, **row)
                                            for row in bounds.to_dict('records'))

        for label, alternative in [('one record per patient', one_record_per_patient(frame)[0])]:
            a, independent = audited(module, alternative, args.database, disease, label)
            selection_rule = one_record_per_patient(frame)[1]
            all_audits[disease][label] = a
            tables['sensitivity'].append(dict(database=args.database, disease=disease,
                                               selection_rule=selection_rule,
                                               **summarize(a, independent, label)))

        weighted = frame.loc[frame.score.isin(direct.levels.level if len(direct.levels) else [])].copy()
        if len(weighted):
            weighted['_patient_weight'] = 1 / weighted.groupby('pid').pid.transform('size')
            patient_target = direct_contrast(weighted, record_weight_col='_patient_weight')
            tables['sensitivity'].append(dict(database=args.database, disease=disease,
                                               analysis='patient-weighted supported-admission sensitivity',
                                               estimand='Delta_w weighted summary, patient-weighted sensitivity',
                                               n=patient_target.n_records, n_patients=patient_target.n_patients,
                                               delta_w_pp=100 * patient_target.estimate,
                                               numerical_se_pp=100 * patient_target.se,
                                               state='descriptive sensitivity, separate estimand',
                                               weight_target='each supported patient contributes total weight one'))

        alternative_scores = ['qsofa_gcs15'] if score == 'qsofa' else []
        alternative_scores.append(score + '_ett_as1')
        if score == 'qsofa':
            alternative_scores.append('qsofa_gcs15_ett_as1')
        for alternative_score in alternative_scores:
            if alternative_score in source:
                alternative = analysis_frame(source, alternative_score)
                a, independent = audited(module, alternative, args.database, disease, alternative_score)
                all_audits[disease][alternative_score] = a
                tables['sensitivity'].append(dict(database=args.database, disease=disease,
                                                   **summarize(a, independent, alternative_score)))

        for endpoint in ['died_strict_status', 'died_v1_timing']:
            if endpoint in source:
                alternative = analysis_frame(source.assign(died=source[endpoint]), score)
                a, independent = audited(module, alternative, args.database, disease, endpoint)
                all_audits[disease][endpoint] = a
                tables['sensitivity'].append(dict(database=args.database, disease=disease,
                                                   **summarize(a, independent, endpoint)))
        if disease in ['sepsis', 'pneumonia']:
            def audit_callback(data, label):
                return audited(module, data, args.database, disease, label)[0]
            comparisons, fine_cells, timing = analyze_robustness(source, args.database, disease, score,
                                                                 audit_callback=audit_callback)
            tables['robustness'].extend(comparisons)
            tables['fine_cell_counts'].extend(fine_cells)
            tables['timing'].extend(timing)
        print(f'Analyzed {args.database} {disease}, n={len(frame)}, state={status_of(audit)}', flush=True)

    for name, rows in tables.items():
        if rows:
            pd.DataFrame(rows).to_csv(output / f'{name}.csv', index=False)
    (output / 'audit_details.json').write_text(json.dumps(clean_json(all_audits), ensure_ascii=False,
                                                        indent=2, allow_nan=False), encoding='utf-8')
    dependencies = [ROOT / 'work/v2/audit/cohort_definition_audit.py',
                    ROOT / 'work/v2/estimands.py', ROOT / 'work/v2/robustness.py']
    provenance = dict(panel_path=str(Path(args.panel).resolve()), panel_sha256=file_hash(args.panel),
                      script_sha256=file_hash(__file__),
                      dependencies=[dict(path=str(path), sha256=file_hash(path)) for path in dependencies],
                      python=sys.version, numpy=np.__version__, pandas=pd.__version__)
    (output / 'analysis_provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

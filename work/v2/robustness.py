"""Paired phenotype, component, hospital and documentation comparisons."""
from __future__ import annotations

import numpy as np
import pandas as pd

from estimands import direct_contrast, paired_difference


def main_frame(data, score):
    d = data.rename(columns={'died': 'y'}).copy()
    d['score'] = d[score]
    return d.dropna(subset=['pid', 'grp', 'score', 'y']).copy()


def variant_frame(source, disease, score, variant):
    d = source.copy()
    position = 'pos_' + variant
    if position in d:
        d['grp'] = np.where(d[position] == 1, 0, np.where(d[position] > 1, 1, np.nan))
    else:
        key = {'heart failure': 'heart_failure', 'COPD': 'copd'}.get(disease, disease)
        membership = f'{key}_{variant}_member'
        priority = f'{key}_{variant}_primary_all_icu'
        if membership not in d or priority not in d:
            return None
        member = pd.to_numeric(d[membership], errors='coerce').eq(1)
        d['grp'] = np.where(member & d[priority].notna(),
                            np.where(d[priority].eq(True), 0, 1), np.nan)
    return main_frame(d, score)


def supported_rows(d, strata):
    counts = d.groupby(strata + ['grp'], observed=True).size().unstack('grp', fill_value=0)
    for group in [0, 1]:
        if group not in counts:
            counts[group] = 0
    keep = counts.loc[(counts[0] > 0) & (counts[1] > 0)].index
    if len(strata) == 1:
        return d.loc[d[strata[0]].isin(keep)].copy()
    return d.loc[pd.MultiIndex.from_frame(d[strata]).isin(keep)].copy()


def contrast_row(d, label, interval_status='descriptive paired sensitivity'):
    c = direct_contrast(d)
    return dict(analysis=label, estimand='Delta_w weighted summary', n=c.n_records,
                n_patients=c.n_patients, delta_w_pp=100 * c.estimate,
                numerical_se_pp=100 * c.se, levels=len(c.levels),
                support_share=c.support_share, interval_status=interval_status), c


def compare_refinement(data, fine_columns, label):
    matched = supported_rows(data, fine_columns)
    if not len(matched):
        return [dict(analysis=label, n=0, state='not estimable, no common fine-cell support')], []
    # The two contrasts use the same records and pooled-count weighting rule.
    # Fine-cell coefficients on group risks differ from the coarse contrast.
    coarse, a = contrast_row(matched, label + ' score-only on matched records')
    fine_data = matched.copy()
    fine_data['score'] = pd.factorize(pd.MultiIndex.from_frame(matched[fine_columns]), sort=True)[0]
    fine, b = contrast_row(fine_data, label + ' fine-cell contrast')
    difference = paired_difference(a, b)
    change = dict(analysis=label + ' fine minus score-only',
                  estimand='difference between Delta_w weighted summaries',
                  n=len(matched), n_patients=matched.pid.nunique(),
                  difference_pp=100 * difference['difference'],
                  numerical_se_pp=100 * difference['se'],
                  numerical_lo_pp=100 * difference['lo'], numerical_hi_pp=100 * difference['hi'],
                  interval_status='descriptive, fine-cell interval calibration unverified')
    counts = matched.groupby(fine_columns + ['grp'], observed=True).agg(
        records=('y', 'size'), deaths=('y', 'sum'), patients=('pid', 'nunique')).reset_index()
    counts['risk'] = counts.deaths / counts.records
    coarse['excluded_records_without_fine_support'] = len(data) - len(matched)
    return [coarse, fine, change], counts.to_dict('records')


def analyze_robustness(source, database, disease, score, audit_callback=None):
    rows, cells, timing = [], [], []
    frame = main_frame(source, score)
    def audited_row(data, label):
        row, contrast = contrast_row(data, label)
        if audit_callback is not None:
            report = audit_callback(data, label)
            interval = report.get('delta_ci_pp')
            row.update(lo_pp=interval[0] if interval else np.nan,
                       hi_pp=interval[1] if interval else np.nan,
                       interval_status=report.get('interval_status'),
                       audit_state=report.get('state', report.get('verdict')))
        return row, contrast
    # Code-list membership and the disease's highest matching position both vary.
    narrow = variant_frame(source, disease, score, 'narrow')
    broad = variant_frame(source, disease, score, 'broad')
    if narrow is not None and broad is not None:
        axis = 'clinical phenotype and priority definition' if database == 'eICU-CRD' else 'code list'
        for label, d in [(f'narrow {axis}', narrow), (f'broad {axis}', broad)]:
            row, _ = audited_row(d, label)
            row['target_comparison'] = 'variant-specific population and observed record weights'
            row['definition_axis'] = axis
            rows.append(row)
        common_ids = set(narrow.admission_id).intersection(broad.admission_id)
        a = narrow.loc[narrow.admission_id.isin(common_ids)].copy()
        b = broad.loc[broad.admission_id.isin(common_ids)].copy()
        levels = set(a.loc[a.grp == 0, 'score']).intersection(a.loc[a.grp == 1, 'score'])
        levels &= set(b.loc[b.grp == 0, 'score']).intersection(b.loc[b.grp == 1, 'score'])
        a, b = a.loc[a.score.isin(levels)], b.loc[b.score.isin(levels)]
        if len(a) and len(b):
            ca, cb = direct_contrast(a), direct_contrast(b)
            assert len(a) == len(b)
            assert np.allclose(ca.levels.weight, cb.levels.weight)
            difference = paired_difference(ca, cb)
            rows.append(dict(analysis='broad minus narrow on common records and common score support',
                             estimand='difference between Delta_w weighted summaries',
                             n=len(a), n_patients=a.pid.nunique(),
                             narrow_delta_w_pp=100 * ca.estimate, broad_delta_w_pp=100 * cb.estimate,
                             difference_pp=100 * difference['difference'],
                             numerical_se_pp=100 * difference['se'],
                             numerical_lo_pp=100 * difference['lo'], numerical_hi_pp=100 * difference['hi'],
                             interval_status='descriptive paired interval, audit gates require separate assessment',
                             target_comparison='same records, same pooled observed score weights'))

    if disease == 'sepsis' and len(frame):
        component_choices = [('q_rr', 'q_bp', 'q_gcs13'), ('q_rr', 'q_sbp', 'q_gcs13'),
                             ('qsofa_rr_point', 'qsofa_sbp_point', 'qsofa_gcs13_point')]
        columns = next((x for x in component_choices if set(x).issubset(frame.columns)), None)
        if columns:
            complete = frame.dropna(subset=list(columns)).copy()
            complete['pattern'] = sum(complete[column].astype(int) * factor
                                      for column, factor in zip(columns, [4, 2, 1]))
            agreement = np.equal(complete[list(columns)].sum(axis=1), complete.score).mean()
            comparisons, counts = compare_refinement(complete, ['score', 'pattern'], 'component pattern')
            for row in comparisons:
                row['component_reconstruction_agreement'] = agreement
            rows.extend(comparisons)
            cells.extend(dict(refinement='component pattern', **row) for row in counts)

    if database == 'eICU-CRD' and 'hospitalid' in frame:
        known = frame.dropna(subset=['hospitalid']).copy()
        comparisons, counts = compare_refinement(known, ['score', 'hospitalid'], 'hospital x score')
        rows.extend(comparisons)
        cells.extend(dict(refinement='hospital x score', **row) for row in counts)
        all_counts = known.groupby(['hospitalid', 'score', 'grp']).size().unstack('grp', fill_value=0)
        for group in [0, 1]:
            if group not in all_counts:
                all_counts[group] = 0
        rows.append(dict(analysis='hospital x score sparsity inventory',
                         n_observed_hospital_score_cells=len(all_counts),
                         n_cells_any_arm_le5=int((all_counts[[0, 1]].min(axis=1) <= 5).sum()),
                         proportion_any_arm_le5=float((all_counts[[0, 1]].min(axis=1) <= 5).mean()),
                         estimand='structural cell counts, no mortality contrast'))

    if 'age' in frame and len(frame):
        refined = frame.copy()
        refined['age_band'] = pd.cut(pd.to_numeric(refined.age, errors='coerce'),
                                     bins=[18, 40, 65, 80, np.inf], right=False,
                                     labels=['18-39', '40-64', '65-79', '80+']).astype('string')
        gender_column = next((name for name in ['sex', 'gender', 'SEX'] if name in refined), None)
        strata = ['score', 'age_band']
        if gender_column:
            genders = refined[gender_column].astype('string').str.strip().str.lower()
            refined['sex_group'] = genders.replace({'m': 'male', 'f': 'female'}).fillna('unknown')
            strata.append('sex_group')
        refined = refined.dropna(subset=['age_band'])
        comparisons, counts = compare_refinement(refined, strata, 'age and sex refinement')
        rows.extend(comparisons)
        cells.extend(dict(refinement='age and sex refinement', **row) for row in counts)

    if database == 'eICU-CRD' and {'diagnosis_by24h_classifiable', 'diagnosis_by24h_has_primary'}.issubset(frame):
        classifiable = frame.loc[frame.diagnosis_by24h_classifiable.eq(True)].copy()
        rebuilt = classifiable.copy()
        rebuilt['grp'] = np.where(rebuilt.diagnosis_by24h_has_primary.eq(True), 0, 1)
        specifications = [('full sample, full-course diagnosis', frame),
                           ('same classifiable subset, full-course diagnosis', classifiable),
                           ('same classifiable subset, never-primary-by-24-hours', rebuilt)]
        for label, d in specifications:
            row, _ = audited_row(d, label)
            timing.append(row)
        timing.append(dict(analysis='classification flow', n=len(frame),
                           classifiable_n=len(classifiable),
                           reclassified_n=int((classifiable.grp.to_numpy() != rebuilt.grp.to_numpy()).sum()),
                           estimand='diagnosis documentation flow'))
        shared_levels = set(classifiable.loc[classifiable.grp == 0, 'score']).intersection(
            classifiable.loc[classifiable.grp == 1, 'score'])
        shared_levels &= set(rebuilt.loc[rebuilt.grp == 0, 'score']).intersection(
            rebuilt.loc[rebuilt.grp == 1, 'score'])
        if shared_levels:
            a = direct_contrast(classifiable.loc[classifiable.score.isin(shared_levels)])
            b = direct_contrast(rebuilt.loc[rebuilt.score.isin(shared_levels)])
            difference = paired_difference(a, b)
            timing.append(dict(analysis='by-24-hours minus full-course grouping on identical supported records',
                               estimand='difference between Delta_w weighted summaries',
                               n=a.n_records, n_patients=a.n_patients,
                               difference_pp=100 * difference['difference'],
                               numerical_lo_pp=100 * difference['lo'], numerical_hi_pp=100 * difference['hi'],
                               interval_status='descriptive paired influence interval',
                               weight_target='identical records and pooled observed score shares'))
        if 'hospitaldischargeoffset' in frame:
            for label, d in [('24-hour hospital survivors, full-course diagnosis', classifiable),
                              ('24-hour hospital survivors, never-primary-by-24-hours', rebuilt)]:
                survivors = d.loc[pd.to_numeric(d.hospitaldischargeoffset, errors='coerce') > 1440]
                row, _ = audited_row(survivors, label)
                row['risk_set'] = 'still hospitalized 24 hours after index ICU admission'
                timing.append(row)

    for group in [rows, cells, timing]:
        for row in group:
            row.update(database=database, disease=disease)
    return rows, cells, timing

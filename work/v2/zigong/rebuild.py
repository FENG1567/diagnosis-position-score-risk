"""Rebuild the deidentified Zigong admission panel using documented units."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('F:/分析专用/meta_measurement_20261103/incoming/zigong')
PRIVATE = Path('F:/分析专用/meta_measurement_20261103/work/paperB_v2/zigong')
OUT = ROOT / 'outputs/v2/zigong'
DISEASES = {
    'sepsis': ('A40', 'A41', 'R652'),
    'pneumonia': ('J12', 'J13', 'J14', 'J15', 'J16', 'J17', 'J18', 'J69'),
    'pancreatitis': ('K85',),
    'heart failure': ('I50', 'I110', 'I130', 'I132'),
    'COPD': ('J44', 'J43'),
}
NARROW = {'sepsis': ('A41',), 'pneumonia': ('J13', 'J14', 'J15', 'J16', 'J17')}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def numeric(series, lower, upper):
    values = pd.to_numeric(series, errors='coerce')
    return values.where(values.between(lower, upper))


def indicator(values, operation):
    return operation(values).astype(float).where(values.notna())


def tri_or(left, right):
    result = pd.Series(np.nan, index=left.index)
    result[(left == 1) | (right == 1)] = 1.0
    result[(left == 0) & (right == 0)] = 0.0
    return result


def add_score(data, name, components):
    block = data[components]
    data[name + '_lower'] = block.sum(axis=1)
    data[name + '_upper'] = data[name + '_lower'] + block.isna().sum(axis=1)
    data[name + '_observed_components'] = block.notna().sum(axis=1)
    data[name] = data[name + '_lower'].where(block.notna().all(axis=1))


def nursing(index):
    mapping = {'temperature': ('temp', 25, 45), 'heart_rate': ('hr', 1, 300),
               'breathing': ('rr', 1, 100), 'Blood_pressure_high': ('sbp_n', 1, 300),
               'Blood_pressure_low': ('dbp_n', 1, 200), 'Invasive_SBP': ('sbp_a', 1, 300),
               'Invasive_diastolic_blood_pressure': ('dbp_a', 1, 200)}
    gcs_columns = ["open_one's_eyes", 'language', 'motion']
    columns = ['INP_NO', 'ChartTime'] + list(mapping) + gcs_columns
    parts = []
    for number, chunk in enumerate(pd.read_csv(SOURCE / 'dtNursingChart.csv', usecols=columns,
                                              chunksize=200000, low_memory=False), 1):
        offset = pd.to_numeric(chunk.ChartTime, errors='coerce') - chunk.INP_NO.map(index)
        chunk = chunk.loc[offset.between(0, 24)].copy()
        if not len(chunk):
            continue
        features = pd.DataFrame({'admission_id': chunk.INP_NO})
        for source, (target, lower, upper) in mapping.items():
            features[target] = numeric(chunk[source], lower, upper)
        gcs = pd.DataFrame(index=chunk.index)
        for name, upper in zip(gcs_columns, [4, 5, 6]):
            digits = chunk[name].astype('string').str.extract(r'^\s*([1-6])(?:\D|$)')[0]
            gcs[name] = numeric(digits, 1, upper)
        features['gcs'] = gcs.sum(axis=1, min_count=3).where(gcs.notna().all(axis=1))
        operations = {column: ['min', 'max'] for column in ['temp', 'rr', 'hr']}
        operations.update({column: ['min'] for column in ['sbp_n', 'dbp_n', 'sbp_a', 'dbp_a', 'gcs']})
        aggregated = features.groupby('admission_id').agg(operations)
        aggregated.columns = ['_'.join(column) for column in aggregated.columns]
        parts.append(aggregated)
        print(f'nursing chunk {number}, retained rows {len(chunk)}', flush=True)
    if not parts:
        return pd.DataFrame(index=pd.Index([], name='admission_id'))
    combined = pd.concat(parts)
    return combined.groupby(level=0).agg({column: 'max' if column.endswith('_max') else 'min'
                                         for column in combined.columns})


def labs(index):
    parts = []
    columns = ['INP_NO', 'LabTime', 'Item', 'LabValue', 'Unit']
    for number, chunk in enumerate(pd.read_csv(SOURCE / 'dtLab.csv', usecols=columns,
                                              chunksize=200000, low_memory=False), 1):
        # Urea mmol/L and blood WBC 10^9/L are the verified relevant item/unit pairs.
        is_urea = chunk.Item.eq('Urea (urea)') & chunk.Unit.eq('mmol/L')
        is_wbc = chunk.Item.eq('White blood cell (WBC)') & chunk.Unit.eq('10^9/L')
        offset = pd.to_numeric(chunk.LabTime, errors='coerce') - chunk.INP_NO.map(index)
        chunk = chunk.loc[(is_urea | is_wbc) & offset.between(-6, 24)].copy()
        if not len(chunk):
            continue
        chunk['feature'] = np.where(chunk.Item.eq('Urea (urea)'), 'urea', 'wbc')
        chunk['number'] = pd.to_numeric(chunk.LabValue, errors='coerce')
        upper = np.where(chunk.feature.eq('urea'), 150, 1000)
        chunk['number'] = chunk.number.where((chunk.number > 0) & (chunk.number <= upper))
        reduced = chunk.groupby(['INP_NO', 'feature']).number.agg(['min', 'max'])
        parts.append(reduced)
        print(f'lab chunk {number}, retained rows {len(chunk)}', flush=True)
    if not parts:
        return pd.DataFrame(index=pd.Index([], name='admission_id'))
    all_parts = pd.concat(parts).groupby(level=[0, 1]).agg({'min': 'min', 'max': 'max'}).unstack('feature')
    all_parts.columns = [f'{feature}_{operation}' for operation, feature in all_parts.columns]
    all_parts.index.name = 'admission_id'
    return all_parts


def compute_scores(data):
    data['sbp_min'] = data[['sbp_n_min', 'sbp_a_min']].min(axis=1)
    data['dbp_min'] = data[['dbp_n_min', 'dbp_a_min']].min(axis=1)
    data['gcs'] = data.gcs_min
    data['rr'] = data.rr_max
    data['bun'] = data.urea_max * 2.801
    data['q_rr'] = indicator(data.rr, lambda x: x >= 22)
    data['q_bp'] = indicator(data.sbp_min, lambda x: x <= 100)
    data['q_gcs13'] = indicator(data.gcs, lambda x: x <= 13)
    data['q_gcs15'] = indicator(data.gcs, lambda x: x < 15)
    data['c_rr'] = indicator(data.rr, lambda x: x >= 30)
    data['c_bp'] = tri_or(indicator(data.sbp_min, lambda x: x < 90),
                           indicator(data.dbp_min, lambda x: x <= 60))
    data['c_urea'] = indicator(data.urea_max, lambda x: x > 7)
    data['c_age'] = indicator(data.age, lambda x: x >= 65)
    data['s_temp'] = tri_or(indicator(data.temp_min, lambda x: x < 36),
                             indicator(data.temp_max, lambda x: x > 38))
    data['s_hr'] = indicator(data.hr_max, lambda x: x > 90)
    data['s_rr'] = indicator(data.rr, lambda x: x > 20)
    data['s_wbc'] = tri_or(indicator(data.wbc_min, lambda x: x < 4),
                            indicator(data.wbc_max, lambda x: x > 12))
    add_score(data, 'sirs_four_criteria', ['s_temp', 's_hr', 's_rr', 's_wbc'])
    data['b_sirs'] = np.nan
    data.loc[data.sirs_four_criteria_lower >= 2, 'b_sirs'] = 1.0
    data.loc[data.sirs_four_criteria_upper < 2, 'b_sirs'] = 0.0
    data['b_bun'] = indicator(data.bun, lambda x: x > 25)
    data['b_age'] = indicator(data.age, lambda x: x > 60)
    add_score(data, 'qsofa', ['q_rr', 'q_bp', 'q_gcs13'])
    add_score(data, 'qsofa_gcs15', ['q_rr', 'q_bp', 'q_gcs15'])
    add_score(data, 'curb65', ['q_gcs15', 'c_urea', 'c_rr', 'c_bp', 'c_age'])
    add_score(data, 'bisap4', ['b_bun', 'q_gcs15', 'b_sirs', 'b_age'])
    return data


def test_regressions():
    x = pd.DataFrame(dict(a=[1.0, np.nan, 0.0], b=[np.nan, np.nan, 0.0]))
    assert tri_or(x.a, x.b).tolist()[0] == 1
    add_score(x, 'sum', ['a', 'b'])
    assert pd.isna(x.loc[0, 'sum']) and x.loc[0, 'sum_lower'] == 1 and x.loc[0, 'sum_upper'] == 2
    assert x.loc[2, 'sum'] == 0
    assert np.isclose(7 * 2.801, 19.607)
    print('PASS tri-state score, partial-component and urea/BUN unit regressions', flush=True)


def main():
    test_regressions()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    source_names = ['dtBaseline.csv', 'dtICD.csv', 'dtTransfer.csv', 'dtNursingChart.csv', 'dtLab.csv', 'dtOutCome.csv', 'datDictionary.csv']
    config = dict(diseases=DISEASES, narrow=NARROW, chart_window_hours=[0, 24], lab_window_hours=[-6, 24],
                  gcs='valid complete eye/verbal/motor on the same nursing row', qsofa_gcs_threshold=13,
                  endpoint='any Dead diagnostic discharge status, missing all statuses excluded',
                  confusion='GCS<15 proxy', bisap='four-item adaptation with four-criteria SIRS, no pleural effusion',
                  unit='one first-ICU-indexed hospital admission',
                  diagnosis_sequence_semantics='sequence only, principal meaning unverified')
    (OUT / 'config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    base = pd.read_csv(SOURCE / 'dtBaseline.csv').rename(columns={'INP_NO': 'admission_id', 'PATIENT_ID': 'pid'})
    assert not base.admission_id.duplicated().any()
    dx = pd.read_csv(SOURCE / 'dtICD.csv', dtype={'ICD_Code': str}).rename(columns={'INP_NO': 'admission_id'})
    transfer = pd.read_csv(SOURCE / 'dtTransfer.csv')
    icu = transfer.loc[transfer.TransferDept.astype(str).str.contains('icu|intensive care', case=False, regex=True)].copy()
    icu['StartTime'] = pd.to_numeric(icu.StartTime, errors='coerce')
    index = icu.dropna(subset=['StartTime']).groupby('INP_NO').StartTime.min()
    base['icu_start_h'] = base.admission_id.map(index)
    base['age'] = numeric(base.Age, 18, 120)
    statuses = dx.groupby('admission_id').Status_Discharge.agg(lambda x: set(x.dropna().astype(str)))
    base['died'] = base.admission_id.map(statuses.map(lambda x: float('Dead' in x) if len(x) else np.nan))
    base['died_strict_status'] = base.admission_id.map(statuses.map(lambda x: float(x == {'Dead'}) if len(x) else np.nan))
    base['mixed_dead_status'] = base.admission_id.map(statuses.map(lambda x: 'Dead' in x and x != {'Dead'}))
    follow = pd.read_csv(SOURCE / 'dtOutCome.csv', usecols=['PATIENT_ID', 'Follow_Vital', 'Death_Date'])
    base = base.merge(follow.rename(columns={'PATIENT_ID': 'pid'}), on='pid', how='left', validate='one_to_one')
    death_time = pd.to_numeric(base.Death_Date, errors='coerce')
    discharge_time = pd.to_numeric(base.DISCHARGE_DATE_TIME, errors='coerce')
    base['died_v1_timing'] = (base.Follow_Vital.astype(str).str.lower().eq('death')
                             & death_time.notna() & (discharge_time.isna() | (death_time <= discharge_time + 24))).astype(float)
    eligibility = pd.DataFrame([dict(n_source_admissions=len(base), n_adult=int(base.age.notna().sum()),
                                     n_index_available=int(base.icu_start_h.notna().sum()),
                                     n_status_unknown=int(base.died.isna().sum()),
                                     n_status_deaths=int(base.died.sum()),
                                     n_v1_timing_deaths=int(base.died_v1_timing.sum()),
                                     n_mixed_dead_status=int(base.mixed_dead_status.sum()))])
    eligibility.to_csv(OUT / 'eligibility_and_endpoints.csv', index=False)
    components = nursing(index).join(labs(index), how='outer')
    data = base.merge(components, on='admission_id', how='left', validate='one_to_one')
    data = data.loc[data.age.notna() & data.icu_start_h.notna()].copy()
    expected = ['sbp_n_min', 'sbp_a_min', 'dbp_n_min', 'dbp_a_min', 'gcs_min', 'rr_max',
                'hr_max', 'temp_min', 'temp_max', 'urea_max', 'wbc_min', 'wbc_max']
    for column in expected:
        if column not in data:
            data[column] = np.nan
    data = compute_scores(data)
    dx['code'] = dx.ICD_Code.fillna('').str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
    dx['position'] = pd.to_numeric(dx.Diagnosis_seq, errors='coerce').where(lambda x: x > 0)
    frames = []
    for disease, prefixes in DISEASES.items():
        matching = dx.loc[dx.code.str.startswith(prefixes)]
        position = matching.groupby('admission_id').position.min().rename('pos')
        selected = data.merge(position, on='admission_id', how='inner', validate='one_to_one')
        selected['disease'] = disease
        selected['grp'] = np.where(selected.pos == 1, 0, np.where(selected.pos > 1, 1, np.nan))
        if disease in NARROW:
            narrow_position = dx.loc[dx.code.str.startswith(NARROW[disease])].groupby('admission_id').position.min()
            selected['pos_narrow'] = selected.admission_id.map(narrow_position)
        frames.append(selected)
    panel = pd.concat(frames, ignore_index=True)
    assert not panel.duplicated(['admission_id', 'disease']).any()
    panel.to_csv(PRIVATE / 'zigong_admission_panel.csv.gz', index=False, compression='gzip')
    qa = []
    score_map = {'sepsis': 'qsofa', 'pneumonia': 'curb65', 'pancreatitis': 'bisap4', 'heart failure': 'qsofa', 'COPD': 'qsofa'}
    for (disease, group), frame in panel.groupby(['disease', 'grp'], dropna=False):
        score = score_map[disease]
        qa.append(dict(disease=disease, grp=group, instrument=score, admissions=len(frame),
                       complete_score=int(frame[score].notna().sum()),
                       known_outcome=int(frame.died.notna().sum()), deaths=int(frame.died.sum()),
                       complete_score_known_outcome=int((frame[score].notna() & frame.died.notna()).sum())))
    pd.DataFrame(qa).to_csv(OUT / 'score_availability.csv', index=False)
    (OUT / 'provenance.json').write_text(json.dumps(dict(
        created_utc=datetime.now(timezone.utc).isoformat(), python=sys.version,
        script_sha256=sha256(__file__), config_sha256=sha256(OUT / 'config.json'),
        input_files=[dict(name=name, sha256=sha256(SOURCE / name), bytes=(SOURCE / name).stat().st_size) for name in source_names],
        private_panel_sha256=sha256(PRIVATE / 'zigong_admission_panel.csv.gz'),
        outcome_source='https://physionet.org/content/icu-infection-zigong-fourth/1.1/'), indent=2), encoding='utf-8')
    print(pd.DataFrame(qa).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()

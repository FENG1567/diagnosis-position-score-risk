"""Aggregate-only Zigong field, endpoint and component feasibility checks."""
from collections import Counter
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('F:/分析专用/meta_measurement_20261103/incoming/zigong')
OUT = ROOT / 'outputs/v2/zigong'


def public_consciousness_counts(raw_counts):
    recognized = {'镇静状', '浅昏迷', '嗜睡', '中昏迷', '清醒', '深嗜睡', '深昏迷',
                  '昏睡', '深嗜睡状', '嗜睡状', '全麻未醒', '昏迷', '谵妄', '模糊',
                  '浅昏迷状', '昏迷状', '痴呆状', '全麻初醒'}
    counts = Counter()
    for value, count in raw_counts.items():
        category = value.strip()
        counts[category if category in recognized else 'other_or_unmapped'] += count
    return dict(counts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(SOURCE / 'dtBaseline.csv')
    dx = pd.read_csv(SOURCE / 'dtICD.csv')
    follow = pd.read_csv(SOURCE / 'dtOutCome.csv',
                         usecols=['PATIENT_ID', 'Follow_Vital', 'Death_Date', 'Follow_Date'])
    status = dx.groupby('INP_NO').Status_Discharge.agg(lambda x: '|'.join(sorted(set(x.dropna()))))
    status.value_counts().rename_axis('status_combination').reset_index(name='admissions').to_csv(
        OUT / 'discharge_status_combinations.csv', index=False)
    data = base.merge(follow, on='PATIENT_ID', validate='one_to_one').merge(status.rename('status'), on='INP_NO')
    data['death_h'] = pd.to_numeric(data.Death_Date, errors='coerce')
    data['discharge_h'] = pd.to_numeric(data.DISCHARGE_DATE_TIME, errors='coerce')
    data['timing'] = data.death_h.le(data.discharge_h).where(data.death_h.notna()).map(
        {True: 'death_on_or_before_discharge', False: 'death_after_discharge'}).fillna('death_time_unavailable')
    data['status_dead'] = data.status.str.contains('Dead')
    data.groupby(['status_dead', 'timing']).size().reset_index(name='admissions').to_csv(
        OUT / 'endpoint_definition_crosscheck.csv', index=False)
    summary = dict(n_admissions=len(base), n_patients=base.PATIENT_ID.nunique(),
                   n_status_any_dead=int(data.status_dead.sum()),
                   n_status_only_dead=int(data.status.eq('Dead').sum()),
                   n_status_all_missing=int(data.status.eq('').sum()),
                   n_death_before_or_at_discharge=int(data.timing.eq('death_on_or_before_discharge').sum()),
                   official_endpoint_source='https://physionet.org/content/icu-infection-zigong-fourth/1.1/',
                   endpoint_decision='Use diagnostic discharge status for hospital mortality, retain unknowns and mixed-status sensitivity.')
    units = Counter()
    for number, chunk in enumerate(pd.read_csv(SOURCE / 'dtLab.csv', usecols=['Item', 'Unit'], chunksize=200000), 1):
        mask = chunk.Item.astype(str).str.contains('urea|bun|white blood|wbc|leukocyte', case=False, regex=True)
        units.update(map(tuple, chunk.loc[mask, ['Item', 'Unit']].fillna('MISSING').to_numpy()))
        print(f'lab metadata chunk {number}', flush=True)
    pd.DataFrame([dict(item=item, unit=unit, records=n) for (item, unit), n in units.items()]).to_csv(
        OUT / 'relevant_lab_units.csv', index=False)
    nursing_columns = ["open_one's_eyes", 'language', 'motion', 'consciousness', 'ChartTime']
    count, components, all_components = 0, Counter(), 0
    consciousness = Counter()
    for number, chunk in enumerate(pd.read_csv(SOURCE / 'dtNursingChart.csv', usecols=nursing_columns,
                                              chunksize=200000, low_memory=False), 1):
        count += len(chunk)
        component_frame = chunk[nursing_columns[:3]]
        components.update(component_frame.notna().sum().to_dict())
        all_components += int(component_frame.notna().all(axis=1).sum())
        consciousness.update(chunk.consciousness.dropna().astype(str).value_counts().to_dict())
        print(f'nursing metadata chunk {number}', flush=True)
    summary.update(n_nursing_rows=count, n_complete_gcs_component_rows=all_components,
                   gcs_component_nonmissing=dict(components),
                   consciousness_categories=public_consciousness_counts(consciousness))
    (OUT / 'feasibility.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

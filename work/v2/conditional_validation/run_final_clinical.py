"""Uniform final conditional-design application; original runs remain immutable."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import apply_conditional_clinical as prior
from analyse_panels import normalize_panel, analysis_frame, SCORES

OUT = ROOT / 'outputs/v2/conditional_validation/clinical/run_03_final'
AMC = Path('F:/分析专用/meta_measurement_20261103/work/paperB_v2/amsterdam/private/qsofa_sepsis_icu_dictionary_unit_repair_outcome.csv.gz')

def main():
    if list((ROOT/'outputs/v2/analysis').glob('*/PENDING_SOURCE_REPAIR.json')):
        raise RuntimeError('Independent source-repair review must pass before final application')
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError('Preserve immutable final application directory')
    validation = json.loads(prior.VALIDATION_MANIFEST.read_text())
    assert validation['status'] == 'complete'
    items = prior.registry()
    for item in items:
        if item['database'] == 'AmsterdamUMCdb':
            item.update(path=AMC, application_ready=True)
            item.pop('pending_reason', None)
    for item in items:
        item['source_sha256'] = prior.sha256(Path(item['path']))
    config = dict(application_id='run_03_final', created_utc=datetime.now(timezone.utc).isoformat(),
                  script_sha256=prior.sha256(Path(__file__)),
                  helper_sha256=prior.sha256(HERE.parent/'conditional_interval.py'),
                  validation_manifest_sha256=prior.sha256(prior.VALIDATION_MANIFEST),
                  sources=[{k:str(v) if isinstance(v,Path) else v for k,v in i.items()} for i in items],
                  alpha=.05, target='theta_D: E(sum a_i Y_i | observed complete-case design)',
                  independence='patient clusters conditionally independent; assumed, not verified',
                  primary_C_modified=False)
    OUT.mkdir(parents=True)
    (OUT/'clinical_application_config.json').write_text(json.dumps(config,indent=2,ensure_ascii=False))
    results, availability, alias = [], [], None
    for item in items:
        path = Path(item['path'])
        assert prior.sha256(path) == item['source_sha256']
        if item['database'] == 'AmsterdamUMCdb':
            raw = pd.read_csv(path,low_memory=False)
            frame = pd.DataFrame({'pid':raw.patientid,'admission_id':raw.admissionid,
                                  'disease':'sepsis','grp':raw.grp,'died':raw.icu_death,
                                  'qsofa':raw.qsofa_main})
            assert not frame.duplicated(['admission_id','disease']).any()
        else:
            frame = normalize_panel(path)
            if item['database'] == 'PEER-adapted-eICU':
                y, d = pd.to_numeric(frame.y,errors='raise'), pd.to_numeric(frame.died,errors='raise')
                assert np.array_equal(y.isna(),d.isna())
                assert np.array_equal(y[y.notna()].to_numpy(),d[d.notna()].to_numpy())
                alias = dict(status='passed',n_rows=len(frame),both_missing=int(y.isna().sum()),
                             both_observed=int(y.notna().sum()),mismatches=0,
                             operation='Drop redundant y in memory only',source_sha256=item['source_sha256'])
                frame = frame.drop(columns='y')
        for disease in item['diseases']:
            sub = frame.loc[frame.disease.eq(disease)].copy()
            score = SCORES[disease][0]
            analytic = analysis_frame(sub, score)
            if analytic.empty:
                raise ValueError(f'Unexpected empty final cell {item["database"]}/{disease}')
            results.append(prior._application_record(item['database'],disease,score,analytic,path,
                                                     item['source_sha256'],item.get('interpretation')))
        assert prior.sha256(path) == item['source_sha256']
        availability.append(dict(database=item['database'],status='applied',sha256=item['source_sha256']))
    assert len(results) == 22
    pd.DataFrame(results).to_csv(OUT/'conditional_clinical_application.csv',index=False)
    pd.DataFrame(availability).to_csv(OUT/'clinical_input_availability.csv',index=False)
    (OUT/'peer_outcome_alias_validation.json').write_text(json.dumps(alias,indent=2))
    report = dict(status='complete',available_analysis_count=len(results),pending_source_count=0,
                  config_sha256=prior.sha256(OUT/'clinical_application_config.json'),
                  results_sha256=prior.sha256(OUT/'conditional_clinical_application.csv'),
                  point_crosschecks_passed=all(r['direct_contrast_point_difference_abs'] is None or
                                               r['direct_contrast_point_difference_abs']<1e-12 for r in results),
                  primary_C_modified=False,raw_patient_records_written=False,
                  full_range_intervals=sum(bool(r['full_range_interval']) for r in results),
                  halfwidth_ge_one=sum(bool(r['halfwidth_ge_one']) for r in results))
    (OUT/'clinical_application_provenance.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)

if __name__ == '__main__':
    main()

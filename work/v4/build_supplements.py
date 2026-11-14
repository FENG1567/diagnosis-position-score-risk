"""Produce submission tables and added analyses from immutable aggregate sources."""
from pathlib import Path
import csv,hashlib,json,re,shutil

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'outputs/v2/delivery'
OUT=ROOT/'outputs/v4/delivery'
PROV=[]

def csvread(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def csvwrite(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def cell(rel,row,key,fmt=None,mult=1):
    value=row[key]
    result=format(float(value)*mult,fmt) if value!='' and fmt else value
    PROV.append(dict(source_csv=rel,source_physical_row_header_1=row['_row'],source_column=key,raw_value=value,display_value=result,multiplier=mult,source_md5=hashlib.md5((ROOT/rel).read_bytes()).hexdigest()))
    return result

def table(headers,rows):
    def clean(x):return str(x).replace('|',' / ').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(clean(x) for x in r)+' |' for r in rows])

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=OUT/'supplementary_data';data.mkdir(exist_ok=True)
    # Existing frozen cells remain unchanged. Only clinical interpretation labels change.
    for p in BASE.glob('s[0-9]*.csv'):shutil.copy2(p,data/p.name)
    for p in BASE.glob('t[1-6].csv'):shutil.copy2(p,OUT/p.name)
    text=(BASE/'tables_v2.md').read_text(encoding='utf-8')
    text=text.replace('# V2 table package (FINAL)','# Main tables')
    text=text.replace('Generated from hash-frozen aggregate CSV/JSON/Markdown inputs. Numeric cell provenance is in `table_numeric_provenance_v2.csv`; copied input hashes and row/column counts are in `source_freeze_manifest.csv`.','Six main tables accompany the manuscript. δ_s denotes a score-specific observed risk difference; Δ_w denotes the record-weighted summary. Source tables and checksums accompany the audit data.')
    text=text.replace('## Table 2. Database-condition eligible cohorts and weighted summaries','## Table 2. Database-condition cohorts and Δ_w weighted summaries; Zigong field groups are unqualified')
    text=text.replace('Primary eligible → complete (incomplete excluded) → shared; complete outside support','Primary or sequence-one† eligible → complete (excluded) → shared; outside support')
    text=text.replace('Never-primary eligible → complete (incomplete excluded) → shared; complete outside support','Never-primary or other-sequence† eligible → complete (excluded) → shared; outside support')
    text=text.replace('## Table 1. Score-level mortality differences in the four primary analysis groups','## Table 1. Score-level δ_s observed mortality differences in the four primary analysis groups')
    marker='- Zigong uses the source-defined hospital-mortality classification based on discharge status. The endpoint definition and discharge-status combination checks are included in the frozen aggregate source snapshot.'
    text=text.replace(marker,'- † Zigong rows compare source sequence-one with other-sequence records. The meaning of Diagnosis_seq as principal-diagnosis rank was not established; these rows are a field-qualification example and do not support a clinical diagnosis-position association. Hospital mortality uses documented discharge status. All pancreatitis applications use adapted BISAP-4; Zigong has 63/47 eligible records but only 14/14 complete records.')
    text=text.replace('Summary interval status','Δ_w weighted-summary policy status')
    text=text.replace('Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI','Cluster IF')
    text=re.sub(r'not computed \([^\n|]*\)','Withheld by policy',text)
    text=text.replace('descriptive paired interval, audit gates require separate assessment','Descriptive')
    text=text.replace('descriptive, fine-cell interval calibration unverified','Descriptive')
    # Table 1 scientific values and Table 2 numerical cells do not change.
    (OUT/'tables_JIC.md').write_text(text,encoding='utf-8')
    raw=csvread(OUT/'t2.csv')
    oldkeys=list(raw[0]);rename={oldkeys[2]:'Primary or sequence-one (unqualified Zigong) eligible-complete-shared; outside support',oldkeys[3]:'Never-primary or other-sequence (unqualified Zigong) eligible-complete-shared; outside support'}
    csvwrite(OUT/'t2.csv',[{rename.get(k,k):v for k,v in row.items()} for row in raw])
    rel='outputs/v3/validation/paired_loss_contrasts.csv'
    contrast_rows=[]
    for i,r in enumerate(csvread(ROOT/rel),2):
        r['_row']=i
        if r['loss']!='brier':continue
        contrast_rows.append({'Database':r['database'],'Condition':r['disease'],'Test population':r['test_group'],'Contrast':r['contrast'],'Brier loss difference':cell(rel,r,'difference','.6f'),'95% CI lower':cell(rel,r,'ci_low','.6f'),'95% CI upper':cell(rel,r,'ci_high','.6f'),'Interval':r['interval_state']})
    csvwrite(data/'s67.csv',contrast_rows)
    rel='outputs/v3/validation/validation_metrics.csv';metrics=[]
    for i,r in enumerate(csvread(ROOT/rel),2):
        r['_row']=i
        metrics.append({'Database':r['database'],'Condition':r['disease'],'Test population':r['test_group'],'Mapping':r['prediction'],'Records':cell(rel,r,'records'),'Observed risk (%)':cell(rel,r,'observed_risk','.2f',100),'Mean predicted risk (%)':cell(rel,r,'mean_predicted_risk','.2f',100),'Brier loss':cell(rel,r,'brier','.6f'),'Calibration intercept':cell(rel,r,'calibration_in_large','.3f'),'Calibration slope':cell(rel,r,'calibration_slope','.3f')})
    csvwrite(data/'s68.csv',metrics)
    rel='outputs/v3/validation/eligibility_counts.csv';flow=[]
    for i,r in enumerate(csvread(ROOT/rel),2):
        r['_row']=i
        flow.append({'Database':r['database'],'Condition':r['disease'],'Role':r['role'],'Diagnosis group':r['diagnosis_group'],'Panel records':cell(rel,r,'panel_records'),'Known group and outcome':cell(rel,r,'group_and_outcome_known_records'),'Complete scores':cell(rel,r,'score_complete_records'),'Patients':cell(rel,r,'patients'),'Events':cell(rel,r,'events'),'Hospitals':cell(rel,r,'hospitals')})
    csvwrite(data/'s69.csv',flow)
    manifest=json.loads((ROOT/'outputs/v3/validation/model_run_manifest.json').read_text(encoding='utf-8'))
    splits=[]
    for db,details in manifest['panel_assertions_and_splits'].items():
        for key,v in details['split'].items():
            splits.append({'Database':db,'Panel-level split field':key,'Recorded value':json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v),'Scope':'combined supplied panel before disease-specific complete-record selection'})
    csvwrite(data/'s70.csv',splits)
    cfg=json.loads((ROOT/'work/v2/audit/benchmark_config.json').read_text(encoding='utf-8'))
    designs=[]
    for r in cfg['designs']:
        designs.append({'Design':r['name'],'Patients':r['n_patients'],'Records per patient: value/probability':json.dumps(r['cluster_sizes']),'Latent Gaussian dependence parameter':r['outcome_icc'],'Score values':json.dumps(r['scores']),'P(group0,score)':json.dumps(r['joint_probabilities_group_score'][0]),'P(group1,score)':json.dumps(r['joint_probabilities_group_score'][1]),'Primary risk vector':json.dumps(r['risks_principal']),'Never-primary risk vector':json.dumps(r['risks_never']),'Prespecified support':json.dumps(r['expected_support'])})
    csvwrite(data/'s71.csv',designs)
    additions=['# Additional supplementary results\n\nThese tables report the exploratory held-out application and the locked simulation design. Prediction-loss differences are neither δ_s nor the Δ_w weighted summary. All original supplementary tables remain available separately.']
    specs=[(67,'Paired held-out Brier loss differences, not δ_s or Δ_w',contrast_rows),(68,'Held-out observed risks, prediction means and loss, not δ_s or Δ_w',metrics),(69,'Role-specific cohort selection counts, not δ_s or Δ_w',flow),(70,'Panel-level split rules and exclusions, not δ_s or Δ_w',splits),(71,'Numerical design inventory for δ_s and Δ_w weighted-summary validation',designs)]
    for n,title,rows in specs:
        additions.append(f'## Supplementary Table {n}. {title}\n\n'+table(list(rows[0]),[list(r.values()) for r in rows]))
        if n==67:additions.append('Intervals are exploratory and pointwise, conditional on the realized fitted and recalibrated maps. Positive primary-minus-broad differences favor broad training; positive recalibrated-minus-fixed differences indicate worse loss after recalibration. Hospital-cluster rows are separate sensitivity results. No subgroup result is omitted based on direction.')
        if n==68:additions.append('Calibration intercept and slope are diagnostic point estimates. They were not used to update the test predictions. A mean prediction does not establish calibration at every score.')
        if n==69:additions.append('Primary training uses the primary records in the train role; broad training uses the all row. Recalibration uses the independent common all cohort. Both policies use the same test records. Rows are overlapping descriptive subsets, not additive populations.')
        if n==70:additions.append('These exclusions describe the combined supplied panel, not a single disease cohort; categories can overlap and must not be summed. eICU hospital roles come from deterministic hash buckets. MIMIC-IV temporal roles use entire possible calendar intervals, excluding ambiguous intervals and patients spanning roles.')
        if n==71:additions.append('Vectors follow the listed score order. Group0 is primary; group1 is never-primary. The dependence value is the latent Gaussian copula parameter, not necessarily a binary-outcome ICC. Cluster-size probabilities refer to patients. Each locked design used 1,000 outer datasets. The separate fine-cell/tiny-arm checks are retained in the original supplementary results. Operational thresholds were not selected by optimizing these results.')
    comp=ROOT/'outputs/v4/composition'
    if comp.exists():
        for p in comp.glob('*.csv'):
            shutil.copy2(p,data/('composition_'+p.name))
        composition_specs=[]
        for number,filename,title in [(72,'demographics.csv','Main-cohort demographics and analytic overlap; counts, not δ_s or Δ_w'),(73,'admission_pathways.csv','Source-specific admission pathways; counts, not δ_s or Δ_w'),(74,'primary_diagnosis_prevalence.csv','Leading priority or billing diagnoses; counts, not δ_s or Δ_w')]:
            rr=csvread(comp/filename)
            if number==72:
                rr=[{'Database':r['database'],'Condition':r['disease'],'Group':r['group'],'Records':r['records'],'Patients':r['patients'],'Age ≥65 / known':r['age_ge65']+' / '+r['age_known'],'Male / known sex':r['male']+' / '+r['sex_known'],'Also in other complete main cohort':r['also_complete_other_main_disease']} for r in rr]
            if number==73:
                rr=[{'Database':r['database'],'Condition':r['disease'],'Group':r['group'],'Source field':r['source_field'],'Category':r['category'],'Records':r['records'],'Denominator':r['denominator'],'Percent':f"{float(r['percent']):.1f}"} for r in rr]
            if number==74:
                rr=[{'Database':r['database'],'Condition':r['disease'],'Group':r['group'],'Diagnosis label':r['diagnosis'],'Records':r['records_with_diagnosis'],'Denominator':r['denominator'],'Percent':f"{float(r['percent_of_admission_records']):.1f}"} for r in rr if int(r['rank'])<=5]
            csvwrite(data/f's{number}.csv',rr)
            additions.append(f'## Supplementary Table {number}. {title}\n\n'+table(list(rr[0]),[list(r.values()) for r in rr]))
            if number==72:additions.append('Age and sex denominators are shown separately; all cohort record denominators, including missing values, are retained in the complete aggregate CSV. The overlap indicator concerns the other complete analytic disease cohort, not all clinical comorbidities. A patient may appear in both diagnosis groups across admissions.')
            if number==73:additions.append('The eICU index ICU admission source and MIMIC hospital admission type are different constructs. Category counts include Unknown and sum to the group record denominator; they were not pooled across sources.')
            if number==74:additions.append('Five leading labels per source-condition-group plus the no-qualifying-label count are displayed. Full ranked counts are supplied in the aggregate CSV. eICU labels are nonexclusive across linked ICU stays and can sum above100%; MIMIC uses the unique discharge billing sequence-one label. No qualifying eICU Primary-priority label is an observation of the documentation field, not proof that a patient had no principal clinical problem.')
        composition_specs=[72,73,74]
    (OUT/'supplementary_results_addendum.md').write_text(('\n\n'.join(additions)+'\n').replace('not δ_s or Δ_w','not δ_s or weighted summary Δ_w'),encoding='utf-8')
    original=(BASE/'supplementary_tables_v2.md').read_text(encoding='utf-8')
    original=original.replace('# V2 supplementary table package (FINAL)','# Original supplementary aggregate tables')
    original='Source-field qualification notice: every Zigong primary/never-primary label below is an unqualified sequence-one/other-sequence field grouping. These diagnostic archive labels do not establish principal-diagnosis rank. Historical versions are labelled diagnostics, not additional clinical findings.\n\n'+original
    (OUT/'supplementary_tables_original.md').write_text(original,encoding='utf-8')
    old_html=(BASE/'supplementary_tables_v2.html').read_text(encoding='utf-8')
    notice='<p><strong>Source qualification notice:</strong> Zigong primary/never-primary archive labels denote unqualified sequence-one/other-sequence fields. They do not establish principal-diagnosis rank. Historical version comparisons are diagnostics.</p>'
    old_html=re.sub(r'(<body[^>]*>)',lambda m:m[1]+notice,old_html,count=1,flags=re.I)
    (OUT/'supplementary_tables_original_source.html').write_text(old_html,encoding='utf-8')
    with (OUT/'supplement_numeric_provenance.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(PROV[0]));w.writeheader();w.writerows(PROV)
    print(json.dumps(dict(main_tables=len(re.findall(r'^## Table ',text,flags=re.M)),added_tables=len(specs)+(3 if comp.exists() else 0),numeric_bindings=len(PROV),designs=len(designs))))

if __name__=='__main__':main()

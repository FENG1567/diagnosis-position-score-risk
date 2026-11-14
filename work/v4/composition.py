"""Aggregate composition of exact frozen main cohorts. No identifiers are exported."""
from pathlib import Path
import csv,gzip,hashlib,json,zipfile,time
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/v4/composition';OUT.mkdir(parents=True,exist_ok=True)
EP=ROOT/'work/v2/eicu/eicu_disease_panel.csv.gz'
MP=Path('F:/分析专用/meta_measurement_20261103/work/paperB_v2/mimic/mimic_iv_v2_score_panel.csv.gz')
ZP=Path('D:/数据库集合/mimic数据/mimic-iv_3.1.0.zip')
E=Path('D:/数据库集合/eicu数据库')
EXPECTED={('eICU','sepsis'):(10467,6109),('eICU','pneumonia'):(2645,8836),('MIMIC-IV','sepsis'):(6679,4125),('MIMIC-IV','pneumonia'):(1640,10862)}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def loadpanel(p,db):
    cols=pd.read_csv(p,nrows=0).columns
    wanted=['pid','admission_id','disease','grp','died','qsofa','curb65','gender','sex','age','age_at_admit','index_patientunitstayid','hospitalid','cohort_main','broad_inclusion','narrow_inclusion']
    d=pd.read_csv(p,usecols=[x for x in wanted if x in cols],dtype={'pid':'string','admission_id':'string'},low_memory=False)
    d=d[d.disease.isin(['sepsis','pneumonia'])].copy()
    if d.duplicated(['admission_id','disease']).any():raise AssertionError('Duplicate admission-disease rows')
    for disease in ['sepsis','pneumonia']:
        q=d[d.disease.eq(disease)].copy();score='qsofa' if disease=='sepsis' else 'curb65'
        q=q.dropna(subset=['pid','admission_id','grp','died',score])
        q=q[q.grp.isin([0,1]) & q.died.isin([0,1])]
        actual=tuple(int(q.grp.eq(g).sum()) for g in [0,1])
        assert actual==EXPECTED[(db,disease)],(db,disease,actual,EXPECTED[(db,disease)])
        yield disease,q

def main():
    t=time.time();cohorts={};traits=[];pathways=[];dxrows=[];checks=[];top=[]
    for db,p in [('eICU',EP),('MIMIC-IV',MP)]:
        for disease,d in loadpanel(p,db):
            cohorts[(db,disease)]=d
            print('MATCH',db,disease,len(d),flush=True)
    print('Reading eICU stay-to-admission map and Primary-priority diagnoses',flush=True)
    patients=pd.read_csv(E/'patient.csv.gz',usecols=['patientunitstayid','patienthealthsystemstayid','unitadmitsource'],dtype={'patienthealthsystemstayid':'string'})
    all_e=set().union(*(set(q.admission_id) for (db,_),q in cohorts.items() if db=='eICU'))
    stays=patients[patients.patienthealthsystemstayid.isin(all_e)]
    mapping=stays.set_index('patientunitstayid').patienthealthsystemstayid
    epieces=[]
    for c in pd.read_csv(E/'diagnosis.csv.gz',usecols=['patientunitstayid','diagnosispriority','diagnosisstring'],chunksize=300000,dtype={'diagnosispriority':'string','diagnosisstring':'string'}):
        c=c[c.patientunitstayid.isin(mapping.index) & c.diagnosispriority.fillna('').str.strip().str.lower().eq('primary')].copy()
        if len(c):
            c['admission_id']=c.patientunitstayid.map(mapping)
            # Controlled diagnostic hierarchy, not free clinical note text. Retain exact complete label.
            c['label']=c.diagnosisstring.fillna('Unknown').str.strip().replace('','Unknown')
            epieces.append(c[['admission_id','label']])
    edx=pd.concat(epieces,ignore_index=True).drop_duplicates(['admission_id','label']) if epieces else pd.DataFrame(columns=['admission_id','label'])
    print('Reading MIMIC hospital admission type and billing-sequence-one diagnoses',flush=True)
    with zipfile.ZipFile(ZP) as z:
        def reader(member,**kw):return pd.read_csv(z.open('mimic-iv-3.1/hosp/'+member),compression='gzip',**kw)
        ad=reader('admissions.csv.gz',usecols=['hadm_id','admission_type'],dtype='string').rename(columns={'hadm_id':'admission_id'})
        dic=reader('d_icd_diagnoses.csv.gz',dtype='string')
        all_m=set().union(*(set(q.admission_id) for (db,_),q in cohorts.items() if db=='MIMIC-IV'))
        pieces=[]
        for c in reader('diagnoses_icd.csv.gz',usecols=['hadm_id','seq_num','icd_code','icd_version'],dtype='string',chunksize=300000):
            c=c[c.hadm_id.isin(all_m) & c.seq_num.eq('1')]
            if len(c):pieces.append(c)
        mdx=pd.concat(pieces,ignore_index=True).merge(dic,on=['icd_code','icd_version'],how='left',validate='many_to_one').rename(columns={'hadm_id':'admission_id','long_title':'label'})
        mdx['label']=mdx.label.fillna('Unmapped billing code')
        mdx=mdx[['admission_id','label']].drop_duplicates()
        if mdx.admission_id.duplicated().any():raise AssertionError('Multiple sequence-one billing diagnoses per admission')
    for (db,disease),d in cohorts.items():
        by_stay=patients.set_index('patientunitstayid').unitadmitsource
        for g,group in [(0,'primary'),(1,'never-primary')]:
            q=d[d.grp.eq(g)].copy();n=len(q)
            ages=pd.to_numeric(q['age'] if db=='eICU' else q['age_at_admit'],errors='coerce')
            sex=q['gender'].astype('string').str.strip().str.lower();knownsex=sex.isin(['male','female','m','f'])
            ageknown=int(ages.notna().sum());old=int(ages.ge(65).sum());male=int(sex.isin(['male','m']).sum())
            other=cohorts[(db,'pneumonia' if disease=='sepsis' else 'sepsis')]
            overlap=int(q.admission_id.isin(other.admission_id).sum())
            traits.append(dict(database=db,disease=disease,group=group,records=n,patients=int(q.pid.nunique()),deaths=int(q.died.sum()),age_known=ageknown,age_ge65=old,age_ge65_percent_of_all_records=100*old/n,sex_known=int(knownsex.sum()),male=male,male_percent_of_all_records=100*male/n,also_complete_other_main_disease=overlap,also_complete_other_percent=100*overlap/n))
            if db=='eICU':
                values=q.index_patientunitstayid.map(by_stay).fillna('Unknown').replace('','Unknown');field='index ICU admission source'
                dx=edx[edx.admission_id.isin(q.admission_id)].copy();dfn='nonexclusive any Primary-priority diagnosis over linked ICU stays'
            else:
                values=q[['admission_id']].merge(ad,on='admission_id',how='left',validate='one_to_one').admission_type.fillna('Unknown').replace('','Unknown');field='hospital admission type'
                dx=mdx[mdx.admission_id.isin(q.admission_id)].copy();dfn='unique discharge billing sequence-one diagnosis'
            counts=values.value_counts(dropna=False)
            assert int(counts.sum())==n
            for label,count in counts.items():pathways.append(dict(database=db,disease=disease,group=group,source_field=field,category=str(label),records=int(count),denominator=n,percent=100*int(count)/n))
            dxknown=int(dx.admission_id.nunique());missing=n-dxknown
            counts=dx.groupby('label').admission_id.nunique().sort_values(ascending=False)
            for rank,(label,count) in enumerate(counts.items(),1):dxrows.append(dict(database=db,disease=disease,group=group,definition=dfn,diagnosis=str(label),rank=rank,records_with_diagnosis=int(count),denominator=n,percent_of_admission_records=100*int(count)/n,exclusive=(db=='MIMIC-IV')))
            dxrows.append(dict(database=db,disease=disease,group=group,definition=dfn,diagnosis='No qualifying priority or sequence-one diagnosis',rank=0,records_with_diagnosis=missing,denominator=n,percent_of_admission_records=100*missing/n,exclusive=(db=='MIMIC-IV')))
            checks.append(dict(database=db,disease=disease,group=group,records=n,expected_records=EXPECTED[(db,disease)][g],match=True,diagnosis_linked_records=dxknown,diagnosis_missing_records=missing,pathway_counts_sum=int(values.value_counts().sum())))
            if len(counts):
                label=counts.index[0];count=int(counts.iloc[0]);top.append(dict(database=db,disease=disease,group=group,label=str(label),count=count,n=n,percent=100*count/n))
    write('demographics.csv',traits);write('admission_pathways.csv',pathways);write('primary_diagnosis_prevalence.csv',dxrows);write('cohort_checks.csv',checks);write('top_diagnoses.csv',top)
    insert='The composition audit reproduced every main analysis group count without changing cohort membership or admission indexing. Source-specific diagnosis and admission-pathway summaries are provided in the added supplementary composition tables. eICU Primary-priority diagnoses were nonexclusive across linked ICU stays; MIMIC-IV used one discharge billing sequence-one diagnosis per admission. These fields were not pooled or interpreted as equivalent. '
    for db in ['eICU','MIMIC-IV']:
        r=next(x for x in top if x['database']==db and x['disease']=='sepsis' and x['group']=='never-primary')
        label=r['label'].split('|')[-1]
        insert+=f"In {db} never-primary sepsis records, the most frequent {'Primary-priority diagnostic label' if db=='eICU' else 'billing sequence-one diagnosis'} was {label} ({r['count']:,}/{r['n']:,}; {r['percent']:.1f}%). "
    r=next(x for x in checks if x['database']=='eICU' and x['disease']=='sepsis' and x['group']=='never-primary')
    insert+=f"In eICU never-primary sepsis, {r['diagnosis_missing_records']:,}/{r['records']:,} records ({100*r['diagnosis_missing_records']/r['records']:.1f}%) had no observed Primary-priority diagnostic row at all; this was not treated as proof of clinical absence. "
    insert+='These descriptions characterize the selected cohorts; they do not identify the cause of between-source risk differences.'
    (OUT/'manuscript_insert.md').write_text(insert+'\n',encoding='utf-8')
    manifest=dict(completed=True,elapsed_seconds=time.time()-t,record_unit='hospital admission',cluster_unit='patient',row_level_exports=False,inputs=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in [EP,MP,E/'patient.csv.gz',E/'diagnosis.csv.gz']],mimic_zip=dict(path=str(ZP),bytes=ZP.stat().st_size,mtime_ns=ZP.stat().st_mtime_ns),notes=['No new eligibility filters','Demographic and pathway denominators include unknown categories','Co-complete main disease indicator is not a diagnosis comorbidity prevalence','eICU multiple primary diagnoses can sum above100%; MIMIC unique seq1 does not','Age top coding does not affect age>=65 threshold'])
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='complete',groups=len(traits),all_counts_match=True,seconds=round(time.time()-t,1))),flush=True)

if __name__=='__main__':main()

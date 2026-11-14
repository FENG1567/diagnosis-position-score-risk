#!/usr/bin/env python3
"""Public, aggregate-only reproduction entry point; no source records are loaded."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,math,os,runpy,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent
GENERATED=ROOT/'_generated'
SUPPLEMENT_MAP={int(k):v for k,v in json.loads((ROOT/'provenance/manuscript_supplement_mapping.json').read_text()).items()}
def published_supplement(old):return ROOT/'results/supplementary_tables'/f'S{SUPPLEMENT_MAP[old]:02d}.csv'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f))

def verify():
 count=0
 for line in (ROOT/'MANIFEST.sha256').read_text().splitlines():
  expected,rel=line.split('  ',1);path=ROOT/rel
  if not path.is_file() or digest(path)!=expected:raise RuntimeError('Checksum mismatch: '+rel)
  count+=1
 if sorted(p.name for p in (ROOT/'results/main_tables').glob('t[1-6].csv'))!=[f't{n}.csv' for n in range(1,7)]:
  raise RuntimeError('Published main-table inventory must be t1.csv through t6.csv')
 if sorted(p.name for p in (ROOT/'results/supplementary_tables').glob('S[0-9][0-9].csv'))!=[f'S{n:02d}.csv' for n in range(1,58)]:
  raise RuntimeError('Published supplementary-table inventory must be S01.csv through S57.csv')
 stems=['fig1_score_specific_risk','fig2_heldout_brier','figS1_audit_states']
 formats=['pdf','tiff','png','svg']
 missing=[f'{stem}.{ext}' for stem in stems for ext in formats if not (ROOT/'results/figures'/f'{stem}.{ext}').is_file()]
 if missing:raise RuntimeError('Missing published figure outputs: '+','.join(missing))
 print(json.dumps({'action':'verify','hashes_verified':count,'main_tables':6,'supplementary_tables':57,'figures':3,'figure_formats':4}),flush=True)

def namespace(rel):
 path=ROOT/rel;ns={'__name__':'release_'+path.stem,'__file__':str(path)}
 # Some source modules use dataclasses, so a registered import is necessary.
 name='release_'+path.stem
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
 sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod

def tables():
 GENERATED.mkdir(exist_ok=True);run=Path(tempfile.mkdtemp(prefix='tables_',dir=GENERATED))
 baseline=run/'baseline'
 subprocess.run([sys.executable,str(ROOT/'work/v2/build_tables_v2.py'),'--mode','final','--output',str(baseline)],cwd=ROOT,check=True)
 revision=run/'v4';revision.mkdir()
 mod=namespace('work/v4/build_supplements.py');mod.BASE=baseline;mod.OUT=revision;mod.main()
 presentation=run/'presentation';inp=presentation/'input';out=presentation/'output'
 inp.mkdir(parents=True);out.mkdir()
 for filename in ['supplementary_tables_original.md','supplementary_results_addendum.md']:
  shutil.copy2(revision/filename,inp/filename)
 code=(ROOT/'work/v5/clean_supplements.py').read_text(encoding='utf-8-sig')
 code=code.split("m=(I/'supplementary_methods.md')",1)[0]
 old="B=Path('/tmp/jic_v5_20261114')"
 if old not in code:raise RuntimeError('Supplementary presentation interface changed')
 code=code.replace(old,'B=Path('+repr(str(presentation))+')',1)
 scope={'__name__':'release_supplementary_presentation'};exec(compile(code,'supplementary_presentation','exec'),scope)
 source=run/'original_source';dest=run/'display_revision'
 records=scope['records']
 index_headers=['Table','Subject','Rows','Columns','CSV']
 def make_input_tree(root):
  main_dir=root/'02_正文表格';supp_dir=root/'04_补充文件/Supplementary_tables_CSV'
  main_dir.mkdir(parents=True,exist_ok=True);supp_dir.mkdir(parents=True,exist_ok=True)
  for n in range(1,7):shutil.copy2(revision/f't{n}.csv',main_dir/f't{n}.csv')
  for n in range(1,54):shutil.copy2(out/'supplementary_data'/f'S{n:02d}.csv',supp_dir/f'S{n:02d}.csv')
  shutil.copy2(ROOT/'docs/legacy/supplementary_tables_rc02.md',root/'04_补充文件/supplementary_tables.md')
  with (root/'04_补充文件/supplementary_table_index.csv').open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.writer(f,lineterminator='\n');w.writerow(index_headers)
   for rec in records:w.writerow([rec['number'],rec['title'],rec['rows'],rec['columns'],rec['csv']])
 make_input_tree(source);shutil.copytree(source,dest)
 transform_audit=run/'display_transform_audit.json'
 subprocess.run([sys.executable,str(ROOT/'work/display_v7/compact_tables.py'),
  '--source',str(source),'--dest',str(dest),'--audit-out',str(transform_audit)],cwd=ROOT,check=True)
 baseline_main=[]
 for n in range(1,7):
  rows=read_csv(revision/f't{n}.csv')
  baseline_main.append({'file':f't{n}.csv','rows':len(rows)-1,'has_header':bool(rows and rows[0])})
 baseline_supp=[]
 for n in range(1,54):
  name=f'S{n:02d}.csv';actual=read_csv(out/'supplementary_data'/name);expected=read_csv(published_supplement(n))
  baseline_supp.append({'file':name,'cell_match':actual==expected,'rows':len(actual)-1})
 original_archives=[]
 for n,key in enumerate(['t1','t2','t3','t5'],start=54):
  name=f'S{n:02d}.csv';archive=dest/'04_补充文件/Supplementary_tables_CSV'/name
  expected=published_supplement(n)
  original_archives.append({'file':name,'source_table':key,'byte_match':digest(archive)==digest(revision/f'{key}.csv') and digest(archive)==digest(expected)})
 display_comparisons=[]
 for n in range(1,7):
  name=f't{n}.csv';actual=read_csv(dest/'02_正文表格'/name);expected=read_csv(ROOT/'results/main_tables'/name)
  display_comparisons.append({'file':name,'cell_match':actual==expected,'rows':len(actual)-1})
 for n in range(1,58):
  name=f'S{n:02d}.csv';actual=read_csv(dest/'04_补充文件/Supplementary_tables_CSV'/name);expected=read_csv(published_supplement(n))
  display_comparisons.append({'file':name,'cell_match':actual==expected,'rows':len(actual)-1})
 audit=json.loads(transform_audit.read_text(encoding='utf-8'))
 audit['source_root']='original_source (temporary aggregate reconstruction)'
 audit['destination_root']='display_revision (temporary display transform output)'
 transform_audit.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 baseline_ok=all(x['cell_match'] for x in baseline_supp) and all(x['byte_match'] for x in original_archives)
 display_ok=all(x['cell_match'] for x in display_comparisons)
 report={'action':'tables','generated_directory':str(run.relative_to(ROOT)),
  'baseline_original_main_tables_built':6,'baseline_original_supplementary_tables_built':53,
  'baseline_original_main_table_rows':baseline_main,
  'baseline_original_supplementary_cell_matches':baseline_supp,
  'full_original_main_archives':original_archives,
  'display_transform_audit':audit,
  'display_comparisons':display_comparisons,
  'all_match':baseline_ok and display_ok}
 (GENERATED/'table_reproduction.json').write_text(json.dumps(report,indent=2))
 (GENERATED/'supplementary_index.json').write_text(json.dumps(scope['records'],ensure_ascii=False,indent=2))
 shutil.copy2(transform_audit,GENERATED/'display_transform_audit.json')
 if not report['all_match']:
  bad=[x['file'] for x in baseline_supp if not x['cell_match']]
  bad += [x['file'] for x in original_archives if not x['byte_match']]
  bad += [x['file'] for x in display_comparisons if not x['cell_match']]
  raise RuntimeError('Published table mismatch: '+','.join(bad))
 print(json.dumps({'action':'tables','baseline_matches':57,'display_matches':63,'directory':str(run.relative_to(ROOT))}),flush=True)

def figures():
 GENERATED.mkdir(exist_ok=True)
 out=GENERATED/'figures';out.mkdir(exist_ok=True)
 subprocess.run([sys.executable,str(ROOT/'work/publication_v12/build_figures.py'),
  '--levels',str(ROOT/'provenance/fig1_score_specific_risk_source.csv'),
  '--s46',str(ROOT/'results/supplementary_tables/S25.csv'),'--out',str(out)],cwd=ROOT,check=True)
 observed1=read_csv(out/'fig1_score_specific_risk_source.csv')
 published1=read_csv(ROOT/'provenance/fig1_score_specific_risk_source.csv')
 if observed1!=published1:raise RuntimeError('Figure 1 scientific source differs')
 observed2=read_csv(out/'fig2_heldout_brier_source.csv')
 s25=read_csv(ROOT/'results/supplementary_tables/S25.csv')
 header=s25[0];contrasts={'primary_fixed_minus_broad_fixed','primary_recalibrated_minus_broad_recalibrated'}
 selected=[(i+2,r) for i,r in enumerate(s25[1:]) if r[header.index('Interval')]=='pointwise_95pct' and r[header.index('Contrast')] in contrasts]
 if not observed2 or observed2[0]!=header+['_source_row'] or len(observed2)-1!=len(selected):
  raise RuntimeError('Figure 2 Brier source schema or row count differs from S25 selection')
 lines=[line for line,_ in selected]
 if [int(r[-1]) for r in observed2[1:]]!=lines:raise RuntimeError('Figure 2 Brier source row identifiers differ from S25 selection')
 numeric={'Brier loss difference','95% CI lower','95% CI upper'}
 for actual,(line,expected) in zip(observed2[1:],selected):
  if any((not math.isclose(float(actual[i]),float(expected[i]),rel_tol=1e-12,abs_tol=1e-15))
         if col in numeric else actual[i]!=expected[i]
         for i,col in enumerate(header)):
   raise RuntimeError(f'Figure 2 Brier value differs from S25 source row {line}')
 if len(observed2)!=25:raise RuntimeError('Figure 2 must contain the 24 prespecified Brier contrasts')
 stems=['fig1_score_specific_risk','fig2_heldout_brier','figS1_audit_states']
 formats=['pdf','tiff','png','svg']
 missing=[f'{stem}.{ext}' for stem in stems for ext in formats if not (out/f'{stem}.{ext}').is_file()]
 if missing:raise RuntimeError('Missing figure outputs: '+','.join(missing))
 report={'action':'figures','figure1_scientific_source_match':True,'figure2_selected_s25_rows':len(observed2)-1,
  'figures':stems,'formats':formats,'figure1_rows':20,'note':'Source-issued intervals are preserved; SVG/PDF rasterization metadata and fonts can change bytes.'}
 (GENERATED/'figure_reproduction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'action':'figures','figures':3,'formats':4,'scientific_source_match':True,'brier_rows':24}),flush=True)

TEST_PATHS=[
 'work/v2/audit/tests','work/v2/test_analysis_integration.py','work/v2/test_conditional_interval.py',
 'work/v2/eicu/test_build_eicu_v2.py','work/v2/mimic/test_m58_mimic_rebuild.py',
 'work/v2/mimic3/test_m58_mimic3_rebuild.py','work/v2/level_validation/test_per_level_validation.py',
 'work/v2/bootstrap_precision/test_bootstrap_precision.py','work/v2/amsterdam/test_unit_mapping_repair.py',
 'work/v3/tests/test_validation_core.py','tests/test_release_wrapper.py']

def tests():
 GENERATED.mkdir(exist_ok=True)
 module_dirs=['work/v2','work/v2/audit','work/v2/eicu','work/v2/mimic','work/v2/mimic3','work/v2/level_validation','work/v2/bootstrap_precision','work/v2/amsterdam','work/v3/validation']
 env=dict(os.environ);env['PYTHONPATH']=os.pathsep.join([*(str(ROOT/p) for p in module_dirs),env.get('PYTHONPATH','')])
 private_check='work/v2/bootstrap_precision/test_bootstrap_precision.py::NumericReducerValidation::test_real_adapter_and_report_smoke'
 # This original smoke includes a hash of a restricted Amsterdam patient panel.
 # Keep the test supplied, but do not require source records in public CI.
 subprocess.run([sys.executable,'-m','pytest','-q','--import-mode=importlib',*TEST_PATHS,'--deselect',private_check,'--junitxml',str(GENERATED/'tests.xml')],cwd=ROOT,env=env,check=True)

def synthetic():
 GENERATED.mkdir(exist_ok=True);out=GENERATED/'synthetic';out.mkdir(exist_ok=True)
 path=out/'synthetic_records.csv'
 with path.open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['pid','score','outcome','definition'])
  for s in range(4):
   for g in range(2):
    for j in range(80):w.writerow([f'SYNTHETIC-{s}-{g}-{j}',s,int(j%(6-g-s)==0),g+1])
 subprocess.run([sys.executable,str(ROOT/'work/v2/audit/cohort_definition_audit.py'),'--input',str(path),'--outdir',str(out/'audit'),'--expected-levels','0,1,2,3','--semantics','synthetic groups; not a clinical dataset','--reps','60'],cwd=ROOT,check=True)
 print('Synthetic demonstration only; never a replacement for clinical source data.',flush=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['verify','tables','figures','test','synthetic','all'],default='verify',nargs='?');args=parser.parse_args()
 if args.action in ['verify','all']:verify()
 if args.action in ['tables','all']:tables()
 if args.action in ['figures','all']:figures()
 if args.action in ['test','all']:tests()
 if args.action=='synthetic':synthetic()

if __name__=='__main__':main()

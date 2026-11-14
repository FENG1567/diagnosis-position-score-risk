#!/usr/bin/env python3
"""Explicitly register a NEW authorized rerun; never label it preregistration."""
from pathlib import Path
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--run-root',type=Path,default=Path('private/reanalysis'))
 p.add_argument('--eicu-panel',type=Path,required=True);p.add_argument('--mimic-panel',type=Path,required=True)
 p.add_argument('--allow-input-differences',action='store_true',help='Record a new-input reproduction attempt; do not claim original-file identity')
 a=p.parse_args();run=(ROOT/a.run_root).resolve()
 if not run.is_relative_to(ROOT/'private'):raise ValueError('Only a private run root may be registered')
 original_path=ROOT/'outputs/v3/validation/freeze_manifest.json';original=json.loads(original_path.read_text())
 inputs={};mismatches=[]
 for key,path in [('eICU',a.eicu_panel),('MIMIC_IV',a.mimic_panel)]:
  path=path.resolve();actual=sha(path);expected=original['input_panels'][key]['sha256']
  inputs[key]={'path':str(path),'sha256':actual,'original_file_match':actual.lower()==expected.lower()}
  if actual.lower()!=expected.lower():mismatches.append(key)
 if mismatches and not a.allow_input_differences:raise ValueError('Different source panel bytes: '+','.join(mismatches)+'; inspect differences before explicitly allowing a NEW-input rerun')
 scriptdir=run/'work/v3/validation'
 targets={'protocol':scriptdir/'design.md','eligibility_code':scriptdir/'count_eligibility.py','fit_code':scriptdir/'fit_and_validate.py'}
 manifest={'status':'reproduction_inputs_registered','created_utc':datetime.now(timezone.utc).isoformat(),'not_preregistration':True,'original_manifest_sha256':sha(original_path),'sha256':{k:sha(v) for k,v in targets.items()},'input_panels':inputs,'input_difference_permission':a.allow_input_differences,'execution':original.get('execution',{}),'protocol_seed':original.get('protocol_seed')}
 out=run/'outputs/v3/validation';out.mkdir(parents=True,exist_ok=True)
 shutil.copy2(original_path,out/'original_study_freeze_manifest.json')
 (out/'freeze_manifest.json').write_text(json.dumps(manifest,indent=2))
 print('Registered NEW private rerun inputs; original public manifest unchanged.')
if __name__=='__main__':main()

"""Release wrapper regressions, using temporary fictional scripts and no clinical data."""
from pathlib import Path
import json,shutil,subprocess,sys
import pytest
WRAPPER=Path(__file__).resolve().parents[1]/'run_private.py'

def fixture(tmp_path):
 root=tmp_path/'checkout';(root/'work/v2').mkdir(parents=True);(root/'outputs').mkdir()
 shutil.copy2(WRAPPER,root/'run_private.py')
 script=root/'work/v2/probe.py'
 script.write_text("from pathlib import Path\nROOT=Path(__file__).resolve().parents[2]\np=Path('F:/分析专用/meta_measurement_20261103/marker.txt')\np.parent.mkdir(parents=True,exist_ok=True)\np.write_text(str(ROOT)+' VERSION_A')\n")
 config=root/'paths.json'
 def configure(folder):config.write_text(json.dumps({'run_root':'private/reanalysis','path_mappings':[{'from_prefix':'F:/分析专用/meta_measurement_20261103','to_prefix':'private/reanalysis/'+folder}]}))
 configure('first');return root,script,config,configure

def invoke(root,script,config):return subprocess.run([sys.executable,str(root/'run_private.py'),'--config',str(config),str(script)],cwd=root,capture_output=True,text=True)

def test_absolute_script_runs_only_in_private_stage(tmp_path):
 root,script,config,_=fixture(tmp_path);before=script.read_bytes()
 result=invoke(root,script.resolve(),config);assert result.returncode==0,result.stderr
 marker=root/'private/reanalysis/first/marker.txt'
 assert str(root/'private/reanalysis') in marker.read_text()
 assert not (root/'marker.txt').exists();assert script.read_bytes()==before

def test_changed_mapping_and_source_apply_on_next_run(tmp_path):
 root,script,config,configure=fixture(tmp_path)
 assert invoke(root,script,config).returncode==0
 configure('second');script.write_text(script.read_text().replace('VERSION_A','VERSION_B'))
 result=invoke(root,script,config);assert result.returncode==0,result.stderr
 assert 'VERSION_B' in (root/'private/reanalysis/second/marker.txt').read_text()
 assert 'VERSION_A' in (root/'private/reanalysis/first/marker.txt').read_text()

def test_output_root_cannot_be_public_results(tmp_path):
 root,script,config,_=fixture(tmp_path);config.write_text(json.dumps({'run_root':'outputs'}))
 result=invoke(root,script,config);assert result.returncode!=0
 assert not (root/'outputs/marker.txt').exists()

"""Recheck immutable v1 tables and current v2 panel/aggregate bindings."""
from pathlib import Path
import csv
import hashlib
import json
import re
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/v2/final_verification'

def digest(p,algorithm='sha256'):
    return hashlib.new(algorithm,p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    snapshot=ROOT/'work/source_snapshot'
    entries=re.findall(r'\| (t\S+\.csv) \| (\d+) \| (\d+) \| ([a-f0-9]{32}) \|',
                       (snapshot/'FROZEN_NUMBERS.md').read_text(encoding='utf-8'))
    assert len(entries)==18
    rows=[]
    for name,lines,size,expected in entries:
        for label,folder in [('received',snapshot/'tables'),('original_project',Path('F:/分析专用/meta_measurement_20261103/outputs/tables'))]:
            p=folder/name
            raw=p.read_bytes()
            row=dict(table=name,location=label,expected_md5=expected,observed_md5=digest(p,'md5'),
                     observed_sha256=digest(p),bytes=len(raw),physical_lines=len(raw.splitlines()))
            row['matches_original_freeze']=(row['observed_md5']==expected and len(raw)==int(size) and row['physical_lines']==int(lines))
            assert row['matches_original_freeze'],row
            rows.append(row)
    with (OUT/'original_18_tables_reverified.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    bindings=[]
    for db in ['eicu','mimic_iv','mimic_iii','zigong']:
        p=ROOT/f'outputs/v2/analysis/{db}/analysis_provenance.json'
        data=json.loads(p.read_text())
        path=Path(data['panel_path'])
        actual=digest(path)
        assert actual==data['panel_sha256']
        assert not (p.parent/'PENDING_SOURCE_REPAIR.json').exists()
        bindings.append(dict(database=db,panel_sha256=actual,provenance_sha256=digest(p),passed=True))
    report=dict(status='passed',verified_utc=datetime.now(timezone.utc).isoformat(),
                original_tables=18,original_copies_checked=len(rows),original_tables_modified=False,
                current_main_panel_bindings=bindings)
    (OUT/'source_integrity_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()

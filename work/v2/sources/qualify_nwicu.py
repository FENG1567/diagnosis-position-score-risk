"""Qualify score fields from release dictionaries before clinical extraction."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = Path('D:/数据库集合/NWICU数据库/northwestern-icu-nwicu-database-0.1.0.zip')
OUT = ROOT / 'outputs/v2/sources'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    provenance = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        def dictionary(suffix):
            name = next(name for name in archive.namelist() if name.endswith(suffix))
            blob = archive.read(name)
            info = archive.getinfo(name)
            provenance.append(dict(member=name, sha256=hashlib.sha256(blob).hexdigest(),
                                   crc=info.CRC, member_bytes=info.file_size))
            return pd.read_csv(gzip.GzipFile(fileobj=io.BytesIO(blob)))
        chart = dictionary('/d_items.csv.gz')
        laboratory = dictionary('/d_labitems.csv.gz')
        charts = chart.loc[chart.linksto.eq('chartevents')].copy()
        text = charts.label.fillna('') + ' ' + charts.abbreviation.fillna('')
        requirements = [
            ('qSOFA', 'respiratory rate', text.str.contains('respirations|respiratory rate|\\bRR\\b', case=False, regex=True).any()),
            ('qSOFA', 'systolic blood pressure', text.str.contains('systolic|ABPs|NBPs', case=False, regex=True).any()),
            ('qSOFA', 'GCS or valid altered mentation field', text.str.contains('glasgow|\\bGCS\\b|mentation|conscious|confus', case=False, regex=True).any()),
            ('adapted CURB-65', 'blood urea nitrogen', laboratory.loc[laboratory.fluid.eq('Blood')].label.str.contains('Urea Nitrogen', case=False).any()),
            ('adapted CURB-65', 'GCS or confusion field', text.str.contains('glasgow|\\bGCS\\b|mentation|conscious|confus', case=False, regex=True).any()),
            ('BISAP-4', 'GCS or valid mental-status field', text.str.contains('glasgow|\\bGCS\\b|mentation|conscious|confus', case=False, regex=True).any()),
        ]
    rows = [dict(database='NWICU 0.1.0', instrument=instrument, required_component=component,
                 found_in_release_dictionary=bool(found),
                 decision='required mental-status field absent, complete-score replication fails metadata gate')
            for instrument, component, found in requirements]
    pd.DataFrame(rows).to_csv(OUT / 'nwicu_score_field_qualification.csv', index=False)
    payload = dict(archive=str(ARCHIVE), archive_bytes=ARCHIVE.stat().st_size,
                   chart_dictionary_rows=len(charts), unique_chart_item_ids=int(charts.itemid.nunique()),
                   provenance=provenance, scope='dictionaries only, before clinical outcomes',
                   source_url='https://physionet.org/content/nwicu-northwestern-icu/0.1.0/',
                   decision='Fail planned complete-score supplementary application. Preserve required predictors as unavailable.')
    (OUT / 'nwicu_qualification.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
    main()

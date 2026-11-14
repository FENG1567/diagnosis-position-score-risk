"""Retrieve official Amsterdam legacy item mappings without clinical rows."""
import hashlib
import json
from pathlib import Path
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'work/v2/sources/amsterdam_metadata'
OUT = ROOT / 'outputs/v2/sources'


def retrieve(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'PaperB-field-reconstruction'})
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    repository = 'AmsterdamUMC/AmsterdamUMCdb'
    info = json.loads(retrieve(f'https://api.github.com/repos/{repository}/commits/master'))
    commit = info['sha']
    records = []
    for relative in ['amsterdamumcdb/dictionary/dictionary.csv', 'amsterdamumcdb/scores.py',
                     'amsterdamumcdb/cohorts.py', 'concepts/severityscores/sofa.ipynb']:
        url = f'https://raw.githubusercontent.com/{repository}/{commit}/{relative}'
        row = dict(relative_path=relative, commit=commit, url=url)
        try:
            blob = retrieve(url)
            target = WORK / Path(relative).name
            target.write_bytes(blob)
            row.update(status='retrieved', bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
        except Exception as error:
            row.update(status='failed', error=f'{type(error).__name__}: {error}')
        records.append(row)
    dictionary_path = WORK / 'dictionary.csv'
    if dictionary_path.exists():
        dictionary = pd.read_csv(dictionary_path, low_memory=False)
        print('Dictionary columns', dictionary.columns.tolist(), flush=True)
        text = dictionary.astype(str).agg(' '.join, axis=1)
        relevant = dictionary.loc[text.str.contains('glasgow|gcs|ademfreq|ademhal|systol|NICE.*diagnos', case=False, regex=True)]
        relevant.to_csv(WORK / 'relevant_dictionary_entries.csv', index=False)
        print('Relevant metadata entries', len(relevant), flush=True)
    (OUT / 'amsterdam_metadata_retrieval.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

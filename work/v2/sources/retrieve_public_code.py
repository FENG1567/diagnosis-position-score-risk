"""Retrieve version-bound public study code for reproducibility assessment."""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'work/v2/sources/public_code'
OUT = ROOT / 'outputs/v2/sources'
REPOSITORIES = ['hlzhou/peer-score', 'RyllMartin/eICU_predicting_PE_ICU_mortality']


def request(url):
    headers = {'User-Agent': 'PaperB-reproducibility-audit', 'Accept': 'application/vnd.github+json'}
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40) as response:
        return response.read()


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for repository in REPOSITORIES:
        row = dict(repository=repository, purpose='assess reproducible fixed-score application before outcome contrasts')
        try:
            info = json.loads(request('https://api.github.com/repos/' + repository))
            branch = info['default_branch']
            commit = json.loads(request(f'https://api.github.com/repos/{repository}/commits/{branch}'))['sha']
            archive_url = f'https://codeload.github.com/{repository}/zip/{commit}'
            blob = request(archive_url)
            directory = WORK / repository.replace('/', '__')
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'source.zip').write_bytes(blob)
            extracted = []
            with zipfile.ZipFile(io.BytesIO(blob)) as archive:
                for member in archive.infolist():
                    if member.is_dir():
                        continue
                    relative = Path(*Path(member.filename).parts[1:])
                    if relative.suffix.lower() not in {'.py', '.r', '.sql', '.md', '.txt', '.ipynb', '.yaml', '.yml', '.json'} and 'license' not in relative.name.lower():
                        continue
                    if member.file_size > 20 * 1024 * 1024:
                        continue
                    target = (directory / relative).resolve()
                    if not target.is_relative_to(directory.resolve()):
                        raise ValueError('Archive member escapes destination.')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(member))
                    extracted.append(str(relative))
            row.update(status='retrieved', commit=commit, url=archive_url,
                       sha256=hashlib.sha256(blob).hexdigest(), bytes=len(blob),
                       license=info.get('license'), extracted_code_files=extracted)
        except Exception as error:
            row.update(status='failed', error=f'{type(error).__name__}: {error}')
        records.append(row)
        print(repository, row['status'], flush=True)
    (OUT / 'public_code_retrieval.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Synchronize generated display files and editor package assets into a release checkout."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIGURE_STEMS = (
    'fig1_score_specific_risk',
    'fig2_heldout_brier',
    'figS1_audit_states',
)
FIGURE_FORMATS = ('pdf', 'tiff', 'png', 'svg')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_files(root: Path) -> list[Path]:
    excluded = {'_generated', '__pycache__', '.pytest_cache'}
    return sorted(
        path for path in root.rglob('*')
        if path.is_file() and not any(part in excluded for part in path.relative_to(root).parts)
    )


def write_manifests(root: Path) -> None:
    third_party = json.loads((root / 'provenance/third_party_sources.json').read_text(encoding='utf-8'))
    rows = []
    for path in public_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in {'MANIFEST.sha256', 'FILE_MANIFEST.csv'}:
            continue
        license_scope = (
            'MIT'
            if path.suffix in {'.py', '.yml', '.yaml'}
            or (rel.startswith('work/') and path.suffix == '.json')
            or rel.startswith('config/')
            or rel == 'LICENSE'
            else 'CC-BY-4.0'
        )
        if rel.startswith('LICENSES/'):
            license_scope = 'license legal text; see LICENSE_SCOPE.md'
        match = next((item for item in third_party if item['file'] == rel), None)
        if match:
            license_scope = match['license'] + ' (upstream copyright)'
        if rel.startswith('third_party/') or '/public_code/' in rel:
            license_scope = 'upstream license; see THIRD_PARTY_NOTICES.md'
        rows.append({
            'file': rel,
            'bytes': path.stat().st_size,
            'sha256': sha256(path),
            'license_scope': license_scope,
        })

    with (root / 'FILE_MANIFEST.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['file', 'bytes', 'sha256', 'license_scope'])
        writer.writeheader()
        writer.writerows(rows)

    checks = [path for path in public_files(root) if path.name != 'MANIFEST.sha256']
    (root / 'MANIFEST.sha256').write_text(
        ''.join(f'{sha256(path)}  {path.relative_to(root).as_posix()}\n' for path in checks),
        encoding='utf-8',
    )


def compare_csvs(left: Path, right: Path) -> None:
    with left.open(encoding='utf-8-sig', newline='') as stream:
        left_rows = list(csv.reader(stream))
    with right.open(encoding='utf-8-sig', newline='') as stream:
        right_rows = list(csv.reader(stream))
    if left_rows != right_rows:
        raise RuntimeError(f'Editor and repository CSV differ: {left.name}')


def frozen_hashes(root: Path) -> dict[str, str]:
    checks = {}
    for line in (root / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        expected, rel = line.split('  ', 1)
        checks[rel] = expected
    return checks


def sync_tables(root: Path, editor: Path) -> None:
    frozen = frozen_hashes(root)
    editor_supp = editor / '04_补充文件/Supplementary_tables_CSV'
    release_supp = root / 'results/supplementary_tables'
    for number in range(1, 54):
        filename = f'S{number:02d}.csv'
        rel = f'results/supplementary_tables/{filename}'
        before = release_supp / filename
        source = editor_supp / filename
        expected = frozen.get(rel)
        if expected is None or not before.is_file() or not source.is_file():
            raise RuntimeError(f'Missing frozen baseline or staged original supplement: {rel}')
        if sha256(before) != expected or sha256(source) != expected:
            raise RuntimeError(f'Original {filename} must remain byte-identical to the frozen package source')

    editor_main = editor / '02_正文表格'
    release_main = root / 'results/main_tables'
    for number in range(1, 7):
        filename = f't{number}.csv'
        source = editor_main / filename
        if not source.is_file():
            raise FileNotFoundError(f'Missing compact editor table: {source}')
        shutil.copy2(source, release_main / filename)
    for number in range(54, 58):
        filename = f'S{number:02d}.csv'
        source = editor_supp / filename
        if not source.is_file():
            raise FileNotFoundError(f'Missing full-table archive from editor: {source}')
        shutil.copy2(source, release_supp / filename)

    for number in range(1, 7):
        filename = f't{number}.csv'
        compare_csvs(editor_main / filename, release_main / filename)
    for number in range(1, 58):
        filename = f'S{number:02d}.csv'
        compare_csvs(editor_supp / filename, release_supp / filename)


def sync_figures(root: Path, editor: Path | None) -> None:
    generated = root / '_generated/figures'
    published = root / 'results/figures'
    published.mkdir(parents=True, exist_ok=True)
    for stem in FIGURE_STEMS:
        for ext in FIGURE_FORMATS:
            src = generated / f'{stem}.{ext}'
            if not src.is_file():
                raise FileNotFoundError(f'Missing generated display figure: {src}')
            if editor is not None and ext in {'png', 'tiff'}:
                editor_image = editor / '03_图片_PDF' / src.name
                if editor_image.is_file() and sha256(editor_image) != sha256(src):
                    raise RuntimeError(f'Editor and reproduction raster differ: {src.name}')
            shutil.copy2(src, published / src.name)
    for ext in FIGURE_FORMATS:
        stale = published / f'fig2_audit_states.{ext}'
        if stale.exists():
            stale.unlink()
    stale_source = published / 'fig2_audit_states_source.csv'
    if stale_source.exists():
        stale_source.unlink()

    fig1_source = generated / 'fig1_score_specific_risk_source.csv'
    fig2_source = generated / 'fig2_heldout_brier_source.csv'
    if not fig1_source.is_file() or not fig2_source.is_file():
        raise FileNotFoundError('Expected Figure 1 and Figure 2 provenance exports under _generated/figures')
    canonical_fig1 = root / 'provenance/fig1_score_specific_risk_source.csv'
    compare_csvs(fig1_source, canonical_fig1)
    shutil.copy2(fig2_source, root / 'provenance/fig2_heldout_brier_source.csv')

    old_policy = root / 'provenance/fig2_audit_states_source.csv'
    new_policy = root / 'provenance/figS1_audit_states_source.csv'
    if old_policy.is_file():
        if new_policy.exists():
            compare_csvs(old_policy, new_policy)
            old_policy.unlink()
        else:
            old_policy.rename(new_policy)

    if editor is not None:
        for filename in ('figure_captions.md', 'figure_captions_中文.md'):
            source = editor / '03_图片_PDF' / filename
            if not source.is_file():
                raise FileNotFoundError(f'Missing editor figure caption: {source}')
            shutil.copy2(source, published / filename)
        shutil.copy2(editor / '03_图片_PDF/figure_captions.md', root / 'docs/figure_captions.md')


def sync_editor_docs(root: Path, editor: Path) -> None:
    files = {
        '04_补充文件/supplementary_methods.md': 'docs/supplementary_methods.md',
        '04_补充文件/supplementary_results.md': 'docs/supplementary_results.md',
        '04_补充文件/supplementary_tables.md': 'docs/supplementary_tables.md',
    }
    for source_rel, target_rel in files.items():
        source = editor / source_rel
        if not source.is_file():
            raise FileNotFoundError(f'Missing editor document: {source}')
        shutil.copy2(source, root / target_rel)

    sync_tables(root, editor)


def update_supplementary_numbering(root: Path) -> None:
    path = root / 'provenance/supplementary_numbering.csv'
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    file_column = 'file'
    existing = {row[file_column] for row in rows}
    archived = [('S54.csv', 't1', 'T1'), ('S55.csv', 't2', 'T2'), ('S56.csv', 't3', 'T3'), ('S57.csv', 't5', 'T5')]
    for filename, source_table, old_number in archived:
        target = f'results/supplementary_tables/{filename}'
        if target in existing:
            continue
        rows.append({
            'display': f'Supplementary Table {int(filename[1:3])}',
            'file': target,
            'old_number': f'Full source {old_number}',
            'derivation': 'Original main-table CSV preserved byte-for-byte before display compaction; row mapping is in display_table_row_mapping.csv.',
            'intermediate_generated_file': target,
        })
        existing.add(target)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_display_row_mapping(root: Path) -> None:
    audit_path = root / '_generated/display_transform_audit.json'
    if not audit_path.is_file():
        raise FileNotFoundError(f'Missing reproducible display-transform audit: {audit_path}')
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    table_to_archive = {'t1': 'S54.csv', 't2': 'S55.csv', 't3': 'S56.csv', 't5': 'S57.csv'}
    rows = []
    for table, mappings in audit.get('row_mappings', {}).items():
        if table == 'supplementary_pivots':
            for supplement, info in mappings.items():
                source_name = info['source_csv']
                for item in info['output_rows']:
                    rows.append({
                        'output_file': 'docs/supplementary_results.md',
                        'output_row': f'{supplement} pivot row {item["output_row"]}',
                        'source_file': f'results/supplementary_tables/{source_name}',
                        'source_data_rows': ';'.join(str(x) for x in item['source_rows']),
                        'transformation': 'Display-only row alignment; source estimates and intervals are copied without reanalysis.',
                    })
            continue
        if table not in {f't{n}' for n in range(1, 7)}:
            raise RuntimeError(f'Unexpected display row-mapping section: {table}')
        archive = table_to_archive.get(table)
        source_file = (
            f'results/supplementary_tables/{archive}' if archive
            else f'Original {table.upper()} reconstructed by the public aggregate table builders'
        )
        for item in mappings:
            rows.append({
                'output_file': f'results/main_tables/{table}.csv',
                'output_row': item['output_row'],
                'source_file': source_file,
                'source_data_rows': ';'.join(str(x) for x in item.get('source_data_rows',[item.get('source_data_row','')])),
                'transformation': 'Display-only compaction; all displayed values retain their frozen source text.',
            })
    target = root / 'provenance/display_table_row_mapping.csv'
    with target.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['output_file', 'output_row', 'source_file', 'source_data_rows', 'transformation'])
        writer.writeheader()
        writer.writerows(rows)


def default_column_info(column: str) -> tuple[str, str]:
    lower = column.lower()
    if 'risk (%)' in lower or 'mortality (%)' in lower:
        meaning = 'Mortality risk in percent, as displayed from the frozen aggregate source.'
    elif 'δ_s' in column or 'delta_s' in lower or '(pp' in lower or 'percentage point' in lower:
        meaning = 'Risk difference in percentage points; source-issued interval and reporting status are retained when shown.'
    elif 'weight' in lower:
        meaning = 'Admission-record weight or share; not a patient share or an external reference-population weight.'
    elif any(token in lower for token in ('record', 'patient', 'death', 'event', 'count', '(n)')):
        meaning = 'Aggregate record, patient, or event count, as identified in the column header.'
    else:
        meaning = 'As stated in the column header or table notes; display values are copied from frozen aggregate summaries.'
    missing = 'Blank, not computed, withheld by policy, and numeric zero are distinct states; preserve the exact source status.'
    return meaning, missing


def update_column_inventory(root: Path) -> None:
    inventory = root / 'docs/column_inventory.csv'
    with inventory.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        old = {(row['file'], row['column']): row for row in reader}
    archive_source = {
        'results/supplementary_tables/S54.csv': 'results/main_tables/t1.csv',
        'results/supplementary_tables/S55.csv': 'results/main_tables/t2.csv',
        'results/supplementary_tables/S56.csv': 'results/main_tables/t3.csv',
        'results/supplementary_tables/S57.csv': 'results/main_tables/t5.csv',
    }
    result_files = sorted((root / 'results/main_tables').glob('t[1-6].csv'))
    result_files += sorted((root / 'results/supplementary_tables').glob('S[0-9][0-9].csv'))
    rows = []
    for path in result_files:
        rel = path.relative_to(root).as_posix()
        prior_file = archive_source.get(rel, rel)
        with path.open(encoding='utf-8-sig', newline='') as stream:
            header = next(csv.reader(stream), [])
        for column in header:
            prior = old.get((prior_file, column)) or old.get((rel, column))
            if prior:
                unit, missing = prior['unit_or_interpretation'], prior['missing_or_refused']
            else:
                unit, missing = default_column_info(column)
            rows.append({
                'file': rel,
                'column': column,
                'unit_or_interpretation': unit,
                'missing_or_refused': missing,
            })
    with inventory.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['file', 'column', 'unit_or_interpretation', 'missing_or_refused'])
        writer.writeheader()
        writer.writerows(rows)


def update_source_maps(root: Path) -> None:
    update_supplementary_numbering(root)
    write_display_row_mapping(root)
    update_column_inventory(root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT, help='release checkout root; defaults to this package')
    parser.add_argument('--editor-root', type=Path, help='optional editor export to compare and copy caption/document files from')
    parser.add_argument('--tables-only', action='store_true', help='copy compact tables after verifying S01-S53 against the frozen manifest; do not update figures, docs, or manifests')
    args = parser.parse_args()
    root = args.repo.resolve()
    editor = args.editor_root.resolve() if args.editor_root else None

    if args.tables_only:
        if editor is None:
            parser.error('--tables-only requires --editor-root')
        sync_tables(root, editor)
        print(json.dumps({'repository': str(root), 'tables_synced': 6, 'supplementary_tables': 57, 'S01_S53_byte_identical': True}, ensure_ascii=False), flush=True)
        return

    sync_figures(root, editor)
    if editor is not None:
        sync_editor_docs(root, editor)
    update_source_maps(root)
    if len(list((root / 'results/main_tables').glob('t[1-6].csv'))) != 6:
        raise RuntimeError('Release must contain exactly six main table CSV files')
    if len(list((root / 'results/supplementary_tables').glob('S[0-9][0-9].csv'))) != 57:
        raise RuntimeError('Release must contain exactly 57 supplementary table CSV files')
    write_manifests(root)
    print(json.dumps({
        'repository': str(root),
        'figures': len(FIGURE_STEMS),
        'figure_formats': list(FIGURE_FORMATS),
        'main_tables': 6,
        'supplementary_tables': 57,
        'manifest_files': len(public_files(root)),
        'editor_checked': editor is not None,
    }, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()

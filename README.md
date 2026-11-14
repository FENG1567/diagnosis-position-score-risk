# Diagnosis position and score-implied mortality risk: reproduction package

This repository accompanies **“Diagnosis Position and Cohort-Dependent Interpretation of Score-Stratified Mortality: A Four-Database Audit Across Five Acute-Care Conditions, Including Acute Pancreatitis.”** The manuscript is prepared for the *Journal of Intensive Care*. Repository: https://github.com/FENG1567/diagnosis-position-score-risk; release: v1.0.0. No article DOI has been assigned.

## What can be reproduced here

The public package supports **aggregate-level reproduction** from the included, author-created frozen summaries. It verifies file checksums, rebuilds six main tables and 57 supplementary tables, rebuilds two main figures and Supplementary Figure S1, and runs the bundled synthetic-data and software tests. It does not include patient-level records, clinical text, raw database files, or private caches. Consequently, rebuilding the published aggregate tables is not an independent patient-level reanalysis and does not recalculate confidence intervals from source records.

The principal comparisons are score-specific mortality risks by diagnosis position for sepsis and pneumonia in eICU and MIMIC-IV. The symbol δ_s denotes an unadjusted, score-specific difference in observed risks; it is not a regression-model estimate. Δ_w denotes a record-weighted summary. The analyses are observational. Zigong diagnosis-group field semantics have not been established well enough for an equivalent primary/secondary interpretation, and BISAP-4 should not be treated as interchangeable with BISAP.

## Requirements and commands

Use Python 3.12 and install the pinned dependencies from the repository root:

    python -m venv .venv
    # Activate the environment using your shell, then:
    python -m pip install -r requirements.txt

Run one of the following from the repository root:

    python reproduce.py verify
    python reproduce.py tables
    python reproduce.py figures
    python reproduce.py test
    python reproduce.py synthetic
    python reproduce.py all

- verify checks MANIFEST.sha256 and the expected table inventory.
- tables reconstructs table outputs from frozen aggregate inputs and compares their cells with the included CSVs.
- figures rebuilds all three figures in PDF, TIFF, PNG and SVG, and checks the scientific source values for Figures 1 and 2; font availability and PDF metadata can affect output bytes.
- test runs the public software tests. One original private-source hash smoke test is explicitly deselected because it requires a restricted Amsterdam patient panel; the test remains supplied for an authorized environment.
- synthetic creates a clearly labeled artificial dataset and runs a demonstration audit; it is not clinical evidence.
- all runs verification, table reconstruction, figure reconstruction, and tests; it does not run the synthetic demonstration.

New files are written under _generated/. These commands require only the files in the package. They do not download data or access an external database.

The complete weighted-summary simulation can be rerun independently, using the supplied frozen seed/design configuration:

    python work/v2/audit/benchmark.py --dry-run
    python work/v2/audit/benchmark.py --output-dir _generated/benchmark
    python work/v2/level_validation/run_per_level_validation.py --output-dir _generated/per_level_validation

These optional simulation runs are more expensive than the public regression suite. Preserve the supplied configuration; outputs under _generated do not overwrite the frozen study summaries. This release was checked using the regression suite and existing frozen aggregates, without repeating the complete simulation benchmark.

## Package layout

- results/main_tables/: six main table CSVs (t1.csv–t6.csv).
- results/supplementary_tables/: 57 supplementary table CSVs (S01.csv–S57.csv).
- results/figures/: two main figures and Supplementary Figure S1, with vector PDF/SVG and 600 dpi LZW TIFF/300 dpi PNG.
- outputs/v2/, outputs/v3/validation/, and outputs/v4/composition/: author-created frozen aggregate inputs used by the audit and reproduction steps.
- provenance/: checksums, source-to-table-cell links, and old-to-current supplementary numbering indexes.
- docs/supplementary_methods.md: methods details for the supplementary analyses.
- work/v2/, work/v3/validation/, work/v4/, and work/v5/: analysis, validation, table/figure, and presentation scripts, respectively.

## Restricted-source reanalysis

A separate guide, [docs/PRIVATE_REANALYSIS.md](docs/PRIVATE_REANALYSIS.md), describes the additional steps for researchers with authorized access to the underlying databases. It lists the relevant source modules and their actual command-line interfaces. There is no single command that reruns every clinical analysis from patient-level data. Access the data directly from its provider and follow the provider's current terms:

- [eICU Collaborative Research Database](https://physionet.org/content/eicu-crd/)
- [MIMIC-IV](https://physionet.org/content/mimiciv/)
- [MIMIC-III](https://physionet.org/content/mimiciii/)
- [Zigong ICU Infection Database, version 1.1](https://physionet.org/content/icu-infection-zigong-fourth/1.1/)
- [AmsterdamUMCdb](https://amsterdammedicaldatascience.nl/)

Raw database files, patient-level extracts, caches, and clinical text are intentionally excluded from this repository and are not covered by the licenses below.

## Licenses

Original code is released under the MIT License. Author-created aggregate summaries and documentation are released under CC BY 4.0. Third-party SQL and dictionary files retain their own licenses and is not relicensed here. Neither license grants access to restricted source datasets or covers patient-level data, caches, or clinical text.

## Citation and contact

Citation metadata is in [CITATION.cff](CITATION.cff). Correspondence: Liwei Liu, [18940835066@163.com](mailto:18940835066@163.com).


The current display numbering matches the 2026-11-15 manuscript. The 57 supplementary CSVs are byte-identical to the preceding display release after renumbering; `provenance/manuscript_supplement_mapping.json` maps prior to current numbers. The original full main Tables 1, 2, 3 and 5 are now Supplementary Tables 16, 17, 27 and 46. Historical provenance files retain their original identifiers unless a current-number column is provided; consult the mapping before using them. The aggregate builders reconstruct the original presentation, then compare the displayed tables using this mapping.

The current figure entry point is `work/publication_v12/build_figures.py`. It preserves the final layout and values. Archived publication files use Arial Bold; regeneration uses installed Arial when available, with Liberation Sans or DejaVu Sans as a portable fallback. Proprietary fonts are not included. To select Arial explicitly, invoke the figure script with `--arial-regular` and `--arial-bold` font-file paths, alongside `--levels`, `--s46` (current S25.csv) and `--out`. Font substitution and export metadata can change appearance and file bytes; source-value validation is separate. Earlier display scripts remain supplied as historical source.

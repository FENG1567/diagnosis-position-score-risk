# Reproducibility status

Release v1.0.0 uses the 2026-11-15 manuscript numbering and final figure layout. It contains six main and 57 supplementary tables and three figures in four formats. All 57 supplementary CSVs preserve their previous bytes after renumbering; the six main CSVs preserve their cell values. The public commands reconstruct aggregate outputs and validate table cells and scientific figure sources. The public software suite excludes one test requiring a restricted Amsterdam patient-panel hash. Patient-level clinical analyses and the complete simulation benchmark are not rerun by `reproduce.py all`.

The distributed figures use Arial Bold. Regeneration selects installed Arial, otherwise Liberation Sans or DejaVu Sans. Font substitution and PDF metadata can alter bytes and appearance. No proprietary font files are included. Final release verification results are recorded in `verification/public_release_checks.json`; GitHub Actions also runs the public commands.

Verification completed on 2026-11-15: 6 main and 57 supplementary table comparisons passed; all three figures rebuilt in four formats with source-value and layout checks passed; 78 software tests and 2 subtests passed, with one restricted-data test deselected. The synthetic demonstration also completed.

Verification completed on 2026-11-15: 6 main and 57 supplementary table comparisons passed; all three figures rebuilt in four formats with source-value and layout checks passed; 78 software tests and 2 subtests passed, with one restricted-data test deselected. The synthetic demonstration also completed.

Verification completed on 2026-11-15: 6 main and 57 supplementary table comparisons passed; all three figures rebuilt in four formats with source-value and layout checks passed; 78 software tests and 2 subtests passed, with one restricted-data test deselected. The synthetic demonstration also completed.

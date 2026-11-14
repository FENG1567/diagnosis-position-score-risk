# Figure source map

| Figure | Current input | Selection and quantity |
| --- | --- | --- |
| 1 | provenance/fig1_score_specific_risk_source.csv | All 20 source–condition–score rows; observed risks, score-specific δ_s, reported confidence intervals and record counts |
| 2 | results/supplementary_tables/S25.csv | Interval=pointwise_95pct; primary_fixed_minus_broad_fixed and primary_recalibrated_minus_broad_recalibrated; all/primary/never_primary; 24 rows; Brier difference ×1,000 |
| S1 | provenance/figS1_audit_states_source.csv; work/v2/audit/cohort_definition_audit.py and protocol.md | Reporting criteria for the record-weighted summary; three point/interval reporting states |

The current plotting entry point is `work/publication_v12/build_figures.py`; `python reproduce.py figures` invokes it. Its historical argument `--s46` now receives current S25.csv. Complete prediction metrics and hospital sensitivities are in current S23–S26 (prior S46–S49; see the old-to-current mapping for the exact order). Main-table row mappings are in `provenance/display_table_row_mapping.csv`, and current output-column descriptions are in `docs/column_inventory.csv`.

`provenance/manuscript_supplement_mapping.json` maps preceding display numbers to current manuscript numbers. Original analysis output paths and source row identifiers retain their historical meaning. Archived publication figures use Arial Bold; regeneration uses installed Arial or the documented font fallback, with all numerical sources preserved.

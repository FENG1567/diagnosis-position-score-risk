# Data dictionary

The six main table files and 57 final supplementary table files preserve the published columns and display precision. See column_inventory.csv for every final column and docs/supplementary_results.md for the full table index. Units are retained in the headers and the corresponding methods/table notes; the inventory is not a replacement for those definitions.

- One clinical record is one hospital admission indexed to its earliest eligible ICU episode. A patient can contribute several records and appear in both source-defined groups. Counts of patients and records are different quantities.
- `delta_s`, `diff_pp` or δ_s is never-primary minus primary observed mortality at score s; group meanings remain source-specific. Δ_w is a record-weighted summary over common support, never a score-specific risk.
- Risks reported as percentages must not be mixed with probability-scale source values. Differences labelled pp are percentage points. Weights are pooled record shares, not patient shares or an external reference population.
- Missing outcomes/components, unsupported scores, policy refusal, and numerical zero are different states. Preserve labels and interval-status fields.
- Brier/log-loss differences in S46 are prediction-loss contrasts, not δ_s or Δ_w. Positive primary-minus-broad loss favors broad training; positive recalibrated-minus-fixed loss indicates greater loss after recalibration.
- CIs are pointwise unless explicitly marked otherwise. Perturbation ranges and missing-score identification bounds are not CIs. θ_D is a distinct conditional-design target.
- Zigong sequence-one/other-sequence contrasts do not establish principal-diagnosis meaning. BISAP-4 omits pleural effusion and is not BISAP. Heart-failure/COPD qSOFA uses are outside the intended population.
- Synthetic data are produced on demand only; their identifiers start SYNTHETIC and do not represent individuals.

Detailed selection, inference, outcome, timing, source semantics and limitations are in supplementary_methods.md. Frozen source inputs under outputs/ are authors' aggregate exports only; source access conditions are described in PRIVATE_REANALYSIS.md.


The current display layer preserves the original S01–S53 bytes. Detailed original main Tables 1, 2, 3 and 5 are supplied as S54–S57; compact main tables remain t1–t6. Figure 2 plots 24 pointwise S46 Brier contrasts; the audit-policy diagram is Supplementary Figure S1. The display transformation is in work/display_v7/compact_tables.py and work/display_v7/build_figures.py. All numerical estimates are copied from the supplied aggregate sources; no model is fitted by the display layer.

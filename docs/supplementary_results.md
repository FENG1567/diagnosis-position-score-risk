# Supplementary results

Full row-level admission pathways and diagnosis counts are available in S05.csv and S06.csv; their long listings are not repeated in this reader. Detailed score-level, cohort-flow, paired-refinement, and selected strategy results are supplied in S16–S46. The displays below compactly align selected source rows.

## Supplementary table index

| Table | Subject | Rows | Columns | CSV |
| --- | --- | --- | --- | --- |
| 1 | Source flow and patient-level sensitivities | 118 | 14 | S01.csv |
| 2 | eICU diagnosis-group counts | 75 | 13 | S02.csv |
| 3 | eICU reconstructed score availability | 25 | 7 | S03.csv |
| 4 | Main-cohort demographics and analytic overlap; counts, not δ_s or weighted summary Δ_w | 8 | 8 | S04.csv |
| 5 | Source-specific admission pathways; counts, not δ_s or weighted summary Δ_w | 86 | 8 | S05.csv |
| 6 | Leading priority or billing diagnoses; counts, not δ_s or weighted summary Δ_w | 48 | 7 | S06.csv |
| 7 | Zigong heart-failure application; diagnosis-sequence semantics unverified | 1 | 9 | S07.csv |
| 8 | Zigong documented discharge-status combinations | 20 | 2 | S08.csv |
| 9 | Zigong discharge status and follow-up death timing | 6 | 3 | S09.csv |
| 10 | Zigong laboratory measurement units | 4 | 3 | S10.csv |
| 11 | Zigong field-group score and outcome availability; diagnosis-sequence semantics unverified | 10 | 8 | S11.csv |
| 12 | Counts by score and diagnosis group | 84 | 6 | S12.csv |
| 13 | Measurement eligibility and selection counts | 9 | 7 | S13.csv |
| 14 | MIMIC-IV reconstructed score coverage | 160 | 16 | S14.csv |
| 15 | MIMIC-III reconstructed score coverage | 160 | 16 | S15.csv |
| 16 | Full score-level observed mortality risks and δ_s in the four primary analysis groups | 20 | 12 | S16.csv |
| 17 | Full database-condition cohort eligibility, complete-score support, and Δ_w summaries | 19 | 9 | S17.csv |
| 18 | Separate score-level missingness identification bounds | 92 | 14 | S18.csv |
| 19 | Perturbation ranges when score-level intervals are withheld | 20 | 11 | S19.csv |
| 20 | Weighted-summary interval refusals by reporting policy | 19 | 25 | S20.csv |
| 21 | Bonferroni score-level δ_s intervals | 20 | 16 | S21.csv |
| 22 | Bonferroni interval-emission summary | 5 | 8 | S22.csv |
| 23 | Role-specific cohort selection counts, not δ_s or weighted summary Δ_w | 36 | 10 | S23.csv |
| 24 | Panel-level split rules and exclusions, not δ_s or weighted summary Δ_w | 17 | 4 | S24.csv |
| 25 | Paired held-out Brier loss differences, not δ_s or weighted summary Δ_w | 56 | 8 | S25.csv |
| 26 | Held-out observed risks, prediction means and loss, not δ_s or weighted summary Δ_w | 48 | 10 | S26.csv |
| 27 | Full paired code-breadth and refinement comparisons | 12 | 9 | S27.csv |
| 28 | Matched-record score-construction contrasts | 6 | 10 | S28.csv |
| 29 | Score-construction weighted summaries Δ_w | 9 | 16 | S29.csv |
| 30 | Patient and hospital clustering sensitivity for weighted summary Δ_w | 10 | 19 | S30.csv |
| 31 | Paired eICU documentation-timing contrasts | 2 | 7 | S31.csv |
| 32 | eICU 24-hour hospital-survivor sensitivity | 4 | 8 | S32.csv |
| 33 | ED-linked cohort component completeness | 16 | 14 | S33.csv |
| 34 | ED-linked cohort weighted summaries Δ_w | 8 | 36 | S34.csv |
| 35 | Linked ED episode counts | 12 | 10 | S35.csv |
| 36 | ED linkage eligibility | 8 | 5 | S36.csv |
| 37 | ED-linked score-level risks and δ_s | 40 | 26 | S37.csv |
| 38 | ED linkage coverage | 2 | 32 | S38.csv |
| 39 | Patient-cluster bootstrap precision analyses | 23 | 63 | S39.csv |
| 40 | Conditional-design θ_D intervals in clinical applications | 22 | 26 | S40.csv |
| 41 | Conditional-design interval simulation results | 26 | 39 | S41.csv |
| 42 | Numerical design inventory for δ_s and Δ_w weighted-summary validation | 11 | 10 | S42.csv |
| 43 | Full simulation simulation policy results | 66 | 22 | S43.csv |
| 44 | Paired simulation strategy comparisons | 66 | 18 | S44.csv |
| 45 | Full sparse-boundary strategy results | 8 | 13 | S45.csv |
| 46 | Full selected audit-strategy and sparse-boundary interval validation results | 21 | 10 | S46.csv |
| 47 | Score-level simultaneous coverage diagnostics | 11 | 13 | S47.csv |
| 48 | Score-level interval validation by design and method | 22 | 20 | S48.csv |
| 49 | Score-level interval precision sensitivity | 135 | 22 | S49.csv |
| 50 | Score-level interval refusal frequencies | 146 | 9 | S50.csv |
| 51 | Score-level coverage sensitivity to rounding | 16 | 12 | S51.csv |
| 52 | Score-level δ_s validation results | 135 | 44 | S52.csv |
| 53 | Adapted PEER-cohort weighted summary Δ_w | 1 | 19 | S53.csv |
| 54 | Amsterdam weighted summary Δ_w by GCS definition and interval method | 4 | 6 | S54.csv |
| 55 | Amsterdam score-level δ_s for GCS ≤13 | 2 | 18 | S55.csv |
| 56 | Amsterdam score-level δ_s for GCS <15 | 2 | 18 | S56.csv |
| 57 | Amsterdam observed mortality by reconstructed qSOFA | 5 | 6 | S57.csv |



## Supplementary Table 4. Composition of the complete main cohorts

Counts are admission records unless a patient count is specified. The pathway and diagnosis-label inventories are supplied in S05.csv and S06.csv; their row totals are listed in the index above.

| Database | Condition | Group | Records | Patients | Age ≥65 / known | Male / known sex | Also in other complete main cohort |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eICU | sepsis | primary | 10467 | 9804 | 5895 / 10462 | 5419 / 10466 | 3274 |
| eICU | sepsis | never-primary | 6109 | 5867 | 3372 / 6107 | 3248 / 6109 | 1897 |
| eICU | pneumonia | primary | 2645 | 2555 | 1540 / 2645 | 1376 / 2645 | 558 |
| eICU | pneumonia | never-primary | 8836 | 8352 | 5103 / 8836 | 4861 / 8835 | 4613 |
| MIMIC-IV | sepsis | primary | 6679 | 5964 | 4199 / 6679 | 3555 / 6679 | 2643 |
| MIMIC-IV | sepsis | never-primary | 4125 | 3872 | 2347 / 4125 | 2361 / 4125 | 1645 |
| MIMIC-IV | pneumonia | primary | 1640 | 1498 | 1110 / 1640 | 927 / 1640 | 121 |
| MIMIC-IV | pneumonia | never-primary | 10862 | 9847 | 6652 / 10862 | 6219 / 10862 | 4167 |

## Supplementary Table 23. Cohort flow by diagnosis group and data role

Within each role, the flow is panel records → known group and outcome → complete scores, with patients, events, and hospital counts retained in the complete S23 CSV.

| Database | Condition | Diagnosis group | Train flow | Recalibration flow | Test flow |
| --- | --- | --- | --- | --- | --- |
| MIMIC-IV | pneumonia | all | 4969 → 4969 → 3824 | 2163 → 2163 → 1464 | 6093 → 6093 → 4228 |
| MIMIC-IV | pneumonia | never_primary | 4071 → 4071 → 3049 | 1999 → 1999 → 1338 | 5703 → 5703 → 3912 |
| MIMIC-IV | pneumonia | primary | 898 → 898 → 775 | 164 → 164 → 126 | 390 → 390 → 316 |
| MIMIC-IV | sepsis | all | 3464 → 3350 → 2634 | 1861 → 1830 → 1339 | 5229 → 5229 → 3816 |
| MIMIC-IV | sepsis | never_primary | 1328 → 1328 → 1049 | 611 → 611 → 459 | 2133 → 2133 → 1571 |
| MIMIC-IV | sepsis | primary | 2022 → 2022 → 1585 | 1219 → 1219 → 880 | 3096 → 3096 → 2245 |
| eICU | pneumonia | all | 11088 → 10953 → 6607 | 3585 → 3568 → 2068 | 3552 → 3492 → 2235 |
| eICU | pneumonia | never_primary | 8346 → 8261 → 5166 | 2736 → 2721 → 1666 | 2406 → 2369 → 1535 |
| eICU | pneumonia | primary | 2742 → 2692 → 1441 | 849 → 847 → 402 | 1146 → 1123 → 700 |
| eICU | sepsis | all | 14199 → 14029 → 9449 | 4968 → 4944 → 3361 | 4145 → 4089 → 2897 |
| eICU | sepsis | never_primary | 5329 → 5279 → 3725 | 1618 → 1611 → 1223 | 1174 → 1153 → 874 |
| eICU | sepsis | primary | 8860 → 8750 → 5724 | 3349 → 3333 → 2138 | 2965 → 2936 → 2023 |

## Supplementary Table 24. Data splitting and role assignment

Each rule applies to the combined supplied panel before disease-specific complete-record selection. Full scope fields remain in S24.csv.

| Database | Panel-level split field | Recorded value |
| --- | --- | --- |
| eICU | split_method | SHA-256 hospital buckets (60% train / 20% recalibration / 20% test); globally exclude patients with cross-role, multihospital, or missing-hospital records |
| eICU | seed | JCE-v3-20261113 |
| eICU | hospitals_total | 205 |
| eICU | hospitals_by_role | {"test": 40, "recalibration": 44, "train": 121} |
| eICU | cross_role_patients_excluded | 737 |
| eICU | patients_with_missing_hospital_excluded | 0 |
| eICU | multi_hospital_patients_excluded_globally | 1199 |
| eICU | multi_hospital_patient_records_excluded_globally | 4426 |
| eICU | patient_count | 45922 |
| MIMIC-IV | split_method | calendar-interval migration split from anchor_year_group plus admission-year shift; intervals wholly <=2013=train, 2014-2016=recalibration, 2017-2022=test; ambiguous/out-of-window records excluded |
| MIMIC-IV | seed | JCE-v3-20261113 |
| MIMIC-IV | temporal_metadata_identifiable | True |
| MIMIC-IV | anchor_year_groups | ["2008 - 2010", "2011 - 2013", "2014 - 2016", "2017 - 2019", "2020 - 2022"] |
| MIMIC-IV | calendar_windows | {"train": "entire possible admission interval <= 2013", "recalibration": "2014-2016", "test": "2017-2022"} |
| MIMIC-IV | unresolved_or_ambiguous_records | 13689 |
| MIMIC-IV | cross_role_patients_excluded | 756 |
| MIMIC-IV | patient_count | 33769 |

## Supplementary Table 25. Held-out Brier-loss differences

Prediction-loss differences are not score-level δ_s or the record-weighted summary Δ_w. Values are copied as source estimates with their pointwise 95% confidence intervals.

| Database | Condition | Test population | Primary-only fixed − broad fixed | Primary-only recalibrated − broad recalibrated | Primary-only recalibrated − fixed | Broad recalibrated − fixed |
| --- | --- | --- | --- | --- | --- | --- |
| MIMIC-IV | pneumonia | all | 0.007381 [0.005685, 0.009095] | 0.000471 [-0.000456, 0.001347] | -0.007420 [-0.010095, -0.004820] | -0.000510 [-0.001050, 0.000000] |
| MIMIC-IV | pneumonia | never_primary | 0.008566 [0.006785, 0.010350] | 0.000353 [-0.000582, 0.001256] | -0.009067 [-0.011849, -0.006446] | -0.000854 [-0.001415, -0.000317] |
| MIMIC-IV | pneumonia | primary | -0.007298 [-0.011632, -0.002597] | 0.001928 [-0.001133, 0.004863] | 0.012975 [0.004574, 0.020642] | 0.003749 [0.002108, 0.005243] |
| MIMIC-IV | sepsis | all | 0.001899 [0.000515, 0.003197] | -0.000247 [-0.001355, 0.000922] | -0.001793 [-0.002748, -0.000795] | 0.000353 [-0.000012, 0.000711] |
| MIMIC-IV | sepsis | never_primary | 0.008808 [0.006410, 0.011224] | 0.000589 [-0.001227, 0.002472] | -0.006180 [-0.007742, -0.004534] | 0.002039 [0.001413, 0.002627] |
| MIMIC-IV | sepsis | primary | -0.002936 [-0.004461, -0.001422] | -0.000832 [-0.002269, 0.000703] | 0.001277 [0.000022, 0.002471] | -0.000827 [-0.001267, -0.000374] |
| eICU | pneumonia | all | 0.002412 [0.000862, 0.004033] | 0.000024 [-0.000217, 0.000272] | -0.002308 [-0.004157, -0.000460] | 0.000081 [-0.000326, 0.000484] |
| eICU | pneumonia | never_primary | 0.003015 [0.001060, 0.004976] | 0.000007 [-0.000295, 0.000309] | -0.003065 [-0.005338, -0.000816] | -0.000057 [-0.000554, 0.000434] |
| eICU | pneumonia | primary | 0.001090 [-0.001503, 0.003742] | 0.000060 [-0.000347, 0.000465] | -0.000649 [-0.003770, 0.002333] | 0.000381 [-0.000306, 0.001040] |
| eICU | sepsis | all | 0.000056 [-0.000063, 0.000167] | 0.000009 [-0.000021, 0.000039] | -0.000035 [-0.000117, 0.000057] | 0.000012 [-0.000034, 0.000053] |
| eICU | sepsis | never_primary | -0.000081 [-0.000299, 0.000135] | 0.000055 [-0.000001, 0.000110] | 0.000087 [-0.000076, 0.000253] | -0.000049 [-0.000132, 0.000033] |
| eICU | sepsis | primary | 0.000116 [-0.000019, 0.000246] | -0.000011 [-0.000048, 0.000026] | -0.000088 [-0.000187, 0.000015] | 0.000039 [-0.000013, 0.000089] |

### Hospital-cluster pointwise intervals (eight source contrasts)

| Database | Condition | Test population | Contrast | Brier loss difference [95% CI] |
| --- | --- | --- | --- | --- |
| eICU | sepsis | all | primary_fixed_minus_broad_fixed | 0.000056 [-0.000109, 0.000222] |
| eICU | sepsis | all | primary_recalibrated_minus_broad_recalibrated | 0.000009 [-0.000020, 0.000045] |
| eICU | sepsis | all | primary_recalibrated_minus_fixed | -0.000035 [-0.000155, 0.000083] |
| eICU | sepsis | all | broad_recalibrated_minus_fixed | 0.000012 [-0.000047, 0.000072] |
| eICU | pneumonia | all | primary_fixed_minus_broad_fixed | 0.002412 [-0.000064, 0.004949] |
| eICU | pneumonia | all | primary_recalibrated_minus_broad_recalibrated | 0.000024 [-0.000263, 0.000269] |
| eICU | pneumonia | all | primary_recalibrated_minus_fixed | -0.002308 [-0.005378, 0.000657] |
| eICU | pneumonia | all | broad_recalibrated_minus_fixed | 0.000081 [-0.000625, 0.000777] |

## Supplementary Table 26. Observed and predicted mortality in held-out groups

All risk values are percentages. Columns compare four mappings on the same test records. Complete Brier/log loss and calibration intercept/slope metrics remain in S26.csv.

| Source / condition | Test population | Records | Observed risk (%) | Primary fixed (%) | Broad fixed (%) | Primary recalibrated (%) | Broad recalibrated (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MIMIC-IV / pneumonia | all | 4228 | 21.24 | 12.48 | 19.28 | 21.28 | 21.18 |
| MIMIC-IV / pneumonia | never_primary | 3912 | 22.03 | 12.44 | 19.23 | 21.21 | 21.14 |
| MIMIC-IV / pneumonia | primary | 316 | 11.39 | 13.03 | 19.79 | 22.08 | 21.73 |
| MIMIC-IV / sepsis | all | 3816 | 26.23 | 21.36 | 25.70 | 24.70 | 24.42 |
| MIMIC-IV / sepsis | never_primary | 1571 | 32.72 | 20.85 | 25.35 | 24.14 | 24.08 |
| MIMIC-IV / sepsis | primary | 2245 | 21.69 | 21.71 | 25.94 | 25.09 | 24.65 |
| eICU / pneumonia | all | 2235 | 16.55 | 12.39 | 16.50 | 17.61 | 17.63 |
| eICU / pneumonia | never_primary | 1535 | 17.59 | 12.70 | 16.94 | 18.03 | 18.10 |
| eICU / pneumonia | primary | 700 | 14.29 | 11.69 | 15.53 | 16.67 | 16.61 |
| eICU / sepsis | all | 2897 | 17.57 | 18.44 | 18.04 | 18.18 | 18.17 |
| eICU / sepsis | never_primary | 874 | 19.22 | 18.65 | 18.25 | 18.38 | 18.38 |
| eICU / sepsis | primary | 2023 | 16.86 | 18.35 | 17.95 | 18.09 | 18.08 |

## Supplementary Table 42. Numerical simulation designs

Panel A describes sampling and dependence; Panel B describes diagnosis–score probabilities and outcome risks. Vectors follow the listed score order. Group 0 is primary; group 1 is never-primary. Cluster-size probabilities refer to patients. The latent Gaussian parameter is not the binary-outcome correlation. All values are copied from S42.csv.

### A. Sampling and dependence

| Design | Patients | Records per patient: value/probability | Latent Gaussian dependence parameter | Score values | Prespecified support |
| --- | --- | --- | --- | --- | --- |
| null_balanced_iid | 1000 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| null_heterogeneous_iid | 1200 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| heterogeneous_random_weights | 1200 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| repeated_admissions_cross_group | 900 | [[3, 1.0]] | 0.3 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| unequal_cluster_sizes | 800 | [[1, 0.55], [2, 0.25], [4, 0.15], [8, 0.05]] | 0.35 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| near_boundary_risks | 1800 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| partial_structural_support | 1000 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3, 4, 5] | [2, 3] |
| rare_common_support_holdout | 800 | [[1, 1.0]] | 0.0 | [0, 1, 2] | [0, 1, 2] |
| few_large_clusters | 16 | [[10, 1.0]] | 0.4 | [0, 1, 2, 3] | [0, 1, 2, 3] |
| no_common_support | 1000 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [] |
| high_icc_unbalanced_holdout | 800 | [[1, 0.7], [10, 0.3]] | 0.6 | [0, 1, 2, 3] | [0, 1, 2, 3] |

### B. Group–score composition and outcome risks

| Design | P(group0,score) | P(group1,score) | Primary risk vector | Never-primary risk vector |
| --- | --- | --- | --- | --- |
| null_balanced_iid | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.1, 0.2, 0.3, 0.4] |
| null_heterogeneous_iid | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.1, 0.4, 0.3] |
| heterogeneous_random_weights | [0.32, 0.1, 0.05, 0.03] | [0.05, 0.1, 0.12, 0.23] | [0.1, 0.4, 0.15, 0.35] | [0.3, 0.2, 0.25, 0.1] |
| repeated_admissions_cross_group | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.25, 0.35, 0.5] |
| unequal_cluster_sizes | [0.2, 0.15, 0.1, 0.05] | [0.05, 0.1, 0.15, 0.2] | [0.08, 0.2, 0.35, 0.5] | [0.18, 0.3, 0.25, 0.6] |
| near_boundary_risks | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.005, 0.02, 0.65, 0.85] | [0.01, 0.025, 0.7, 0.8] |
| partial_structural_support | [0.1, 0.1, 0.15, 0.15, 0.0, 0.0] | [0.0, 0.0, 0.1, 0.1, 0.15, 0.15] | [0.1, 0.15, 0.2, 0.25, 0.3, 0.35] | [0.08, 0.1, 0.4, 0.45, 0.3, 0.5] |
| rare_common_support_holdout | [0.249, 0.249, 0.002] | [0.249, 0.249, 0.002] | [0.1, 0.2, 0.3] | [0.15, 0.25, 0.35] |
| few_large_clusters | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.25, 0.35, 0.5] |
| no_common_support | [0.25, 0.25, 0.0, 0.0] | [0.0, 0.0, 0.25, 0.25] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.25, 0.35, 0.5] |
| high_icc_unbalanced_holdout | [0.25, 0.15, 0.07, 0.03] | [0.03, 0.07, 0.15, 0.25] | [0.15, 0.3, 0.45, 0.6] | [0.2, 0.2, 0.5, 0.55] |

## Supplementary Figure S1. Criteria for reporting the record-weighted summary Δ_w and its confidence interval

![Supplementary Figure S1](Supplementary_figure_S1/figS1_audit_states.png)

**Supplementary Figure S1.** The prespecified criteria distinguish three reporting states. Invalid required inputs or no shared score level produce no point estimate or confidence interval (CI). Otherwise, loss of target score support or unmet interval criteria retains the observed-support point estimate without a CI. Criteria require ≥20 records per score level, ≥10 records and ≥20 distinct patients per score-by-group cell, ≥20 patients overall, and at least one death and one survivor in every target cell. Patient-cluster resampling uses 60 draws; a usable draw retains every target score and ≥10 deaths in each diagnosis group over common support; ≥20 usable draws are required. CIs use a normal influence-function approximation; resampling determines whether a CI is reported.

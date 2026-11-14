# Supplementary tables

All Zigong primary/never-primary labels denote unqualified sequence-one/other-sequence field groups. Δ_w denotes a weighted summary; patient clustering does not change the record-weighted target.



## Supplementary Table 1. Source flow and patient-level sensitivities

| Database | Condition | Row type | Group / analysis | Records / source n | Patients | Score complete | Outcome known | Analyzed | Δ_w (pp) | CI lower (pp) | CI upper (pp) | Interval status | Selection rule / estimand |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | Eligibility flow | primary | 16,101 | 14,878 | 10,564 | 15,931 | 10,467 |  |  |  |  |  |
| eICU-CRD | sepsis | Eligibility flow | never-primary | 8,563 | 8,204 | 6,166 | 8,478 | 6,109 |  |  |  |  |  |
| eICU-CRD | pneumonia | Eligibility flow | primary | 4,955 | 4,737 | 2,684 | 4,876 | 2,645 |  |  |  |  |  |
| eICU-CRD | pneumonia | Eligibility flow | never-primary | 14,313 | 13,360 | 8,928 | 14,166 | 8,836 |  |  |  |  |  |
| eICU-CRD | pancreatitis | Eligibility flow | primary | 255 | 247 | 154 | 254 | 153 |  |  |  |  |  |
| eICU-CRD | pancreatitis | Eligibility flow | never-primary | 346 | 340 | 202 | 342 | 198 |  |  |  |  |  |
| eICU-CRD | heart failure | Eligibility flow | primary | 4,507 | 4,173 | 2,568 | 4,472 | 2,548 |  |  |  |  |  |
| eICU-CRD | heart failure | Eligibility flow | never-primary | 11,055 | 10,073 | 7,073 | 10,919 | 6,992 |  |  |  |  |  |
| eICU-CRD | COPD | Eligibility flow | primary | 2,617 | 2,344 | 1,550 | 2,598 | 1,541 |  |  |  |  |  |
| eICU-CRD | COPD | Eligibility flow | never-primary | 10,026 | 8,756 | 6,218 | 9,927 | 6,162 |  |  |  |  |  |
| eICU-CRD | sepsis | Sensitivity | one record per patient | 15,217 | 15,217 |  |  |  | -0.10 | -1.34 | 1.14 | computed | one admission per patient selected by prespecified hash |
| eICU-CRD | sepsis | Sensitivity | patient-weighted supported-admission sensitivity | 16,576 | 15,217 |  |  |  | -0.01 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| eICU-CRD | sepsis | Sensitivity | qsofa_gcs15 | 16,576 | 15,217 |  |  |  | 0.24 | — | — | not computed (degenerate_outcome_cell) | Delta_w weighted summary |
| eICU-CRD | pneumonia | Sensitivity | one record per patient | 10,724 | 10,724 |  |  |  | 3.77 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| eICU-CRD | pneumonia | Sensitivity | patient-weighted supported-admission sensitivity | 11,481 | 10,724 |  |  |  | 3.87 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| eICU-CRD | pancreatitis | Sensitivity | one record per patient | 343 | 343 |  |  |  | 1.11 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| eICU-CRD | pancreatitis | Sensitivity | patient-weighted supported-admission sensitivity | 351 | 343 |  |  |  | 0.79 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| eICU-CRD | heart failure | Sensitivity | one record per patient | 8,611 | 8,611 |  |  |  | 3.28 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| eICU-CRD | heart failure | Sensitivity | patient-weighted supported-admission sensitivity | 9,540 | 8,611 |  |  |  | 3.45 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| eICU-CRD | heart failure | Sensitivity | qsofa_gcs15 | 9,540 | 8,611 |  |  |  | 3.59 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| eICU-CRD | COPD | Sensitivity | one record per patient | 6,711 | 6,711 |  |  |  | 4.68 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| eICU-CRD | COPD | Sensitivity | patient-weighted supported-admission sensitivity | 7,703 | 6,711 |  |  |  | 4.72 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| eICU-CRD | COPD | Sensitivity | qsofa_gcs15 | 7,703 | 6,711 |  |  |  | 4.33 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | sepsis | Eligibility flow | primary | 8,756 | 7,764 | 6,679 | 8,756 | 6,679 |  |  |  |  |  |
| MIMIC-IV | sepsis | Eligibility flow | never-primary | 5,366 | 5,024 | 4,125 | 5,366 | 4,125 |  |  |  |  |  |
| MIMIC-IV | pneumonia | Eligibility flow | primary | 1,936 | 1,755 | 1,640 | 1,936 | 1,640 |  |  |  |  |  |
| MIMIC-IV | pneumonia | Eligibility flow | never-primary | 15,087 | 13,441 | 10,862 | 15,087 | 10,862 |  |  |  |  |  |
| MIMIC-IV | pancreatitis | Eligibility flow | primary | 476 | 440 | 389 | 476 | 389 |  |  |  |  |  |
| MIMIC-IV | pancreatitis | Eligibility flow | never-primary | 922 | 881 | 678 | 922 | 678 |  |  |  |  |  |
| MIMIC-IV | heart failure | Eligibility flow | primary | 2,941 | 2,427 | 2,760 | 2,941 | 2,760 |  |  |  |  |  |
| MIMIC-IV | heart failure | Eligibility flow | never-primary | 19,721 | 15,229 | 16,514 | 19,721 | 16,514 |  |  |  |  |  |
| MIMIC-IV | COPD | Eligibility flow | primary | 489 | 391 | 440 | 489 | 440 |  |  |  |  |  |
| MIMIC-IV | COPD | Eligibility flow | never-primary | 11,410 | 8,909 | 9,619 | 11,410 | 9,619 |  |  |  |  |  |
| MIMIC-IV | sepsis | Sensitivity | one record per patient | 9,398 | 9,398 |  |  |  | 11.80 | 9.98 | 13.61 | computed | chronological first eligible admission |
| MIMIC-IV | sepsis | Sensitivity | patient-weighted supported-admission sensitivity | 10,804 | 9,398 |  |  |  | 12.15 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-IV | sepsis | Sensitivity | qsofa_gcs15 | 10,804 | 9,398 |  |  |  | 11.23 | — | — | not computed (degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | sepsis | Sensitivity | qsofa_ett_as1 | 13,924 | 11,999 |  |  |  | 9.19 | 7.66 | 10.73 | computed | Delta_w weighted summary |
| MIMIC-IV | sepsis | Sensitivity | qsofa_gcs15_ett_as1 | 13,924 | 11,999 |  |  |  | 9.33 | — | — | not computed (degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | pneumonia | Sensitivity | one record per patient | 10,976 | 10,976 |  |  |  | 9.00 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-IV | pneumonia | Sensitivity | patient-weighted supported-admission sensitivity | 12,502 | 10,976 |  |  |  | 8.87 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-IV | pneumonia | Sensitivity | curb65_ett_as1 | 16,531 | 14,331 |  |  |  | 9.71 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | pancreatitis | Sensitivity | one record per patient | 981 | 981 |  |  |  | 6.95 | 2.69 | 11.20 | computed | chronological first eligible admission |
| MIMIC-IV | pancreatitis | Sensitivity | patient-weighted supported-admission sensitivity | 1,067 | 988 |  |  |  | 6.38 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-IV | pancreatitis | Sensitivity | bisap4_ett_as1 | 1,291 | 1,185 |  |  |  | 6.12 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | heart failure | Sensitivity | one record per patient | 14,338 | 14,338 |  |  |  | 0.28 | -1.36 | 1.91 | computed | chronological first eligible admission |
| MIMIC-IV | heart failure | Sensitivity | patient-weighted supported-admission sensitivity | 19,274 | 14,338 |  |  |  | -0.77 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-IV | heart failure | Sensitivity | qsofa_gcs15 | 19,274 | 14,338 |  |  |  | 0.02 | — | — | not computed (degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | heart failure | Sensitivity | qsofa_ett_as1 | 22,350 | 16,461 |  |  |  | 0.80 | -0.73 | 2.33 | computed | Delta_w weighted summary |
| MIMIC-IV | heart failure | Sensitivity | qsofa_gcs15_ett_as1 | 22,350 | 16,461 |  |  |  | 1.24 | — | — | not computed (degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | COPD | Sensitivity | one record per patient | 7,825 | 7,825 |  |  |  | 5.09 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-IV | COPD | Sensitivity | patient-weighted supported-admission sensitivity | 10,059 | 7,825 |  |  |  | 5.97 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-IV | COPD | Sensitivity | qsofa_gcs15 | 10,059 | 7,825 |  |  |  | 6.27 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | COPD | Sensitivity | qsofa_ett_as1 | 11,747 | 9,001 |  |  |  | 6.64 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-IV | COPD | Sensitivity | qsofa_gcs15_ett_as1 | 11,747 | 9,001 |  |  |  | 6.39 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | sepsis | Eligibility flow | primary | 3,398 | 3,075 | 2,958 | 3,398 | 2,958 |  |  |  |  |  |
| MIMIC-III | sepsis | Eligibility flow | never-primary | 2,914 | 2,725 | 2,630 | 2,914 | 2,630 |  |  |  |  |  |
| MIMIC-III | pneumonia | Eligibility flow | primary | 1,756 | 1,559 | 1,603 | 1,756 | 1,603 |  |  |  |  |  |
| MIMIC-III | pneumonia | Eligibility flow | never-primary | 8,544 | 7,690 | 7,545 | 8,544 | 7,545 |  |  |  |  |  |
| MIMIC-III | pancreatitis | Eligibility flow | primary | 366 | 344 | 320 | 366 | 320 |  |  |  |  |  |
| MIMIC-III | pancreatitis | Eligibility flow | never-primary | 587 | 574 | 495 | 587 | 495 |  |  |  |  |  |
| MIMIC-III | heart failure | Eligibility flow | primary | 1,543 | 1,316 | 1,467 | 1,543 | 1,467 |  |  |  |  |  |
| MIMIC-III | heart failure | Eligibility flow | never-primary | 11,904 | 9,312 | 10,952 | 11,904 | 10,952 |  |  |  |  |  |
| MIMIC-III | COPD | Eligibility flow | primary | 309 | 244 | 294 | 309 | 294 |  |  |  |  |  |
| MIMIC-III | COPD | Eligibility flow | never-primary | 5,988 | 4,706 | 5,463 | 5,988 | 5,463 |  |  |  |  |  |
| MIMIC-III | sepsis | Sensitivity | one record per patient | 4,957 | 4,957 |  |  |  | 9.13 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-III | sepsis | Sensitivity | patient-weighted supported-admission sensitivity | 5,588 | 4,957 |  |  |  | 9.14 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-III | sepsis | Sensitivity | qsofa_gcs15 | 5,588 | 4,957 |  |  |  | 8.73 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | sepsis | Sensitivity | qsofa_ett_as1 | 6,147 | 5,427 |  |  |  | 8.03 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | sepsis | Sensitivity | qsofa_gcs15_ett_as1 | 6,147 | 5,427 |  |  |  | 8.17 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | pneumonia | Sensitivity | one record per patient | 7,974 | 7,974 |  |  |  | 5.31 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-III | pneumonia | Sensitivity | patient-weighted supported-admission sensitivity | 9,148 | 7,974 |  |  |  | 5.41 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-III | pneumonia | Sensitivity | curb65_ett_as1 | 10,035 | 8,693 |  |  |  | 6.13 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | pancreatitis | Sensitivity | one record per patient | 779 | 779 |  |  |  | 3.93 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-III | pancreatitis | Sensitivity | patient-weighted supported-admission sensitivity | 815 | 779 |  |  |  | 3.91 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-III | pancreatitis | Sensitivity | bisap4_ett_as1 | 891 | 845 |  |  |  | 4.99 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | heart failure | Sensitivity | one record per patient | 9,490 | 9,490 |  |  |  | 1.35 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-III | heart failure | Sensitivity | patient-weighted supported-admission sensitivity | 12,419 | 9,490 |  |  |  | 0.50 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-III | heart failure | Sensitivity | qsofa_gcs15 | 12,419 | 9,490 |  |  |  | 1.32 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | heart failure | Sensitivity | qsofa_ett_as1 | 13,090 | 9,936 |  |  |  | 1.68 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | heart failure | Sensitivity | qsofa_gcs15_ett_as1 | 13,090 | 9,936 |  |  |  | 1.68 | — | — | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | COPD | Sensitivity | one record per patient | 4,500 | 4,500 |  |  |  | 1.06 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | chronological first eligible admission |
| MIMIC-III | COPD | Sensitivity | patient-weighted supported-admission sensitivity | 5,757 | 4,500 |  |  |  | 0.09 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| MIMIC-III | COPD | Sensitivity | qsofa_gcs15 | 5,757 | 4,500 |  |  |  | 3.50 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | COPD | Sensitivity | qsofa_ett_as1 | 6,142 | 4,767 |  |  |  | 3.23 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| MIMIC-III | COPD | Sensitivity | qsofa_gcs15_ett_as1 | 6,142 | 4,767 |  |  |  | 4.13 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | sepsis | Eligibility flow | primary | 167 | 167 | 48 | 167 | 48 |  |  |  |  |  |
| Zigong | sepsis | Eligibility flow | never-primary | 374 | 374 | 90 | 373 | 89 |  |  |  |  |  |
| Zigong | pneumonia | Eligibility flow | primary | 235 | 235 | 43 | 234 | 42 |  |  |  |  |  |
| Zigong | pneumonia | Eligibility flow | never-primary | 1,463 | 1,463 | 388 | 1,463 | 388 |  |  |  |  |  |
| Zigong | pancreatitis | Eligibility flow | primary | 63 | 63 | 14 | 63 | 14 |  |  |  |  |  |
| Zigong | pancreatitis | Eligibility flow | never-primary | 47 | 47 | 14 | 47 | 14 |  |  |  |  |  |
| Zigong | heart failure | Eligibility flow | primary | 53 | 53 | 10 | 53 | 10 |  |  |  |  |  |
| Zigong | heart failure | Eligibility flow | never-primary | 553 | 553 | 138 | 552 | 137 |  |  |  |  |  |
| Zigong | COPD | Eligibility flow | primary | 68 | 68 | 18 | 68 | 18 |  |  |  |  |  |
| Zigong | COPD | Eligibility flow | never-primary | 523 | 523 | 146 | 522 | 145 |  |  |  |  |  |
| Zigong | sepsis | Sensitivity | one record per patient | 137 | 137 |  |  |  | 4.80 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| Zigong | sepsis | Sensitivity | patient-weighted supported-admission sensitivity | 137 | 137 |  |  |  | 4.80 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| Zigong | sepsis | Sensitivity | qsofa_gcs15 | 136 | 136 |  |  |  | 4.28 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | sepsis | Sensitivity | died_strict_status | 137 | 137 |  |  |  | 4.80 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | sepsis | Sensitivity | died_v1_timing | 138 | 138 |  |  |  | 2.55 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | pneumonia | Sensitivity | one record per patient | 430 | 430 |  |  |  | 6.33 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| Zigong | pneumonia | Sensitivity | patient-weighted supported-admission sensitivity | 430 | 430 |  |  |  | 6.33 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| Zigong | pneumonia | Sensitivity | died_strict_status | 430 | 430 |  |  |  | 6.08 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | pneumonia | Sensitivity | died_v1_timing | 431 | 431 |  |  |  | -6.03 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | pancreatitis | Sensitivity | one record per patient | 28 | 28 |  |  |  | -5.36 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| Zigong | pancreatitis | Sensitivity | patient-weighted supported-admission sensitivity | 28 | 28 |  |  |  | -5.36 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| Zigong | pancreatitis | Sensitivity | died_strict_status | 28 | 28 |  |  |  | -5.36 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | pancreatitis | Sensitivity | died_v1_timing | 28 | 28 |  |  |  | 30.71 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | heart failure | Sensitivity | one record per patient | 147 | 147 |  |  |  | -9.36 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| Zigong | heart failure | Sensitivity | patient-weighted supported-admission sensitivity | 147 | 147 |  |  |  | -9.36 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| Zigong | heart failure | Sensitivity | qsofa_gcs15 | 125 | 125 |  |  |  | -8.42 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | heart failure | Sensitivity | died_strict_status | 147 | 147 |  |  |  | -10.07 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | heart failure | Sensitivity | died_v1_timing | 148 | 148 |  |  |  | 15.62 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | COPD | Sensitivity | one record per patient | 146 | 146 |  |  |  | 5.46 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | one admission per patient selected by prespecified hash |
| Zigong | COPD | Sensitivity | patient-weighted supported-admission sensitivity | 146 | 146 |  |  |  | 5.46 | — | — |  | Delta_w weighted summary, patient-weighted sensitivity |
| Zigong | COPD | Sensitivity | qsofa_gcs15 | 160 | 160 |  |  |  | 4.95 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | COPD | Sensitivity | died_strict_status | 146 | 146 |  |  |  | 5.46 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |
| Zigong | COPD | Sensitivity | died_v1_timing | 147 | 147 |  |  |  | 13.60 | — | — | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | Delta_w weighted summary |

**Notes.**

- One-record-per-patient analyses use the prespecified chronological first admission where dates are available; eICU uses the prespecified hash selection because full admission dates are unavailable. Patient-weighted supported-admission results are separate estimands.

## Supplementary Table 2. eICU diagnosis-group counts

| disease | disease_key | code_list | position_scope_or_sensitivity | n_admissions | n_known_outcome | deaths | mortality | qsofa_gcs13_complete_n | qsofa_gcs13_mean_complete | qsofa_gcs15_complete_n | curb65_complete_n | bisap4_complete_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| heart failure | heart_failure | narrow | primary_full_course | 4507 | 4472 | 428 | 0.09570661896243292 | 2568 | 1.8975856697819315 | 2568 | 2334 | 1753 |
| heart failure | heart_failure | narrow | never_primary_full_course | 11055 | 10919 | 1541 | 0.14113014012272185 | 7073 | 2.062632546302842 | 7073 | 6472 | 5074 |
| heart failure | heart_failure | narrow | not_classifiable_by_index24_sensitivity | 1771 | 1753 | 339 | 0.19338277239018825 | 1095 | 2.2273972602739724 | 1095 | 1029 | 871 |
| heart failure | heart_failure | narrow | primary_by_index24_sensitivity | 4088 | 4056 | 367 | 0.09048323471400395 | 2322 | 1.8755383290267011 | 2322 | 2099 | 1568 |
| heart failure | heart_failure | narrow | never_primary_by_index24_sensitivity | 9703 | 9582 | 1263 | 0.13180964308077645 | 6224 | 2.0353470437017993 | 6224 | 5678 | 4388 |
| heart failure | heart_failure | broad | primary_full_course | 4507 | 4472 | 428 | 0.09570661896243292 | 2568 | 1.8975856697819315 | 2568 | 2334 | 1753 |
| heart failure | heart_failure | broad | never_primary_full_course | 11055 | 10919 | 1541 | 0.14113014012272185 | 7073 | 2.062632546302842 | 7073 | 6472 | 5074 |
| heart failure | heart_failure | broad | not_classifiable_by_index24_sensitivity | 1771 | 1753 | 339 | 0.19338277239018825 | 1095 | 2.2273972602739724 | 1095 | 1029 | 871 |
| heart failure | heart_failure | broad | primary_by_index24_sensitivity | 4088 | 4056 | 367 | 0.09048323471400395 | 2322 | 1.8755383290267011 | 2322 | 2099 | 1568 |
| heart failure | heart_failure | broad | never_primary_by_index24_sensitivity | 9703 | 9582 | 1263 | 0.13180964308077645 | 6224 | 2.0353470437017993 | 6224 | 5678 | 4388 |
| heart failure | heart_failure | legacy_v1 | primary_full_course | 4507 | 4472 | 428 | 0.09570661896243292 | 2568 | 1.8975856697819315 | 2568 | 2334 | 1753 |
| heart failure | heart_failure | legacy_v1 | never_primary_full_course | 11055 | 10919 | 1541 | 0.14113014012272185 | 7073 | 2.062632546302842 | 7073 | 6472 | 5074 |
| heart failure | heart_failure | legacy_v1 | not_classifiable_by_index24_sensitivity | 1771 | 1753 | 339 | 0.19338277239018825 | 1095 | 2.2273972602739724 | 1095 | 1029 | 871 |
| heart failure | heart_failure | legacy_v1 | primary_by_index24_sensitivity | 4088 | 4056 | 367 | 0.09048323471400395 | 2322 | 1.8755383290267011 | 2322 | 2099 | 1568 |
| heart failure | heart_failure | legacy_v1 | never_primary_by_index24_sensitivity | 9703 | 9582 | 1263 | 0.13180964308077645 | 6224 | 2.0353470437017993 | 6224 | 5678 | 4388 |
| pneumonia | pneumonia | narrow | primary_full_course | 4864 | 4785 | 658 | 0.1375130616509927 | 2918 | 2.123029472241261 | 2918 | 2622 | 2254 |
| pneumonia | pneumonia | narrow | never_primary_full_course | 13973 | 13833 | 2529 | 0.18282368249837344 | 9398 | 2.268354969142371 | 9398 | 8727 | 7708 |
| pneumonia | pneumonia | narrow | not_classifiable_by_index24_sensitivity | 3005 | 2979 | 620 | 0.20812353138637127 | 2016 | 2.3700396825396823 | 2016 | 1923 | 1690 |
| pneumonia | pneumonia | narrow | primary_by_index24_sensitivity | 4244 | 4172 | 562 | 0.13470757430488975 | 2562 | 2.1046057767369244 | 2562 | 2286 | 1967 |
| pneumonia | pneumonia | narrow | never_primary_by_index24_sensitivity | 11588 | 11467 | 2005 | 0.17484956832650214 | 7738 | 2.241276815714655 | 7738 | 7140 | 6305 |
| pneumonia | pneumonia | broad | primary_full_course | 4955 | 4876 | 679 | 0.139253486464315 | 2981 | 2.1325058705132505 | 2981 | 2684 | 2310 |
| pneumonia | pneumonia | broad | never_primary_full_course | 14313 | 14166 | 2610 | 0.18424396442185514 | 9614 | 2.2748075722904098 | 9614 | 8928 | 7897 |
| pneumonia | pneumonia | broad | not_classifiable_by_index24_sensitivity | 3064 | 3038 | 640 | 0.21066491112574062 | 2045 | 2.3706601466992665 | 2045 | 1953 | 1718 |
| pneumonia | pneumonia | broad | primary_by_index24_sensitivity | 4313 | 4241 | 576 | 0.13581702428672482 | 2609 | 2.1119202759678037 | 2609 | 2331 | 2007 |
| pneumonia | pneumonia | broad | never_primary_by_index24_sensitivity | 11891 | 11763 | 2073 | 0.17623055343024738 | 7941 | 2.2502203752675984 | 7941 | 7328 | 6482 |
| pneumonia | pneumonia | legacy_v1 | primary_full_course | 4955 | 4876 | 679 | 0.139253486464315 | 2981 | 2.1325058705132505 | 2981 | 2684 | 2310 |
| pneumonia | pneumonia | legacy_v1 | never_primary_full_course | 14313 | 14166 | 2610 | 0.18424396442185514 | 9614 | 2.2748075722904098 | 9614 | 8928 | 7897 |
| pneumonia | pneumonia | legacy_v1 | not_classifiable_by_index24_sensitivity | 3064 | 3038 | 640 | 0.21066491112574062 | 2045 | 2.3706601466992665 | 2045 | 1953 | 1718 |
| pneumonia | pneumonia | legacy_v1 | primary_by_index24_sensitivity | 4313 | 4241 | 576 | 0.13581702428672482 | 2609 | 2.1119202759678037 | 2609 | 2331 | 2007 |
| pneumonia | pneumonia | legacy_v1 | never_primary_by_index24_sensitivity | 11891 | 11763 | 2073 | 0.17623055343024738 | 7941 | 2.2502203752675984 | 7941 | 7328 | 6482 |
| COPD | copd | narrow | primary_full_course | 2617 | 2598 | 163 | 0.06274056966897613 | 1550 | 1.949032258064516 | 1550 | 1343 | 1177 |
| COPD | copd | narrow | never_primary_full_course | 10026 | 9927 | 1099 | 0.11070816963836003 | 6218 | 2.071888066902541 | 6218 | 5577 | 4758 |
| COPD | copd | narrow | not_classifiable_by_index24_sensitivity | 1068 | 1058 | 147 | 0.1389413988657845 | 674 | 2.2240356083086055 | 674 | 608 | 507 |
| COPD | copd | narrow | primary_by_index24_sensitivity | 2379 | 2362 | 143 | 0.06054191363251482 | 1408 | 1.9296875 | 1408 | 1216 | 1062 |
| COPD | copd | narrow | never_primary_by_index24_sensitivity | 9196 | 9105 | 972 | 0.10675453047775947 | 5686 | 2.055575096728808 | 5686 | 5096 | 4366 |
| COPD | copd | broad | primary_full_course | 2856 | 2832 | 196 | 0.0692090395480226 | 1711 | 1.9707773232028054 | 1711 | 1488 | 1302 |
| COPD | copd | broad | never_primary_full_course | 10158 | 10059 | 1103 | 0.10965304702256685 | 6306 | 2.072629241991754 | 6306 | 5660 | 4832 |
| COPD | copd | broad | not_classifiable_by_index24_sensitivity | 1127 | 1116 | 154 | 0.13799283154121864 | 723 | 2.228215767634855 | 723 | 654 | 548 |
| COPD | copd | broad | primary_by_index24_sensitivity | 2573 | 2551 | 165 | 0.06468051744413955 | 1538 | 1.9525357607282186 | 1538 | 1333 | 1161 |
| COPD | copd | broad | never_primary_by_index24_sensitivity | 9314 | 9224 | 980 | 0.106244579358196 | 5756 | 2.054899235580264 | 5756 | 5161 | 4425 |
| COPD | copd | legacy_v1 | primary_full_course | 2639 | 2619 | 165 | 0.06300114547537228 | 1561 | 1.948750800768738 | 1561 | 1353 | 1186 |
| COPD | copd | legacy_v1 | never_primary_full_course | 10170 | 10071 | 1108 | 0.11001886605103764 | 6318 | 2.072333016777461 | 6318 | 5672 | 4841 |
| COPD | copd | legacy_v1 | not_classifiable_by_index24_sensitivity | 1110 | 1100 | 154 | 0.14 | 711 | 2.2348804500703237 | 711 | 642 | 538 |
| COPD | copd | legacy_v1 | primary_by_index24_sensitivity | 2398 | 2380 | 144 | 0.06050420168067227 | 1417 | 1.9287226534932957 | 1417 | 1224 | 1069 |
| COPD | copd | legacy_v1 | never_primary_by_index24_sensitivity | 9301 | 9210 | 975 | 0.10586319218241043 | 5751 | 2.054077551730134 | 5751 | 5159 | 4420 |
| sepsis | sepsis | narrow | primary_full_course | 16101 | 15931 | 2881 | 0.1808423827757203 | 10564 | 2.2759371450208254 | 10564 | 9885 | 8707 |
| sepsis | sepsis | narrow | never_primary_full_course | 8563 | 8478 | 1678 | 0.19792403868836989 | 6166 | 2.273272786247162 | 6166 | 5760 | 5134 |
| sepsis | sepsis | narrow | not_classifiable_by_index24_sensitivity | 2677 | 2645 | 716 | 0.2706994328922495 | 1842 | 2.3566775244299674 | 1842 | 1761 | 1557 |
| sepsis | sepsis | narrow | primary_by_index24_sensitivity | 14116 | 13973 | 2384 | 0.17061475703141774 | 9161 | 2.261106866062657 | 9161 | 8543 | 7515 |
| sepsis | sepsis | narrow | never_primary_by_index24_sensitivity | 7871 | 7791 | 1459 | 0.1872673597740983 | 5727 | 2.2708224201152434 | 5727 | 5341 | 4769 |
| sepsis | sepsis | broad | primary_full_course | 16109 | 15939 | 2881 | 0.18075161553422422 | 10567 | 2.275669537238573 | 10567 | 9888 | 8709 |
| sepsis | sepsis | broad | never_primary_full_course | 8572 | 8487 | 1679 | 0.1978319783197832 | 6173 | 2.273286894540742 | 6173 | 5767 | 5139 |
| sepsis | sepsis | broad | not_classifiable_by_index24_sensitivity | 2680 | 2648 | 717 | 0.2707703927492447 | 1845 | 2.3555555555555556 | 1845 | 1764 | 1560 |
| sepsis | sepsis | broad | primary_by_index24_sensitivity | 14122 | 13979 | 2384 | 0.17054152657557764 | 9163 | 2.2609407399323365 | 9163 | 8545 | 7516 |
| sepsis | sepsis | broad | never_primary_by_index24_sensitivity | 7879 | 7799 | 1459 | 0.18707526605975125 | 5732 | 2.2709351011863226 | 5732 | 5346 | 4772 |
| sepsis | sepsis | legacy_v1 | primary_full_course | 16101 | 15931 | 2881 | 0.1808423827757203 | 10564 | 2.2759371450208254 | 10564 | 9885 | 8707 |
| sepsis | sepsis | legacy_v1 | never_primary_full_course | 8563 | 8478 | 1678 | 0.19792403868836989 | 6166 | 2.273272786247162 | 6166 | 5760 | 5134 |
| sepsis | sepsis | legacy_v1 | not_classifiable_by_index24_sensitivity | 2677 | 2645 | 716 | 0.2706994328922495 | 1842 | 2.3566775244299674 | 1842 | 1761 | 1557 |
| sepsis | sepsis | legacy_v1 | primary_by_index24_sensitivity | 14116 | 13973 | 2384 | 0.17061475703141774 | 9161 | 2.261106866062657 | 9161 | 8543 | 7515 |
| sepsis | sepsis | legacy_v1 | never_primary_by_index24_sensitivity | 7871 | 7791 | 1459 | 0.1872673597740983 | 5727 | 2.2708224201152434 | 5727 | 5341 | 4769 |
| acute pancreatitis | pancreatitis | narrow | primary_full_course | 255 | 254 | 15 | 0.05905511811023622 | 179 | 1.7486033519553073 | 179 | 166 | 154 |
| acute pancreatitis | pancreatitis | narrow | never_primary_full_course | 346 | 342 | 38 | 0.1111111111111111 | 230 | 1.9521739130434783 | 230 | 220 | 202 |
| acute pancreatitis | pancreatitis | narrow | not_classifiable_by_index24_sensitivity | 73 | 73 | 17 | 0.2328767123287671 | 43 | 2.2325581395348837 | 43 | 43 | 38 |
| acute pancreatitis | pancreatitis | narrow | primary_by_index24_sensitivity | 223 | 222 | 11 | 0.04954954954954955 | 161 | 1.7018633540372672 | 161 | 148 | 137 |
| acute pancreatitis | pancreatitis | narrow | never_primary_by_index24_sensitivity | 305 | 301 | 25 | 0.08305647840531562 | 205 | 1.9121951219512194 | 205 | 195 | 181 |
| acute pancreatitis | pancreatitis | broad | primary_full_course | 255 | 254 | 15 | 0.05905511811023622 | 179 | 1.7486033519553073 | 179 | 166 | 154 |
| acute pancreatitis | pancreatitis | broad | never_primary_full_course | 346 | 342 | 38 | 0.1111111111111111 | 230 | 1.9521739130434783 | 230 | 220 | 202 |
| acute pancreatitis | pancreatitis | broad | not_classifiable_by_index24_sensitivity | 73 | 73 | 17 | 0.2328767123287671 | 43 | 2.2325581395348837 | 43 | 43 | 38 |
| acute pancreatitis | pancreatitis | broad | primary_by_index24_sensitivity | 223 | 222 | 11 | 0.04954954954954955 | 161 | 1.7018633540372672 | 161 | 148 | 137 |
| acute pancreatitis | pancreatitis | broad | never_primary_by_index24_sensitivity | 305 | 301 | 25 | 0.08305647840531562 | 205 | 1.9121951219512194 | 205 | 195 | 181 |
| acute pancreatitis | pancreatitis | legacy_v1 | primary_full_course | 538 | 535 | 27 | 0.05046728971962617 | 365 | 1.6958904109589041 | 365 | 341 | 310 |
| acute pancreatitis | pancreatitis | legacy_v1 | never_primary_full_course | 1044 | 1035 | 107 | 0.10338164251207729 | 696 | 1.9209770114942528 | 696 | 658 | 585 |
| acute pancreatitis | pancreatitis | legacy_v1 | not_classifiable_by_index24_sensitivity | 131 | 129 | 23 | 0.17829457364341086 | 79 | 2.1772151898734178 | 79 | 76 | 68 |
| acute pancreatitis | pancreatitis | legacy_v1 | primary_by_index24_sensitivity | 490 | 487 | 18 | 0.03696098562628337 | 338 | 1.6627218934911243 | 338 | 314 | 285 |
| acute pancreatitis | pancreatitis | legacy_v1 | never_primary_by_index24_sensitivity | 961 | 954 | 93 | 0.09748427672955975 | 644 | 1.8975155279503106 | 644 | 609 | 542 |

## Supplementary Table 3. eICU reconstructed score availability

| disease | score | n_cohort | n_complete | n_incomplete | n_lower_equals_upper | n_partial_bounds |
| --- | --- | --- | --- | --- | --- | --- |
| heart_failure | qsofa_gcs13 | 15562 | 9641 | 5921 | 9641 | 5921 |
| heart_failure | qsofa_gcs15_sensitivity | 15562 | 9641 | 5921 | 9641 | 5921 |
| heart_failure | curb65_gcs_proxy | 15562 | 8806 | 6756 | 8806 | 6756 |
| heart_failure | curb65_direct_confusion_sensitivity | 15562 | 0 | 15562 | 0 | 15562 |
| heart_failure | bisap4_operationalized | 15562 | 6827 | 8735 | 6827 | 8735 |
| pneumonia | qsofa_gcs13 | 19268 | 12595 | 6673 | 12595 | 6673 |
| pneumonia | qsofa_gcs15_sensitivity | 19268 | 12595 | 6673 | 12595 | 6673 |
| pneumonia | curb65_gcs_proxy | 19268 | 11612 | 7656 | 11612 | 7656 |
| pneumonia | curb65_direct_confusion_sensitivity | 19268 | 0 | 19268 | 0 | 19268 |
| pneumonia | bisap4_operationalized | 19268 | 10207 | 9061 | 10207 | 9061 |
| copd | qsofa_gcs13 | 13014 | 8017 | 4997 | 8017 | 4997 |
| copd | qsofa_gcs15_sensitivity | 13014 | 8017 | 4997 | 8017 | 4997 |
| copd | curb65_gcs_proxy | 13014 | 7148 | 5866 | 7148 | 5866 |
| copd | curb65_direct_confusion_sensitivity | 13014 | 0 | 13014 | 0 | 13014 |
| copd | bisap4_operationalized | 13014 | 6134 | 6880 | 6134 | 6880 |
| sepsis | qsofa_gcs13 | 24681 | 16740 | 7941 | 16740 | 7941 |
| sepsis | qsofa_gcs15_sensitivity | 24681 | 16740 | 7941 | 16740 | 7941 |
| sepsis | curb65_gcs_proxy | 24681 | 15655 | 9026 | 15655 | 9026 |
| sepsis | curb65_direct_confusion_sensitivity | 24681 | 0 | 24681 | 0 | 24681 |
| sepsis | bisap4_operationalized | 24681 | 13848 | 10833 | 13848 | 10833 |
| pancreatitis | qsofa_gcs13 | 601 | 409 | 192 | 409 | 192 |
| pancreatitis | qsofa_gcs15_sensitivity | 601 | 409 | 192 | 409 | 192 |
| pancreatitis | curb65_gcs_proxy | 601 | 386 | 215 | 386 | 215 |
| pancreatitis | curb65_direct_confusion_sensitivity | 601 | 0 | 601 | 0 | 601 |
| pancreatitis | bisap4_operationalized | 601 | 356 | 245 | 356 | 245 |

## Supplementary Table 4. Main-cohort demographics and analytic overlap; counts, not δ_s or weighted summary Δ_w

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

## Supplementary Table 5. Source-specific admission pathways; counts, not δ_s or weighted summary Δ_w

| Database | Condition | Group | Source field | Category | Records | Denominator | Percent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eICU | sepsis | primary | index ICU admission source | Emergency Department | 6858 | 10467 | 65.5 |
| eICU | sepsis | primary | index ICU admission source | Floor | 1643 | 10467 | 15.7 |
| eICU | sepsis | primary | index ICU admission source | Direct Admit | 558 | 10467 | 5.3 |
| eICU | sepsis | primary | index ICU admission source | Operating Room | 357 | 10467 | 3.4 |
| eICU | sepsis | primary | index ICU admission source | Acute Care/Floor | 317 | 10467 | 3.0 |
| eICU | sepsis | primary | index ICU admission source | Other Hospital | 304 | 10467 | 2.9 |
| eICU | sepsis | primary | index ICU admission source | Step-Down Unit (SDU) | 233 | 10467 | 2.2 |
| eICU | sepsis | primary | index ICU admission source | Recovery Room | 84 | 10467 | 0.8 |
| eICU | sepsis | primary | index ICU admission source | Other ICU | 70 | 10467 | 0.7 |
| eICU | sepsis | primary | index ICU admission source | PACU | 31 | 10467 | 0.3 |
| eICU | sepsis | primary | index ICU admission source | Unknown | 5 | 10467 | 0.0 |
| eICU | sepsis | primary | index ICU admission source | ICU | 4 | 10467 | 0.0 |
| eICU | sepsis | primary | index ICU admission source | Observation | 2 | 10467 | 0.0 |
| eICU | sepsis | primary | index ICU admission source | Chest Pain Center | 1 | 10467 | 0.0 |
| eICU | sepsis | never-primary | index ICU admission source | Emergency Department | 3751 | 6109 | 61.4 |
| eICU | sepsis | never-primary | index ICU admission source | Floor | 1096 | 6109 | 17.9 |
| eICU | sepsis | never-primary | index ICU admission source | Operating Room | 341 | 6109 | 5.6 |
| eICU | sepsis | never-primary | index ICU admission source | Direct Admit | 295 | 6109 | 4.8 |
| eICU | sepsis | never-primary | index ICU admission source | Other Hospital | 210 | 6109 | 3.4 |
| eICU | sepsis | never-primary | index ICU admission source | Step-Down Unit (SDU) | 155 | 6109 | 2.5 |
| eICU | sepsis | never-primary | index ICU admission source | Recovery Room | 92 | 6109 | 1.5 |
| eICU | sepsis | never-primary | index ICU admission source | Acute Care/Floor | 84 | 6109 | 1.4 |
| eICU | sepsis | never-primary | index ICU admission source | Other ICU | 49 | 6109 | 0.8 |
| eICU | sepsis | never-primary | index ICU admission source | PACU | 15 | 6109 | 0.2 |
| eICU | sepsis | never-primary | index ICU admission source | Unknown | 10 | 6109 | 0.2 |
| eICU | sepsis | never-primary | index ICU admission source | ICU | 7 | 6109 | 0.1 |
| eICU | sepsis | never-primary | index ICU admission source | Chest Pain Center | 3 | 6109 | 0.0 |
| eICU | sepsis | never-primary | index ICU admission source | ICU to SDU | 1 | 6109 | 0.0 |
| eICU | pneumonia | primary | index ICU admission source | Emergency Department | 1639 | 2645 | 62.0 |
| eICU | pneumonia | primary | index ICU admission source | Floor | 374 | 2645 | 14.1 |
| eICU | pneumonia | primary | index ICU admission source | Acute Care/Floor | 218 | 2645 | 8.2 |
| eICU | pneumonia | primary | index ICU admission source | Direct Admit | 204 | 2645 | 7.7 |
| eICU | pneumonia | primary | index ICU admission source | Step-Down Unit (SDU) | 76 | 2645 | 2.9 |
| eICU | pneumonia | primary | index ICU admission source | Other Hospital | 59 | 2645 | 2.2 |
| eICU | pneumonia | primary | index ICU admission source | Operating Room | 43 | 2645 | 1.6 |
| eICU | pneumonia | primary | index ICU admission source | Other ICU | 17 | 2645 | 0.6 |
| eICU | pneumonia | primary | index ICU admission source | Recovery Room | 7 | 2645 | 0.3 |
| eICU | pneumonia | primary | index ICU admission source | ICU | 4 | 2645 | 0.2 |
| eICU | pneumonia | primary | index ICU admission source | Unknown | 2 | 2645 | 0.1 |
| eICU | pneumonia | primary | index ICU admission source | PACU | 1 | 2645 | 0.0 |
| eICU | pneumonia | primary | index ICU admission source | Chest Pain Center | 1 | 2645 | 0.0 |
| eICU | pneumonia | never-primary | index ICU admission source | Emergency Department | 5486 | 8836 | 62.1 |
| eICU | pneumonia | never-primary | index ICU admission source | Floor | 1584 | 8836 | 17.9 |
| eICU | pneumonia | never-primary | index ICU admission source | Direct Admit | 543 | 8836 | 6.1 |
| eICU | pneumonia | never-primary | index ICU admission source | Other Hospital | 334 | 8836 | 3.8 |
| eICU | pneumonia | never-primary | index ICU admission source | Operating Room | 259 | 8836 | 2.9 |
| eICU | pneumonia | never-primary | index ICU admission source | Acute Care/Floor | 245 | 8836 | 2.8 |
| eICU | pneumonia | never-primary | index ICU admission source | Step-Down Unit (SDU) | 213 | 8836 | 2.4 |
| eICU | pneumonia | never-primary | index ICU admission source | Recovery Room | 77 | 8836 | 0.9 |
| eICU | pneumonia | never-primary | index ICU admission source | Other ICU | 56 | 8836 | 0.6 |
| eICU | pneumonia | never-primary | index ICU admission source | PACU | 14 | 8836 | 0.2 |
| eICU | pneumonia | never-primary | index ICU admission source | Chest Pain Center | 10 | 8836 | 0.1 |
| eICU | pneumonia | never-primary | index ICU admission source | Unknown | 7 | 8836 | 0.1 |
| eICU | pneumonia | never-primary | index ICU admission source | ICU | 6 | 8836 | 0.1 |
| eICU | pneumonia | never-primary | index ICU admission source | ICU to SDU | 2 | 8836 | 0.0 |
| MIMIC-IV | sepsis | primary | hospital admission type | EW EMER. | 4574 | 6679 | 68.5 |
| MIMIC-IV | sepsis | primary | hospital admission type | URGENT | 1039 | 6679 | 15.6 |
| MIMIC-IV | sepsis | primary | hospital admission type | OBSERVATION ADMIT | 961 | 6679 | 14.4 |
| MIMIC-IV | sepsis | primary | hospital admission type | DIRECT EMER. | 99 | 6679 | 1.5 |
| MIMIC-IV | sepsis | primary | hospital admission type | ELECTIVE | 2 | 6679 | 0.0 |
| MIMIC-IV | sepsis | primary | hospital admission type | DIRECT OBSERVATION | 2 | 6679 | 0.0 |
| MIMIC-IV | sepsis | primary | hospital admission type | AMBULATORY OBSERVATION | 1 | 6679 | 0.0 |
| MIMIC-IV | sepsis | primary | hospital admission type | EU OBSERVATION | 1 | 6679 | 0.0 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | EW EMER. | 2089 | 4125 | 50.6 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | OBSERVATION ADMIT | 851 | 4125 | 20.6 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | URGENT | 788 | 4125 | 19.1 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | DIRECT EMER. | 183 | 4125 | 4.4 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | SURGICAL SAME DAY ADMISSION | 156 | 4125 | 3.8 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | ELECTIVE | 57 | 4125 | 1.4 |
| MIMIC-IV | sepsis | never-primary | hospital admission type | EU OBSERVATION | 1 | 4125 | 0.0 |
| MIMIC-IV | pneumonia | primary | hospital admission type | EW EMER. | 1234 | 1640 | 75.2 |
| MIMIC-IV | pneumonia | primary | hospital admission type | OBSERVATION ADMIT | 180 | 1640 | 11.0 |
| MIMIC-IV | pneumonia | primary | hospital admission type | URGENT | 178 | 1640 | 10.9 |
| MIMIC-IV | pneumonia | primary | hospital admission type | DIRECT EMER. | 42 | 1640 | 2.6 |
| MIMIC-IV | pneumonia | primary | hospital admission type | ELECTIVE | 3 | 1640 | 0.2 |
| MIMIC-IV | pneumonia | primary | hospital admission type | EU OBSERVATION | 2 | 1640 | 0.1 |
| MIMIC-IV | pneumonia | primary | hospital admission type | SURGICAL SAME DAY ADMISSION | 1 | 1640 | 0.1 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | EW EMER. | 6350 | 10862 | 58.5 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | URGENT | 1852 | 10862 | 17.1 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | OBSERVATION ADMIT | 1843 | 10862 | 17.0 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | SURGICAL SAME DAY ADMISSION | 381 | 10862 | 3.5 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | DIRECT EMER. | 322 | 10862 | 3.0 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | ELECTIVE | 105 | 10862 | 1.0 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | EU OBSERVATION | 6 | 10862 | 0.1 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | DIRECT OBSERVATION | 2 | 10862 | 0.0 |
| MIMIC-IV | pneumonia | never-primary | hospital admission type | AMBULATORY OBSERVATION | 1 | 10862 | 0.0 |

## Supplementary Table 6. Leading priority or billing diagnoses; counts, not δ_s or weighted summary Δ_w

| Database | Condition | Group | Diagnosis label | Records | Denominator | Percent |
| --- | --- | --- | --- | --- | --- | --- |
| eICU | sepsis | primary | cardiovascular / shock / hypotension / sepsis | 3597 | 10467 | 34.4 |
| eICU | sepsis | primary | cardiovascular / shock / hypotension / sepsis / severe | 2471 | 10467 | 23.6 |
| eICU | sepsis | primary | cardiovascular / shock / hypotension / septic shock | 1943 | 10467 | 18.6 |
| eICU | sepsis | primary | infectious diseases / systemic/other infections / sepsis | 886 | 10467 | 8.5 |
| eICU | sepsis | primary | infectious diseases / systemic/other infections / sepsis / severe | 786 | 10467 | 7.5 |
| eICU | sepsis | primary | No qualifying priority or sequence-one diagnosis | 0 | 10467 | 0.0 |
| eICU | sepsis | never-primary | pulmonary / respiratory failure / acute respiratory failure | 458 | 6109 | 7.5 |
| eICU | sepsis | never-primary | pulmonary / pulmonary infections / pneumonia | 150 | 6109 | 2.5 |
| eICU | sepsis | never-primary | cardiovascular / cardiac arrest / cardiac arrest | 134 | 6109 | 2.2 |
| eICU | sepsis | never-primary | pulmonary / respiratory failure / acute respiratory distress | 114 | 6109 | 1.9 |
| eICU | sepsis | never-primary | neurologic / altered mental status / pain / change in mental status | 95 | 6109 | 1.6 |
| eICU | sepsis | never-primary | No qualifying priority or sequence-one diagnosis | 2856 | 6109 | 46.8 |
| eICU | pneumonia | primary | pulmonary / pulmonary infections / pneumonia | 1523 | 2645 | 57.6 |
| eICU | pneumonia | primary | pulmonary / pulmonary infections / pneumonia / community-acquired | 278 | 2645 | 10.5 |
| eICU | pneumonia | primary | pulmonary / pulmonary infections / pneumonia / aspiration | 233 | 2645 | 8.8 |
| eICU | pneumonia | primary | pulmonary / pulmonary infections / pneumonia / hospital acquired (not ventilator-associated) | 168 | 2645 | 6.4 |
| eICU | pneumonia | primary | pulmonary / respiratory failure / acute respiratory failure | 141 | 2645 | 5.3 |
| eICU | pneumonia | primary | No qualifying priority or sequence-one diagnosis | 0 | 2645 | 0.0 |
| eICU | pneumonia | never-primary | pulmonary / respiratory failure / acute respiratory failure | 1181 | 8836 | 13.4 |
| eICU | pneumonia | never-primary | cardiovascular / shock / hypotension / sepsis | 927 | 8836 | 10.5 |
| eICU | pneumonia | never-primary | cardiovascular / shock / hypotension / sepsis / severe | 786 | 8836 | 8.9 |
| eICU | pneumonia | never-primary | cardiovascular / shock / hypotension / septic shock | 557 | 8836 | 6.3 |
| eICU | pneumonia | never-primary | infectious diseases / systemic/other infections / sepsis | 318 | 8836 | 3.6 |
| eICU | pneumonia | never-primary | No qualifying priority or sequence-one diagnosis | 2015 | 8836 | 22.8 |
| MIMIC-IV | sepsis | primary | Sepsis, unspecified organism | 2065 | 6679 | 30.9 |
| MIMIC-IV | sepsis | primary | Unspecified septicemia | 1754 | 6679 | 26.3 |
| MIMIC-IV | sepsis | primary | Sepsis due to Escherichia coli [E. coli] | 433 | 6679 | 6.5 |
| MIMIC-IV | sepsis | primary | Other specified sepsis | 384 | 6679 | 5.7 |
| MIMIC-IV | sepsis | primary | Septicemia due to escherichia coli [E. coli] | 363 | 6679 | 5.4 |
| MIMIC-IV | sepsis | primary | No qualifying priority or sequence-one diagnosis | 0 | 6679 | 0.0 |
| MIMIC-IV | sepsis | never-primary | Bloodstream infection due to central venous catheter, initial encounter | 87 | 4125 | 2.1 |
| MIMIC-IV | sepsis | never-primary | Other postoperative infection | 83 | 4125 | 2.0 |
| MIMIC-IV | sepsis | never-primary | COVID-19 | 77 | 4125 | 1.9 |
| MIMIC-IV | sepsis | never-primary | Infection and inflammatory reaction due to other cardiac and vascular devices, implants and grafts, initial encounter | 66 | 4125 | 1.6 |
| MIMIC-IV | sepsis | never-primary | Other and unspecified infection due to central venous catheter | 57 | 4125 | 1.4 |
| MIMIC-IV | sepsis | never-primary | No qualifying priority or sequence-one diagnosis | 0 | 4125 | 0.0 |
| MIMIC-IV | pneumonia | primary | Pneumonia, organism unspecified | 504 | 1640 | 30.7 |
| MIMIC-IV | pneumonia | primary | Pneumonitis due to inhalation of food or vomitus | 359 | 1640 | 21.9 |
| MIMIC-IV | pneumonia | primary | Pneumonia, unspecified organism | 214 | 1640 | 13.0 |
| MIMIC-IV | pneumonia | primary | Pneumonitis due to inhalation of food and vomit | 210 | 1640 | 12.8 |
| MIMIC-IV | pneumonia | primary | Bacterial pneumonia, unspecified | 78 | 1640 | 4.8 |
| MIMIC-IV | pneumonia | primary | No qualifying priority or sequence-one diagnosis | 0 | 1640 | 0.0 |
| MIMIC-IV | pneumonia | never-primary | Sepsis, unspecified organism | 998 | 10862 | 9.2 |
| MIMIC-IV | pneumonia | never-primary | Unspecified septicemia | 830 | 10862 | 7.6 |
| MIMIC-IV | pneumonia | never-primary | COVID-19 | 361 | 10862 | 3.3 |
| MIMIC-IV | pneumonia | never-primary | Acute respiratory failure | 206 | 10862 | 1.9 |
| MIMIC-IV | pneumonia | never-primary | Other specified sepsis | 186 | 10862 | 1.7 |
| MIMIC-IV | pneumonia | never-primary | No qualifying priority or sequence-one diagnosis | 0 | 10862 | 0.0 |

## Supplementary Table 7. Zigong heart-failure application; diagnosis-sequence semantics unverified

| Database | Condition / instrument | Eligible sequence-one / other-sequence | Complete sequence-one / other-sequence | Shared sequence-one / other-sequence | Supported score levels | Δ_w weighted summary (percentage points) | 95% patient-cluster CI | Interval status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Zigong | heart failure / qSOFA | 53 / 553 | 10 / 137 | 10 / 137 | 4 | -9.36 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |

**Notes.**

- This cell is supplementary to the 19 source-condition cells in Table 2. qSOFA is outside intended use for heart failure; interpret as a source-specific application.

## Supplementary Table 8. Zigong documented discharge-status combinations

| status_combination | admissions |
| --- | --- |
| Recovered | 741 |
| Others\|Recovered | 554 |
| Cured\|Others\|Recovered | 330 |
| Recovered\|Uncovered | 272 |
| Cured\|Recovered | 245 |
| Uncovered | 176 |
| Dead | 153 |
| Others\|Recovered\|Uncovered | 130 |
| Others | 41 |
| Cured\|Recovered\|Uncovered | 37 |
| Cured\|Others\|Recovered\|Uncovered | 34 |
| Others\|Uncovered | 27 |
| Cured | 23 |
| Cured\|Others | 14 |
| Dead\|Others | 5 |
| Cured\|Uncovered | 3 |
|  | 2 |
| Cured\|Dead\|Others\|Recovered | 1 |
| Dead\|Others\|Recovered | 1 |
| Dead\|Recovered | 1 |

## Supplementary Table 9. Zigong discharge status and follow-up death timing

| status_dead | timing | admissions |
| --- | --- | --- |
| False | death_after_discharge | 761 |
| False | death_on_or_before_discharge | 382 |
| False | death_time_unavailable | 1486 |
| True | death_after_discharge | 67 |
| True | death_on_or_before_discharge | 64 |
| True | death_time_unavailable | 30 |

## Supplementary Table 10. Zigong laboratory measurement units

| item | unit | records |
| --- | --- | --- |
| Urea (urea) | mmol/L | 16586 |
| White blood cell (WBC) | 10^9/L | 17262 |
| Leukocytes (Leu) | Leu/uL | 9 |
| White blood cell (WBC) | /HPF | 5 |

## Supplementary Table 11. Zigong field-group score and outcome availability; diagnosis-sequence semantics unverified

| disease | grp | instrument | admissions | complete_score | known_outcome | deaths | complete_score_known_outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| COPD | 0.0 | qsofa | 68 | 18 | 68 | 3 | 18 |
| COPD | 1.0 | qsofa | 523 | 146 | 522 | 25 | 145 |
| heart failure | 0.0 | qsofa | 53 | 10 | 53 | 3 | 10 |
| heart failure | 1.0 | qsofa | 553 | 138 | 552 | 45 | 137 |
| pancreatitis | 0.0 | bisap4 | 63 | 14 | 63 | 4 | 14 |
| pancreatitis | 1.0 | bisap4 | 47 | 14 | 47 | 1 | 14 |
| pneumonia | 0.0 | curb65 | 235 | 43 | 234 | 12 | 42 |
| pneumonia | 1.0 | curb65 | 1463 | 388 | 1463 | 97 | 388 |
| sepsis | 0.0 | qsofa | 167 | 48 | 167 | 10 | 48 |
| sepsis | 1.0 | qsofa | 374 | 90 | 373 | 25 | 89 |

**Notes.**

# Additional supplementary results

These tables report the exploratory held-out application and the locked simulation design. Prediction-loss differences are neither δ_s nor the Δ_w weighted summary. All original supplementary tables remain available separately.

## Supplementary Table 12. Counts by score and diagnosis group

| disease | analysis | score | grp | n | deaths |
| --- | --- | --- | --- | --- | --- |
| sepsis | timed nursing GCS | 0.0 | 0.0 | 41 | 1.0 |
| sepsis | timed nursing GCS | 0.0 | 1.0 | 24 | 2.0 |
| sepsis | timed nursing GCS | 1.0 | 0.0 | 1151 | 80.0 |
| sepsis | timed nursing GCS | 1.0 | 1.0 | 741 | 43.0 |
| sepsis | timed nursing GCS | 2.0 | 0.0 | 5151 | 618.0 |
| sepsis | timed nursing GCS | 2.0 | 1.0 | 2885 | 320.0 |
| sepsis | timed nursing GCS | 3.0 | 0.0 | 4124 | 1166.0 |
| sepsis | timed nursing GCS | 3.0 | 1.0 | 2459 | 737.0 |
| sepsis | timed GCS excluding meds1 | 0.0 | 0.0 | 41 | 1.0 |
| sepsis | timed GCS excluding meds1 | 0.0 | 1.0 | 24 | 2.0 |
| sepsis | timed GCS excluding meds1 | 1.0 | 0.0 | 1151 | 80.0 |
| sepsis | timed GCS excluding meds1 | 1.0 | 1.0 | 740 | 43.0 |
| sepsis | timed GCS excluding meds1 | 2.0 | 0.0 | 5145 | 616.0 |
| sepsis | timed GCS excluding meds1 | 2.0 | 1.0 | 2882 | 319.0 |
| sepsis | timed GCS excluding meds1 | 3.0 | 0.0 | 4081 | 1155.0 |
| sepsis | timed GCS excluding meds1 | 3.0 | 1.0 | 2438 | 730.0 |
| sepsis | APACHE valid GCS with timed fallback | 0.0 | 0.0 | 66 | 1.0 |
| sepsis | APACHE valid GCS with timed fallback | 0.0 | 1.0 | 35 | 3.0 |
| sepsis | APACHE valid GCS with timed fallback | 1.0 | 0.0 | 1598 | 132.0 |
| sepsis | APACHE valid GCS with timed fallback | 1.0 | 1.0 | 1010 | 70.0 |
| sepsis | APACHE valid GCS with timed fallback | 2.0 | 0.0 | 7768 | 1148.0 |
| sepsis | APACHE valid GCS with timed fallback | 2.0 | 1.0 | 3843 | 558.0 |
| sepsis | APACHE valid GCS with timed fallback | 3.0 | 0.0 | 4527 | 1253.0 |
| sepsis | APACHE valid GCS with timed fallback | 3.0 | 1.0 | 2721 | 828.0 |
| pneumonia | timed nursing GCS | 0.0 | 0.0 | 17 | 0.0 |
| pneumonia | timed nursing GCS | 0.0 | 1.0 | 38 | 2.0 |
| pneumonia | timed nursing GCS | 1.0 | 0.0 | 154 | 5.0 |
| pneumonia | timed nursing GCS | 1.0 | 1.0 | 378 | 19.0 |
| pneumonia | timed nursing GCS | 2.0 | 0.0 | 465 | 31.0 |
| pneumonia | timed nursing GCS | 2.0 | 1.0 | 1373 | 92.0 |
| pneumonia | timed nursing GCS | 3.0 | 0.0 | 852 | 81.0 |
| pneumonia | timed nursing GCS | 3.0 | 1.0 | 2541 | 330.0 |
| pneumonia | timed nursing GCS | 4.0 | 0.0 | 769 | 129.0 |
| pneumonia | timed nursing GCS | 4.0 | 1.0 | 2984 | 626.0 |
| pneumonia | timed nursing GCS | 5.0 | 0.0 | 388 | 93.0 |
| pneumonia | timed nursing GCS | 5.0 | 1.0 | 1522 | 473.0 |
| pneumonia | timed GCS excluding meds1 | 0.0 | 0.0 | 17 | 0.0 |
| pneumonia | timed GCS excluding meds1 | 0.0 | 1.0 | 38 | 2.0 |
| pneumonia | timed GCS excluding meds1 | 1.0 | 0.0 | 154 | 5.0 |
| pneumonia | timed GCS excluding meds1 | 1.0 | 1.0 | 377 | 19.0 |
| pneumonia | timed GCS excluding meds1 | 2.0 | 0.0 | 462 | 31.0 |
| pneumonia | timed GCS excluding meds1 | 2.0 | 1.0 | 1369 | 91.0 |
| pneumonia | timed GCS excluding meds1 | 3.0 | 0.0 | 847 | 81.0 |
| pneumonia | timed GCS excluding meds1 | 3.0 | 1.0 | 2518 | 321.0 |
| pneumonia | timed GCS excluding meds1 | 4.0 | 0.0 | 766 | 128.0 |
| pneumonia | timed GCS excluding meds1 | 4.0 | 1.0 | 2960 | 623.0 |
| pneumonia | timed GCS excluding meds1 | 5.0 | 0.0 | 386 | 93.0 |
| pneumonia | timed GCS excluding meds1 | 5.0 | 1.0 | 1510 | 463.0 |
| pneumonia | APACHE valid GCS with timed fallback | 0.0 | 0.0 | 25 | 0.0 |
| pneumonia | APACHE valid GCS with timed fallback | 0.0 | 1.0 | 64 | 1.0 |
| pneumonia | APACHE valid GCS with timed fallback | 1.0 | 0.0 | 207 | 7.0 |
| pneumonia | APACHE valid GCS with timed fallback | 1.0 | 1.0 | 580 | 44.0 |
| pneumonia | APACHE valid GCS with timed fallback | 2.0 | 0.0 | 729 | 51.0 |
| pneumonia | APACHE valid GCS with timed fallback | 2.0 | 1.0 | 1940 | 140.0 |
| pneumonia | APACHE valid GCS with timed fallback | 3.0 | 0.0 | 1190 | 132.0 |
| pneumonia | APACHE valid GCS with timed fallback | 3.0 | 1.0 | 3420 | 473.0 |
| pneumonia | APACHE valid GCS with timed fallback | 4.0 | 0.0 | 1088 | 188.0 |
| pneumonia | APACHE valid GCS with timed fallback | 4.0 | 1.0 | 3700 | 829.0 |
| pneumonia | APACHE valid GCS with timed fallback | 5.0 | 0.0 | 466 | 114.0 |
| pneumonia | APACHE valid GCS with timed fallback | 5.0 | 1.0 | 1733 | 543.0 |
| pancreatitis | timed nursing GCS | 1.0 | 0.0 | 50 | 0.0 |
| pancreatitis | timed nursing GCS | 1.0 | 1.0 | 44 | 0.0 |
| pancreatitis | timed nursing GCS | 2.0 | 0.0 | 63 | 3.0 |
| pancreatitis | timed nursing GCS | 2.0 | 1.0 | 69 | 4.0 |
| pancreatitis | timed nursing GCS | 3.0 | 0.0 | 25 | 3.0 |
| pancreatitis | timed nursing GCS | 3.0 | 1.0 | 62 | 11.0 |
| pancreatitis | timed nursing GCS | 4.0 | 0.0 | 15 | 6.0 |
| pancreatitis | timed nursing GCS | 4.0 | 1.0 | 23 | 7.0 |
| pancreatitis | timed GCS excluding meds1 | 1.0 | 0.0 | 50 | 0.0 |
| pancreatitis | timed GCS excluding meds1 | 1.0 | 1.0 | 44 | 0.0 |
| pancreatitis | timed GCS excluding meds1 | 2.0 | 0.0 | 62 | 3.0 |
| pancreatitis | timed GCS excluding meds1 | 2.0 | 1.0 | 68 | 4.0 |
| pancreatitis | timed GCS excluding meds1 | 3.0 | 0.0 | 24 | 3.0 |
| pancreatitis | timed GCS excluding meds1 | 3.0 | 1.0 | 62 | 11.0 |
| pancreatitis | timed GCS excluding meds1 | 4.0 | 0.0 | 15 | 6.0 |
| pancreatitis | timed GCS excluding meds1 | 4.0 | 1.0 | 23 | 7.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 1.0 | 0.0 | 78 | 1.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 1.0 | 1.0 | 79 | 2.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 2.0 | 0.0 | 71 | 4.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 2.0 | 1.0 | 82 | 6.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 3.0 | 0.0 | 34 | 6.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 3.0 | 1.0 | 83 | 16.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 4.0 | 0.0 | 13 | 4.0 |
| pancreatitis | APACHE valid GCS with timed fallback | 4.0 | 1.0 | 26 | 7.0 |

## Supplementary Table 13. Measurement eligibility and selection counts

| disease | analysis | eligible | complete | meds1 | apache_gcs_valid | original_timed_gcs_valid |
| --- | --- | --- | --- | --- | --- | --- |
| sepsis | timed nursing GCS | 24664 | 16576 | 299 | 23769 | 18352 |
| sepsis | timed GCS excluding meds1 | 24664 | 16502 | 299 | 23769 | 18352 |
| sepsis | APACHE valid GCS with timed fallback | 24664 | 21568 | 299 | 23769 | 18352 |
| pneumonia | timed nursing GCS | 19268 | 11481 | 299 | 18284 | 13876 |
| pneumonia | timed GCS excluding meds1 | 19268 | 11404 | 299 | 18284 | 13876 |
| pneumonia | APACHE valid GCS with timed fallback | 19268 | 15142 | 299 | 18284 | 13876 |
| pancreatitis | timed nursing GCS | 601 | 351 | 7 | 582 | 446 |
| pancreatitis | timed GCS excluding meds1 | 601 | 348 | 7 | 582 | 446 |
| pancreatitis | APACHE valid GCS with timed fallback | 601 | 466 | 7 | 582 | 446 |

## Supplementary Table 14. MIMIC-IV reconstructed score coverage

| definition | grp | score | n_rows | n_hadm | n_pid | n_died_observed | n_died | n_score_complete | n_score_partial | n_score_any_observed_component | observed_points_total | mean_score_lower | mean_score_upper | n_score_all_components_unknown | n_outcome_missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| heart failure | 0.0 | qsofa | 2941 | 2941 | 2427 | 2941 | 343 | 2760 | 176 | 2936 | 5311 | 1.8058483509010541 | 1.8724923495409724 | 5 | 0 |
| heart failure | 0.0 | qsofa_gcs15 | 2941 | 2941 | 2427 | 2941 | 343 | 2760 | 176 | 2936 | 5891 | 2.0030601836110167 | 2.069704182250935 | 5 | 0 |
| heart failure | 0.0 | curb65 | 2941 | 2941 | 2427 | 2941 | 343 | 2735 | 206 | 2941 | 9609 | 3.267256035362122 | 3.3451207072424345 | 0 | 0 |
| heart failure | 0.0 | bisap4 | 2941 | 2941 | 2427 | 2941 | 343 | 2245 | 696 | 2941 | 7851 | 2.669500170010201 | 2.921115266916015 | 0 | 0 |
| heart failure | 0.0 | qsofa_ett_as1 | 2941 | 2941 | 2427 | 2941 | 343 | 2902 | 34 | 2936 | 5611 | 1.9078544712682761 | 1.9245154709282557 | 5 | 0 |
| heart failure | 0.0 | qsofa_gcs15_ett_as1 | 2941 | 2941 | 2427 | 2941 | 343 | 2902 | 34 | 2936 | 6145 | 2.0894253655219313 | 2.106086365181911 | 5 | 0 |
| heart failure | 0.0 | curb65_ett_as1 | 2941 | 2941 | 2427 | 2941 | 343 | 2875 | 66 | 2941 | 9863 | 3.3536212172730364 | 3.3815028901734103 | 0 | 0 |
| heart failure | 0.0 | bisap4_ett_as1 | 2941 | 2941 | 2427 | 2941 | 343 | 2373 | 568 | 2941 | 8105 | 2.7558653519211154 | 2.957497449846991 | 0 | 0 |
| heart failure | 1.0 | qsofa | 19721 | 19721 | 15229 | 19721 | 3010 | 16514 | 3159 | 19673 | 36980 | 1.8751584605243141 | 2.045383094163582 | 48 | 0 |
| heart failure | 1.0 | qsofa_gcs15 | 19721 | 19721 | 15229 | 19721 | 3010 | 16514 | 3159 | 19673 | 40771 | 2.067390091780336 | 2.2376147254196033 | 48 | 0 |
| heart failure | 1.0 | curb65 | 19721 | 19721 | 15229 | 19721 | 3010 | 16292 | 3429 | 19721 | 62304 | 3.1592718421986716 | 3.3451143451143452 | 0 | 0 |
| heart failure | 1.0 | bisap4 | 19721 | 19721 | 15229 | 19721 | 3010 | 13938 | 5783 | 19721 | 51669 | 2.6199989858526442 | 2.9375285228943766 | 0 | 0 |
| heart failure | 1.0 | qsofa_ett_as1 | 19721 | 19721 | 15229 | 19721 | 3010 | 19448 | 225 | 19673 | 42707 | 2.1655595558034584 | 2.1847776481922825 | 48 | 0 |
| heart failure | 1.0 | qsofa_gcs15_ett_as1 | 19721 | 19721 | 15229 | 19721 | 3010 | 19448 | 225 | 19673 | 45609 | 2.312712337102581 | 2.331930429491405 | 48 | 0 |
| heart failure | 1.0 | curb65_ett_as1 | 19721 | 19721 | 15229 | 19721 | 3010 | 19188 | 533 | 19721 | 67142 | 3.4045940875209166 | 3.439430049186147 | 0 | 0 |
| heart failure | 1.0 | bisap4_ett_as1 | 19721 | 19721 | 15229 | 19721 | 3010 | 16627 | 3094 | 19721 | 56507 | 2.8653212311748897 | 3.0318442269661783 | 0 | 0 |
| pneumonia | 0.0 | qsofa | 1936 | 1936 | 1755 | 1936 | 265 | 1688 | 242 | 1930 | 3728 | 1.9256198347107438 | 2.0609504132231407 | 6 | 0 |
| pneumonia | 0.0 | qsofa_gcs15 | 1936 | 1936 | 1755 | 1936 | 265 | 1688 | 242 | 1930 | 4091 | 2.113119834710744 | 2.2484504132231407 | 6 | 0 |
| pneumonia | 0.0 | curb65 | 1936 | 1936 | 1755 | 1936 | 265 | 1640 | 296 | 1936 | 6004 | 3.1012396694214877 | 3.2675619834710745 | 0 | 0 |
| pneumonia | 0.0 | bisap4 | 1936 | 1936 | 1755 | 1936 | 265 | 1511 | 425 | 1936 | 4894 | 2.527892561983471 | 2.770661157024793 | 0 | 0 |
| pneumonia | 0.0 | qsofa_ett_as1 | 1936 | 1936 | 1755 | 1936 | 265 | 1914 | 16 | 1930 | 4104 | 2.1198347107438016 | 2.137913223140496 | 6 | 0 |
| pneumonia | 0.0 | qsofa_gcs15_ett_as1 | 1936 | 1936 | 1755 | 1936 | 265 | 1914 | 16 | 1930 | 4425 | 2.2856404958677685 | 2.303719008264463 | 6 | 0 |
| pneumonia | 0.0 | curb65_ett_as1 | 1936 | 1936 | 1755 | 1936 | 265 | 1861 | 75 | 1936 | 6338 | 3.2737603305785123 | 3.322830578512397 | 0 | 0 |
| pneumonia | 0.0 | bisap4_ett_as1 | 1936 | 1936 | 1755 | 1936 | 265 | 1714 | 222 | 1936 | 5228 | 2.700413223140496 | 2.8259297520661155 | 0 | 0 |
| pneumonia | 1.0 | qsofa | 15087 | 15087 | 13441 | 15087 | 3542 | 11029 | 4004 | 15033 | 29199 | 1.935374826009147 | 2.2146881421091007 | 54 | 0 |
| pneumonia | 1.0 | qsofa_gcs15 | 15087 | 15087 | 13441 | 15087 | 3542 | 11029 | 4004 | 15033 | 31535 | 2.0902101146682575 | 2.369523430768211 | 54 | 0 |
| pneumonia | 1.0 | curb65 | 15087 | 15087 | 13441 | 15087 | 3542 | 10862 | 4225 | 15087 | 45140 | 2.991979850202161 | 3.288990521641148 | 0 | 0 |
| pneumonia | 1.0 | bisap4 | 15087 | 15087 | 13441 | 15087 | 3542 | 10078 | 5009 | 15087 | 37265 | 2.470007291045271 | 2.8317757009345796 | 0 | 0 |
| pneumonia | 1.0 | qsofa_ett_as1 | 15087 | 15087 | 13441 | 15087 | 3542 | 14897 | 136 | 15033 | 34658 | 2.2972095181281897 | 2.3174918804268576 | 54 | 0 |
| pneumonia | 1.0 | qsofa_gcs15_ett_as1 | 15087 | 15087 | 13441 | 15087 | 3542 | 14897 | 136 | 15033 | 36503 | 2.4195002319878043 | 2.4397825942864717 | 54 | 0 |
| pneumonia | 1.0 | curb65_ett_as1 | 15087 | 15087 | 13441 | 15087 | 3542 | 14670 | 417 | 15087 | 50108 | 3.3212699675217072 | 3.359249685159409 | 0 | 0 |
| pneumonia | 1.0 | bisap4_ett_as1 | 15087 | 15087 | 13441 | 15087 | 3542 | 13681 | 1406 | 15087 | 42233 | 2.799297408364817 | 2.90203486445284 | 0 | 0 |
| COPD | 0.0 | qsofa | 489 | 489 | 391 | 489 | 29 | 440 | 49 | 489 | 824 | 1.6850715746421268 | 1.7852760736196318 | 0 | 0 |
| COPD | 0.0 | qsofa_gcs15 | 489 | 489 | 391 | 489 | 29 | 440 | 49 | 489 | 902 | 1.8445807770961145 | 1.9447852760736197 | 0 | 0 |
| COPD | 0.0 | curb65 | 489 | 489 | 391 | 489 | 29 | 429 | 60 | 489 | 1393 | 2.8486707566462166 | 2.9754601226993866 | 0 | 0 |
| COPD | 0.0 | bisap4 | 489 | 489 | 391 | 489 | 29 | 384 | 105 | 489 | 1133 | 2.3169734151329244 | 2.5501022494887526 | 0 | 0 |
| COPD | 0.0 | qsofa_ett_as1 | 489 | 489 | 391 | 489 | 29 | 487 | 2 | 489 | 899 | 1.8384458077709611 | 1.8425357873210635 | 0 | 0 |
| COPD | 0.0 | qsofa_gcs15_ett_as1 | 489 | 489 | 391 | 489 | 29 | 487 | 2 | 489 | 970 | 1.983640081799591 | 1.9877300613496933 | 0 | 0 |
| COPD | 0.0 | curb65_ett_as1 | 489 | 489 | 391 | 489 | 29 | 475 | 14 | 489 | 1461 | 2.9877300613496933 | 3.01840490797546 | 0 | 0 |
| COPD | 0.0 | bisap4_ett_as1 | 489 | 489 | 391 | 489 | 29 | 425 | 64 | 489 | 1201 | 2.4560327198364007 | 2.593047034764826 | 0 | 0 |
| COPD | 1.0 | qsofa | 11410 | 11410 | 8909 | 11410 | 1658 | 9619 | 1762 | 11381 | 21128 | 1.8517090271691499 | 2.0163891323400525 | 29 | 0 |
| COPD | 1.0 | qsofa_gcs15 | 11410 | 11410 | 8909 | 11410 | 1658 | 9619 | 1762 | 11381 | 23401 | 2.050920245398773 | 2.2156003505696757 | 29 | 0 |
| COPD | 1.0 | curb65 | 11410 | 11410 | 8909 | 11410 | 1658 | 9479 | 1931 | 11410 | 34351 | 3.0106047326906222 | 3.1923751095530237 | 0 | 0 |
| COPD | 1.0 | bisap4 | 11410 | 11410 | 8909 | 11410 | 1658 | 8214 | 3196 | 11410 | 28490 | 2.496932515337423 | 2.8013146362839616 | 0 | 0 |
| COPD | 1.0 | qsofa_ett_as1 | 11410 | 11410 | 8909 | 11410 | 1658 | 11260 | 121 | 11381 | 24422 | 2.1404031551270815 | 2.1591586327782646 | 29 | 0 |
| COPD | 1.0 | qsofa_gcs15_ett_as1 | 11410 | 11410 | 8909 | 11410 | 1658 | 11260 | 121 | 11381 | 26147 | 2.291586327782647 | 2.31034180543383 | 29 | 0 |
| COPD | 1.0 | curb65_ett_as1 | 11410 | 11410 | 8909 | 11410 | 1658 | 11097 | 313 | 11410 | 37097 | 3.2512708150744962 | 3.287116564417178 | 0 | 0 |
| COPD | 1.0 | bisap4_ett_as1 | 11410 | 11410 | 8909 | 11410 | 1658 | 9712 | 1698 | 11410 | 31236 | 2.737598597721297 | 2.896056091148116 | 0 | 0 |
| sepsis | 0.0 | qsofa | 8756 | 8756 | 7764 | 8756 | 2182 | 6679 | 2045 | 8724 | 17958 | 2.0509365006852445 | 2.299223389675651 | 32 | 0 |
| sepsis | 0.0 | qsofa_gcs15 | 8756 | 8756 | 7764 | 8756 | 2182 | 6679 | 2045 | 8724 | 19510 | 2.228186386477844 | 2.4764732754682504 | 32 | 0 |
| sepsis | 0.0 | curb65 | 8756 | 8756 | 7764 | 8756 | 2182 | 6569 | 2187 | 8756 | 27929 | 3.1896984924623117 | 3.4571722247601646 | 0 | 0 |
| sepsis | 0.0 | bisap4 | 8756 | 8756 | 7764 | 8756 | 2182 | 6270 | 2486 | 8756 | 23198 | 2.649383280036546 | 2.9520328917313843 | 0 | 0 |
| sepsis | 0.0 | qsofa_ett_as1 | 8756 | 8756 | 7764 | 8756 | 2182 | 8643 | 81 | 8724 | 20644 | 2.3576975788031063 | 2.3782549109182276 | 32 | 0 |
| sepsis | 0.0 | qsofa_gcs15_ett_as1 | 8756 | 8756 | 7764 | 8756 | 2182 | 8643 | 81 | 8724 | 21959 | 2.5078803106441296 | 2.528437642759251 | 32 | 0 |
| sepsis | 0.0 | curb65_ett_as1 | 8756 | 8756 | 7764 | 8756 | 2182 | 8510 | 246 | 8756 | 30378 | 3.4693924166285974 | 3.509136592051165 | 0 | 0 |
| sepsis | 0.0 | bisap4_ett_as1 | 8756 | 8756 | 7764 | 8756 | 2182 | 8192 | 564 | 8756 | 25647 | 2.9290772042028324 | 3.0039972590223845 | 0 | 0 |
| sepsis | 1.0 | qsofa | 5366 | 5366 | 5024 | 5366 | 1801 | 4125 | 1216 | 5341 | 10686 | 1.9914275065225493 | 2.235557212076034 | 25 | 0 |
| sepsis | 1.0 | qsofa_gcs15 | 5366 | 5366 | 5024 | 5366 | 1801 | 4125 | 1216 | 5341 | 11633 | 2.1679090570257173 | 2.4120387625792024 | 25 | 0 |
| sepsis | 1.0 | curb65 | 5366 | 5366 | 5024 | 5366 | 1801 | 4093 | 1273 | 5366 | 16347 | 3.046403279910548 | 3.3039508013417818 | 0 | 0 |
| sepsis | 1.0 | bisap4 | 5366 | 5366 | 5024 | 5366 | 1801 | 3910 | 1456 | 5366 | 13648 | 2.543421543048826 | 2.840290719344018 | 0 | 0 |
| sepsis | 1.0 | qsofa_ett_as1 | 5366 | 5366 | 5024 | 5366 | 1801 | 5281 | 60 | 5341 | 12468 | 2.3235184494968317 | 2.3488632128214686 | 25 | 0 |
| sepsis | 1.0 | qsofa_gcs15_ett_as1 | 5366 | 5366 | 5024 | 5366 | 1801 | 5281 | 60 | 5341 | 13220 | 2.4636600819977637 | 2.4890048453224005 | 25 | 0 |
| sepsis | 1.0 | curb65_ett_as1 | 5366 | 5366 | 5024 | 5366 | 1801 | 5225 | 141 | 5366 | 17934 | 3.342154304882594 | 3.3809168840849795 | 0 | 0 |
| sepsis | 1.0 | bisap4_ett_as1 | 5366 | 5366 | 5024 | 5366 | 1801 | 5002 | 364 | 5366 | 15235 | 2.839172568020872 | 2.917256802087216 | 0 | 0 |
| pancreatitis | 0.0 | qsofa | 476 | 476 | 440 | 476 | 42 | 423 | 51 | 474 | 740 | 1.5546218487394958 | 1.6743697478991597 | 2 | 0 |
| pancreatitis | 0.0 | qsofa_gcs15 | 476 | 476 | 440 | 476 | 42 | 423 | 51 | 474 | 828 | 1.7394957983193278 | 1.8592436974789917 | 2 | 0 |
| pancreatitis | 0.0 | curb65 | 476 | 476 | 440 | 476 | 42 | 417 | 59 | 476 | 1047 | 2.1995798319327733 | 2.3340336134453783 | 0 | 0 |
| pancreatitis | 0.0 | bisap4 | 476 | 476 | 440 | 476 | 42 | 389 | 87 | 476 | 947 | 1.9894957983193278 | 2.180672268907563 | 0 | 0 |
| pancreatitis | 0.0 | qsofa_ett_as1 | 476 | 476 | 440 | 476 | 42 | 471 | 3 | 474 | 823 | 1.7289915966386555 | 1.7478991596638656 | 2 | 0 |
| pancreatitis | 0.0 | qsofa_gcs15_ett_as1 | 476 | 476 | 440 | 476 | 42 | 471 | 3 | 474 | 900 | 1.8907563025210083 | 1.9096638655462186 | 2 | 0 |
| pancreatitis | 0.0 | curb65_ett_as1 | 476 | 476 | 440 | 476 | 42 | 465 | 11 | 476 | 1119 | 2.350840336134454 | 2.384453781512605 | 0 | 0 |
| pancreatitis | 0.0 | bisap4_ett_as1 | 476 | 476 | 440 | 476 | 42 | 437 | 39 | 476 | 1019 | 2.1407563025210083 | 2.23109243697479 | 0 | 0 |
| pancreatitis | 1.0 | qsofa | 922 | 922 | 881 | 922 | 166 | 728 | 191 | 919 | 1624 | 1.7613882863340564 | 1.9859002169197397 | 3 | 0 |
| pancreatitis | 1.0 | qsofa_gcs15 | 922 | 922 | 881 | 922 | 166 | 728 | 191 | 919 | 1823 | 1.9772234273318872 | 2.2017353579175705 | 3 | 0 |
| pancreatitis | 1.0 | curb65 | 922 | 922 | 881 | 922 | 166 | 717 | 205 | 922 | 2413 | 2.617136659436009 | 2.8600867678958783 | 0 | 0 |
| pancreatitis | 1.0 | bisap4 | 922 | 922 | 881 | 922 | 166 | 678 | 244 | 922 | 2068 | 2.24295010845987 | 2.527114967462039 | 0 | 0 |
| pancreatitis | 1.0 | qsofa_ett_as1 | 922 | 922 | 881 | 922 | 166 | 904 | 15 | 919 | 1946 | 2.110629067245119 | 2.1377440347071586 | 3 | 0 |
| pancreatitis | 1.0 | qsofa_gcs15_ett_as1 | 922 | 922 | 881 | 922 | 166 | 904 | 15 | 919 | 2087 | 2.2635574837310197 | 2.2906724511930587 | 3 | 0 |
| pancreatitis | 1.0 | curb65_ett_as1 | 922 | 922 | 881 | 922 | 166 | 890 | 32 | 922 | 2677 | 2.903470715835141 | 2.9490238611713666 | 0 | 0 |
| pancreatitis | 1.0 | bisap4_ett_as1 | 922 | 922 | 881 | 922 | 166 | 854 | 68 | 922 | 2332 | 2.529284164859002 | 2.6160520607375273 | 0 | 0 |
| sepsis_narrow | 0.0 | qsofa | 8544 | 8544 | 7582 | 8544 | 2145 | 6523 | 1989 | 8512 | 17539 | 2.0527855805243447 | 2.300561797752809 | 32 | 0 |
| sepsis_narrow | 0.0 | qsofa_gcs15 | 8544 | 8544 | 7582 | 8544 | 2145 | 6523 | 1989 | 8512 | 19052 | 2.2298689138576777 | 2.4776451310861423 | 32 | 0 |
| sepsis_narrow | 0.0 | curb65 | 8544 | 8544 | 7582 | 8544 | 2145 | 6416 | 2128 | 8544 | 27260 | 3.1905430711610485 | 3.4575140449438204 | 0 | 0 |
| sepsis_narrow | 0.0 | bisap4 | 8544 | 8544 | 7582 | 8544 | 2145 | 6125 | 2419 | 8544 | 22643 | 2.6501638576779025 | 2.952247191011236 | 0 | 0 |
| sepsis_narrow | 0.0 | qsofa_ett_as1 | 8544 | 8544 | 7582 | 8544 | 2145 | 8434 | 78 | 8512 | 20158 | 2.359316479400749 | 2.3800327715355807 | 32 | 0 |
| sepsis_narrow | 0.0 | qsofa_gcs15_ett_as1 | 8544 | 8544 | 7582 | 8544 | 2145 | 8434 | 78 | 8512 | 21441 | 2.5094803370786516 | 2.530196629213483 | 32 | 0 |
| sepsis_narrow | 0.0 | curb65_ett_as1 | 8544 | 8544 | 7582 | 8544 | 2145 | 8305 | 239 | 8544 | 29649 | 3.4701544943820224 | 3.510065543071161 | 0 | 0 |
| sepsis_narrow | 0.0 | bisap4_ett_as1 | 8544 | 8544 | 7582 | 8544 | 2145 | 7994 | 550 | 8544 | 25032 | 2.9297752808988764 | 3.004798689138577 | 0 | 0 |
| sepsis_narrow | 1.0 | qsofa | 5066 | 5066 | 4763 | 5066 | 1694 | 3910 | 1133 | 5043 | 10098 | 1.9932885906040267 | 2.233912356889064 | 23 | 0 |
| sepsis_narrow | 1.0 | qsofa_gcs15 | 5066 | 5066 | 4763 | 5066 | 1694 | 3910 | 1133 | 5043 | 11006 | 2.17252270035531 | 2.4131464666403475 | 23 | 0 |
| sepsis_narrow | 1.0 | curb65 | 5066 | 5066 | 4763 | 5066 | 1694 | 3881 | 1185 | 5066 | 15432 | 3.0461902881958154 | 3.2994472956968024 | 0 | 0 |
| sepsis_narrow | 1.0 | bisap4 | 5066 | 5066 | 4763 | 5066 | 1694 | 3709 | 1357 | 5066 | 12899 | 2.5461902881958154 | 2.8387287801026453 | 0 | 0 |
| sepsis_narrow | 1.0 | qsofa_ett_as1 | 5066 | 5066 | 4763 | 5066 | 1694 | 4988 | 55 | 5043 | 11777 | 2.324713778128701 | 2.3493880773786024 | 23 | 0 |
| sepsis_narrow | 1.0 | qsofa_gcs15_ett_as1 | 5066 | 5066 | 4763 | 5066 | 1694 | 4988 | 55 | 5043 | 12495 | 2.466442953020134 | 2.4911172522700356 | 23 | 0 |
| sepsis_narrow | 1.0 | curb65_ett_as1 | 5066 | 5066 | 4763 | 5066 | 1694 | 4937 | 129 | 5066 | 16921 | 3.3401105408606395 | 3.3774180813264905 | 0 | 0 |
| sepsis_narrow | 1.0 | bisap4_ett_as1 | 5066 | 5066 | 4763 | 5066 | 1694 | 4727 | 339 | 5066 | 14388 | 2.8401105408606395 | 2.9166995657323334 | 0 | 0 |
| pneumonia_narrow | 0.0 | qsofa | 362 | 362 | 342 | 362 | 34 | 313 | 47 | 360 | 666 | 1.839779005524862 | 1.9861878453038675 | 2 | 0 |
| pneumonia_narrow | 0.0 | qsofa_gcs15 | 362 | 362 | 342 | 362 | 34 | 313 | 47 | 360 | 720 | 1.988950276243094 | 2.1353591160220993 | 2 | 0 |
| pneumonia_narrow | 0.0 | curb65 | 362 | 362 | 342 | 362 | 34 | 307 | 55 | 362 | 1076 | 2.972375690607735 | 3.138121546961326 | 0 | 0 |
| pneumonia_narrow | 0.0 | bisap4 | 362 | 362 | 342 | 362 | 34 | 285 | 77 | 362 | 849 | 2.345303867403315 | 2.5718232044198897 | 0 | 0 |
| pneumonia_narrow | 0.0 | qsofa_ett_as1 | 362 | 362 | 342 | 362 | 34 | 358 | 2 | 360 | 748 | 2.0662983425414363 | 2.088397790055249 | 2 | 0 |
| pneumonia_narrow | 0.0 | qsofa_gcs15_ett_as1 | 362 | 362 | 342 | 362 | 34 | 358 | 2 | 360 | 794 | 2.1933701657458564 | 2.2154696132596685 | 2 | 0 |
| pneumonia_narrow | 0.0 | curb65_ett_as1 | 362 | 362 | 342 | 362 | 34 | 351 | 11 | 362 | 1150 | 3.1767955801104972 | 3.218232044198895 | 0 | 0 |
| pneumonia_narrow | 0.0 | bisap4_ett_as1 | 362 | 362 | 342 | 362 | 34 | 327 | 35 | 362 | 923 | 2.5497237569060776 | 2.6519337016574585 | 0 | 0 |
| pneumonia_narrow | 1.0 | qsofa | 3125 | 3125 | 2935 | 3125 | 642 | 1895 | 1216 | 3111 | 6001 | 1.92032 | 2.32704 | 14 | 0 |
| pneumonia_narrow | 1.0 | qsofa_gcs15 | 3125 | 3125 | 2935 | 3125 | 642 | 1895 | 1216 | 3111 | 6375 | 2.04 | 2.44672 | 14 | 0 |
| pneumonia_narrow | 1.0 | curb65 | 3125 | 3125 | 2935 | 3125 | 642 | 1872 | 1253 | 3125 | 9025 | 2.888 | 3.30912 | 0 | 0 |
| pneumonia_narrow | 1.0 | bisap4 | 3125 | 3125 | 2935 | 3125 | 642 | 1751 | 1374 | 3125 | 7338 | 2.34816 | 2.82656 | 0 | 0 |
| pneumonia_narrow | 1.0 | qsofa_ett_as1 | 3125 | 3125 | 2935 | 3125 | 642 | 3077 | 34 | 3111 | 7529 | 2.40928 | 2.43456 | 14 | 0 |
| pneumonia_narrow | 1.0 | qsofa_gcs15_ett_as1 | 3125 | 3125 | 2935 | 3125 | 642 | 3077 | 34 | 3111 | 7799 | 2.49568 | 2.52096 | 14 | 0 |
| pneumonia_narrow | 1.0 | curb65_ett_as1 | 3125 | 3125 | 2935 | 3125 | 642 | 3038 | 87 | 3125 | 10449 | 3.34368 | 3.38336 | 0 | 0 |
| pneumonia_narrow | 1.0 | bisap4_ett_as1 | 3125 | 3125 | 2935 | 3125 | 642 | 2853 | 272 | 3125 | 8762 | 2.80384 | 2.9008 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa | 2946 | 2946 | 2432 | 2946 | 344 | 2764 | 177 | 2941 | 5321 | 1.8061778682959946 | 1.8730482009504412 | 5 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa_gcs15 | 2946 | 2946 | 2432 | 2946 | 344 | 2764 | 177 | 2941 | 5902 | 2.0033944331296674 | 2.0702647657841142 | 5 | 0 |
| heart failure_legacy_broad | 0.0 | curb65 | 2946 | 2946 | 2432 | 2946 | 344 | 2739 | 207 | 2946 | 9622 | 3.26612355736592 | 3.344195519348269 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | bisap4 | 2946 | 2946 | 2432 | 2946 | 344 | 2248 | 698 | 2946 | 7863 | 2.669042769857434 | 2.9209097080787507 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa_ett_as1 | 2946 | 2946 | 2432 | 2946 | 344 | 2907 | 34 | 2941 | 5623 | 1.9086897488119483 | 1.9253224711473185 | 5 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa_gcs15_ett_as1 | 2946 | 2946 | 2432 | 2946 | 344 | 2907 | 34 | 2941 | 6157 | 2.0899524779361847 | 2.106585200271555 | 5 | 0 |
| heart failure_legacy_broad | 0.0 | curb65_ett_as1 | 2946 | 2946 | 2432 | 2946 | 344 | 2880 | 66 | 2946 | 9877 | 3.3526816021724373 | 3.3805159538357095 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | bisap4_ett_as1 | 2946 | 2946 | 2432 | 2946 | 344 | 2377 | 569 | 2946 | 8118 | 2.7556008146639512 | 2.9572301425661913 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa | 19873 | 19873 | 15364 | 19873 | 3016 | 16649 | 3176 | 19825 | 37241 | 1.8739495798319328 | 2.043727670709002 | 48 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa_gcs15 | 19873 | 19873 | 15364 | 19873 | 3016 | 16649 | 3176 | 19825 | 41064 | 2.066321139234137 | 2.2360992301112064 | 48 | 0 |
| heart failure_legacy_broad | 1.0 | curb65 | 19873 | 19873 | 15364 | 19873 | 3016 | 16426 | 3447 | 19873 | 62698 | 3.154933829819353 | 3.3402606551602676 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | bisap4 | 19873 | 19873 | 15364 | 19873 | 3016 | 14051 | 5822 | 19873 | 52013 | 2.61726966235596 | 2.9343833341719923 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa_ett_as1 | 19873 | 19873 | 15364 | 19873 | 3016 | 19597 | 228 | 19825 | 43009 | 2.164192623157047 | 2.183414683238565 | 48 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa_gcs15_ett_as1 | 19873 | 19873 | 15364 | 19873 | 3016 | 19597 | 228 | 19825 | 45933 | 2.311326925979973 | 2.3305489860614905 | 48 | 0 |
| heart failure_legacy_broad | 1.0 | curb65_ett_as1 | 19873 | 19873 | 15364 | 19873 | 3016 | 19336 | 537 | 19873 | 67567 | 3.399939616565189 | 3.434710411110552 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | bisap4_ett_as1 | 19873 | 19873 | 15364 | 19873 | 3016 | 16753 | 3120 | 19873 | 56882 | 2.8622754491017965 | 3.0288330901222764 | 0 | 0 |
| COPD_legacy_broad | 0.0 | qsofa | 522 | 522 | 422 | 522 | 30 | 467 | 55 | 522 | 878 | 1.681992337164751 | 1.7873563218390804 | 0 | 0 |
| COPD_legacy_broad | 0.0 | qsofa_gcs15 | 522 | 522 | 422 | 522 | 30 | 467 | 55 | 522 | 961 | 1.8409961685823755 | 1.946360153256705 | 0 | 0 |
| COPD_legacy_broad | 0.0 | curb65 | 522 | 522 | 422 | 522 | 30 | 456 | 66 | 522 | 1486 | 2.846743295019157 | 2.9770114942528734 | 0 | 0 |
| COPD_legacy_broad | 0.0 | bisap4 | 522 | 522 | 422 | 522 | 30 | 408 | 114 | 522 | 1208 | 2.314176245210728 | 2.553639846743295 | 0 | 0 |
| COPD_legacy_broad | 0.0 | qsofa_ett_as1 | 522 | 522 | 422 | 522 | 30 | 520 | 2 | 522 | 963 | 1.8448275862068966 | 1.8486590038314177 | 0 | 0 |
| COPD_legacy_broad | 0.0 | qsofa_gcs15_ett_as1 | 522 | 522 | 422 | 522 | 30 | 520 | 2 | 522 | 1039 | 1.9904214559386972 | 1.9942528735632183 | 0 | 0 |
| COPD_legacy_broad | 0.0 | curb65_ett_as1 | 522 | 522 | 422 | 522 | 30 | 508 | 14 | 522 | 1564 | 2.996168582375479 | 3.024904214559387 | 0 | 0 |
| COPD_legacy_broad | 0.0 | bisap4_ett_as1 | 522 | 522 | 422 | 522 | 30 | 453 | 69 | 522 | 1286 | 2.4636015325670497 | 2.6015325670498086 | 0 | 0 |
| COPD_legacy_broad | 1.0 | qsofa | 11993 | 11993 | 9340 | 11993 | 1727 | 10107 | 1853 | 11960 | 22169 | 1.8484949553906445 | 2.0137580255148837 | 33 | 0 |
| COPD_legacy_broad | 1.0 | qsofa_gcs15 | 11993 | 11993 | 9340 | 11993 | 1727 | 10107 | 1853 | 11960 | 24547 | 2.0467772867506047 | 2.2120403568748435 | 33 | 0 |
| COPD_legacy_broad | 1.0 | curb65 | 11993 | 11993 | 9340 | 11993 | 1727 | 9962 | 2031 | 11993 | 35942 | 2.9969148670057533 | 3.1791044776119404 | 0 | 0 |
| COPD_legacy_broad | 1.0 | bisap4 | 11993 | 11993 | 9340 | 11993 | 1727 | 8644 | 3349 | 11993 | 29775 | 2.4826982406403735 | 2.7861252397231717 | 0 | 0 |
| COPD_legacy_broad | 1.0 | qsofa_ett_as1 | 11993 | 11993 | 9340 | 11993 | 1727 | 11835 | 125 | 11960 | 25631 | 2.1371633452847494 | 2.156341199032769 | 33 | 0 |
| COPD_legacy_broad | 1.0 | qsofa_gcs15_ett_as1 | 11993 | 11993 | 9340 | 11993 | 1727 | 11835 | 125 | 11960 | 27443 | 2.2882514800300173 | 2.307429333778037 | 33 | 0 |
| COPD_legacy_broad | 1.0 | curb65_ett_as1 | 11993 | 11993 | 9340 | 11993 | 1727 | 11667 | 326 | 11993 | 38838 | 3.2383890602851664 | 3.2744934545151336 | 0 | 0 |
| COPD_legacy_broad | 1.0 | bisap4_ett_as1 | 11993 | 11993 | 9340 | 11993 | 1727 | 10225 | 1768 | 11993 | 32671 | 2.7241724339197866 | 2.8815142166263654 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa | 529 | 529 | 479 | 529 | 43 | 474 | 53 | 527 | 827 | 1.563327032136106 | 1.6748582230623819 | 2 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa_gcs15 | 529 | 529 | 479 | 529 | 43 | 474 | 53 | 527 | 927 | 1.7523629489603025 | 1.8638941398865785 | 2 | 0 |
| pancreatitis_legacy_broad | 0.0 | curb65 | 529 | 529 | 479 | 529 | 43 | 467 | 62 | 529 | 1173 | 2.217391304347826 | 2.344045368620038 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | bisap4 | 529 | 529 | 479 | 529 | 43 | 434 | 95 | 529 | 1052 | 1.988657844990548 | 2.175803402646503 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa_ett_as1 | 529 | 529 | 479 | 529 | 43 | 524 | 3 | 527 | 918 | 1.7353497164461247 | 1.7523629489603025 | 2 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa_gcs15_ett_as1 | 529 | 529 | 479 | 529 | 43 | 524 | 3 | 527 | 1005 | 1.8998109640831757 | 1.9168241965973536 | 2 | 0 |
| pancreatitis_legacy_broad | 0.0 | curb65_ett_as1 | 529 | 529 | 479 | 529 | 43 | 517 | 12 | 529 | 1251 | 2.3648393194706996 | 2.3969754253308126 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | bisap4_ett_as1 | 529 | 529 | 479 | 529 | 43 | 484 | 45 | 529 | 1130 | 2.1361058601134215 | 2.228733459357278 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa | 1366 | 1366 | 1243 | 1366 | 208 | 1120 | 242 | 1362 | 2362 | 1.7291361639824305 | 1.9202049780380674 | 4 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa_gcs15 | 1366 | 1366 | 1243 | 1366 | 208 | 1120 | 242 | 1362 | 2668 | 1.9531478770131772 | 2.144216691068814 | 4 | 0 |
| pancreatitis_legacy_broad | 1.0 | curb65 | 1366 | 1366 | 1243 | 1366 | 208 | 1101 | 265 | 1366 | 3491 | 2.555636896046852 | 2.7650073206442167 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | bisap4 | 1366 | 1366 | 1243 | 1366 | 208 | 1018 | 348 | 1366 | 3009 | 2.2027818448023426 | 2.4743777452415814 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa_ett_as1 | 1366 | 1366 | 1243 | 1366 | 208 | 1346 | 16 | 1362 | 2793 | 2.0446559297218156 | 2.0658857979502194 | 4 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa_gcs15_ett_as1 | 1366 | 1366 | 1243 | 1366 | 208 | 1346 | 16 | 1362 | 3025 | 2.214494875549048 | 2.2357247437774523 | 4 | 0 |
| pancreatitis_legacy_broad | 1.0 | curb65_ett_as1 | 1366 | 1366 | 1243 | 1366 | 208 | 1324 | 42 | 1366 | 3848 | 2.8169838945827235 | 2.856515373352855 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | bisap4_ett_as1 | 1366 | 1366 | 1243 | 1366 | 208 | 1242 | 124 | 1366 | 3366 | 2.4641288433382136 | 2.5658857979502194 | 0 | 0 |

## Supplementary Table 15. MIMIC-III reconstructed score coverage

| definition | grp | score | n_rows | n_hadm | n_pid | n_died_observed | n_died | n_score_complete | n_score_partial | n_score_any_observed_component | observed_points_total | mean_score_lower | mean_score_upper | n_score_all_components_unknown | n_outcome_missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| heart failure | 0.0 | qsofa | 1543 | 1543 | 1316 | 1543 | 186 | 1467 | 42 | 1509 | 2956 | 1.915748541801685 | 2.0090732339598185 | 34 | 0 |
| heart failure | 0.0 | qsofa_gcs15 | 1543 | 1543 | 1316 | 1543 | 186 | 1467 | 42 | 1509 | 3204 | 2.0764744005184705 | 2.169799092676604 | 34 | 0 |
| heart failure | 0.0 | curb65 | 1543 | 1543 | 1316 | 1543 | 186 | 1461 | 82 | 1543 | 5130 | 3.324692158133506 | 3.4290343486714194 | 0 | 0 |
| heart failure | 0.0 | bisap4 | 1543 | 1543 | 1316 | 1543 | 186 | 1321 | 222 | 1543 | 4361 | 2.8263123784834736 | 3.001944264419961 | 0 | 0 |
| heart failure | 0.0 | qsofa_ett_as1 | 1543 | 1543 | 1316 | 1543 | 186 | 1503 | 6 | 1509 | 3053 | 1.9786130913804278 | 2.0486066104990277 | 34 | 0 |
| heart failure | 0.0 | qsofa_gcs15_ett_as1 | 1543 | 1543 | 1316 | 1543 | 186 | 1503 | 6 | 1509 | 3284 | 2.1283214517174334 | 2.1983149708360337 | 34 | 0 |
| heart failure | 0.0 | curb65_ett_as1 | 1543 | 1543 | 1316 | 1543 | 186 | 1497 | 46 | 1543 | 5210 | 3.3765392093324693 | 3.457550226830849 | 0 | 0 |
| heart failure | 0.0 | bisap4_ett_as1 | 1543 | 1543 | 1316 | 1543 | 186 | 1354 | 189 | 1543 | 4441 | 2.878159429682437 | 3.0304601425793907 | 0 | 0 |
| heart failure | 1.0 | qsofa | 11904 | 11904 | 9312 | 11904 | 1782 | 10952 | 696 | 11648 | 23995 | 2.015709005376344 | 2.1390288978494625 | 256 | 0 |
| heart failure | 1.0 | qsofa_gcs15 | 11904 | 11904 | 9312 | 11904 | 1782 | 10952 | 696 | 11648 | 25748 | 2.162970430107527 | 2.286290322580645 | 256 | 0 |
| heart failure | 1.0 | curb65 | 11904 | 11904 | 9312 | 11904 | 1782 | 10921 | 983 | 11904 | 38917 | 3.2692372311827955 | 3.404317876344086 | 0 | 0 |
| heart failure | 1.0 | bisap4 | 11904 | 11904 | 9312 | 11904 | 1782 | 10003 | 1901 | 11904 | 33160 | 2.7856182795698925 | 2.9810987903225805 | 0 | 0 |
| heart failure | 1.0 | qsofa_ett_as1 | 11904 | 11904 | 9312 | 11904 | 1782 | 11587 | 61 | 11648 | 25296 | 2.125 | 2.1948084677419355 | 256 | 0 |
| heart failure | 1.0 | qsofa_gcs15_ett_as1 | 11904 | 11904 | 9312 | 11904 | 1782 | 11587 | 61 | 11648 | 26839 | 2.2546202956989245 | 2.32442876344086 | 256 | 0 |
| heart failure | 1.0 | curb65_ett_as1 | 11904 | 11904 | 9312 | 11904 | 1782 | 11555 | 349 | 11904 | 40008 | 3.3608870967741935 | 3.442456317204301 | 0 | 0 |
| heart failure | 1.0 | bisap4_ett_as1 | 11904 | 11904 | 9312 | 11904 | 1782 | 10592 | 1312 | 11904 | 34251 | 2.8772681451612905 | 3.0192372311827955 | 0 | 0 |
| pneumonia | 0.0 | qsofa | 1756 | 1756 | 1559 | 1756 | 282 | 1616 | 98 | 1714 | 3592 | 2.0455580865603644 | 2.173120728929385 | 42 | 0 |
| pneumonia | 0.0 | qsofa_gcs15 | 1756 | 1756 | 1559 | 1756 | 282 | 1616 | 98 | 1714 | 3847 | 2.190774487471526 | 2.318337129840547 | 42 | 0 |
| pneumonia | 0.0 | curb65 | 1756 | 1756 | 1559 | 1756 | 282 | 1603 | 153 | 1756 | 5726 | 3.2608200455580865 | 3.40375854214123 | 0 | 0 |
| pneumonia | 0.0 | bisap4 | 1756 | 1756 | 1559 | 1756 | 282 | 1549 | 207 | 1756 | 4701 | 2.677107061503417 | 2.8280182232346243 | 0 | 0 |
| pneumonia | 0.0 | qsofa_ett_as1 | 1756 | 1756 | 1559 | 1756 | 282 | 1701 | 13 | 1714 | 3734 | 2.1264236902050113 | 2.2055808656036446 | 42 | 0 |
| pneumonia | 0.0 | qsofa_gcs15_ett_as1 | 1756 | 1756 | 1559 | 1756 | 282 | 1701 | 13 | 1714 | 3975 | 2.2636674259681095 | 2.3428246013667424 | 42 | 0 |
| pneumonia | 0.0 | curb65_ett_as1 | 1756 | 1756 | 1559 | 1756 | 282 | 1688 | 68 | 1756 | 5854 | 3.3337129840546695 | 3.428246013667426 | 0 | 0 |
| pneumonia | 0.0 | bisap4_ett_as1 | 1756 | 1756 | 1559 | 1756 | 282 | 1634 | 122 | 1756 | 4829 | 2.75 | 2.85250569476082 | 0 | 0 |
| pneumonia | 1.0 | qsofa | 8544 | 8544 | 7690 | 8544 | 1845 | 7569 | 835 | 8404 | 18171 | 2.126755617977528 | 2.27375936329588 | 140 | 0 |
| pneumonia | 1.0 | qsofa_gcs15 | 8544 | 8544 | 7690 | 8544 | 1845 | 7569 | 835 | 8404 | 19171 | 2.2437968164794007 | 2.390800561797753 | 140 | 0 |
| pneumonia | 1.0 | curb65 | 8544 | 8544 | 7690 | 8544 | 1845 | 7545 | 999 | 8544 | 27071 | 3.168422284644195 | 3.323384831460674 | 0 | 0 |
| pneumonia | 1.0 | bisap4 | 8544 | 8544 | 7690 | 8544 | 1845 | 7251 | 1293 | 8544 | 22995 | 2.6913623595505616 | 2.868679775280899 | 0 | 0 |
| pneumonia | 1.0 | qsofa_ett_as1 | 8544 | 8544 | 7690 | 8544 | 1845 | 8373 | 31 | 8404 | 19366 | 2.266619850187266 | 2.3194054307116105 | 140 | 0 |
| pneumonia | 1.0 | qsofa_gcs15_ett_as1 | 8544 | 8544 | 7690 | 8544 | 1845 | 8373 | 31 | 8404 | 20253 | 2.370435393258427 | 2.4232209737827715 | 140 | 0 |
| pneumonia | 1.0 | curb65_ett_as1 | 8544 | 8544 | 7690 | 8544 | 1845 | 8347 | 197 | 8544 | 28153 | 3.295060861423221 | 3.355805243445693 | 0 | 0 |
| pneumonia | 1.0 | bisap4_ett_as1 | 8544 | 8544 | 7690 | 8544 | 1845 | 8024 | 520 | 8544 | 24077 | 2.818000936329588 | 2.9011001872659175 | 0 | 0 |
| COPD | 0.0 | qsofa | 309 | 309 | 244 | 309 | 25 | 294 | 6 | 300 | 543 | 1.7572815533980584 | 1.8640776699029127 | 9 | 0 |
| COPD | 0.0 | qsofa_gcs15 | 309 | 309 | 244 | 309 | 25 | 294 | 6 | 300 | 589 | 1.9061488673139158 | 2.01294498381877 | 9 | 0 |
| COPD | 0.0 | curb65 | 309 | 309 | 244 | 309 | 25 | 292 | 17 | 309 | 914 | 2.957928802588997 | 3.0906148867313914 | 0 | 0 |
| COPD | 0.0 | bisap4 | 309 | 309 | 244 | 309 | 25 | 274 | 35 | 309 | 754 | 2.440129449838188 | 2.6019417475728157 | 0 | 0 |
| COPD | 0.0 | qsofa_ett_as1 | 309 | 309 | 244 | 309 | 25 | 300 | 0 | 300 | 556 | 1.7993527508090614 | 1.8867313915857604 | 9 | 0 |
| COPD | 0.0 | qsofa_gcs15_ett_as1 | 309 | 309 | 244 | 309 | 25 | 300 | 0 | 300 | 599 | 1.9385113268608414 | 2.0258899676375406 | 9 | 0 |
| COPD | 0.0 | curb65_ett_as1 | 309 | 309 | 244 | 309 | 25 | 298 | 11 | 309 | 924 | 2.9902912621359223 | 3.103559870550162 | 0 | 0 |
| COPD | 0.0 | bisap4_ett_as1 | 309 | 309 | 244 | 309 | 25 | 280 | 29 | 309 | 764 | 2.472491909385113 | 2.614886731391586 | 0 | 0 |
| COPD | 1.0 | qsofa | 5988 | 5988 | 4706 | 5988 | 854 | 5463 | 407 | 5870 | 11984 | 2.0013360053440215 | 2.1285905143620574 | 118 | 0 |
| COPD | 1.0 | qsofa_gcs15 | 5988 | 5988 | 4706 | 5988 | 854 | 5463 | 407 | 5870 | 12921 | 2.157815631262525 | 2.285070140280561 | 118 | 0 |
| COPD | 1.0 | curb65 | 5988 | 5988 | 4706 | 5988 | 854 | 5443 | 545 | 5988 | 18996 | 3.1723446893787575 | 3.311122244488978 | 0 | 0 |
| COPD | 1.0 | bisap4 | 5988 | 5988 | 4706 | 5988 | 854 | 5034 | 954 | 5988 | 16229 | 2.7102538410153643 | 2.903306613226453 | 0 | 0 |
| COPD | 1.0 | qsofa_ett_as1 | 5988 | 5988 | 4706 | 5988 | 854 | 5842 | 28 | 5870 | 12785 | 2.135103540414162 | 2.1988977955911824 | 118 | 0 |
| COPD | 1.0 | qsofa_gcs15_ett_as1 | 5988 | 5988 | 4706 | 5988 | 854 | 5842 | 28 | 5870 | 13592 | 2.269873079492318 | 2.3336673346693386 | 118 | 0 |
| COPD | 1.0 | curb65_ett_as1 | 5988 | 5988 | 4706 | 5988 | 854 | 5821 | 167 | 5988 | 19667 | 3.2844021376085504 | 3.3597194388777556 | 0 | 0 |
| COPD | 1.0 | bisap4_ett_as1 | 5988 | 5988 | 4706 | 5988 | 854 | 5385 | 603 | 5988 | 16900 | 2.822311289245157 | 2.9519038076152304 | 0 | 0 |
| sepsis | 0.0 | qsofa | 3398 | 3398 | 3075 | 3398 | 956 | 2958 | 376 | 3334 | 7522 | 2.213655091230135 | 2.381400824014126 | 64 | 0 |
| sepsis | 0.0 | qsofa_gcs15 | 3398 | 3398 | 3075 | 3398 | 956 | 2958 | 376 | 3334 | 7993 | 2.35226603884638 | 2.520011771630371 | 64 | 0 |
| sepsis | 0.0 | curb65 | 3398 | 3398 | 3075 | 3398 | 956 | 2948 | 450 | 3398 | 11479 | 3.3781636256621543 | 3.554149499705709 | 0 | 0 |
| sepsis | 0.0 | bisap4 | 3398 | 3398 | 3075 | 3398 | 956 | 2900 | 498 | 3398 | 9775 | 2.8766921718658036 | 3.0491465567981164 | 0 | 0 |
| sepsis | 0.0 | qsofa_ett_as1 | 3398 | 3398 | 3075 | 3398 | 956 | 3307 | 27 | 3334 | 8004 | 2.3555032371983518 | 2.4199529134785167 | 64 | 0 |
| sepsis | 0.0 | qsofa_gcs15_ett_as1 | 3398 | 3398 | 3075 | 3398 | 956 | 3307 | 27 | 3334 | 8440 | 2.483814008240141 | 2.548263684520306 | 64 | 0 |
| sepsis | 0.0 | curb65_ett_as1 | 3398 | 3398 | 3075 | 3398 | 956 | 3295 | 103 | 3398 | 11926 | 3.5097115950559155 | 3.5824014125956447 | 0 | 0 |
| sepsis | 0.0 | bisap4_ett_as1 | 3398 | 3398 | 3075 | 3398 | 956 | 3247 | 151 | 3398 | 10222 | 3.0082401412595643 | 3.0773984696880516 | 0 | 0 |
| sepsis | 1.0 | qsofa | 2914 | 2914 | 2725 | 2914 | 1017 | 2630 | 227 | 2857 | 6371 | 2.186341798215511 | 2.322923816060398 | 57 | 0 |
| sepsis | 1.0 | qsofa_gcs15 | 2914 | 2914 | 2725 | 2914 | 1017 | 2630 | 227 | 2857 | 6771 | 2.3236101578586137 | 2.4601921757035004 | 57 | 0 |
| sepsis | 1.0 | curb65 | 2914 | 2914 | 2725 | 2914 | 1017 | 2626 | 288 | 2914 | 9361 | 3.212422786547701 | 3.355181880576527 | 0 | 0 |
| sepsis | 1.0 | bisap4 | 2914 | 2914 | 2725 | 2914 | 1017 | 2544 | 370 | 2914 | 8002 | 2.746053534660261 | 2.8994509265614274 | 0 | 0 |
| sepsis | 1.0 | qsofa_ett_as1 | 2914 | 2914 | 2725 | 2914 | 1017 | 2840 | 17 | 2857 | 6729 | 2.309196980096088 | 2.373713109128346 | 57 | 0 |
| sepsis | 1.0 | qsofa_gcs15_ett_as1 | 2914 | 2914 | 2725 | 2914 | 1017 | 2840 | 17 | 2857 | 7079 | 2.4293067947838023 | 2.4938229238160603 | 57 | 0 |
| sepsis | 1.0 | curb65_ett_as1 | 2914 | 2914 | 2725 | 2914 | 1017 | 2835 | 79 | 2914 | 9669 | 3.3181194234728895 | 3.388812628689087 | 0 | 0 |
| sepsis | 1.0 | bisap4_ett_as1 | 2914 | 2914 | 2725 | 2914 | 1017 | 2750 | 164 | 2914 | 8310 | 2.8517501715854494 | 2.933081674673988 | 0 | 0 |
| pancreatitis | 0.0 | qsofa | 366 | 366 | 344 | 366 | 40 | 335 | 25 | 360 | 633 | 1.7295081967213115 | 1.8469945355191257 | 6 | 0 |
| pancreatitis | 0.0 | qsofa_gcs15 | 366 | 366 | 344 | 366 | 40 | 335 | 25 | 360 | 693 | 1.8934426229508197 | 2.010928961748634 | 6 | 0 |
| pancreatitis | 0.0 | curb65 | 366 | 366 | 344 | 366 | 40 | 333 | 33 | 366 | 936 | 2.557377049180328 | 2.691256830601093 | 0 | 0 |
| pancreatitis | 0.0 | bisap4 | 366 | 366 | 344 | 366 | 40 | 320 | 46 | 366 | 837 | 2.2868852459016393 | 2.442622950819672 | 0 | 0 |
| pancreatitis | 0.0 | qsofa_ett_as1 | 366 | 366 | 344 | 366 | 40 | 359 | 1 | 360 | 668 | 1.825136612021858 | 1.8770491803278688 | 6 | 0 |
| pancreatitis | 0.0 | qsofa_gcs15_ett_as1 | 366 | 366 | 344 | 366 | 40 | 359 | 1 | 360 | 723 | 1.9754098360655739 | 2.0273224043715845 | 6 | 0 |
| pancreatitis | 0.0 | curb65_ett_as1 | 366 | 366 | 344 | 366 | 40 | 357 | 9 | 366 | 966 | 2.639344262295082 | 2.7076502732240435 | 0 | 0 |
| pancreatitis | 0.0 | bisap4_ett_as1 | 366 | 366 | 344 | 366 | 40 | 344 | 22 | 366 | 867 | 2.3688524590163933 | 2.459016393442623 | 0 | 0 |
| pancreatitis | 1.0 | qsofa | 587 | 587 | 574 | 587 | 103 | 518 | 57 | 575 | 1144 | 1.948892674616695 | 2.110732538330494 | 12 | 0 |
| pancreatitis | 1.0 | qsofa_gcs15 | 587 | 587 | 574 | 587 | 103 | 518 | 57 | 575 | 1238 | 2.1090289608177173 | 2.270868824531516 | 12 | 0 |
| pancreatitis | 1.0 | curb65 | 587 | 587 | 574 | 587 | 103 | 515 | 72 | 587 | 1673 | 2.8500851788756387 | 3.028960817717206 | 0 | 0 |
| pancreatitis | 1.0 | bisap4 | 587 | 587 | 574 | 587 | 103 | 495 | 92 | 587 | 1451 | 2.471890971039182 | 2.6626916524701874 | 0 | 0 |
| pancreatitis | 1.0 | qsofa_ett_as1 | 587 | 587 | 574 | 587 | 103 | 568 | 7 | 575 | 1234 | 2.10221465076661 | 2.1754684838160134 | 12 | 0 |
| pancreatitis | 1.0 | qsofa_gcs15_ett_as1 | 587 | 587 | 574 | 587 | 103 | 568 | 7 | 575 | 1317 | 2.2436115843270867 | 2.3168654173764907 | 12 | 0 |
| pancreatitis | 1.0 | curb65_ett_as1 | 587 | 587 | 574 | 587 | 103 | 565 | 22 | 587 | 1752 | 2.9846678023850086 | 3.0749574105621806 | 0 | 0 |
| pancreatitis | 1.0 | bisap4_ett_as1 | 587 | 587 | 574 | 587 | 103 | 547 | 40 | 587 | 1530 | 2.606473594548552 | 2.708688245315162 | 0 | 0 |
| sepsis_narrow | 0.0 | qsofa | 3387 | 3387 | 3066 | 3387 | 953 | 2947 | 376 | 3323 | 7497 | 2.2134632418069087 | 2.3817537643932685 | 64 | 0 |
| sepsis_narrow | 0.0 | qsofa_gcs15 | 3387 | 3387 | 3066 | 3387 | 953 | 2947 | 376 | 3323 | 7967 | 2.3522291113079423 | 2.5205196338943017 | 64 | 0 |
| sepsis_narrow | 0.0 | curb65 | 3387 | 3387 | 3066 | 3387 | 953 | 2937 | 450 | 3387 | 11444 | 3.378801299084736 | 3.5553587245349867 | 0 | 0 |
| sepsis_narrow | 0.0 | bisap4 | 3387 | 3387 | 3066 | 3387 | 953 | 2889 | 498 | 3387 | 9744 | 2.8768821966341895 | 3.0498966637142013 | 0 | 0 |
| sepsis_narrow | 0.0 | qsofa_ett_as1 | 3387 | 3387 | 3066 | 3387 | 953 | 3296 | 27 | 3323 | 7979 | 2.3557720696781814 | 2.4204310599350456 | 64 | 0 |
| sepsis_narrow | 0.0 | qsofa_gcs15_ett_as1 | 3387 | 3387 | 3066 | 3387 | 953 | 3296 | 27 | 3323 | 8414 | 2.4842043105993503 | 2.548863300856215 | 64 | 0 |
| sepsis_narrow | 0.0 | curb65_ett_as1 | 3387 | 3387 | 3066 | 3387 | 953 | 3284 | 103 | 3387 | 11891 | 3.5107764983761443 | 3.5837023914969 | 0 | 0 |
| sepsis_narrow | 0.0 | bisap4_ett_as1 | 3387 | 3387 | 3066 | 3387 | 953 | 3236 | 151 | 3387 | 10191 | 3.008857395925598 | 3.0782403306761146 | 0 | 0 |
| sepsis_narrow | 1.0 | qsofa | 2828 | 2828 | 2651 | 2828 | 981 | 2553 | 219 | 2772 | 6160 | 2.1782178217821784 | 2.315063649222065 | 56 | 0 |
| sepsis_narrow | 1.0 | qsofa_gcs15 | 2828 | 2828 | 2651 | 2828 | 981 | 2553 | 219 | 2772 | 6555 | 2.317892503536068 | 2.454738330975955 | 56 | 0 |
| sepsis_narrow | 1.0 | curb65 | 2828 | 2828 | 2651 | 2828 | 981 | 2549 | 279 | 2828 | 9068 | 3.2065063649222063 | 3.3497171145685996 | 0 | 0 |
| sepsis_narrow | 1.0 | bisap4 | 2828 | 2828 | 2651 | 2828 | 981 | 2471 | 357 | 2828 | 7757 | 2.742927864214993 | 2.896039603960396 | 0 | 0 |
| sepsis_narrow | 1.0 | qsofa_ett_as1 | 2828 | 2828 | 2651 | 2828 | 981 | 2755 | 17 | 2772 | 6505 | 2.30021216407355 | 2.3656294200848658 | 56 | 0 |
| sepsis_narrow | 1.0 | qsofa_gcs15_ett_as1 | 2828 | 2828 | 2651 | 2828 | 981 | 2755 | 17 | 2772 | 6852 | 2.422913719943423 | 2.4883309759547383 | 56 | 0 |
| sepsis_narrow | 1.0 | curb65_ett_as1 | 2828 | 2828 | 2651 | 2828 | 981 | 2750 | 78 | 2828 | 9365 | 3.3115275813295617 | 3.3833097595473833 | 0 | 0 |
| sepsis_narrow | 1.0 | bisap4_ett_as1 | 2828 | 2828 | 2651 | 2828 | 981 | 2669 | 159 | 2828 | 8054 | 2.8479490806223478 | 2.9296322489391797 | 0 | 0 |
| pneumonia_narrow | 0.0 | qsofa | 339 | 339 | 322 | 339 | 40 | 309 | 22 | 331 | 689 | 2.032448377581121 | 2.168141592920354 | 8 | 0 |
| pneumonia_narrow | 0.0 | qsofa_gcs15 | 339 | 339 | 322 | 339 | 40 | 309 | 22 | 331 | 733 | 2.162241887905605 | 2.297935103244838 | 8 | 0 |
| pneumonia_narrow | 0.0 | curb65 | 339 | 339 | 322 | 339 | 40 | 307 | 32 | 339 | 1075 | 3.1710914454277286 | 3.321533923303835 | 0 | 0 |
| pneumonia_narrow | 0.0 | bisap4 | 339 | 339 | 322 | 339 | 40 | 293 | 46 | 339 | 864 | 2.5486725663716814 | 2.7168141592920354 | 0 | 0 |
| pneumonia_narrow | 0.0 | qsofa_ett_as1 | 339 | 339 | 322 | 339 | 40 | 329 | 2 | 331 | 724 | 2.135693215339233 | 2.2123893805309733 | 8 | 0 |
| pneumonia_narrow | 0.0 | qsofa_gcs15_ett_as1 | 339 | 339 | 322 | 339 | 40 | 329 | 2 | 331 | 765 | 2.256637168141593 | 2.3333333333333335 | 8 | 0 |
| pneumonia_narrow | 0.0 | curb65_ett_as1 | 339 | 339 | 322 | 339 | 40 | 327 | 12 | 339 | 1107 | 3.265486725663717 | 3.3569321533923304 | 0 | 0 |
| pneumonia_narrow | 0.0 | bisap4_ett_as1 | 339 | 339 | 322 | 339 | 40 | 313 | 26 | 339 | 896 | 2.6430678466076696 | 2.752212389380531 | 0 | 0 |
| pneumonia_narrow | 1.0 | qsofa | 2047 | 2047 | 1902 | 2047 | 399 | 1740 | 268 | 2008 | 4599 | 2.246702491450904 | 2.4347826086956523 | 39 | 0 |
| pneumonia_narrow | 1.0 | qsofa_gcs15 | 2047 | 2047 | 1902 | 2047 | 399 | 1740 | 268 | 2008 | 4761 | 2.3258426966292136 | 2.513922813873962 | 39 | 0 |
| pneumonia_narrow | 1.0 | curb65 | 2047 | 2047 | 1902 | 2047 | 399 | 1739 | 308 | 2047 | 6591 | 3.2198339032730825 | 3.4103566194430877 | 0 | 0 |
| pneumonia_narrow | 1.0 | bisap4 | 2047 | 2047 | 1902 | 2047 | 399 | 1690 | 357 | 2047 | 5546 | 2.70933072789448 | 2.911577918905716 | 0 | 0 |
| pneumonia_narrow | 1.0 | qsofa_ett_as1 | 2047 | 2047 | 1902 | 2047 | 399 | 2001 | 7 | 2008 | 4945 | 2.4157303370786516 | 2.4763067904250122 | 39 | 0 |
| pneumonia_narrow | 1.0 | qsofa_gcs15_ett_as1 | 2047 | 2047 | 1902 | 2047 | 399 | 2001 | 7 | 2008 | 5084 | 2.4836345872007817 | 2.5442110405471423 | 39 | 0 |
| pneumonia_narrow | 1.0 | curb65_ett_as1 | 2047 | 2047 | 1902 | 2047 | 399 | 2000 | 47 | 2047 | 6914 | 3.3776257938446506 | 3.4406448461162675 | 0 | 0 |
| pneumonia_narrow | 1.0 | bisap4_ett_as1 | 2047 | 2047 | 1902 | 2047 | 399 | 1937 | 110 | 2047 | 5869 | 2.867122618466048 | 2.941866145578896 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa | 1547 | 1547 | 1320 | 1547 | 187 | 1470 | 43 | 1513 | 2963 | 1.9153199741435036 | 2.009049773755656 | 34 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa_gcs15 | 1547 | 1547 | 1320 | 1547 | 187 | 1470 | 43 | 1513 | 3211 | 2.0756302521008405 | 2.1693600517129927 | 34 | 0 |
| heart failure_legacy_broad | 0.0 | curb65 | 1547 | 1547 | 1320 | 1547 | 187 | 1464 | 83 | 1547 | 5138 | 3.321266968325792 | 3.425985778926955 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | bisap4 | 1547 | 1547 | 1320 | 1547 | 187 | 1323 | 224 | 1547 | 4369 | 2.8241758241758244 | 3.0006464124111183 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa_ett_as1 | 1547 | 1547 | 1320 | 1547 | 187 | 1507 | 6 | 1513 | 3061 | 1.9786683904330964 | 2.048480930833872 | 34 | 0 |
| heart failure_legacy_broad | 0.0 | qsofa_gcs15_ett_as1 | 1547 | 1547 | 1320 | 1547 | 187 | 1507 | 6 | 1513 | 3292 | 2.127989657401422 | 2.197802197802198 | 34 | 0 |
| heart failure_legacy_broad | 0.0 | curb65_ett_as1 | 1547 | 1547 | 1320 | 1547 | 187 | 1501 | 46 | 1547 | 5219 | 3.3736263736263736 | 3.4544279250161605 | 0 | 0 |
| heart failure_legacy_broad | 0.0 | bisap4_ett_as1 | 1547 | 1547 | 1320 | 1547 | 187 | 1357 | 190 | 1547 | 4450 | 2.876535229476406 | 3.029088558500323 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa | 11924 | 11924 | 9331 | 11924 | 1781 | 10971 | 697 | 11668 | 24024 | 2.014760147601476 | 2.1379570613887955 | 256 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa_gcs15 | 11924 | 11924 | 9331 | 11924 | 1781 | 10971 | 697 | 11668 | 25780 | 2.1620261657162025 | 2.285223079503522 | 256 | 0 |
| heart failure_legacy_broad | 1.0 | curb65 | 11924 | 11924 | 9331 | 11924 | 1781 | 10940 | 984 | 11924 | 38967 | 3.2679469976517947 | 3.4028849379402883 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | bisap4 | 11924 | 11924 | 9331 | 11924 | 1781 | 10021 | 1903 | 11924 | 33205 | 2.784719892653472 | 2.9801241194230124 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa_ett_as1 | 11924 | 11924 | 9331 | 11924 | 1781 | 11607 | 61 | 11668 | 25326 | 2.123951694062395 | 2.193643072794364 | 256 | 0 |
| heart failure_legacy_broad | 1.0 | qsofa_gcs15_ett_as1 | 11924 | 11924 | 9331 | 11924 | 1781 | 11607 | 61 | 11668 | 26872 | 2.2536061724253607 | 2.3232975511573297 | 256 | 0 |
| heart failure_legacy_broad | 1.0 | curb65_ett_as1 | 11924 | 11924 | 9331 | 11924 | 1781 | 11575 | 349 | 11924 | 40059 | 3.359527004360953 | 3.440959409594096 | 0 | 0 |
| heart failure_legacy_broad | 1.0 | bisap4_ett_as1 | 11924 | 11924 | 9331 | 11924 | 1781 | 10610 | 1314 | 11924 | 34297 | 2.87629989936263 | 3.01819859107682 | 0 | 0 |
| COPD_legacy_broad | 0.0 | qsofa | 324 | 324 | 258 | 324 | 25 | 307 | 7 | 314 | 567 | 1.75 | 1.8641975308641976 | 10 | 0 |
| COPD_legacy_broad | 0.0 | qsofa_gcs15 | 324 | 324 | 258 | 324 | 25 | 307 | 7 | 314 | 614 | 1.8950617283950617 | 2.009259259259259 | 10 | 0 |
| COPD_legacy_broad | 0.0 | curb65 | 324 | 324 | 258 | 324 | 25 | 305 | 19 | 324 | 956 | 2.950617283950617 | 3.0925925925925926 | 0 | 0 |
| COPD_legacy_broad | 0.0 | bisap4 | 324 | 324 | 258 | 324 | 25 | 286 | 38 | 324 | 787 | 2.4290123456790123 | 2.5987654320987654 | 0 | 0 |
| COPD_legacy_broad | 0.0 | qsofa_ett_as1 | 324 | 324 | 258 | 324 | 25 | 314 | 0 | 314 | 584 | 1.8024691358024691 | 1.8950617283950617 | 10 | 0 |
| COPD_legacy_broad | 0.0 | qsofa_gcs15_ett_as1 | 324 | 324 | 258 | 324 | 25 | 314 | 0 | 314 | 628 | 1.9382716049382716 | 2.0308641975308643 | 10 | 0 |
| COPD_legacy_broad | 0.0 | curb65_ett_as1 | 324 | 324 | 258 | 324 | 25 | 312 | 12 | 324 | 970 | 2.993827160493827 | 3.1141975308641974 | 0 | 0 |
| COPD_legacy_broad | 0.0 | bisap4_ett_as1 | 324 | 324 | 258 | 324 | 25 | 293 | 31 | 324 | 801 | 2.4722222222222223 | 2.6203703703703702 | 0 | 0 |
| COPD_legacy_broad | 1.0 | qsofa | 6253 | 6253 | 4908 | 6253 | 883 | 5703 | 428 | 6131 | 12496 | 1.998400767631537 | 2.1255397409243564 | 122 | 0 |
| COPD_legacy_broad | 1.0 | qsofa_gcs15 | 6253 | 6253 | 4908 | 6253 | 883 | 5703 | 428 | 6131 | 13476 | 2.1551255397409244 | 2.282264513033744 | 122 | 0 |
| COPD_legacy_broad | 1.0 | curb65 | 6253 | 6253 | 4908 | 6253 | 883 | 5681 | 572 | 6253 | 19776 | 3.162641931872701 | 3.3011354549816088 | 0 | 0 |
| COPD_legacy_broad | 1.0 | bisap4 | 6253 | 6253 | 4908 | 6253 | 883 | 5253 | 1000 | 6253 | 16864 | 2.6969454661762353 | 2.8898128898128896 | 0 | 0 |
| COPD_legacy_broad | 1.0 | qsofa_ett_as1 | 6253 | 6253 | 4908 | 6253 | 883 | 6102 | 29 | 6131 | 13332 | 2.132096593635055 | 2.195266272189349 | 122 | 0 |
| COPD_legacy_broad | 1.0 | qsofa_gcs15_ett_as1 | 6253 | 6253 | 4908 | 6253 | 883 | 6102 | 29 | 6131 | 14175 | 2.2669118822964975 | 2.3300815608507914 | 122 | 0 |
| COPD_legacy_broad | 1.0 | curb65_ett_as1 | 6253 | 6253 | 4908 | 6253 | 883 | 6079 | 174 | 6253 | 20475 | 3.274428274428274 | 3.3489525027986566 | 0 | 0 |
| COPD_legacy_broad | 1.0 | bisap4_ett_as1 | 6253 | 6253 | 4908 | 6253 | 883 | 5624 | 629 | 6253 | 17563 | 2.808731808731809 | 2.9376299376299375 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa | 432 | 432 | 395 | 432 | 42 | 400 | 25 | 425 | 754 | 1.7453703703703705 | 1.8518518518518519 | 7 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa_gcs15 | 432 | 432 | 395 | 432 | 42 | 400 | 25 | 425 | 825 | 1.9097222222222223 | 2.0162037037037037 | 7 | 0 |
| pancreatitis_legacy_broad | 0.0 | curb65 | 432 | 432 | 395 | 432 | 42 | 398 | 34 | 432 | 1095 | 2.5347222222222223 | 2.6574074074074074 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | bisap4 | 432 | 432 | 395 | 432 | 42 | 382 | 50 | 432 | 981 | 2.2708333333333335 | 2.4166666666666665 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa_ett_as1 | 432 | 432 | 395 | 432 | 42 | 424 | 1 | 425 | 793 | 1.8356481481481481 | 1.8865740740740742 | 7 | 0 |
| pancreatitis_legacy_broad | 0.0 | qsofa_gcs15_ett_as1 | 432 | 432 | 395 | 432 | 42 | 424 | 1 | 425 | 858 | 1.9861111111111112 | 2.037037037037037 | 7 | 0 |
| pancreatitis_legacy_broad | 0.0 | curb65_ett_as1 | 432 | 432 | 395 | 432 | 42 | 422 | 10 | 432 | 1128 | 2.611111111111111 | 2.678240740740741 | 0 | 0 |
| pancreatitis_legacy_broad | 0.0 | bisap4_ett_as1 | 432 | 432 | 395 | 432 | 42 | 406 | 26 | 432 | 1014 | 2.3472222222222223 | 2.4375 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa | 1022 | 1022 | 916 | 1022 | 142 | 919 | 80 | 999 | 1893 | 1.8522504892367906 | 2.0 | 23 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa_gcs15 | 1022 | 1022 | 916 | 1022 | 142 | 919 | 80 | 999 | 2060 | 2.015655577299413 | 2.163405088062622 | 23 | 0 |
| pancreatitis_legacy_broad | 1.0 | curb65 | 1022 | 1022 | 916 | 1022 | 142 | 912 | 110 | 1022 | 2763 | 2.703522504892368 | 2.8649706457925634 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | bisap4 | 1022 | 1022 | 916 | 1022 | 142 | 848 | 174 | 1022 | 2385 | 2.3336594911937376 | 2.535225048923679 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa_ett_as1 | 1022 | 1022 | 916 | 1022 | 142 | 991 | 8 | 999 | 2027 | 1.9833659491193738 | 2.0587084148727985 | 23 | 0 |
| pancreatitis_legacy_broad | 1.0 | qsofa_gcs15_ett_as1 | 1022 | 1022 | 916 | 1022 | 142 | 991 | 8 | 999 | 2178 | 2.131115459882583 | 2.2064579256360077 | 23 | 0 |
| pancreatitis_legacy_broad | 1.0 | curb65_ett_as1 | 1022 | 1022 | 916 | 1022 | 142 | 984 | 38 | 1022 | 2881 | 2.818982387475538 | 2.908023483365949 | 0 | 0 |
| pancreatitis_legacy_broad | 1.0 | bisap4_ett_as1 | 1022 | 1022 | 916 | 1022 | 142 | 921 | 101 | 1022 | 2503 | 2.449119373776908 | 2.5782778864970646 | 0 | 0 |

## Supplementary Table 16. Full score-level observed mortality risks and δ_s in the four primary analysis groups

| Database | Condition | Instrument | Score level | Total supported records | Never-primary records / patients | Never-primary deaths / risk (95% CI; status) | Primary records / patients | Primary deaths / risk (95% CI; status) | δ_s (percentage points; 95% CI; status) | Pooled observed record weight | CI method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | qSOFA | 0 | 65 | 24 / 24 | 2/24; 8.33% [2.09, 27.88]; computed | 41 / 41 | 1/41; 2.44% [0.34, 15.39]; computed | 5.89 [-6.13, 17.92]; computed | 0.003921 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | sepsis | qSOFA | 1 | 1,892 | 741 / 736 | 43/741; 5.80% [4.33, 7.73]; computed | 1,151 / 1,140 | 80/1,151; 6.95% [5.62, 8.57]; computed | -1.15 [-3.38, 1.09]; computed | 0.114141 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | sepsis | qSOFA | 2 | 8,036 | 2,885 / 2,817 | 320/2,885; 11.09% [9.99, 12.29]; computed | 5,151 / 4,970 | 618/5,151; 12.00% [11.14, 12.91]; computed | -0.91 [-2.36, 0.55]; computed | 0.484797 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | sepsis | qSOFA | 3 | 6,583 | 2,459 / 2,390 | 737/2,459; 29.97% [28.19, 31.82]; computed | 4,124 / 3,948 | 1,166/4,124; 28.27% [26.91, 29.68]; computed | 1.70 [-0.58, 3.98]; computed | 0.397140 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | pneumonia | CURB-65 | 0 | 55 | 38 / 38 | 2/38; 5.26% [1.32, 18.75]; computed | 17 / 17 | 0/17; 0.00% not computed; too few distinct patients | 5.26 not computed; too few distinct patients in a definition | 0.004791 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | pneumonia | CURB-65 | 1 | 532 | 378 / 374 | 19/378; 5.03% [3.23, 7.75]; computed | 154 / 151 | 5/154; 3.25% [1.36, 7.57]; computed | 1.78 [-1.78, 5.34]; computed | 0.046337 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | pneumonia | CURB-65 | 2 | 1,838 | 1,373 / 1,341 | 92/1,373; 6.70% [5.49, 8.15]; computed | 465 / 457 | 31/465; 6.67% [4.73, 9.31]; computed | 0.03 [-2.58, 2.65]; computed | 0.160091 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | pneumonia | CURB-65 | 3 | 3,393 | 2,541 / 2,472 | 330/2,541; 12.99% [11.74, 14.35]; computed | 852 / 845 | 81/852; 9.51% [7.71, 11.67]; computed | 3.48 [1.12, 5.84]; computed | 0.295532 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | pneumonia | CURB-65 | 4 | 3,753 | 2,984 / 2,916 | 626/2,984; 20.98% [19.55, 22.48]; computed | 769 / 758 | 129/769; 16.78% [14.29, 19.59]; computed | 4.20 [1.19, 7.22]; computed | 0.326888 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| eICU-CRD | pneumonia | CURB-65 | 5 | 1,910 | 1,522 / 1,494 | 473/1,522; 31.08% [28.79, 33.46]; computed | 388 / 381 | 93/388; 23.97% [19.98, 28.47]; computed | 7.11 [2.27, 11.95]; computed | 0.166362 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | sepsis | qSOFA | 0 | 85 | 37 / 37 | 9/37; 24.32% [13.17, 40.52]; computed | 48 / 47 | 2/48; 4.17% [1.08, 14.81]; computed | 20.16 [4.96, 35.36]; computed | 0.007867 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | sepsis | qSOFA | 1 | 1,429 | 601 / 595 | 154/601; 25.62% [22.28, 29.28]; computed | 828 / 808 | 69/828; 8.33% [6.64, 10.41]; computed | 17.29 [13.32, 21.26]; computed | 0.132266 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | sepsis | qSOFA | 2 | 6,525 | 2,513 / 2,393 | 706/2,513; 28.09% [26.36, 29.90]; computed | 4,012 / 3,666 | 659/4,012; 16.43% [15.30, 17.61]; computed | 11.67 [9.57, 13.77]; computed | 0.603943 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | sepsis | qSOFA | 3 | 2,765 | 974 / 955 | 402/974; 41.27% [38.21, 44.41]; computed | 1,791 / 1,698 | 613/1,791; 34.23% [32.03, 36.49]; computed | 7.05 [3.25, 10.84]; computed | 0.255924 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | pneumonia | CURB-65 | 0 | 123 | 110 / 110 | 5/110; 4.55% [1.90, 10.46]; computed | 13 / 13 | 0/13; 0.00% not computed; too few distinct patients | 4.55 not computed; too few distinct patients in a definition | 0.009838 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | pneumonia | CURB-65 | 1 | 866 | 738 / 720 | 70/738; 9.49% [7.58, 11.81]; computed | 128 / 120 | 8/128; 6.25% [3.14, 12.07]; computed | 3.24 [-1.49, 7.96]; computed | 0.069269 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | pneumonia | CURB-65 | 2 | 2,404 | 2,103 / 2,021 | 256/2,103; 12.17% [10.84, 13.64]; computed | 301 / 287 | 14/301; 4.65% [2.77, 7.70]; computed | 7.52 [4.76, 10.28]; computed | 0.192289 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | pneumonia | CURB-65 | 3 | 3,716 | 3,244 / 3,081 | 603/3,244; 18.59% [17.28, 19.97]; computed | 472 / 453 | 34/472; 7.20% [5.19, 9.92]; computed | 11.38 [8.70, 14.07]; computed | 0.297232 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | pneumonia | CURB-65 | 4 | 3,769 | 3,256 / 3,122 | 816/3,256; 25.06% [23.60, 26.59]; computed | 513 / 497 | 77/513; 15.01% [12.17, 18.37]; computed | 10.05 [6.62, 13.48]; computed | 0.301472 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |
| MIMIC-IV | pneumonia | CURB-65 | 5 | 1,624 | 1,411 / 1,367 | 509/1,411; 36.07% [33.60, 38.62]; computed | 213 / 209 | 60/213; 28.17% [22.53, 34.59]; computed | 7.90 [1.38, 14.43]; computed | 0.129899 | Patient-cluster sandwich; logit-Wald risk CIs / Wald δ_s CI |

Complete row-level data are also supplied in S16.csv.

## Supplementary Table 17. Full database-condition cohort eligibility, complete-score support, and Δ_w summaries

| Database | Condition / instrument | Primary or sequence-one (unqualified Zigong) eligible-complete-shared; outside support | Never-primary or other-sequence (unqualified Zigong) eligible-complete-shared; outside support | Common-support score levels | Computed δ_s CIs excluding zero / computed δ_s CIs | Δ_w weighted summary (percentage points) | 95% patient-cluster CI for Δ_w weighted summary | Summary interval status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis / qSOFA | 16,101 → 10,467 (5,634 excluded) → 10,467 (0 outside support) | 8,563 → 6,109 (2,454 excluded) → 6,109 (0 outside support) | 4 | 0 / 4 | 0.13 | [-1.05, 1.30] | computed |
| eICU-CRD | pneumonia / CURB-65 | 4,955 → 2,645 (2,310 excluded) → 2,645 (0 outside support) | 14,313 → 8,836 (5,477 excluded) → 8,836 (0 outside support) | 6 | 3 / 5 | 3.70 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| eICU-CRD | pancreatitis / BISAP-4 | 255 → 153 (102 excluded) → 153 (0 outside support) | 346 → 198 (148 excluded) → 198 (0 outside support) | 4 | 0 / 2 | 0.78 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| eICU-CRD | heart failure / qSOFA | 4,507 → 2,548 (1,959 excluded) → 2,548 (0 outside support) | 11,055 → 6,992 (4,063 excluded) → 6,992 (0 outside support) | 4 | 2 / 3 | 3.38 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| eICU-CRD | COPD / qSOFA | 2,617 → 1,541 (1,076 excluded) → 1,541 (0 outside support) | 10,026 → 6,162 (3,864 excluded) → 6,162 (0 outside support) | 4 | 3 / 3 | 4.41 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| MIMIC-IV | sepsis / qSOFA | 8,756 → 6,679 (2,077 excluded) → 6,679 (0 outside support) | 5,366 → 4,125 (1,241 excluded) → 4,125 (0 outside support) | 4 | 4 / 4 | 11.30 | [9.61, 12.98] | computed |
| MIMIC-IV | pneumonia / CURB-65 | 1,936 → 1,640 (296 excluded) → 1,640 (0 outside support) | 15,087 → 10,862 (4,225 excluded) → 10,862 (0 outside support) | 6 | 4 / 5 | 9.16 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| MIMIC-IV | pancreatitis / BISAP-4 | 476 → 389 (87 excluded) → 389 (0 outside support) | 922 → 678 (244 excluded) → 678 (0 outside support) | 5 | 3 / 4 | 6.43 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| MIMIC-IV | heart failure / qSOFA | 2,941 → 2,760 (181 excluded) → 2,760 (0 outside support) | 19,721 → 16,514 (3,207 excluded) → 16,514 (0 outside support) | 4 | 1 / 4 | -0.02 | [-1.37, 1.32] | computed |
| MIMIC-IV | COPD / qSOFA | 489 → 440 (49 excluded) → 440 (0 outside support) | 11,410 → 9,619 (1,791 excluded) → 9,619 (0 outside support) | 4 | 3 / 3 | 6.78 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| MIMIC-III | sepsis / qSOFA | 3,398 → 2,958 (440 excluded) → 2,958 (0 outside support) | 2,914 → 2,630 (284 excluded) → 2,630 (0 outside support) | 4 | 2 / 3 | 8.61 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| MIMIC-III | pneumonia / CURB-65 | 1,756 → 1,603 (153 excluded) → 1,603 (0 outside support) | 8,544 → 7,545 (999 excluded) → 7,545 (0 outside support) | 6 | 4 / 5 | 5.92 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| MIMIC-III | pancreatitis / BISAP-4 | 366 → 320 (46 excluded) → 320 (0 outside support) | 587 → 495 (92 excluded) → 495 (0 outside support) | 5 | 1 / 4 | 4.41 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| MIMIC-III | heart failure / qSOFA | 1,543 → 1,467 (76 excluded) → 1,467 (0 outside support) | 11,904 → 10,952 (952 excluded) → 10,952 (0 outside support) | 4 | 0 / 3 | 1.24 | not computed | not computed (degenerate_outcome_cell) |
| MIMIC-III | COPD / qSOFA | 309 → 294 (15 excluded) → 294 (0 outside support) | 5,988 → 5,463 (525 excluded) → 5,463 (0 outside support) | 4 | 1 / 3 | 2.73 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| Zigong | sepsis / qSOFA | 167 → 48 (119 excluded) → 48 (0 outside support) | 374 → 89 (285 excluded) → 89 (0 outside support) | 4 | 0 / 1 | 4.80 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| Zigong | pneumonia / CURB-65 | 235 → 42 (193 excluded) → 42 (0 outside support) | 1,463 → 388 (1,075 excluded) → 388 (0 outside support) | 6 | 0 / 1 | 6.33 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| Zigong | pancreatitis / BISAP-4 | 63 → 14 (49 excluded) → 14 (0 outside support) | 47 → 14 (33 excluded) → 14 (0 outside support) | 4 | 0 / 0 | -5.36 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| Zigong | COPD / qSOFA | 68 → 18 (50 excluded) → 18 (0 outside support) | 523 → 145 (378 excluded) → 128 (17 outside support) | 3 | 0 / 0 | 5.46 | not computed | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |

Complete row-level data are also supplied in S17.csv.

## Supplementary Table 18. Separate score-level missingness identification bounds

| Database | Disease | Score level | Estimand | Fixed primary n | Optional primary n | Primary risk lower | Primary risk upper | Fixed never-primary n | Optional never-primary n | Never-primary risk lower | Never-primary risk upper | δ_s lower bound | δ_s upper bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | 0 | delta_s missingness identification bounds | 41 | 422 | 0.0024096385542168677 | 0.550561797752809 | 24 | 236 | 0.00909090909090909 | 0.65625 | -0.5414708886619 | 0.6538403614457832 |
| eICU-CRD | sepsis | 1 | delta_s missingness identification bounds | 1151 | 1947 | 0.028139289482940557 | 0.23826458036984352 | 741 | 925 | 0.028401585204755615 | 0.21836506159014557 | -0.2098629951650879 | 0.190225772107205 |
| eICU-CRD | sepsis | 2 | delta_s missingness identification bounds | 5151 | 5323 | 0.06530698509986262 | 0.2643622200584226 | 2885 | 2303 | 0.0692940666955392 | 0.2575976845151954 | -0.19506815336288338 | 0.19229069941533278 |
| eICU-CRD | sepsis | 3 | delta_s missingness identification bounds | 4124 | 4062 | 0.15972602739726027 | 0.4095808383233533 | 2459 | 1709 | 0.20065341682548327 | 0.41706161137440756 | -0.20892742149787003 | 0.2573355839771473 |
| eICU-CRD | pneumonia | 0 | delta_s missingness identification bounds | 17 | 73 | 0.0 | 0.10526315789473684 | 38 | 186 | 0.009523809523809525 | 0.3076923076923077 | -0.09573934837092732 | 0.3076923076923077 |
| eICU-CRD | pneumonia | 1 | delta_s missingness identification bounds | 154 | 387 | 0.009652509652509652 | 0.15819209039548024 | 378 | 954 | 0.01557377049180328 | 0.2673469387755102 | -0.14261831990367696 | 0.25769442912300056 |
| eICU-CRD | pneumonia | 2 | delta_s missingness identification bounds | 465 | 1038 | 0.02198581560283688 | 0.2222222222222222 | 1373 | 2442 | 0.02633085289066972 | 0.24380165289256198 | -0.1958913693315525 | 0.2218158372897251 |
| eICU-CRD | pneumonia | 3 | delta_s missingness identification bounds | 852 | 1621 | 0.03633916554508748 | 0.2965328467153285 | 2541 | 3748 | 0.058981233243967826 | 0.31653786707882536 | -0.23755161347136067 | 0.2801987015337379 |
| eICU-CRD | pneumonia | 4 | delta_s missingness identification bounds | 769 | 1415 | 0.06782334384858044 | 0.3910561370123692 | 2984 | 3396 | 0.11361161524500907 | 0.38816813700051894 | -0.2774445217673601 | 0.32034479315193853 |
| eICU-CRD | pneumonia | 5 | delta_s missingness identification bounds | 388 | 595 | 0.11045130641330166 | 0.44234404536862004 | 1522 | 1383 | 0.19306122448979593 | 0.46939807789580174 | -0.2492828208788241 | 0.3589467714825001 |
| eICU-CRD | pancreatitis | 0 | delta_s missingness identification bounds | 0 | 16 | 0.0 | 0.0 | 0 | 12 | 0.0 | 0.0 | 0.0 | 0.0 |
| eICU-CRD | pancreatitis | 1 | delta_s missingness identification bounds | 50 | 62 | 0.0 | 0.0196078431372549 | 44 | 77 | 0.0 | 0.08333333333333333 | -0.0196078431372549 | 0.08333333333333333 |
| eICU-CRD | pancreatitis | 2 | delta_s missingness identification bounds | 63 | 83 | 0.020833333333333332 | 0.07692307692307693 | 69 | 115 | 0.023255813953488372 | 0.19753086419753085 | -0.053667262969588556 | 0.1766975308641975 |
| eICU-CRD | pancreatitis | 3 | delta_s missingness identification bounds | 25 | 50 | 0.0410958904109589 | 0.18518518518518517 | 62 | 76 | 0.0873015873015873 | 0.3108108108108108 | -0.09788359788359788 | 0.2697149203998519 |
| eICU-CRD | pancreatitis | 4 | delta_s missingness identification bounds | 15 | 15 | 0.20689655172413793 | 0.4375 | 23 | 32 | 0.14583333333333334 | 0.4666666666666667 | -0.29166666666666663 | 0.2597701149425288 |
| eICU-CRD | heart failure | 0 | delta_s missingness identification bounds | 18 | 288 | 0.0 | 0.4 | 57 | 506 | 0.0019305019305019305 | 0.45098039215686275 | -0.3980694980694981 | 0.45098039215686275 |
| eICU-CRD | heart failure | 1 | delta_s missingness identification bounds | 698 | 991 | 0.010559006211180125 | 0.12355212355212356 | 1398 | 1846 | 0.023973727422003283 | 0.17031934877896054 | -0.09957839613012028 | 0.15976034256778043 |
| eICU-CRD | heart failure | 2 | delta_s missingness identification bounds | 1360 | 1768 | 0.041666666666666664 | 0.2064102564102564 | 3581 | 3689 | 0.057117224880382775 | 0.23156377612298823 | -0.1492930315298736 | 0.18989710945632157 |
| eICU-CRD | heart failure | 3 | delta_s missingness identification bounds | 472 | 1093 | 0.06002824858757062 | 0.37681159420289856 | 1956 | 2452 | 0.12582445459157787 | 0.39719240297274977 | -0.2509871396113207 | 0.33716415438517916 |
| eICU-CRD | COPD | 0 | delta_s missingness identification bounds | 6 | 156 | 0.0 | 0.45454545454545453 | 48 | 537 | 0.0 | 0.43529411764705883 | -0.45454545454545453 | 0.43529411764705883 |
| eICU-CRD | COPD | 1 | delta_s missingness identification bounds | 440 | 560 | 0.010224948875255624 | 0.06926406926406926 | 1277 | 1864 | 0.01840080294412847 | 0.14485654303708886 | -0.05086326631994079 | 0.13463159416183323 |
| eICU-CRD | COPD | 2 | delta_s missingness identification bounds | 720 | 981 | 0.022126613398893668 | 0.1385390428211587 | 3024 | 3547 | 0.0418498615860609 | 0.1988998262883613 | -0.09668918123509779 | 0.17677321288946765 |
| eICU-CRD | COPD | 3 | delta_s missingness identification bounds | 375 | 573 | 0.04826038159371493 | 0.23148148148148148 | 1813 | 2274 | 0.09401709401709402 | 0.32235621521335805 | -0.13746438746438747 | 0.2740958336196431 |
| MIMIC-IV | sepsis | 0 | delta_s missingness identification bounds | 48 | 59 | 0.028169014084507043 | 0.4523809523809524 | 37 | 44 | 0.14754098360655737 | 0.5087719298245614 | -0.304839968774395 | 0.48060291574005437 |
| MIMIC-IV | sepsis | 1 | delta_s missingness identification bounds | 828 | 362 | 0.06546489563567362 | 0.21265560165975103 | 601 | 301 | 0.1949367088607595 | 0.37307152875175315 | -0.017718892798991526 | 0.3076066331160795 |
| MIMIC-IV | sepsis | 2 | delta_s missingness identification bounds | 4012 | 2053 | 0.12593158799923562 | 0.3078034682080925 | 2513 | 1224 | 0.2196639701306783 | 0.4048089591567852 | -0.08813949807741422 | 0.2788773711575496 |
| MIMIC-IV | sepsis | 3 | delta_s missingness identification bounds | 1791 | 1777 | 0.21745299751684993 | 0.5362204724409448 | 974 | 982 | 0.26499670402109426 | 0.5951875442321303 | -0.2712237684198506 | 0.37773454671528034 |
| MIMIC-IV | pneumonia | 0 | delta_s missingness identification bounds | 13 | 6 | 0.0 | 0.0 | 110 | 106 | 0.025252525252525252 | 0.1796875 | 0.025252525252525252 | 0.1796875 |
| MIMIC-IV | pneumonia | 1 | delta_s missingness identification bounds | 128 | 50 | 0.04597701149425287 | 0.09090909090909091 | 738 | 804 | 0.04943502824858757 | 0.22685185185185186 | -0.04147406266050334 | 0.180874840357599 |
| MIMIC-IV | pneumonia | 2 | delta_s missingness identification bounds | 301 | 129 | 0.03389830508474576 | 0.09748427672955975 | 2103 | 1928 | 0.0706401766004415 | 0.26414342629482074 | -0.026844100129118253 | 0.23024512121007498 |
| MIMIC-IV | pneumonia | 3 | delta_s missingness identification bounds | 472 | 209 | 0.053712480252764615 | 0.1576923076923077 | 3244 | 2866 | 0.11587240584166027 | 0.3636144578313253 | -0.04181990185064742 | 0.3099019775785607 |
| MIMIC-IV | pneumonia | 4 | delta_s missingness identification bounds | 513 | 174 | 0.12300319488817892 | 0.24041811846689895 | 3256 | 2328 | 0.17537072856221791 | 0.4172438500119417 | -0.06504738990468104 | 0.2942406551237628 |
| MIMIC-IV | pneumonia | 5 | delta_s missingness identification bounds | 213 | 50 | 0.25316455696202533 | 0.3598326359832636 | 1411 | 674 | 0.28773318258903335 | 0.47770700636942676 | -0.07209945339423024 | 0.22454244940740142 |
| MIMIC-IV | pancreatitis | 0 | delta_s missingness identification bounds | 1 | 8 | 0.0 | 0.0 | 7 | 17 | 0.0 | 0.2222222222222222 | 0.0 | 0.2222222222222222 |
| MIMIC-IV | pancreatitis | 1 | delta_s missingness identification bounds | 136 | 38 | 0.011627906976744186 | 0.028985507246376812 | 138 | 98 | 0.04 | 0.1342281879194631 | 0.011014492753623189 | 0.12260028094271891 |
| MIMIC-IV | pancreatitis | 2 | delta_s missingness identification bounds | 135 | 63 | 0.031413612565445025 | 0.09154929577464789 | 220 | 176 | 0.06318681318681318 | 0.21825396825396826 | -0.028362482587834706 | 0.18684035568852322 |
| MIMIC-IV | pancreatitis | 3 | delta_s missingness identification bounds | 71 | 52 | 0.0625 | 0.21951219512195122 | 191 | 156 | 0.1513157894736842 | 0.3803418803418803 | -0.06819640564826701 | 0.3178418803418803 |
| MIMIC-IV | pancreatitis | 4 | delta_s missingness identification bounds | 46 | 17 | 0.2631578947368421 | 0.40384615384615385 | 122 | 59 | 0.23125 | 0.40559440559440557 | -0.17259615384615384 | 0.14243651085756348 |
| MIMIC-IV | heart failure | 0 | delta_s missingness identification bounds | 49 | 9 | 0.018518518518518517 | 0.09433962264150944 | 319 | 150 | 0.019559902200488997 | 0.17941952506596306 | -0.07477972044102044 | 0.16090100654744455 |
| MIMIC-IV | heart failure | 1 | delta_s missingness identification bounds | 714 | 55 | 0.03430079155672823 | 0.05103448275862069 | 3506 | 932 | 0.04580520732883317 | 0.12644889357218125 | -0.0052292754297875235 | 0.09214810201545302 |
| MIMIC-IV | heart failure | 2 | delta_s missingness identification bounds | 1692 | 178 | 0.10497539639147074 | 0.13444893248701673 | 9925 | 3117 | 0.09044892540038171 | 0.19063759618908024 | -0.04400000708663501 | 0.0856621997976095 |
| MIMIC-IV | heart failure | 3 | delta_s missingness identification bounds | 305 | 135 | 0.20246913580246914 | 0.34411764705882353 | 2764 | 2365 | 0.16279604506783169 | 0.4198645598194131 | -0.18132160199099184 | 0.21739542401694398 |
| MIMIC-IV | COPD | 0 | delta_s missingness identification bounds | 9 | 1 | 0.0 | 0.0 | 211 | 83 | 0.02973977695167286 | 0.13983050847457626 | 0.02973977695167286 | 0.13983050847457626 |
| MIMIC-IV | COPD | 1 | delta_s missingness identification bounds | 166 | 15 | 0.01694915254237288 | 0.041176470588235294 | 2206 | 492 | 0.050972762645914396 | 0.11096829477292203 | 0.009796292057679103 | 0.09401914223054915 |
| MIMIC-IV | COPD | 2 | delta_s missingness identification bounds | 219 | 48 | 0.04296875 | 0.09565217391304348 | 5691 | 1742 | 0.08687454677302393 | 0.18253331192807834 | -0.008777627140019548 | 0.13956456192807834 |
| MIMIC-IV | COPD | 3 | delta_s missingness identification bounds | 46 | 34 | 0.0547945205479452 | 0.20754716981132076 | 1511 | 1353 | 0.15486542443064183 | 0.41989795918367345 | -0.052681745380678935 | 0.36510343863572825 |
| MIMIC-III | sepsis | 0 | delta_s missingness identification bounds | 15 | 67 | 0.0 | 0.6938775510204082 | 25 | 60 | 0.10606060606060606 | 0.5909090909090909 | -0.5878169449598021 | 0.5909090909090909 |
| MIMIC-III | sepsis | 1 | delta_s missingness identification bounds | 293 | 111 | 0.08426966292134831 | 0.2287390029325513 | 306 | 105 | 0.20157068062827224 | 0.3164179104477612 | -0.02716832230427907 | 0.2321482475264129 |
| MIMIC-III | sepsis | 2 | delta_s missingness identification bounds | 1423 | 437 | 0.15535714285714286 | 0.27510917030567683 | 1235 | 281 | 0.2579957356076759 | 0.35119047619047616 | -0.017113434698000918 | 0.1958333333333333 |
| MIMIC-III | sepsis | 3 | delta_s missingness identification bounds | 1227 | 395 | 0.3328748280605227 | 0.46738351254480287 | 1064 | 236 | 0.38301415487094087 | 0.48065348237317285 | -0.084369357673862 | 0.14777865431265014 |
| MIMIC-III | pneumonia | 0 | delta_s missingness identification bounds | 5 | 11 | 0.0 | 0.0 | 37 | 57 | 0.011363636363636364 | 0.16279069767441862 | 0.011363636363636364 | 0.16279069767441862 |
| MIMIC-III | pneumonia | 1 | delta_s missingness identification bounds | 87 | 49 | 0.029850746268656716 | 0.06741573033707865 | 389 | 239 | 0.041736227045075125 | 0.1291866028708134 | -0.025679503292003525 | 0.09933585660215669 |
| MIMIC-III | pneumonia | 2 | delta_s missingness identification bounds | 267 | 88 | 0.03188405797101449 | 0.07581227436823104 | 1386 | 519 | 0.08507135016465422 | 0.16201497617426822 | 0.009259075796423183 | 0.13013091820325373 |
| MIMIC-III | pneumonia | 3 | delta_s missingness identification bounds | 439 | 116 | 0.09345794392523364 | 0.15250544662309368 | 2269 | 739 | 0.14300960512273211 | 0.24290348742903486 | -0.009495841500361563 | 0.14944554350380124 |
| MIMIC-III | pneumonia | 4 | delta_s missingness identification bounds | 564 | 101 | 0.18252730109204368 | 0.23979591836734693 | 2496 | 583 | 0.22365217391304348 | 0.3137037037037037 | -0.016143744454303444 | 0.13117640261166003 |
| MIMIC-III | pneumonia | 5 | delta_s missingness identification bounds | 241 | 39 | 0.26591760299625467 | 0.33070866141732286 | 968 | 186 | 0.33086190917516217 | 0.41418983700862894 | 0.00015324775783931432 | 0.14827223401237427 |
| MIMIC-III | pancreatitis | 0 | delta_s missingness identification bounds | 1 | 5 | 0.0 | 0.0 | 3 | 15 | 0.0 | 0.25 | 0.0 | 0.25 |
| MIMIC-III | pancreatitis | 1 | delta_s missingness identification bounds | 65 | 21 | 0.023529411764705882 | 0.045454545454545456 | 51 | 44 | 0.05319148936170213 | 0.11538461538461539 | 0.007736943907156672 | 0.09185520361990951 |
| MIMIC-III | pancreatitis | 2 | delta_s missingness identification bounds | 116 | 33 | 0.027210884353741496 | 0.05084745762711865 | 168 | 68 | 0.07111111111111111 | 0.15083798882681565 | 0.020263653483992464 | 0.12362710447307415 |
| MIMIC-III | pancreatitis | 3 | delta_s missingness identification bounds | 89 | 31 | 0.09649122807017543 | 0.17894736842105263 | 169 | 58 | 0.14832535885167464 | 0.2620320855614973 | -0.030622009569377995 | 0.16554085749132189 |
| MIMIC-III | pancreatitis | 4 | delta_s missingness identification bounds | 49 | 13 | 0.2982456140350877 | 0.4074074074074074 | 104 | 19 | 0.28448275862068967 | 0.36036036036036034 | -0.12292464878671772 | 0.06211474632527264 |
| MIMIC-III | heart failure | 0 | delta_s missingness identification bounds | 20 | 34 | 0.0 | 0.09090909090909091 | 210 | 281 | 0.015730337078651686 | 0.20703125 | -0.07517875383043923 | 0.20703125 |
| MIMIC-III | heart failure | 1 | delta_s missingness identification bounds | 328 | 44 | 0.04087193460490463 | 0.06006006006006006 | 2041 | 447 | 0.05340008343763037 | 0.10272045028142589 | -0.006659976622429689 | 0.061848515676521255 |
| MIMIC-III | heart failure | 2 | delta_s missingness identification bounds | 803 | 76 | 0.10829493087557604 | 0.128992628992629 | 5325 | 928 | 0.11057692307692307 | 0.16011539848539488 | -0.018415705915705932 | 0.05182046760981884 |
| MIMIC-III | heart failure | 3 | delta_s missingness identification bounds | 316 | 66 | 0.17647058823529413 | 0.22839506172839505 | 3376 | 764 | 0.19081272084805653 | 0.26280247608328644 | -0.037582340880338516 | 0.08633188784799231 |
| MIMIC-III | COPD | 0 | delta_s missingness identification bounds | 8 | 9 | 0.0 | 0.0 | 111 | 133 | 0.00904977375565611 | 0.1865671641791045 | 0.00904977375565611 | 0.1865671641791045 |
| MIMIC-III | COPD | 1 | delta_s missingness identification bounds | 91 | 9 | 0.02 | 0.02197802197802198 | 1031 | 230 | 0.04797353184449959 | 0.10156971375807941 | 0.02599550986647761 | 0.0815697137580794 |
| MIMIC-III | COPD | 2 | delta_s missingness identification bounds | 145 | 15 | 0.07547169811320754 | 0.08904109589041095 | 2697 | 510 | 0.10013003901170352 | 0.15523338048090524 | 0.011088943121292563 | 0.07976168236769769 |
| MIMIC-III | COPD | 3 | delta_s missingness identification bounds | 50 | 15 | 0.15625 | 0.21568627450980393 | 1624 | 414 | 0.1813953488372093 | 0.26288361320208453 | -0.03429092567259462 | 0.10663361320208453 |
| Zigong | sepsis | 0 | delta_s missingness identification bounds | 2 | 45 | 0.0 | 0.6 | 5 | 115 | 0.009009009009009009 | 0.7142857142857143 | -0.590990990990991 | 0.7142857142857143 |
| Zigong | sepsis | 1 | delta_s missingness identification bounds | 7 | 80 | 0.0 | 0.5 | 26 | 225 | 0.00423728813559322 | 0.3902439024390244 | -0.4957627118644068 | 0.3902439024390244 |
| Zigong | sepsis | 2 | delta_s missingness identification bounds | 24 | 104 | 0.008403361344537815 | 0.30303030303030304 | 42 | 254 | 0.01079136690647482 | 0.35 | -0.29223893612382823 | 0.34159663865546214 |
| Zigong | sepsis | 3 | delta_s missingness identification bounds | 15 | 69 | 0.0 | 0.25 | 16 | 144 | 0.006756756756756757 | 0.4642857142857143 | -0.24324324324324326 | 0.4642857142857143 |
| Zigong | pneumonia | 0 | delta_s missingness identification bounds | 1 | 7 | 0.0 | 0.0 | 3 | 135 | 0.0 | 0.6666666666666666 | 0.0 | 0.6666666666666666 |
| Zigong | pneumonia | 1 | delta_s missingness identification bounds | 3 | 32 | 0.0 | 0.25 | 39 | 473 | 0.006211180124223602 | 0.47058823529411764 | -0.24378881987577639 | 0.47058823529411764 |
| Zigong | pneumonia | 2 | delta_s missingness identification bounds | 6 | 115 | 0.0 | 0.5 | 100 | 771 | 0.007263922518159807 | 0.35172413793103446 | -0.4927360774818402 | 0.35172413793103446 |
| Zigong | pneumonia | 3 | delta_s missingness identification bounds | 6 | 170 | 0.0 | 0.5714285714285714 | 137 | 803 | 0.013468013468013467 | 0.3279569892473118 | -0.5579605579605579 | 0.3279569892473118 |
| Zigong | pneumonia | 4 | delta_s missingness identification bounds | 22 | 120 | 0.021897810218978103 | 0.2962962962962963 | 95 | 510 | 0.02631578947368421 | 0.38461538461538464 | -0.2699805068226121 | 0.3627175743964065 |
| Zigong | pneumonia | 5 | delta_s missingness identification bounds | 4 | 39 | 0.0 | 0.3333333333333333 | 14 | 144 | 0.013422818791946308 | 0.4782608695652174 | -0.319910514541387 | 0.4782608695652174 |
| Zigong | pancreatitis | 0 | delta_s missingness identification bounds | 0 | 5 | 0.0 | 0.0 | 0 | 4 | 0.0 | 0.0 | 0.0 | 0.0 |
| Zigong | pancreatitis | 1 | delta_s missingness identification bounds | 3 | 28 | 0.0 | 0.0 | 2 | 12 | 0.0 | 0.0 | 0.0 | 0.0 |
| Zigong | pancreatitis | 2 | delta_s missingness identification bounds | 4 | 45 | 0.0 | 0.3333333333333333 | 2 | 25 | 0.0 | 0.0 | -0.3333333333333333 | 0.0 |
| Zigong | pancreatitis | 3 | delta_s missingness identification bounds | 5 | 24 | 0.0 | 0.375 | 5 | 22 | 0.037037037037037035 | 0.2 | -0.33796296296296297 | 0.2 |
| Zigong | pancreatitis | 4 | delta_s missingness identification bounds | 2 | 6 | 0.16666666666666666 | 0.75 | 5 | 13 | 0.0 | 0.0 | -0.75 | -0.16666666666666666 |
| Zigong | heart failure | 0 | delta_s missingness identification bounds | 1 | 21 | 0.0 | 0.5 | 8 | 166 | 0.006097560975609756 | 0.6111111111111112 | -0.49390243902439024 | 0.6111111111111112 |
| Zigong | heart failure | 1 | delta_s missingness identification bounds | 4 | 38 | 0.024390243902439025 | 0.4 | 38 | 322 | 0.0029411764705882353 | 0.3620689655172414 | -0.3970588235294118 | 0.33767872161480234 |
| Zigong | heart failure | 2 | delta_s missingness identification bounds | 3 | 38 | 0.025 | 0.5 | 61 | 367 | 0.0225 | 0.4157303370786517 | -0.4775 | 0.3907303370786517 |
| Zigong | heart failure | 3 | delta_s missingness identification bounds | 2 | 21 | 0.0 | 0.3333333333333333 | 30 | 211 | 0.026905829596412557 | 0.5 | -0.30642750373692074 | 0.5 |
| Zigong | COPD | 0 | delta_s missingness identification bounds | 0 | 22 | 0.0 | 1.0 | 17 | 137 | 0.0 | 0.2916666666666667 | -1.0 | 0.2916666666666667 |
| Zigong | COPD | 1 | delta_s missingness identification bounds | 6 | 37 | 0.0 | 0.14285714285714285 | 42 | 312 | 0.0 | 0.2631578947368421 | -0.14285714285714285 | 0.2631578947368421 |
| Zigong | COPD | 2 | delta_s missingness identification bounds | 9 | 42 | 0.0 | 0.25 | 65 | 331 | 0.018518518518518517 | 0.30120481927710846 | -0.23148148148148148 | 0.30120481927710846 |
| Zigong | COPD | 3 | delta_s missingness identification bounds | 3 | 27 | 0.0 | 0.5 | 21 | 156 | 0.0 | 0.3225806451612903 | -0.5 | 0.3225806451612903 |

**Notes.**

- Missingness bounds are identification bounds from incomplete component scores, not confidence intervals. Perturbation ranges are not confidence intervals and hold observed good-level risks and record weights fixed.

## Supplementary Table 19. Perturbation ranges when score-level intervals are withheld

| Database | Disease | Score level | Estimand | Δ_w point (pp) | Record weight on levels without δ_s CI | Unsupported interval levels | Good-level contribution (pp) | Perturbation lower (pp) | Perturbation upper (pp) | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | weighted | Delta_w weighted summary perturbation range | 0.1273480523914114 | 0.0 | 0 | 0.1273480523914114 | 0.1273480523914114 | 0.1273480523914114 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| eICU-CRD | pneumonia | weighted | Delta_w weighted summary perturbation range | 3.698218842732749 | 0.00479052347356502 | 1 | 3.673005561292933 | 3.1939532139364313 | 4.152057908649435 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| eICU-CRD | pancreatitis | weighted | Delta_w weighted summary perturbation range | 0.77696891441632 | 0.37606837606837606 | 2 | 1.812519515184312 | -35.794318091653295 | 39.41935712202192 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| eICU-CRD | heart failure | weighted | Delta_w weighted summary perturbation range | 3.375244127321511 | 0.007861635220125786 | 1 | 3.361451784830062 | 2.575288262817484 | 4.14761530684264 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| eICU-CRD | COPD | weighted | Delta_w weighted summary perturbation range | 4.411725941225043 | 0.007010255744515124 | 1 | 4.411725941225043 | 3.710700366773531 | 5.112751515676556 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-IV | sepsis | weighted | Delta_w weighted summary perturbation range | 11.295813284083817 | 0.0 | 0 | 11.295813284083817 | 11.295813284083817 | 11.295813284083817 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-IV | pneumonia | weighted | Delta_w weighted summary perturbation range | 9.156230972275353 | 0.009838425851863702 | 1 | 9.111510854766882 | 8.12766826958051 | 10.095353439953252 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-IV | pancreatitis | weighted | Delta_w weighted summary perturbation range | 6.430432384191246 | 0.007497656982193065 | 1 | 6.430432384191246 | 5.680666685971938 | 7.180198082410552 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-IV | heart failure | weighted | Delta_w weighted summary perturbation range | -0.02417208811848169 | 0.0 | 0 | -0.02417208811848169 | -0.02417208811848169 | -0.02417208811848169 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-IV | COPD | weighted | Delta_w weighted summary perturbation range | 6.775298213248441 | 0.021870961328163834 | 1 | 6.692375137122703 | 4.505279004306319 | 8.879471269939087 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-III | sepsis | weighted | Delta_w weighted summary perturbation range | 8.609603850854947 | 0.0071581961345740875 | 1 | 8.409174359086874 | 7.693354745629464 | 9.124993972544283 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-III | pneumonia | weighted | Delta_w weighted summary perturbation range | 5.915587681122555 | 0.004591167468299082 | 1 | 5.903179120397422 | 5.444062373567514 | 6.362295867227331 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-III | pancreatitis | weighted | Delta_w weighted summary perturbation range | 4.412525332181596 | 0.0049079754601227 | 1 | 4.412525332181596 | 3.9217277861693254 | 4.903322878193865 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-III | heart failure | weighted | Delta_w weighted summary perturbation range | 1.238264590657891 | 0.01852000966261374 | 1 | 1.176531225115845 | -0.6754697411455287 | 3.028532191377219 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| MIMIC-III | COPD | weighted | Delta_w weighted summary perturbation range | 2.726591891001211 | 0.020670488101441724 | 1 | 2.689347768295911 | 0.6222989581517384 | 4.756396578440084 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| Zigong | sepsis | weighted | Delta_w weighted summary perturbation range | 4.7963623967273605 | 0.5182481751824818 | 3 | 1.4337851929092804 | -50.391032325338905 | 53.25860271115745 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| Zigong | pneumonia | weighted | Delta_w weighted summary perturbation range | 6.327182326380034 | 0.727906976744186 | 5 | 0.5858462223211306 | -72.20485145209747 | 73.37654389673973 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| Zigong | pancreatitis | weighted | Delta_w weighted summary perturbation range | -5.357142857142856 | 1.0 | 4 | 0.0 | -100.0 | 100.0 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| Zigong | heart failure | weighted | Delta_w weighted summary perturbation range | -9.360848452121715 | 1.0 | 4 | 0.0 | -100.0 | 100.0 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |
| Zigong | COPD | weighted | Delta_w weighted summary perturbation range | 5.458377239199157 | 1.0 | 3 | 0.0 | -100.0 | 100.0 | not a confidence interval; observed good-level risks and record weights held fixed; other risk differences range from -1 to 1 |

**Notes.**

- Missingness bounds are identification bounds from incomplete component scores, not confidence intervals. Perturbation ranges are not confidence intervals and hold observed good-level risks and record weights fixed.

## Supplementary Table 20. Weighted-summary interval refusals by reporting policy

| source_key | database | disease | score_variant | primary_C_state | primary_C_interval_status | primary_C_refusal_reasons | primary_C_estimable | primary_C_point_pp_reported | primary_C_normal_if_ci_lower_pp | primary_C_normal_if_ci_upper_pp | primary_C_old60_percentile_ci_lower_pp | primary_C_old60_percentile_ci_upper_pp | primary_C_old60_usable_draws | primary_C_old60_requested_draws | audit_point_pp_unrounded | audit_numerical_se_pp | skipped_under_primary_C | skip_reason | diagnostic_run_status | peer_y_died_aliases_validated_equal | peer_standard_score_equals_curb65 | primary_C_normal_if_ci_width_pp | primary_C_old60_percentile_ci_width_pp | score_column |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eicu | eICU-CRD | pneumonia | curb65 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 3.69821884273 |  |  |  |  | 0 | 60 | 3.69821884273 | 0.78 | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| eicu | eICU-CRD | pancreatitis | bisap4 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 0.776968914416 |  |  |  |  | 0 | 60 | 0.776968914416 | 3 | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| eicu | eICU-CRD | heart failure | qsofa | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 3.37524412732 |  |  |  |  | 0 | 60 | 3.37524412732 | 0.73 | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| eicu | eICU-CRD | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 4.41172594123 |  |  |  |  | 0 | 60 | 4.41172594123 | 0.74 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iv | MIMIC-IV | pneumonia | curb65 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 9.15623097228 |  |  |  |  | 0 | 60 | 9.15623097228 | 0.86 | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iv | MIMIC-IV | pancreatitis | bisap4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 6.43043238419 |  |  |  |  | 0 | 60 | 6.43043238419 | 2.04 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iv | MIMIC-IV | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 6.77529821325 |  |  |  |  | 0 | 60 | 6.77529821325 | 1.14 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iii | MIMIC-III | sepsis | qsofa | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 8.60960385085 |  |  |  |  | 0 | 60 | 8.60960385085 | 1.22 | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iii | MIMIC-III | pneumonia | curb65 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 5.91558768112 |  |  |  |  | 0 | 60 | 5.91558768112 | 0.98 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iii | MIMIC-III | pancreatitis | bisap4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 4.41252533218 |  |  |  |  | 0 | 60 | 4.41252533218 | 2.45 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iii | MIMIC-III | heart failure | qsofa | interval withheld: degenerate_outcome_cell | not computed (degenerate_outcome_cell) | degenerate_outcome_cell | False | 1.23826459066 |  |  |  |  | 0 | 60 | 1.23826459066 | 0.97 | True | not computed (degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| mimic_iii | MIMIC-III | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 2.726591891 |  |  |  |  | 0 | 60 | 2.726591891 | 2.13 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| zigong | Zigong | sepsis | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 4.79636239673 |  |  |  |  | 0 | 60 | 4.79636239673 | 3.35 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| zigong | Zigong | pneumonia | curb65 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 6.32718232638 |  |  |  |  | 0 | 60 | 6.32718232638 | 2.52 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| zigong | Zigong | pancreatitis | bisap4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | -5.35714285714 |  |  |  |  | 0 | 60 | -5.35714285714 | 12.28 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| zigong | Zigong | heart failure | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | -9.36084845212 |  |  |  |  | 0 | 60 | -9.36084845212 | 13.77 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| zigong | Zigong | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 5.4583772392 |  |  |  |  | 0 | 60 | 5.4583772392 | 2.01 | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |  |  |
| peer | PEER-adapted-eICU | pneumonia | adapted CURB-65 (`score`, validated equal to `curb65`) | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 1.64 |  |  |  |  | 0 | 60 | 1.6403314949 | 1.08835633618 | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C | True | True |  |  |  |
| amsterdam | AmsterdamUMCdb 1.0.2 | sepsis | GCS ≤13 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) | too_few_distinct_patients_per_score_definition_cell | False | 18.91 |  |  |  |  | 0 | 60 | 18.9096497186 | 7.66494427928 | True | not computed (too_few_distinct_patients_per_score_definition_cell) | skipped_under_primary_C |  |  |  |  | qsofa_main |

## Supplementary Table 21. Bonferroni score-level δ_s intervals

| database | disease | level | estimand | family_size | family_alpha | critical_value | delta_pp | se_pp | pointwise_lower_pp | pointwise_upper_pp | adjusted_lower_pp | adjusted_upper_pp | adjusted_excludes_zero | interval_status | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | 0 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 5.89430894308943 | 6.13473090181204 | -6.13 | 17.92 | -12.653077214007261 | 24.44169510018612 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | sepsis | 1 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | -1.1475088844881707 | 1.140621773369351 | -3.38 | 1.09 | -4.5959979589844915 | 2.3009801900081497 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | sepsis | 2 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | -0.905815935860077 | 0.7404857933819632 | -2.36 | 0.55 | -3.144557320529891 | 1.332925448809737 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | sepsis | 3 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 1.6980122900140393 | 1.1630662706513477 | -0.58 | 3.98 | -1.8183341632090546 | 5.214358743237133 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | pneumonia | 0 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 5.263157894736842 |  |  |  |  |  | False | point only under primary audit gate | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | pneumonia | 1 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 1.7797017797017798 | 1.8182435871492966 | -1.78 | 5.34 | -3.717469404866658 | 7.2768729642702175 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | pneumonia | 2 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 0.033988832240834654 | 1.3350465366635604 | -2.58 | 2.65 | -4.002312686034345 | 4.070290350516014 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | pneumonia | 3 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 3.479970733491859 | 1.2057703129249733 | 1.12 | 5.84 | -0.16548462038145917 | 7.125426087365177 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | pneumonia | 4 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 4.203519769067449 | 1.5399089595127462 | 1.19 | 7.22 | -0.4521508016530402 | 8.859190339787936 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| eICU-CRD | pneumonia | 5 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 7.108457401411597 | 2.470414749299978 | 2.27 | 11.95 | -0.3604498834898384 | 14.577364686313032 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | sepsis | 0 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 20.15765765765766 | 7.754078161331601 | 4.96 | 35.36 | -3.285568174472553 | 43.600883489787876 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | sepsis | 1 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 17.290626733222407 | 2.024653379098127 | 13.32 | 21.26 | 11.169408271087136 | 23.41184519535768 | True | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | sepsis | 2 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 11.668188827865784 | 1.0713304909677324 | 9.57 | 13.77 | 8.429190958866945 | 14.907186696864622 | True | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | sepsis | 3 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 7.046411615458082 | 1.9373663984159752 | 3.25 | 10.84 | 1.189091499168868 | 12.903731731747294 | True | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | pneumonia | 0 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 4.545454545454546 |  |  |  |  |  | False | point only under primary audit gate | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | pneumonia | 1 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 3.2350948509485096 | 2.4101170882054235 | -1.49 | 7.96 | -4.051512016446413 | 10.521701718343431 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | pneumonia | 2 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 7.5219232768249125 | 1.4067801727008837 | 4.76 | 10.28 | 3.2687464840949274 | 11.775100069554897 | True | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | pneumonia | 3 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 11.38477293151372 | 1.3713472364782957 | 8.7 | 14.07 | 7.238722003197121 | 15.53082385983032 | True | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | pneumonia | 4 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 10.051678472731107 | 1.749273663054248 | 6.62 | 13.48 | 4.7630269177748925 | 15.34033002768732 | True | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |
| MIMIC-IV | pneumonia | 5 | delta_s observed mortality difference | 20 | 0.05 | 3.023341439739154 | 7.904692506563121 | 3.3311589770429686 | 1.38 | 14.43 | -2.166538471089975 | 17.975923484216217 | False | adjusted normal interval | Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained |

## Supplementary Table 22. Bonferroni interval-emission summary

| database | disease | family_size | planned_levels | issued_intervals | pointwise_excludes_zero | adjusted_excludes_zero | point_only_levels |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | 20 | 4 | 4 | 0 | 0 | 0 |
| eICU-CRD | pneumonia | 20 | 6 | 5 | 3 | 0 | 1 |
| MIMIC-IV | sepsis | 20 | 4 | 4 | 4 | 3 | 0 |
| MIMIC-IV | pneumonia | 20 | 6 | 5 | 4 | 3 | 1 |
| all primary sources | all primary conditions | 20 | 20 | 18 | 11 | 6 | 2 |

## Supplementary Table 23. Role-specific cohort selection counts, not δ_s or weighted summary Δ_w

| Database | Condition | Role | Diagnosis group | Panel records | Known group and outcome | Complete scores | Patients | Events | Hospitals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU | sepsis | train | all | 14199 | 14029 | 9449 | 8744 | 1734 | 105 |
| eICU | sepsis | train | primary | 8860 | 8750 | 5724 | 5419 | 1076 | 102 |
| eICU | sepsis | train | never_primary | 5329 | 5279 | 3725 | 3600 | 658 | 94 |
| eICU | sepsis | recalibration | all | 4968 | 4944 | 3361 | 3199 | 623 | 38 |
| eICU | sepsis | recalibration | primary | 3349 | 3333 | 2138 | 2055 | 393 | 36 |
| eICU | sepsis | recalibration | never_primary | 1618 | 1611 | 1223 | 1177 | 230 | 35 |
| eICU | sepsis | test | all | 4145 | 4089 | 2897 | 2701 | 509 | 40 |
| eICU | sepsis | test | primary | 2965 | 2936 | 2023 | 1915 | 341 | 38 |
| eICU | sepsis | test | never_primary | 1174 | 1153 | 874 | 842 | 168 | 39 |
| eICU | pneumonia | train | all | 11088 | 10953 | 6607 | 6175 | 1095 | 100 |
| eICU | pneumonia | train | primary | 2742 | 2692 | 1441 | 1391 | 172 | 89 |
| eICU | pneumonia | train | never_primary | 8346 | 8261 | 5166 | 4895 | 923 | 98 |
| eICU | pneumonia | recalibration | all | 3585 | 3568 | 2068 | 2008 | 358 | 40 |
| eICU | pneumonia | recalibration | primary | 849 | 847 | 402 | 398 | 61 | 35 |
| eICU | pneumonia | recalibration | never_primary | 2736 | 2721 | 1666 | 1621 | 297 | 39 |
| eICU | pneumonia | test | all | 3552 | 3492 | 2235 | 2122 | 370 | 39 |
| eICU | pneumonia | test | primary | 1146 | 1123 | 700 | 674 | 100 | 36 |
| eICU | pneumonia | test | never_primary | 2406 | 2369 | 1535 | 1477 | 270 | 39 |
| MIMIC-IV | sepsis | train | all | 3464 | 3350 | 2634 | 2393 | 675 | 0 |
| MIMIC-IV | sepsis | train | primary | 2022 | 2022 | 1585 | 1467 | 344 | 0 |
| MIMIC-IV | sepsis | train | never_primary | 1328 | 1328 | 1049 | 1005 | 331 | 0 |
| MIMIC-IV | sepsis | recalibration | all | 1861 | 1830 | 1339 | 1287 | 321 | 0 |
| MIMIC-IV | sepsis | recalibration | primary | 1219 | 1219 | 880 | 855 | 175 | 0 |
| MIMIC-IV | sepsis | recalibration | never_primary | 611 | 611 | 459 | 452 | 146 | 0 |
| MIMIC-IV | sepsis | test | all | 5229 | 5229 | 3816 | 3550 | 1001 | 0 |
| MIMIC-IV | sepsis | test | primary | 3096 | 3096 | 2245 | 2128 | 487 | 0 |
| MIMIC-IV | sepsis | test | never_primary | 2133 | 2133 | 1571 | 1512 | 514 | 0 |
| MIMIC-IV | pneumonia | train | all | 4969 | 4969 | 3824 | 3446 | 709 | 0 |
| MIMIC-IV | pneumonia | train | primary | 898 | 898 | 775 | 704 | 95 | 0 |
| MIMIC-IV | pneumonia | train | never_primary | 4071 | 4071 | 3049 | 2857 | 614 | 0 |
| MIMIC-IV | pneumonia | recalibration | all | 2163 | 2163 | 1464 | 1405 | 305 | 0 |
| MIMIC-IV | pneumonia | recalibration | primary | 164 | 164 | 126 | 125 | 21 | 0 |
| MIMIC-IV | pneumonia | recalibration | never_primary | 1999 | 1999 | 1338 | 1289 | 284 | 0 |
| MIMIC-IV | pneumonia | test | all | 6093 | 6093 | 4228 | 3968 | 898 | 0 |
| MIMIC-IV | pneumonia | test | primary | 390 | 390 | 316 | 306 | 36 | 0 |
| MIMIC-IV | pneumonia | test | never_primary | 5703 | 5703 | 3912 | 3712 | 862 | 0 |

## Supplementary Table 24. Panel-level split rules and exclusions, not δ_s or weighted summary Δ_w

| Database | Panel-level split field | Recorded value | Scope |
| --- | --- | --- | --- |
| eICU | split_method | SHA-256 hospital buckets (60% train / 20% recalibration / 20% test); globally exclude patients with cross-role, multihospital, or missing-hospital records | combined supplied panel before disease-specific complete-record selection |
| eICU | seed | JCE-v3-20261113 | combined supplied panel before disease-specific complete-record selection |
| eICU | hospitals_total | 205 | combined supplied panel before disease-specific complete-record selection |
| eICU | hospitals_by_role | {"test": 40, "recalibration": 44, "train": 121} | combined supplied panel before disease-specific complete-record selection |
| eICU | cross_role_patients_excluded | 737 | combined supplied panel before disease-specific complete-record selection |
| eICU | patients_with_missing_hospital_excluded | 0 | combined supplied panel before disease-specific complete-record selection |
| eICU | multi_hospital_patients_excluded_globally | 1199 | combined supplied panel before disease-specific complete-record selection |
| eICU | multi_hospital_patient_records_excluded_globally | 4426 | combined supplied panel before disease-specific complete-record selection |
| eICU | patient_count | 45922 | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | split_method | calendar-interval migration split from anchor_year_group plus admission-year shift; intervals wholly <=2013=train, 2014-2016=recalibration, 2017-2022=test; ambiguous/out-of-window records excluded | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | seed | JCE-v3-20261113 | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | temporal_metadata_identifiable | True | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | anchor_year_groups | ["2008 - 2010", "2011 - 2013", "2014 - 2016", "2017 - 2019", "2020 - 2022"] | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | calendar_windows | {"train": "entire possible admission interval <= 2013", "recalibration": "2014-2016", "test": "2017-2022"} | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | unresolved_or_ambiguous_records | 13689 | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | cross_role_patients_excluded | 756 | combined supplied panel before disease-specific complete-record selection |
| MIMIC-IV | patient_count | 33769 | combined supplied panel before disease-specific complete-record selection |

## Supplementary Table 25. Paired held-out Brier loss differences, not δ_s or weighted summary Δ_w

| Database | Condition | Test population | Contrast | Brier loss difference | 95% CI lower | 95% CI upper | Interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eICU | sepsis | all | primary_fixed_minus_broad_fixed | 0.000056 | -0.000063 | 0.000167 | pointwise_95pct |
| eICU | sepsis | all | primary_recalibrated_minus_broad_recalibrated | 0.000009 | -0.000021 | 0.000039 | pointwise_95pct |
| eICU | sepsis | all | primary_recalibrated_minus_fixed | -0.000035 | -0.000117 | 0.000057 | pointwise_95pct |
| eICU | sepsis | all | broad_recalibrated_minus_fixed | 0.000012 | -0.000034 | 0.000053 | pointwise_95pct |
| eICU | sepsis | primary | primary_fixed_minus_broad_fixed | 0.000116 | -0.000019 | 0.000246 | pointwise_95pct |
| eICU | sepsis | primary | primary_recalibrated_minus_broad_recalibrated | -0.000011 | -0.000048 | 0.000026 | pointwise_95pct |
| eICU | sepsis | primary | primary_recalibrated_minus_fixed | -0.000088 | -0.000187 | 0.000015 | pointwise_95pct |
| eICU | sepsis | primary | broad_recalibrated_minus_fixed | 0.000039 | -0.000013 | 0.000089 | pointwise_95pct |
| eICU | sepsis | never_primary | primary_fixed_minus_broad_fixed | -0.000081 | -0.000299 | 0.000135 | pointwise_95pct |
| eICU | sepsis | never_primary | primary_recalibrated_minus_broad_recalibrated | 0.000055 | -0.000001 | 0.000110 | pointwise_95pct |
| eICU | sepsis | never_primary | primary_recalibrated_minus_fixed | 0.000087 | -0.000076 | 0.000253 | pointwise_95pct |
| eICU | sepsis | never_primary | broad_recalibrated_minus_fixed | -0.000049 | -0.000132 | 0.000033 | pointwise_95pct |
| eICU | sepsis | all | primary_fixed_minus_broad_fixed | 0.000056 | -0.000109 | 0.000222 | hospital_cluster_pointwise_95pct |
| eICU | sepsis | all | primary_recalibrated_minus_broad_recalibrated | 0.000009 | -0.000020 | 0.000045 | hospital_cluster_pointwise_95pct |
| eICU | sepsis | all | primary_recalibrated_minus_fixed | -0.000035 | -0.000155 | 0.000083 | hospital_cluster_pointwise_95pct |
| eICU | sepsis | all | broad_recalibrated_minus_fixed | 0.000012 | -0.000047 | 0.000072 | hospital_cluster_pointwise_95pct |
| eICU | pneumonia | all | primary_fixed_minus_broad_fixed | 0.002412 | 0.000862 | 0.004033 | pointwise_95pct |
| eICU | pneumonia | all | primary_recalibrated_minus_broad_recalibrated | 0.000024 | -0.000217 | 0.000272 | pointwise_95pct |
| eICU | pneumonia | all | primary_recalibrated_minus_fixed | -0.002308 | -0.004157 | -0.000460 | pointwise_95pct |
| eICU | pneumonia | all | broad_recalibrated_minus_fixed | 0.000081 | -0.000326 | 0.000484 | pointwise_95pct |
| eICU | pneumonia | primary | primary_fixed_minus_broad_fixed | 0.001090 | -0.001503 | 0.003742 | pointwise_95pct |
| eICU | pneumonia | primary | primary_recalibrated_minus_broad_recalibrated | 0.000060 | -0.000347 | 0.000465 | pointwise_95pct |
| eICU | pneumonia | primary | primary_recalibrated_minus_fixed | -0.000649 | -0.003770 | 0.002333 | pointwise_95pct |
| eICU | pneumonia | primary | broad_recalibrated_minus_fixed | 0.000381 | -0.000306 | 0.001040 | pointwise_95pct |
| eICU | pneumonia | never_primary | primary_fixed_minus_broad_fixed | 0.003015 | 0.001060 | 0.004976 | pointwise_95pct |
| eICU | pneumonia | never_primary | primary_recalibrated_minus_broad_recalibrated | 0.000007 | -0.000295 | 0.000309 | pointwise_95pct |
| eICU | pneumonia | never_primary | primary_recalibrated_minus_fixed | -0.003065 | -0.005338 | -0.000816 | pointwise_95pct |
| eICU | pneumonia | never_primary | broad_recalibrated_minus_fixed | -0.000057 | -0.000554 | 0.000434 | pointwise_95pct |
| eICU | pneumonia | all | primary_fixed_minus_broad_fixed | 0.002412 | -0.000064 | 0.004949 | hospital_cluster_pointwise_95pct |
| eICU | pneumonia | all | primary_recalibrated_minus_broad_recalibrated | 0.000024 | -0.000263 | 0.000269 | hospital_cluster_pointwise_95pct |
| eICU | pneumonia | all | primary_recalibrated_minus_fixed | -0.002308 | -0.005378 | 0.000657 | hospital_cluster_pointwise_95pct |
| eICU | pneumonia | all | broad_recalibrated_minus_fixed | 0.000081 | -0.000625 | 0.000777 | hospital_cluster_pointwise_95pct |
| MIMIC-IV | sepsis | all | primary_fixed_minus_broad_fixed | 0.001899 | 0.000515 | 0.003197 | pointwise_95pct |
| MIMIC-IV | sepsis | all | primary_recalibrated_minus_broad_recalibrated | -0.000247 | -0.001355 | 0.000922 | pointwise_95pct |
| MIMIC-IV | sepsis | all | primary_recalibrated_minus_fixed | -0.001793 | -0.002748 | -0.000795 | pointwise_95pct |
| MIMIC-IV | sepsis | all | broad_recalibrated_minus_fixed | 0.000353 | -0.000012 | 0.000711 | pointwise_95pct |
| MIMIC-IV | sepsis | primary | primary_fixed_minus_broad_fixed | -0.002936 | -0.004461 | -0.001422 | pointwise_95pct |
| MIMIC-IV | sepsis | primary | primary_recalibrated_minus_broad_recalibrated | -0.000832 | -0.002269 | 0.000703 | pointwise_95pct |
| MIMIC-IV | sepsis | primary | primary_recalibrated_minus_fixed | 0.001277 | 0.000022 | 0.002471 | pointwise_95pct |
| MIMIC-IV | sepsis | primary | broad_recalibrated_minus_fixed | -0.000827 | -0.001267 | -0.000374 | pointwise_95pct |
| MIMIC-IV | sepsis | never_primary | primary_fixed_minus_broad_fixed | 0.008808 | 0.006410 | 0.011224 | pointwise_95pct |
| MIMIC-IV | sepsis | never_primary | primary_recalibrated_minus_broad_recalibrated | 0.000589 | -0.001227 | 0.002472 | pointwise_95pct |
| MIMIC-IV | sepsis | never_primary | primary_recalibrated_minus_fixed | -0.006180 | -0.007742 | -0.004534 | pointwise_95pct |
| MIMIC-IV | sepsis | never_primary | broad_recalibrated_minus_fixed | 0.002039 | 0.001413 | 0.002627 | pointwise_95pct |
| MIMIC-IV | pneumonia | all | primary_fixed_minus_broad_fixed | 0.007381 | 0.005685 | 0.009095 | pointwise_95pct |
| MIMIC-IV | pneumonia | all | primary_recalibrated_minus_broad_recalibrated | 0.000471 | -0.000456 | 0.001347 | pointwise_95pct |
| MIMIC-IV | pneumonia | all | primary_recalibrated_minus_fixed | -0.007420 | -0.010095 | -0.004820 | pointwise_95pct |
| MIMIC-IV | pneumonia | all | broad_recalibrated_minus_fixed | -0.000510 | -0.001050 | 0.000000 | pointwise_95pct |
| MIMIC-IV | pneumonia | primary | primary_fixed_minus_broad_fixed | -0.007298 | -0.011632 | -0.002597 | pointwise_95pct |
| MIMIC-IV | pneumonia | primary | primary_recalibrated_minus_broad_recalibrated | 0.001928 | -0.001133 | 0.004863 | pointwise_95pct |
| MIMIC-IV | pneumonia | primary | primary_recalibrated_minus_fixed | 0.012975 | 0.004574 | 0.020642 | pointwise_95pct |
| MIMIC-IV | pneumonia | primary | broad_recalibrated_minus_fixed | 0.003749 | 0.002108 | 0.005243 | pointwise_95pct |
| MIMIC-IV | pneumonia | never_primary | primary_fixed_minus_broad_fixed | 0.008566 | 0.006785 | 0.010350 | pointwise_95pct |
| MIMIC-IV | pneumonia | never_primary | primary_recalibrated_minus_broad_recalibrated | 0.000353 | -0.000582 | 0.001256 | pointwise_95pct |
| MIMIC-IV | pneumonia | never_primary | primary_recalibrated_minus_fixed | -0.009067 | -0.011849 | -0.006446 | pointwise_95pct |
| MIMIC-IV | pneumonia | never_primary | broad_recalibrated_minus_fixed | -0.000854 | -0.001415 | -0.000317 | pointwise_95pct |

## Supplementary Table 26. Held-out observed risks, prediction means and loss, not δ_s or weighted summary Δ_w

| Database | Condition | Test population | Mapping | Records | Observed risk (%) | Mean predicted risk (%) | Brier loss | Calibration intercept | Calibration slope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU | sepsis | all | primary_only_fixed | 2897 | 17.57 | 18.44 | 0.136962 | -0.062 | 1.061 |
| eICU | sepsis | all | broad_fixed | 2897 | 17.57 | 18.04 | 0.136906 | -0.034 | 1.046 |
| eICU | sepsis | all | primary_only_recalibrated | 2897 | 17.57 | 18.18 | 0.136927 | -0.043 | 1.061 |
| eICU | sepsis | all | broad_recalibrated | 2897 | 17.57 | 18.17 | 0.136918 | -0.043 | 1.046 |
| eICU | sepsis | primary | primary_only_fixed | 2023 | 16.86 | 18.35 | 0.134345 | -0.108 | 0.948 |
| eICU | sepsis | primary | broad_fixed | 2023 | 16.86 | 17.95 | 0.134229 | -0.080 | 0.934 |
| eICU | sepsis | primary | primary_only_recalibrated | 2023 | 16.86 | 18.09 | 0.134257 | -0.090 | 0.948 |
| eICU | sepsis | primary | broad_recalibrated | 2023 | 16.86 | 18.08 | 0.134268 | -0.089 | 0.934 |
| eICU | sepsis | never_primary | primary_only_fixed | 874 | 19.22 | 18.65 | 0.143021 | 0.040 | 1.300 |
| eICU | sepsis | never_primary | broad_fixed | 874 | 19.22 | 18.25 | 0.143102 | 0.068 | 1.282 |
| eICU | sepsis | never_primary | primary_only_recalibrated | 874 | 19.22 | 18.38 | 0.143108 | 0.058 | 1.300 |
| eICU | sepsis | never_primary | broad_recalibrated | 874 | 19.22 | 18.38 | 0.143053 | 0.058 | 1.282 |
| eICU | pneumonia | all | primary_only_fixed | 2235 | 16.55 | 12.39 | 0.133914 | 0.350 | 1.225 |
| eICU | pneumonia | all | broad_fixed | 2235 | 16.55 | 16.50 | 0.131502 | 0.004 | 1.104 |
| eICU | pneumonia | all | primary_only_recalibrated | 2235 | 16.55 | 17.61 | 0.131606 | -0.077 | 1.225 |
| eICU | pneumonia | all | broad_recalibrated | 2235 | 16.55 | 17.63 | 0.131582 | -0.079 | 1.104 |
| eICU | pneumonia | primary | primary_only_fixed | 700 | 14.29 | 11.69 | 0.117493 | 0.238 | 1.238 |
| eICU | pneumonia | primary | broad_fixed | 700 | 14.29 | 15.53 | 0.116403 | -0.102 | 1.116 |
| eICU | pneumonia | primary | primary_only_recalibrated | 700 | 14.29 | 16.67 | 0.116844 | -0.189 | 1.238 |
| eICU | pneumonia | primary | broad_recalibrated | 700 | 14.29 | 16.61 | 0.116784 | -0.186 | 1.116 |
| eICU | pneumonia | never_primary | primary_only_fixed | 1535 | 17.59 | 12.70 | 0.141402 | 0.396 | 1.206 |
| eICU | pneumonia | never_primary | broad_fixed | 1535 | 17.59 | 16.94 | 0.138387 | 0.048 | 1.087 |
| eICU | pneumonia | never_primary | primary_only_recalibrated | 1535 | 17.59 | 18.03 | 0.138338 | -0.031 | 1.206 |
| eICU | pneumonia | never_primary | broad_recalibrated | 1535 | 17.59 | 18.10 | 0.138330 | -0.036 | 1.087 |
| MIMIC-IV | sepsis | all | primary_only_fixed | 3816 | 26.23 | 21.36 | 0.189500 | 0.284 | 0.708 |
| MIMIC-IV | sepsis | all | broad_fixed | 3816 | 26.23 | 25.70 | 0.187602 | 0.028 | 1.178 |
| MIMIC-IV | sepsis | all | primary_only_recalibrated | 3816 | 26.23 | 24.70 | 0.187707 | 0.085 | 0.708 |
| MIMIC-IV | sepsis | all | broad_recalibrated | 3816 | 26.23 | 24.42 | 0.187955 | 0.098 | 1.178 |
| MIMIC-IV | sepsis | primary | primary_only_fixed | 2245 | 21.69 | 21.71 | 0.161123 | -0.001 | 0.975 |
| MIMIC-IV | sepsis | primary | broad_fixed | 2245 | 21.69 | 25.94 | 0.164059 | -0.240 | 1.622 |
| MIMIC-IV | sepsis | primary | primary_only_recalibrated | 2245 | 21.69 | 25.09 | 0.162400 | -0.200 | 0.975 |
| MIMIC-IV | sepsis | primary | broad_recalibrated | 2245 | 21.69 | 24.65 | 0.163232 | -0.170 | 1.622 |
| MIMIC-IV | sepsis | never_primary | primary_only_fixed | 1571 | 32.72 | 20.85 | 0.230053 | 0.649 | 0.510 |
| MIMIC-IV | sepsis | never_primary | broad_fixed | 1571 | 32.72 | 25.35 | 0.221245 | 0.367 | 0.848 |
| MIMIC-IV | sepsis | never_primary | primary_only_recalibrated | 1571 | 32.72 | 24.14 | 0.223873 | 0.450 | 0.510 |
| MIMIC-IV | sepsis | never_primary | broad_recalibrated | 1571 | 32.72 | 24.08 | 0.223284 | 0.437 | 0.848 |
| MIMIC-IV | pneumonia | all | primary_only_fixed | 4228 | 21.24 | 12.48 | 0.167190 | 0.680 | 0.765 |
| MIMIC-IV | pneumonia | all | broad_fixed | 4228 | 21.24 | 19.28 | 0.159809 | 0.126 | 1.119 |
| MIMIC-IV | pneumonia | all | primary_only_recalibrated | 4228 | 21.24 | 21.28 | 0.159770 | -0.002 | 0.765 |
| MIMIC-IV | pneumonia | all | broad_recalibrated | 4228 | 21.24 | 21.18 | 0.159299 | 0.004 | 1.119 |
| MIMIC-IV | pneumonia | primary | primary_only_fixed | 316 | 11.39 | 13.03 | 0.095047 | -0.160 | 1.078 |
| MIMIC-IV | pneumonia | primary | broad_fixed | 316 | 11.39 | 19.79 | 0.102345 | -0.672 | 1.575 |
| MIMIC-IV | pneumonia | primary | primary_only_recalibrated | 316 | 11.39 | 22.08 | 0.108021 | -0.843 | 1.078 |
| MIMIC-IV | pneumonia | primary | broad_recalibrated | 316 | 11.39 | 21.73 | 0.106094 | -0.795 | 1.575 |
| MIMIC-IV | pneumonia | never_primary | primary_only_fixed | 3912 | 22.03 | 12.44 | 0.173017 | 0.735 | 0.763 |
| MIMIC-IV | pneumonia | never_primary | broad_fixed | 3912 | 22.03 | 19.23 | 0.164451 | 0.178 | 1.114 |
| MIMIC-IV | pneumonia | never_primary | primary_only_recalibrated | 3912 | 22.03 | 21.21 | 0.163950 | 0.053 | 0.763 |
| MIMIC-IV | pneumonia | never_primary | broad_recalibrated | 3912 | 22.03 | 21.14 | 0.163597 | 0.055 | 1.114 |

## Supplementary Table 27. Full paired code-breadth and refinement comparisons

| Analysis block | Database | Condition | Records (patients) | Narrow / score-only Δ_w weighted summary | Broad / refined Δ_w weighted summary | Paired difference (percentage points; numerical interval) | Cell inventory / reconstruction | Interval status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Paired code breadth | eICU-CRD | sepsis | 16,576 (15,217) | 0.13 | 0.13 | 0.00 [0.00, 0.00] | Same records; common score support | descriptive paired interval, audit gates require separate assessment |
| Paired code breadth | eICU-CRD | pneumonia | 11,222 (10,476) | 3.52 | 3.56 | 0.04 [-0.06, 0.13] | Same records; common score support | descriptive paired interval, audit gates require separate assessment |
| Paired code breadth | MIMIC-IV | sepsis | 10,433 (9,094) | 11.32 | 11.35 | 0.02 [-0.08, 0.13] | Same records; common score support | descriptive paired interval, audit gates require separate assessment |
| Paired code breadth | MIMIC-IV | pneumonia | 2,179 (2,056) | 10.37 | 11.04 | 0.66 [-0.38, 1.71] | Same records; common score support | descriptive paired interval, audit gates require separate assessment |
| Paired code breadth | MIMIC-III | sepsis | 5,500 (4,881) | 8.57 | 8.57 | -0.01 [-0.17, 0.15] | Same records; common score support | descriptive paired interval, audit gates require separate assessment |
| Paired code breadth | MIMIC-III | pneumonia | 2,046 (1,884) | 8.08 | 8.07 | -0.01 [-1.57, 1.54] | Same records; common score support | descriptive paired interval, audit gates require separate assessment |
| Hospital × score | eICU-CRD | sepsis | 16,234 (14,892) | 0.24 | 0.24 | -0.00 [-0.80, 0.79] | 533 hospital-score cells; 366 with either arm ≤5; 68.67% | descriptive, fine-cell interval calibration unverified |
| Hospital × score | eICU-CRD | pneumonia | 10,402 (9,728) | 3.91 | 3.04 | -0.87 [-1.92, 0.18] | 809 hospital-score cells; 701 with either arm ≤5; 86.65% | descriptive, fine-cell interval calibration unverified |
| Component pattern | eICU-CRD | sepsis | 16,576 (15,217) | 0.13 | 0.08 | -0.05 [-0.14, 0.03] | 100.00% | descriptive, fine-cell interval calibration unverified |
| Component pattern | MIMIC-IV | sepsis | 10,804 (9,398) | 11.30 | 11.21 | -0.09 [-0.18, 0.01] | 100.00% | descriptive, fine-cell interval calibration unverified |
| Component pattern | MIMIC-III | sepsis | 5,588 (4,957) | 8.61 | 8.26 | -0.35 [-0.60, -0.09] | 100.00% | descriptive, fine-cell interval calibration unverified |
| Component pattern | Zigong | sepsis | 133 (133) | 3.99 | 4.05 | 0.07 [-1.47, 1.61] | 100.00% | descriptive, fine-cell interval calibration unverified |

Complete row-level data are also supplied in S27.csv.

## Supplementary Table 28. Matched-record score-construction contrasts

| disease | alternative | n_matched | main_delta_w_pp | alternative_delta_w_pp | difference_pp | numerical_lo_pp | numerical_hi_pp | estimand | interval_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sepsis | timed GCS excluding meds1 | 16502 | 0.1009918157827517 | 0.1009918157827517 | 0.0 | 0.0 | 0.0 | difference between Delta_w weighted summaries on matched records | descriptive paired influence interval |
| sepsis | APACHE valid GCS with timed fallback | 16502 | 0.1009918157827517 | -0.22736618823389376 | -0.3283580040166455 | -0.48871398280283623 | -0.1680020252304547 | difference between Delta_w weighted summaries on matched records | descriptive paired influence interval |
| pneumonia | timed GCS excluding meds1 | 11404 | 3.54780980006211 | 3.54780980006211 | 0.0 | 0.0 | 0.0 | difference between Delta_w weighted summaries on matched records | descriptive paired influence interval |
| pneumonia | APACHE valid GCS with timed fallback | 11404 | 3.54780980006211 | 3.6277179851879797 | 0.07990818512586956 | -0.02523987454290167 | 0.18505624479464078 | difference between Delta_w weighted summaries on matched records | descriptive paired influence interval |
| pancreatitis | timed GCS excluding meds1 | 348 | 0.6408098133096642 | 0.6408098133096642 | 0.0 | 0.0 | 0.0 | difference between Delta_w weighted summaries on matched records | descriptive paired influence interval |
| pancreatitis | APACHE valid GCS with timed fallback | 348 | 0.6408098133096642 | -0.26122139303451963 | -0.9020312063441838 | -2.572699503401768 | 0.7686370907134005 | difference between Delta_w weighted summaries on matched records | descriptive paired influence interval |

## Supplementary Table 29. Score-construction weighted summaries Δ_w

| database | disease | analysis | estimand | n | n_patients | n_inference_clusters | delta_w_pp | numerical_se_pp | lo_pp | hi_pp | support_share | levels | state | interval_status | weight_target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | timed nursing GCS | Delta_w weighted summary | 16576 | 15217 | 15217 | 0.1273480523914114 | 0.6003643777030951 | -1.05 | 1.3 | 1.0 | 4 | estimable | computed | observed pooled record shares within common support |
| eICU-CRD | sepsis | timed GCS excluding meds1 | Delta_w weighted summary | 16502 | 15146 | 15146 | 0.1009918157827517 | 0.6008453669188831 | -1.08 | 1.28 | 1.0 | 4 | estimable | computed | observed pooled record shares within common support |
| eICU-CRD | sepsis | APACHE valid GCS with timed fallback | Delta_w weighted summary | 21568 | 19681 | 19681 | 0.657699405940891 | 0.5449502501909447 | -0.41 | 1.73 | 1.0 | 4 | estimable | computed | observed pooled record shares within common support |
| eICU-CRD | pneumonia | timed nursing GCS | Delta_w weighted summary | 11481 | 10724 | 10724 | 3.698218842732749 | 0.7764584954699939 |  |  | 1.0 | 6 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support |
| eICU-CRD | pneumonia | timed GCS excluding meds1 | Delta_w weighted summary | 11404 | 10650 | 10650 | 3.54780980006211 | 0.7779924965509025 |  |  | 1.0 | 6 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support |
| eICU-CRD | pneumonia | APACHE valid GCS with timed fallback | Delta_w weighted summary | 15142 | 14040 | 14040 | 3.718666509210654 | 0.6657472208287287 |  |  | 1.0 | 6 | interval withheld: degenerate_outcome_cell | not computed (degenerate_outcome_cell) | observed pooled record shares within common support |
| eICU-CRD | pancreatitis | timed nursing GCS | Delta_w weighted summary | 351 | 343 | 343 | 0.77696891441632 | 2.995381215904904 |  |  | 1.0 | 4 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support |
| eICU-CRD | pancreatitis | timed GCS excluding meds1 | Delta_w weighted summary | 348 | 340 | 340 | 0.6408098133096642 | 3.0388076549364404 |  |  | 1.0 | 4 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support |
| eICU-CRD | pancreatitis | APACHE valid GCS with timed fallback | Delta_w weighted summary | 466 | 452 | 452 | 1.0610353469493792 | 2.742183852977228 |  |  | 1.0 | 4 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) | observed pooled record shares within common support |

## Supplementary Table 30. Patient and hospital clustering sensitivity for weighted summary Δ_w

| database | disease | analysis | estimand | cluster_definition | n_input_records | n_supported_records | n_patients | n_hospitals | n_patients_across_hospitals | delta_w_pp | primary_patient_se_pp | sensitivity_se_pp | degrees_freedom | lower_pp | upper_pp | interval_status | variance_formula | limitation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | hospital | 16576 | 16576 | 15217 | 184 | 206 | 0.1273480523914114 | 0.6003643777030951 | 0.6959418456447894 | 183 | -1.2457535013076828 | 1.5004496060905057 | descriptive asymptotic t interval | V_hospital | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | sepsis | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | patient and hospital, two-way inclusion-exclusion | 16576 | 16576 | 15217 | 184 | 206 | 0.1273480523914114 | 0.6003643777030951 | 0.6959191179532345 | 183 | -1.2457086593014413 | 1.5004047640842642 | descriptive asymptotic t interval | V_patient + V_hospital - V_patient_hospital_intersection | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | pneumonia | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | hospital | 11481 | 11481 | 10724 | 179 | 103 | 3.698218842732749 | 0.7764584954699939 | 0.8970446920010561 | 178 | 1.9280079913636992 | 5.4684296941018 | descriptive asymptotic t interval | V_hospital | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | pneumonia | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | patient and hospital, two-way inclusion-exclusion | 11481 | 11481 | 10724 | 179 | 103 | 3.698218842732749 | 0.7764584954699939 | 0.8966573437769524 | 178 | 1.9287723769463587 | 5.46766530851914 | descriptive asymptotic t interval | V_patient + V_hospital - V_patient_hospital_intersection | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | pancreatitis | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | hospital | 351 | 351 | 343 | 107 | 3 | 0.77696891441632 | 2.995381215904904 | 2.573426254224938 | 106 | -4.325098930565492 | 5.879036759398131 | descriptive asymptotic t interval | V_hospital | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | pancreatitis | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | patient and hospital, two-way inclusion-exclusion | 351 | 351 | 343 | 107 | 3 | 0.77696891441632 | 2.995381215904904 | 2.5669271659332487 | 106 | -4.312213855914416 | 5.866151684747056 | descriptive asymptotic t interval | V_patient + V_hospital - V_patient_hospital_intersection | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | heart failure | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | hospital | 9540 | 9540 | 8611 | 185 | 95 | 3.375244127321511 | 0.7286869809701032 | 0.7116363678895701 | 184 | 1.971227885673469 | 4.779260368969553 | descriptive asymptotic t interval | V_hospital | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | heart failure | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | patient and hospital, two-way inclusion-exclusion | 9540 | 9540 | 8611 | 185 | 95 | 3.375244127321511 | 0.7286869809701032 | 0.7117157297575463 | 184 | 1.9710713094266186 | 4.779416945216404 | descriptive asymptotic t interval | V_patient + V_hospital - V_patient_hospital_intersection | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | COPD | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | hospital | 7703 | 7703 | 6711 | 180 | 92 | 4.411725941225043 | 0.7371390858619822 | 0.8610061350569992 | 179 | 2.7126978563462214 | 6.110754026103865 | descriptive asymptotic t interval | V_hospital | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |
| eICU-CRD | COPD | clustering sensitivity after revised primary results | Delta_w record-weighted summary on identical complete-case records | patient and hospital, two-way inclusion-exclusion | 7703 | 7703 | 6711 | 180 | 92 | 4.411725941225043 | 0.7371390858619822 | 0.860360667347095 | 179 | 2.7139715612855446 | 6.1094803211645425 | descriptive asymptotic t interval | V_patient + V_hospital - V_patient_hospital_intersection | crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures |

## Supplementary Table 31. Paired eICU documentation-timing contrasts

| Condition | Comparison | Records | Patients | Difference in Δ_w (pp) | Descriptive paired interval (pp) | Interval status |
| --- | --- | --- | --- | --- | --- | --- |
| sepsis | by-24-hours minus full-course grouping on identical supported records | 14,753 | 13,598 | 0.44 | [-0.11, 0.99] | descriptive paired influence interval |
| pneumonia | by-24-hours minus full-course grouping on identical supported records | 9,542 | 8,951 | 0.21 | [-0.34, 0.75] | descriptive paired influence interval |

**Notes.**

- These contrasts use identical classifiable records and pooled observed score weights. The intervals are descriptive paired influence intervals, not audit-gated summary CIs.

## Supplementary Table 32. eICU 24-hour hospital-survivor sensitivity

| Condition | Analysis | Risk set | Records | Patients | Δ_w / paired difference (pp) | Numerical interval (pp) | Interval status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sepsis | 24-hour hospital survivors, full-course diagnosis | still hospitalized 24 hours after index ICU admission | 13,980 | 12,894 | -1.16 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| sepsis | 24-hour hospital survivors, never-primary-by-24-hours | still hospitalized 24 hours after index ICU admission | 13,980 | 12,894 | -0.18 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| pneumonia | 24-hour hospital survivors, full-course diagnosis | still hospitalized 24 hours after index ICU admission | 9,248 | 8,682 | 2.28 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| pneumonia | 24-hour hospital survivors, never-primary-by-24-hours | still hospitalized 24 hours after index ICU admission | 9,248 | 8,682 | 2.60 | not computed | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |

**Notes.**

- This survivor sensitivity conditions on remaining hospitalized 24 hours after index ICU admission and is separate from the primary three-way documentation comparison.

## Supplementary Table 33. ED-linked cohort component completeness

| disease | cohort | cohort_label | hospital_group | grp | n_main_admission_records | n_score_complete | score_complete_pct | n_outcome_complete | outcome_complete_pct | n_score_and_outcome_complete | n_analysis_frame_records | n_main_patients | n_analysis_frame_patients |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | primary hospital billing position | 0 | 8756 | 6679 | 76.27912288716308 | 8756 | 100.0 | 6679 | 6679 | 7764 | 5964 |
| sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | never-primary hospital billing position | 1 | 5366 | 4125 | 76.87290346626911 | 5366 | 100.0 | 4125 | 4125 | 5024 | 3872 |
| sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | primary hospital billing position | 0 | 4199 | 3353 | 79.85234579661824 | 4199 | 100.0 | 3353 | 3353 | 3746 | 3030 |
| sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | never-primary hospital billing position | 1 | 1367 | 1048 | 76.66422823701537 | 1367 | 100.0 | 1048 | 1048 | 1313 | 1007 |
| sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | primary hospital billing position | 0 | 1200 | 944 | 78.66666666666667 | 1200 | 100.0 | 944 | 944 | 1146 | 903 |
| sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | never-primary hospital billing position | 1 | 203 | 172 | 84.72906403940887 | 203 | 100.0 | 172 | 172 | 196 | 167 |
| sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | primary hospital billing position | 0 | 1200 | 944 | 78.66666666666667 | 1200 | 100.0 | 944 | 944 | 1146 | 903 |
| sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | never-primary hospital billing position | 1 | 203 | 172 | 84.72906403940887 | 203 | 100.0 | 172 | 172 | 196 | 167 |
| pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | primary hospital billing position | 0 | 1936 | 1640 | 84.7107438016529 | 1936 | 100.0 | 1640 | 1640 | 1755 | 1498 |
| pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | never-primary hospital billing position | 1 | 15087 | 10862 | 71.99575793729701 | 15087 | 100.0 | 10862 | 10862 | 13441 | 9847 |
| pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | primary hospital billing position | 0 | 708 | 600 | 84.7457627118644 | 708 | 100.0 | 600 | 600 | 668 | 570 |
| pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | never-primary hospital billing position | 1 | 5176 | 3648 | 70.47913446676971 | 5176 | 100.0 | 3648 | 3648 | 4700 | 3362 |
| pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | primary hospital billing position | 0 | 415 | 361 | 86.98795180722891 | 415 | 100.0 | 361 | 361 | 387 | 338 |
| pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | never-primary hospital billing position | 1 | 1305 | 1026 | 78.62068965517241 | 1305 | 100.0 | 1026 | 1026 | 1208 | 962 |
| pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | primary hospital billing position | 0 | 415 | 361 | 86.98795180722891 | 415 | 100.0 | 361 | 361 | 387 | 338 |
| pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | never-primary hospital billing position | 1 | 1305 | 1026 | 78.62068965517241 | 1305 | 100.0 | 1026 | 1026 | 1208 | 962 |

## Supplementary Table 34. ED-linked cohort weighted summaries Δ_w

| analysis | estimand | n | n_patients | n_inference_clusters | delta_w_pp | numerical_se_pp | lo_pp | hi_pp | support_share | levels | state | interval_status | weight_target | disease | cohort | cohort_label | score | n_analysis_frame_records_all_levels | n_analysis_frame_primary_records | n_analysis_frame_never_primary_records | n_analysis_frame_primary_patients | n_analysis_frame_never_primary_patients | n_supported_records | n_supported_patients | n_records_outside_common_support | support_share_pct_of_complete_analysis_records | common_support_levels | weight_by_score_level | C_state | C_interval_status | C_verdict | normal_IF_delta_ci_pp_gated_by_C | bootstrap_ci_pp_gated_by_C | difference_from_full_main_delta_w_pp_descriptive | difference_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full main ICU-indexed complete-score hospital cohort | Delta_w record-weighted summary (never-primary minus primary) | 10804 | 9398 | 9398 | 11.295813284083817 | 0.8605864145358404 | 9.61 | 12.98 | 1.0 | 4 | estimable | computed | observed pooled record shares within common support | sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | qsofa | 10804 | 6679 | 4125 | 5964 | 3872 | 10804 | 9398 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0] | {"0.0": 0.007867456497593484, "1.0": 0.1322658274713069, "2.0": 0.6039429840799704, "3.0": 0.2559237319511292} | estimable | computed | estimable | [9.61, 12.98] | [9.81, 12.85] |  | different observed cohort/common support/record weights; descriptive only |
| Linked ED episode, any ED diagnosis | Delta_w record-weighted summary (never-primary minus primary) | 4401 | 3895 | 3895 | 4.69266055770278 | 1.4182428892927623 |  |  | 1.0 | 4 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) | observed pooled record shares within common support | sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | qsofa | 4401 | 3353 | 1048 | 3030 | 1007 | 4401 | 3895 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0] | {"0.0": 0.007952738014087708, "1.0": 0.12406271301976823, "2.0": 0.6364462622131334, "3.0": 0.2315382867530107} | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) | interval withheld: too_few_distinct_patients_per_score_definition_cell | null | null | -6.603152726381037 | different observed cohort/common support/record weights; descriptive only |
| Linked ED episode with MAIN-matching ED code | Delta_w record-weighted summary (never-primary minus primary) | 1116 | 1054 | 1054 | -3.7913751051590423 | 2.878612777877874 |  |  | 1.0 | 4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | observed pooled record shares within common support | sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | qsofa | 1116 | 944 | 172 | 903 | 167 | 1116 | 1054 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0] | {"0.0": 0.005376344086021506, "1.0": 0.08422939068100359, "2.0": 0.660394265232975, "3.0": 0.25} | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | null | null | -15.08718838924286 | different observed cohort/common support/record weights; descriptive only |
| MAIN-matching ED episode ends by index ICU | Delta_w record-weighted summary (never-primary minus primary) | 1116 | 1054 | 1054 | -3.7913751051590423 | 2.878612777877874 |  |  | 1.0 | 4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | observed pooled record shares within common support | sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | qsofa | 1116 | 944 | 172 | 903 | 167 | 1116 | 1054 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0] | {"0.0": 0.005376344086021506, "1.0": 0.08422939068100359, "2.0": 0.660394265232975, "3.0": 0.25} | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | null | null | -15.08718838924286 | different observed cohort/common support/record weights; descriptive only |
| Full main ICU-indexed complete-score hospital cohort | Delta_w record-weighted summary (never-primary minus primary) | 12502 | 10976 | 10976 | 9.156230972275353 | 0.8583091833088273 |  |  | 1.0 | 6 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | 12502 | 1640 | 10862 | 1498 | 9847 | 12502 | 10976 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] | {"0.0": 0.009838425851863702, "1.0": 0.06926891697328427, "2.0": 0.1922892337226044, "3.0": 0.2972324428091505, "4.0": 0.30147176451767715, "5.0": 0.12989921612541994} | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | null | null |  | different observed cohort/common support/record weights; descriptive only |
| Linked ED episode, any ED diagnosis | Delta_w record-weighted summary (never-primary minus primary) | 4248 | 3817 | 3817 | 7.1795025029298785 | 1.3656672042992635 |  |  | 1.0 | 6 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | 4248 | 600 | 3648 | 570 | 3362 | 4248 | 3817 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] | {"0.0": 0.009651600753295669, "1.0": 0.0713276836158192, "2.0": 0.19538606403013184, "3.0": 0.2846045197740113, "4.0": 0.2959039548022599, "5.0": 0.1431261770244821} | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | null | null | -1.976728469345474 | different observed cohort/common support/record weights; descriptive only |
| Linked ED episode with MAIN-matching ED code | Delta_w record-weighted summary (never-primary minus primary) | 1387 | 1262 | 1262 | 6.131088351269183 | 1.9696030763666093 |  |  | 1.0 | 6 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | observed pooled record shares within common support | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | 1387 | 361 | 1026 | 338 | 962 | 1387 | 1262 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] | {"0.0": 0.006488824801730353, "1.0": 0.06705118961788031, "2.0": 0.18601297764960345, "3.0": 0.273972602739726, "4.0": 0.2999279019466474, "5.0": 0.1665465032444124} | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | null | null | -3.02514262100617 | different observed cohort/common support/record weights; descriptive only |
| MAIN-matching ED episode ends by index ICU | Delta_w record-weighted summary (never-primary minus primary) | 1387 | 1262 | 1262 | 6.131088351269183 | 1.9696030763666093 |  |  | 1.0 | 6 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | observed pooled record shares within common support | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | 1387 | 361 | 1026 | 338 | 962 | 1387 | 1262 | 0 | 100.0 | [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] | {"0.0": 0.006488824801730353, "1.0": 0.06705118961788031, "2.0": 0.18601297764960345, "3.0": 0.273972602739726, "4.0": 0.2999279019466474, "5.0": 0.1665465032444124} | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | null | null | -3.02514262100617 | different observed cohort/common support/record weights; descriptive only |

## Supplementary Table 35. Linked ED episode counts

| disease | cohort | cohort_label | hospital_group | grp | n_qualifying_ed_episodes | n_analysis_admissions_with_qualifying_episode | n_analysis_admissions_with_multiple_qualifying_episodes | max_qualifying_episodes_per_admission | analysis_unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | primary hospital billing position | 0 | 3360 | 3353 | 7 | 2 | one hospital admission per disease |
| sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | never-primary hospital billing position | 1 | 1049 | 1048 | 1 | 2 | one hospital admission per disease |
| sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | primary hospital billing position | 0 | 944 | 944 | 0 | 1 | one hospital admission per disease |
| sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | never-primary hospital billing position | 1 | 172 | 172 | 0 | 1 | one hospital admission per disease |
| sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | primary hospital billing position | 0 | 944 | 944 | 0 | 1 | one hospital admission per disease |
| sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | never-primary hospital billing position | 1 | 172 | 172 | 0 | 1 | one hospital admission per disease |
| pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | primary hospital billing position | 0 | 601 | 600 | 1 | 2 | one hospital admission per disease |
| pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | never-primary hospital billing position | 1 | 3653 | 3648 | 5 | 2 | one hospital admission per disease |
| pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | primary hospital billing position | 0 | 361 | 361 | 0 | 1 | one hospital admission per disease |
| pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | never-primary hospital billing position | 1 | 1026 | 1026 | 0 | 1 | one hospital admission per disease |
| pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | primary hospital billing position | 0 | 361 | 361 | 0 | 1 | one hospital admission per disease |
| pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | never-primary hospital billing position | 1 | 1026 | 1026 | 0 | 1 | one hospital admission per disease |

## Supplementary Table 36. ED linkage eligibility

| disease | failure | n_rows | n_distinct_stays | interpretation |
| --- | --- | --- | --- | --- |
| sepsis | HADM matched target main disease admission but subject_id mismatched | 0 | 0.0 | excluded from all ED-linked cohorts |
| sepsis | Target main disease admissions without subject-verified ED HADM link | 7691 |  | no ED cohort link observed; not classified as a data error |
| sepsis | ED diagnosis rows without matching stay_id | 0 |  | not used for ED code matching |
| sepsis | ED diagnosis rows with stay_id but subject_id mismatch | 0 |  | not used for ED code matching |
| pneumonia | HADM matched target main disease admission but subject_id mismatched | 0 | 0.0 | excluded from all ED-linked cohorts |
| pneumonia | Target main disease admissions without subject-verified ED HADM link | 10099 |  | no ED cohort link observed; not classified as a data error |
| pneumonia | ED diagnosis rows without matching stay_id | 0 |  | not used for ED code matching |
| pneumonia | ED diagnosis rows with stay_id but subject_id mismatch | 0 |  | not used for ED code matching |

## Supplementary Table 37. ED-linked score-level risks and δ_s

| level | n | n_never | n_primary | patients_never | patients_primary | events_never | events_primary | risk_never | risk_primary | diff_pp | risk_never_ci_pp | risk_primary_ci_pp | delta_ci_pp | risk_never_ci_status | risk_primary_ci_status | delta_ci_status | weight | disease | cohort | cohort_label | score | estimand | support_record_weight | C_state | C_interval_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0 | 85 | 37 | 48 | 37 | 47 | 9.0 | 2.0 | 24.32 | 4.17 | 20.16 | [13.17, 40.52] | [1.08, 14.81] | [4.96, 35.36] | computed | computed | computed | 0.007867456497593484 | sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.007867456497593484 | estimable | computed |
| 1.0 | 1429 | 601 | 828 | 595 | 808 | 154.0 | 69.0 | 25.62 | 8.33 | 17.29 | [22.28, 29.28] | [6.64, 10.41] | [13.32, 21.26] | computed | computed | computed | 0.1322658274713069 | sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.1322658274713069 | estimable | computed |
| 2.0 | 6525 | 2513 | 4012 | 2393 | 3666 | 706.0 | 659.0 | 28.09 | 16.43 | 11.67 | [26.36, 29.9] | [15.3, 17.61] | [9.57, 13.77] | computed | computed | computed | 0.6039429840799704 | sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.6039429840799704 | estimable | computed |
| 3.0 | 2765 | 974 | 1791 | 955 | 1698 | 402.0 | 613.0 | 41.27 | 34.23 | 7.05 | [38.21, 44.41] | [32.03, 36.49] | [3.25, 10.84] | computed | computed | computed | 0.2559237319511292 | sepsis | row1_full_main | Full main ICU-indexed complete-score hospital cohort | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2559237319511292 | estimable | computed |
| 0.0 | 35 | 15 | 20 | 15 | 19 | 2.0 | 1.0 | 13.33 | 5.0 | 8.33 |  |  |  | too few distinct patients | too few distinct patients | too few distinct patients in a definition | 0.007952738014087708 | sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.007952738014087708 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) |
| 1.0 | 546 | 152 | 394 | 151 | 385 | 36.0 | 26.0 | 23.68 | 6.6 | 17.09 | [17.58, 31.1] | [4.53, 9.52] | [9.88, 24.29] | computed | computed | computed | 0.12406271301976823 | sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.12406271301976823 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) |
| 2.0 | 2801 | 673 | 2128 | 653 | 1970 | 121.0 | 293.0 | 17.98 | 13.77 | 4.21 | [15.24, 21.08] | [12.36, 15.31] | [0.96, 7.47] | computed | computed | computed | 0.6364462622131334 | sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.6364462622131334 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) |
| 3.0 | 1019 | 208 | 811 | 206 | 768 | 60.0 | 240.0 | 28.85 | 29.59 | -0.75 | [23.08, 35.4] | [26.52, 32.86] | [-7.65, 6.16] | computed | computed | computed | 0.2315382867530107 | sepsis | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2315382867530107 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) |
| 0.0 | 6 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |  | too few distinct patients | too few distinct patients | too few distinct patients in a definition | 0.005376344086021506 | sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.005376344086021506 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 1.0 | 94 | 15 | 79 | 15 | 79 | 0.0 | 5.0 | 0.0 | 6.33 | -6.33 |  | [2.66, 14.33] |  | too few distinct patients | computed | too few distinct patients in a definition | 0.08422939068100359 | sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.08422939068100359 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 2.0 | 737 | 125 | 612 | 121 | 594 | 12.0 | 74.0 | 9.6 | 12.09 | -2.49 | [5.52, 16.18] | [9.73, 14.93] | [-8.29, 3.3] | computed | computed | computed | 0.660394265232975 | sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.660394265232975 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 3.0 | 279 | 31 | 248 | 31 | 239 | 8.0 | 80.0 | 25.81 | 32.26 | -6.45 | [13.46, 43.75] | [26.61, 38.47] | [-22.95, 10.04] | computed | computed | computed | 0.25 | sepsis | row3_ed_coded | Linked ED episode with MAIN-matching ED code | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.25 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 0.0 | 6 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |  | too few distinct patients | too few distinct patients | too few distinct patients in a definition | 0.005376344086021506 | sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.005376344086021506 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 1.0 | 94 | 15 | 79 | 15 | 79 | 0.0 | 5.0 | 0.0 | 6.33 | -6.33 |  | [2.66, 14.33] |  | too few distinct patients | computed | too few distinct patients in a definition | 0.08422939068100359 | sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.08422939068100359 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 2.0 | 737 | 125 | 612 | 121 | 594 | 12.0 | 74.0 | 9.6 | 12.09 | -2.49 | [5.52, 16.18] | [9.73, 14.93] | [-8.29, 3.3] | computed | computed | computed | 0.660394265232975 | sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.660394265232975 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 3.0 | 279 | 31 | 248 | 31 | 239 | 8.0 | 80.0 | 25.81 | 32.26 | -6.45 | [13.46, 43.75] | [26.61, 38.47] | [-22.95, 10.04] | computed | computed | computed | 0.25 | sepsis | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | qsofa | score-level risk difference; contributes to Delta_w record-weighted summary | 0.25 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 0.0 | 123 | 110 | 13 | 110 | 13 | 5.0 | 0.0 | 4.55 | 0.0 | 4.55 | [1.9, 10.46] |  |  | computed | too few distinct patients | too few distinct patients in a definition | 0.009838425851863702 | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.009838425851863702 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 1.0 | 866 | 738 | 128 | 720 | 120 | 70.0 | 8.0 | 9.49 | 6.25 | 3.24 | [7.58, 11.81] | [3.14, 12.07] | [-1.49, 7.96] | computed | computed | computed | 0.06926891697328427 | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.06926891697328427 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 2.0 | 2404 | 2103 | 301 | 2021 | 287 | 256.0 | 14.0 | 12.17 | 4.65 | 7.52 | [10.84, 13.64] | [2.77, 7.7] | [4.76, 10.28] | computed | computed | computed | 0.1922892337226044 | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.1922892337226044 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 3.0 | 3716 | 3244 | 472 | 3081 | 453 | 603.0 | 34.0 | 18.59 | 7.2 | 11.38 | [17.28, 19.97] | [5.19, 9.92] | [8.7, 14.07] | computed | computed | computed | 0.2972324428091505 | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2972324428091505 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 4.0 | 3769 | 3256 | 513 | 3122 | 497 | 816.0 | 77.0 | 25.06 | 15.01 | 10.05 | [23.6, 26.59] | [12.17, 18.37] | [6.62, 13.48] | computed | computed | computed | 0.30147176451767715 | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.30147176451767715 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 5.0 | 1624 | 1411 | 213 | 1367 | 209 | 509.0 | 60.0 | 36.07 | 28.17 | 7.9 | [33.6, 38.62] | [22.53, 34.59] | [1.38, 14.43] | computed | computed | computed | 0.12989921612541994 | pneumonia | row1_full_main | Full main ICU-indexed complete-score hospital cohort | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.12989921612541994 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 0.0 | 41 | 36 | 5 | 36 | 5 | 2.0 | 0.0 | 5.56 | 0.0 | 5.56 | [1.39, 19.67] |  |  | computed | too few distinct patients | too few distinct patients in a definition | 0.009651600753295669 | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.009651600753295669 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 1.0 | 303 | 252 | 51 | 250 | 50 | 18.0 | 3.0 | 7.14 | 5.88 | 1.26 | [4.54, 11.05] | [1.91, 16.73] | [-5.94, 8.47] | computed | computed | computed | 0.0713276836158192 | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.0713276836158192 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 2.0 | 830 | 719 | 111 | 703 | 106 | 74.0 | 3.0 | 10.29 | 2.7 | 7.59 | [8.27, 12.74] | [0.87, 8.08] | [3.84, 11.34] | computed | computed | computed | 0.19538606403013184 | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.19538606403013184 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 3.0 | 1209 | 1047 | 162 | 993 | 158 | 165.0 | 10.0 | 15.76 | 6.17 | 9.59 | [13.67, 18.1] | [3.35, 11.1] | [5.27, 13.9] | computed | computed | computed | 0.2846045197740113 | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2846045197740113 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 4.0 | 1257 | 1074 | 183 | 1032 | 182 | 224.0 | 25.0 | 20.86 | 13.66 | 7.2 | [18.53, 23.4] | [9.4, 19.44] | [1.65, 12.74] | computed | computed | computed | 0.2959039548022599 | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2959039548022599 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 5.0 | 608 | 520 | 88 | 501 | 88 | 173.0 | 25.0 | 33.27 | 28.41 | 4.86 | [29.33, 37.45] | [19.98, 38.68] | [-5.38, 15.1] | computed | computed | computed | 0.1431261770244821 | pneumonia | row2_linked_ed_episode | Linked ED episode, any ED diagnosis | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.1431261770244821 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) |
| 0.0 | 9 | 6 | 3 | 6 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |  | too few distinct patients | too few distinct patients | too few distinct patients in a definition | 0.006488824801730353 | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.006488824801730353 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 1.0 | 93 | 64 | 29 | 64 | 28 | 4.0 | 2.0 | 6.25 | 6.9 | -0.65 | [2.36, 15.51] | [1.72, 23.83] | [-11.63, 10.33] | computed | computed | computed | 0.06705118961788031 | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.06705118961788031 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 2.0 | 258 | 183 | 75 | 182 | 71 | 15.0 | 1.0 | 8.2 | 1.33 | 6.86 | [5.0, 13.16] | [0.19, 8.89] | [2.12, 11.61] | computed | computed | computed | 0.18601297764960345 | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.18601297764960345 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 3.0 | 380 | 292 | 88 | 278 | 86 | 36.0 | 5.0 | 12.33 | 5.68 | 6.65 | [9.0, 16.66] | [2.38, 12.95] | [0.51, 12.78] | computed | computed | computed | 0.273972602739726 | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.273972602739726 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 4.0 | 416 | 305 | 111 | 295 | 110 | 57.0 | 13.0 | 18.69 | 11.71 | 6.98 | [14.67, 23.51] | [6.92, 19.15] | [-0.5, 14.45] | computed | computed | computed | 0.2999279019466474 | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2999279019466474 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 5.0 | 231 | 176 | 55 | 170 | 55 | 68.0 | 18.0 | 38.64 | 32.73 | 5.91 | [31.77, 45.98] | [21.69, 46.08] | [-8.37, 20.19] | computed | computed | computed | 0.1665465032444124 | pneumonia | row3_ed_coded | Linked ED episode with MAIN-matching ED code | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.1665465032444124 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 0.0 | 9 | 6 | 3 | 6 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |  | too few distinct patients | too few distinct patients | too few distinct patients in a definition | 0.006488824801730353 | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.006488824801730353 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 1.0 | 93 | 64 | 29 | 64 | 28 | 4.0 | 2.0 | 6.25 | 6.9 | -0.65 | [2.36, 15.51] | [1.72, 23.83] | [-11.63, 10.33] | computed | computed | computed | 0.06705118961788031 | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.06705118961788031 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 2.0 | 258 | 183 | 75 | 182 | 71 | 15.0 | 1.0 | 8.2 | 1.33 | 6.86 | [5.0, 13.16] | [0.19, 8.89] | [2.12, 11.61] | computed | computed | computed | 0.18601297764960345 | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.18601297764960345 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 3.0 | 380 | 292 | 88 | 278 | 86 | 36.0 | 5.0 | 12.33 | 5.68 | 6.65 | [9.0, 16.66] | [2.38, 12.95] | [0.51, 12.78] | computed | computed | computed | 0.273972602739726 | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.273972602739726 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 4.0 | 416 | 305 | 111 | 295 | 110 | 57.0 | 13.0 | 18.69 | 11.71 | 6.98 | [14.67, 23.51] | [6.92, 19.15] | [-0.5, 14.45] | computed | computed | computed | 0.2999279019466474 | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.2999279019466474 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |
| 5.0 | 231 | 176 | 55 | 170 | 55 | 68.0 | 18.0 | 38.64 | 32.73 | 5.91 | [31.77, 45.98] | [21.69, 46.08] | [-8.37, 20.19] | computed | computed | computed | 0.1665465032444124 | pneumonia | row4_ed_code_ends_by_icu | MAIN-matching ED episode ends by index ICU | curb65 | score-level risk difference; contributes to Delta_w record-weighted summary | 0.1665465032444124 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) |

## Supplementary Table 38. ED linkage coverage

| disease | hospital31_main_disease_admissions | hospital31_admissions_with_ed_hadm_match_any_subject | hospital31_admissions_with_subject_verified_ed_link | hospital31_admissions_without_subject_verified_ed_link | ed_episode_rows_with_hadm_match_to_hospital_disease | ed_episode_rows_hadm_match_subject_verified | ed_episode_rows_hadm_match_subject_mismatch | subject_mismatch_hadm_count | verified_episode_rows_with_valid_ed_times | verified_episode_rows_with_invalid_or_missing_ed_times | verified_episode_rows_ed_start_before_index_icu | verified_episode_rows_ed_end_by_index_icu | verified_episode_rows_ed_end_by_index_icu_plus24h | main_admissions_with_nonmissing_hospital_to_icu_hours | main_admissions_icu_0_to_24h_after_hospital_admit | verified_ed_episode_starts_before_hospital_admittime | verified_ed_episode_ends_before_hospital_admittime | verified_ed_episode_starts_after_hospital_admittime | ed_release | hospital_release | compatibility_interpretation | diagnosis_rows | diagnosis_rows_without_matching_stay_id | diagnosis_rows_with_stay_subject_mismatch | diagnosis_rows_with_verified_stay_subject | unique_diagnosis_stays | edstays_rows_total | edstays_unique_stays | edstays_rows_with_hadm_id | edstays_rows_without_hadm_id | edstays_unique_hadm_ids_with_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sepsis | 14122 | 6431 | 6431 | 7691 | 6442 | 6442 | 0 | 0 | 6442 | 0 | 6442 | 6442 | 6442 | 14122 | 11480 | 6428 | 15 | 14 | MIMIC-IV-ED 2.2 | MIMIC-IV Hospital 3.1 (repaired main panel) | empirical HADM + subject linkage and chronology; no blanket release equivalence assumed | 899050 | 0 | 0 | 899050 | 423989 | 425087 | 425087 | 203016 | 222071 | 202441 |
| pneumonia | 17023 | 6924 | 6924 | 10099 | 6937 | 6937 | 0 | 0 | 6937 | 0 | 6937 | 6937 | 6937 | 17023 | 13577 | 6927 | 15 | 10 | MIMIC-IV-ED 2.2 | MIMIC-IV Hospital 3.1 (repaired main panel) | empirical HADM + subject linkage and chronology; no blanket release equivalence assumed | 899050 | 0 | 0 | 899050 | 423989 | 425087 | 425087 | 203016 | 222071 | 202441 |

## Supplementary Table 39. Patient-cluster bootstrap precision analyses

| source_key | database | disease | score_variant | primary_C_state | primary_C_interval_status | primary_C_refusal_reasons | primary_C_estimable | primary_C_point_pp_reported | primary_C_normal_if_ci_lower_pp | primary_C_normal_if_ci_upper_pp | primary_C_old60_percentile_ci_lower_pp | primary_C_old60_percentile_ci_upper_pp | primary_C_old60_usable_draws | primary_C_old60_requested_draws | audit_point_pp_unrounded | audit_numerical_se_pp | precision_bootstrap_status | precision_requested_draws | precision_usable_draws | precision_refused_no_support | precision_refused_lost_levels | precision_refused_few_events | precision_valid_draws | precision_C_percentile_ci_lower_pp | precision_C_percentile_ci_upper_pp | precision_C_percentile_ci_width_pp | normal_if_ci_exact_lower_pp | normal_if_ci_exact_upper_pp | normal_if_ci_exact_width_pp | precision_lower_endpoint_mc95_lower_pp | precision_lower_endpoint_mc95_upper_pp | precision_lower_endpoint_mc95_rank_low | precision_lower_endpoint_mc95_rank_high | precision_lower_endpoint_mc95_binomial_coverage | precision_upper_endpoint_mc95_lower_pp | precision_upper_endpoint_mc95_upper_pp | precision_upper_endpoint_mc95_rank_low | precision_upper_endpoint_mc95_rank_high | precision_upper_endpoint_mc95_binomial_coverage | direct_point_unrounded_pp | direct_numerical_se_pp | n_complete_case_records | n_patient_clusters_in_resampling_universe | n_patients_with_supported_records | n_records_on_common_support | n_support_levels | observed_support_levels | patients_without_support_cells_in_universe | bootstrap_batch_size | direct_estimator_agreement | direct_point_vs_primary_C_difference_pp | primary_C_normal_if_ci_width_pp | primary_C_old60_percentile_ci_width_pp | precision_minus_old60_lower_endpoint_pp | precision_minus_old60_upper_endpoint_pp | precision_minus_old60_width_pp | skipped_under_primary_C | skip_reason | diagnostic_run_status | peer_y_died_aliases_validated_equal | peer_standard_score_equals_curb65 | score_column |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eicu | eICU-CRD | sepsis | qsofa | estimable | computed |  | True | 0.127348052391 | -1.05 | 1.3 | -1.04 | 1.13 | 60 | 60 | 0.127348052391 | 0.6 | computed | 5000 | 5000 | 0 | 0 | 0 | 5000 | -1.08707718897 | 1.29303443131 | 2.38011162028 | -1.04936612791 | 1.30406223269 | 2.3534283606 | -1.12310737518 | -1.04689573981 | 104 | 148 | 0.953845864924 | 1.25331425159 | 1.34714274485 | 4853 | 4897 | 0.953845864924 | 0.127348052391 | 0.600364377703 | 16576 | 15217 | 15217 | 16576 | 4 | 0.0\|1.0\|2.0\|3.0 | 0 | 64 | True | 0 | 2.35 | 2.17 | -0.0470771889698 | 0.163034431311 | 0.210111620281 | False |  | computed |  |  |  |
| eicu | eICU-CRD | pneumonia | curb65 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 3.69821884273 |  |  |  |  | 0 | 60 | 3.69821884273 | 0.78 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| eicu | eICU-CRD | pancreatitis | bisap4 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 0.776968914416 |  |  |  |  | 0 | 60 | 0.776968914416 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| eicu | eICU-CRD | heart failure | qsofa | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 3.37524412732 |  |  |  |  | 0 | 60 | 3.37524412732 | 0.73 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| eicu | eICU-CRD | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 4.41172594123 |  |  |  |  | 0 | 60 | 4.41172594123 | 0.74 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iv | MIMIC-IV | sepsis | qsofa | estimable | computed |  | True | 11.2958132841 | 9.61 | 12.98 | 9.81 | 12.85 | 60 | 60 | 11.2958132841 | 0.86 | computed | 5000 | 5000 | 0 | 0 | 0 | 5000 | 9.62696759291 | 13.0443395918 | 3.41737199884 | 9.60906391159 | 12.9825626566 | 3.37349874498 | 9.54337777416 | 9.68465373461 | 104 | 148 | 0.953845864924 | 12.9639567282 | 13.1076048441 | 4853 | 4897 | 0.953845864924 | 11.2958132841 | 0.860586414536 | 10804 | 9398 | 9398 | 10804 | 4 | 0.0\|1.0\|2.0\|3.0 | 0 | 64 | True | 0 | 3.37 | 3.04 | -0.183032407087 | 0.194339591754 | 0.377371998841 | False |  | computed |  |  |  |
| mimic_iv | MIMIC-IV | pneumonia | curb65 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 9.15623097228 |  |  |  |  | 0 | 60 | 9.15623097228 | 0.86 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iv | MIMIC-IV | pancreatitis | bisap4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 6.43043238419 |  |  |  |  | 0 | 60 | 6.43043238419 | 2.04 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iv | MIMIC-IV | heart failure | qsofa | estimable | computed |  | True | -0.0241720881185 | -1.37 | 1.32 | -1.36 | 1.31 | 60 | 60 | -0.0241720881185 | 0.69 | computed | 5000 | 5000 | 0 | 0 | 0 | 5000 | -1.3359355287 | 1.32353162323 | 2.65946715192 | -1.3674260721 | 1.31908189587 | 2.68650796797 | -1.38479473782 | -1.27625885308 | 104 | 148 | 0.953845864924 | 1.26388367656 | 1.37653405935 | 4853 | 4897 | 0.953845864924 | -0.0241720881185 | 0.685333665298 | 19274 | 14338 | 14338 | 19274 | 4 | 0.0\|1.0\|2.0\|3.0 | 0 | 64 | True | -9.02056207508e-17 | 2.69 | 2.67 | 0.024064471302 | 0.0135316232264 | -0.0105328480755 | False |  | computed |  |  |  |
| mimic_iv | MIMIC-IV | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 6.77529821325 |  |  |  |  | 0 | 60 | 6.77529821325 | 1.14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iii | MIMIC-III | sepsis | qsofa | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 8.60960385085 |  |  |  |  | 0 | 60 | 8.60960385085 | 1.22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iii | MIMIC-III | pneumonia | curb65 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 5.91558768112 |  |  |  |  | 0 | 60 | 5.91558768112 | 0.98 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iii | MIMIC-III | pancreatitis | bisap4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 4.41252533218 |  |  |  |  | 0 | 60 | 4.41252533218 | 2.45 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iii | MIMIC-III | heart failure | qsofa | interval withheld: degenerate_outcome_cell | not computed (degenerate_outcome_cell) | degenerate_outcome_cell | False | 1.23826459066 |  |  |  |  | 0 | 60 | 1.23826459066 | 0.97 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| mimic_iii | MIMIC-III | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 2.726591891 |  |  |  |  | 0 | 60 | 2.726591891 | 2.13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| zigong | Zigong | sepsis | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 4.79636239673 |  |  |  |  | 0 | 60 | 4.79636239673 | 3.35 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| zigong | Zigong | pneumonia | curb65 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | 6.32718232638 |  |  |  |  | 0 | 60 | 6.32718232638 | 2.52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| zigong | Zigong | pancreatitis | bisap4 | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | -5.35714285714 |  |  |  |  | 0 | 60 | -5.35714285714 | 12.28 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| zigong | Zigong | heart failure | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;too_few_records_per_score_level;degenerate_outcome_cell | False | -9.36084845212 |  |  |  |  | 0 | 60 | -9.36084845212 | 13.77 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, too_few_records_per_score_level, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| zigong | Zigong | COPD | qsofa | interval withheld: too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_records_per_score_definition_cell;too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 5.4583772392 |  |  |  |  | 0 | 60 | 5.4583772392 | 2.01 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_records_per_score_definition_cell, too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C |  |  |  |
| peer | PEER-adapted-eICU | pneumonia | adapted CURB-65 (`score`, validated equal to `curb65`) | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | too_few_distinct_patients_per_score_definition_cell;degenerate_outcome_cell | False | 1.64 |  |  |  |  | 0 | 60 | 1.6403314949 | 1.08835633618 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | skipped_under_primary_C | True | True |  |
| amsterdam | AmsterdamUMCdb 1.0.2 | sepsis | GCS ≤13 | interval withheld: too_few_distinct_patients_per_score_definition_cell | not computed (too_few_distinct_patients_per_score_definition_cell) | too_few_distinct_patients_per_score_definition_cell | False | 18.91 |  |  |  |  | 0 | 60 | 18.9096497186 | 7.66494427928 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | True | not computed (too_few_distinct_patients_per_score_definition_cell) | skipped_under_primary_C |  |  | qsofa_main |
| amsterdam | AmsterdamUMCdb 1.0.2 | sepsis | GCS <15 | estimable | computed |  | True | 18.43 | 3.2 | 33.67 | -1.51 | 33.24 | 60 | 60 | 18.4326477298 | 7.774210597 | computed | 5000 | 4994 | 0 | 0 | 6 | 4994 | 3.44253950531 | 34.1478942854 | 30.7053547801 | 3.19519495965 | 33.6701004999 | 30.4749055403 | 2.83212090178 | 4.03522534086 | 104 | 148 | 0.953864009765 | 33.7039403965 | 34.7870879121 | 4847 | 4891 | 0.953864009765 | 18.4326477298 | 7.774210597 | 254 | 244 | 244 | 254 | 2 | 2.0\|3.0 | 0 | 64 | True | 0 | 30.47 | 34.75 | 4.95253950531 | 0.907894285379 | -4.04464521993 | False |  | computed |  |  | qsofa_gcs_lt15 |

## Supplementary Table 40. Conditional-design θ_D intervals in clinical applications

| database | disease | instrument | conditional_estimand | interval_method | confidence_level | n_records | n_patients | n_supported_records | n_supported_patients | n_common_support_levels | state | conditional_interval_emitted | point_pp | lower_pp | upper_pp | halfwidth_pp | actual_width_pp | full_range_interval | halfwidth_ge_one | sum_squared_cluster_ranges | direct_contrast_point_difference_abs | patient_cluster_independence_assumed_not_verified | does_not_modify_or_replace_primary_C | source_panel_path | interpretation_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eICU-CRD | sepsis | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 16576 | 15217 | 16576 | 15217 | 4 | conditional interval computed | True | 0.12734805239141347 | -2.258445598650299 | 2.513141703433126 | 2.3857936510417126 | 4.771587302083425 | False | False | 0.00030860381403914204 | 2.0816681711721685e-17 | True | True | C:\Users\aaa12\Documents\Codex\2026-11-08\codex-journal-of-clinical-epidemiology-8\work\v2\eicu\eicu_disease_panel.csv.gz |  |
| eICU-CRD | pneumonia | curb65 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 11481 | 10724 | 11481 | 10724 | 6 | conditional interval computed | True | 3.6982188427327505 | 0.47035884170692555 | 6.926078843758576 | 3.227860001025825 | 6.455720002051652 | False | False | 0.0005648913343916839 | 1.3877787807814457e-17 | True | True | C:\Users\aaa12\Documents\Codex\2026-11-08\codex-journal-of-clinical-epidemiology-8\work\v2\eicu\eicu_disease_panel.csv.gz |  |
| eICU-CRD | pancreatitis | bisap4 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 351 | 343 | 351 | 343 | 4 | conditional interval computed | True | 0.7769689144163192 | -14.60960624135596 | 16.1635440701886 | 15.386575155772281 | 30.773150311544562 | False | False | 0.012835697016892356 | 8.673617379884035e-18 | True | True | C:\Users\aaa12\Documents\Codex\2026-11-08\codex-journal-of-clinical-epidemiology-8\work\v2\eicu\eicu_disease_panel.csv.gz |  |
| eICU-CRD | heart failure | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 9540 | 8611 | 9540 | 8611 | 4 | conditional interval computed | True | 3.375244127321511 | -0.17261381527947858 | 6.923102069922502 | 3.5478579426009897 | 7.095715885201981 | False | False | 0.0006824455034354262 | 0.0 | True | True | C:\Users\aaa12\Documents\Codex\2026-11-08\codex-journal-of-clinical-epidemiology-8\work\v2\eicu\eicu_disease_panel.csv.gz |  |
| eICU-CRD | COPD | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 7703 | 6711 | 7703 | 6711 | 4 | conditional interval computed | True | 4.411725941225042 | -0.08918722926425302 | 8.912639111714334 | 4.500913170489294 | 9.001826340978589 | False | False | 0.0010983400038020483 | 2.0816681711721685e-17 | True | True | C:\Users\aaa12\Documents\Codex\2026-11-08\codex-journal-of-clinical-epidemiology-8\work\v2\eicu\eicu_disease_panel.csv.gz |  |
| MIMIC-IV | sepsis | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 10804 | 9398 | 10804 | 9398 | 4 | conditional interval computed | True | 11.295813284083819 | 8.114896470958435 | 14.4767300972092 | 3.1809168131253833 | 6.361833626250765 | False | False | 0.000548580234072958 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic\mimic_iv_score_panel.csv.gz |  |
| MIMIC-IV | pneumonia | curb65 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 12502 | 10976 | 12502 | 10976 | 6 | conditional interval computed | True | 9.156230972275353 | 4.90010107293029 | 13.412360871620413 | 4.256129899345062 | 8.512259798690122 | False | False | 0.0009821216412966315 | 0.0 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic\mimic_iv_score_panel.csv.gz |  |
| MIMIC-IV | pancreatitis | bisap4 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 1067 | 988 | 1067 | 988 | 5 | conditional interval computed | True | 6.4304323841912465 | -3.362347634048864 | 16.223212402431358 | 9.79278001824011 | 19.58556003648022 | False | False | 0.005199331757978385 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic\mimic_iv_score_panel.csv.gz |  |
| MIMIC-IV | heart failure | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 19274 | 14338 | 19274 | 14338 | 4 | conditional interval computed | True | -0.024172088118481865 | -3.833518359151754 | 3.7851741829147896 | 3.809346271033272 | 7.618692542066544 | False | False | 0.0007867494285535359 | 1.734723475976807e-18 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic\mimic_iv_score_panel.csv.gz |  |
| MIMIC-IV | COPD | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 10059 | 7825 | 10059 | 7825 | 4 | conditional interval computed | True | 6.7752982132484405 | -2.188588064844825 | 15.739184491341707 | 8.963886278093264 | 17.927772556186532 | False | False | 0.004356404605034132 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic\mimic_iv_score_panel.csv.gz |  |
| MIMIC-III | sepsis | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 5588 | 4957 | 5588 | 4957 | 4 | conditional interval computed | True | 8.609603850854949 | 4.414843559246311 | 12.804364142463587 | 4.194760291608638 | 8.389520583217275 | False | False | 0.0009540031938117709 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic3\mimic_iii_score_panel.csv.gz |  |
| MIMIC-III | pneumonia | curb65 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 9148 | 7974 | 9148 | 7974 | 6 | conditional interval computed | True | 5.9155876811225525 | 1.4505732854617024 | 10.380602076783402 | 4.465014395660851 | 8.930028791321702 | False | False | 0.001080889402944576 | 2.0816681711721685e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic3\mimic_iii_score_panel.csv.gz |  |
| MIMIC-III | pancreatitis | bisap4 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 815 | 779 | 815 | 779 | 5 | conditional interval computed | True | 4.4125253321815965 | -5.9723530183933855 | 14.797403682756578 | 10.384878350574981 | 20.769756701149962 | False | False | 0.005847070889560707 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic3\mimic_iii_score_panel.csv.gz |  |
| MIMIC-III | heart failure | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 12419 | 9490 | 12419 | 9490 | 4 | conditional interval computed | True | 1.2382645906578889 | -3.6733115347346676 | 6.149840716050446 | 4.911576125392557 | 9.823152250785114 | False | False | 0.0013079082868171744 | 2.0816681711721685e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic3\mimic_iii_score_panel.csv.gz |  |
| MIMIC-III | COPD | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 5757 | 4500 | 5757 | 4500 | 4 | conditional interval computed | True | 2.726591891001209 | -9.047014016520617 | 14.500197798523034 | 11.773605907521825 | 23.54721181504365 | False | False | 0.007515441899899579 | 2.0816681711721685e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\mimic3\mimic_iii_score_panel.csv.gz |  |
| Zigong | sepsis | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 137 | 137 | 137 | 137 | 4 | conditional interval computed | True | 4.7963623967273605 | -20.30367592871149 | 29.89640072216621 | 25.10003832543885 | 50.2000766508777 | False | False | 0.0341573603461557 | 0.0 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\zigong\zigong_admission_panel.csv.gz |  |
| Zigong | pneumonia | curb65 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 430 | 430 | 430 | 430 | 6 | conditional interval computed | True | 6.327182326380032 | -20.224755862543226 | 32.87912051530329 | 26.55193818892326 | 53.10387637784652 | False | False | 0.03822328326842779 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\zigong\zigong_admission_panel.csv.gz |  |
| Zigong | pancreatitis | bisap4 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 28 | 28 | 28 | 28 | 4 | conditional interval computed | True | -5.357142857142858 | -58.96041577326281 | 48.24613005897709 | 53.60327291611995 | 107.2065458322399 | False | False | 0.15578231292517003 | 1.3877787807814457e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\zigong\zigong_admission_panel.csv.gz |  |
| Zigong | heart failure | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 147 | 147 | 147 | 147 | 4 | conditional interval computed | True | -9.360848452121717 | -56.07988440022349 | 37.35818749598006 | 46.71903594810178 | 93.43807189620354 | False | False | 0.11833774169474998 | 2.7755575615628914e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\zigong\zigong_admission_panel.csv.gz |  |
| Zigong | COPD | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 163 | 163 | 146 | 146 | 3 | conditional interval computed | True | 5.458377239199157 | -28.731949041197947 | 39.64870351959626 | 34.1903262803971 | 68.3806525607942 | False | False | 0.0633785096911387 | 0.0 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\zigong\zigong_admission_panel.csv.gz |  |
| AmsterdamUMCdb | sepsis | qsofa | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 254 | 244 | 253 | 243 | 2 | conditional interval computed | True | 18.909649718644353 | -3.3956117863334105 | 41.21491122362212 | 22.305261504977764 | 44.61052300995553 | False | False | 0.02697429921439098 | 2.7755575615628914e-17 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\amsterdam\private\qsofa_sepsis_icu_dictionary-specified units_outcome.csv.gz |  |
| PEER-adapted-eICU | pneumonia | curb65 | theta_D: conditional-design mean contrast on actual observed common support | patient-cluster conditional Hoeffding interval | 0.95 | 3565 | 3365 | 3565 | 3365 | 6 | conditional interval computed | True | 1.640331494904508 | -3.803212262968879 | 7.083875252777895 | 5.443543757873387 | 10.887087515746774 | False | False | 0.0016065674691991215 | 0.0 | True | True | F:\分析专用\meta_measurement_20261103\work\paperB\published_application\adapted_peer_population.csv.gz | Adapted published PEER population; original PEER model results are not reproduced. |

## Supplementary Table 41. Conditional-design interval simulation results

| design | family | contrast_pattern | requested_bad_score_record_mass | actual_bad_score_record_mass | n_replicates | n_conditional_truth_defined_datasets | conditional_estimand_defined_rate | conditional_estimand_defined_rate_mcse | n_intervals_emitted | n_supported_datasets_withheld | interval_output_rate_all_datasets | interval_output_rate_all_datasets_mcse | interval_output_rate_given_conditional_estimand | interval_output_rate_given_conditional_estimand_mcse | n_conditional_covered | conditional_coverage | conditional_coverage_mcse | median_width_pp | mean_width_pp | width_p05_pp | width_p95_pp | n_full_range_intervals | full_range_rate_among_emitted | full_range_rate_mcse | n_halfwidth_ge_one | halfwidth_ge_one_rate_among_emitted | halfwidth_ge_one_rate_mcse | n_population_truth_defined_datasets | population_target_support_match_rate | n_population_target_support_lost | population_target_support_loss_rate | population_target_support_loss_rate_mcse | n_population_truth_interval_diagnostics | population_truth_covered_diagnostic_count | population_truth_coverage_diagnostic_not_conditional_coverage | population_truth_coverage_diagnostic_mcse | mean_conditional_minus_population_truth_pp_among_emitted | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 999 | 0.999 | 0.0009994998749374613 | 17.20680748916945 | 17.213136555080535 | 17.184705875395405 | 17.263433947453056 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 999 | 0.999 | 0.0009994998749374613 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| null_heterogeneous_iid | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 998 | 0.998 | 0.0014127986409959495 | 15.703391712836396 | 15.707960135108875 | 15.686720446158587 | 15.746211849232418 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 999 | 0.999 | 0.0009994998749374613 | -0.006916666666666657 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| heterogeneous_random_weights | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 998 | 0.998 | 0.0014127986409959495 | 21.308544748485282 | 21.363961984293187 | 20.23974957347856 | 22.687183367933336 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 999 | 0.999 | 0.0009994998749374613 | 0.008991666666666903 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| repeated_admissions_cross_group | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 18.111880889214092 | 18.112536474510453 | 18.108815273394043 | 18.118462713493034 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | -0.0024370370370363254 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| unequal_cluster_sizes | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 26.089278316899915 | 26.10032717218768 | 25.51546891062273 | 26.741635125778675 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | -0.005534681073175798 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| near_boundary_risks | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 12.815580475593318 | 12.818293158685881 | 12.806568542932395 | 12.838158680573994 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.003943055555555534 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| partial_structural_support | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 997 | 0.997 | 0.0017294507798720387 | 24.861934841992074 | 24.880656887785356 | 24.135454872280498 | 25.69181290156317 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 997 | 0.997 | 0.0017294507798720387 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| rare_common_support_holdout | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 19.237750117206055 | 19.244170843235892 | 19.21098881739818 | 19.29649847386958 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 0.642 | 358 | 0.358 | 0.01516034300403523 | 1000 | 1000 | 1.0 | 0.0 | -9.853229343548264e-17 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| few_large_clusters | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 135.9383654021983 | 135.9698156808393 | 135.83391821876614 | 136.24494054905514 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0039375000000006575 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| no_common_support | original_frozen_dgp |  |  |  | 1000 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 |  |  | 0 |  |  |  |  |  |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  | 0 | 0 |  |  |  | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| high_icc_unbalanced_holdout | original_frozen_dgp |  |  |  | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 30.422664880629227 | 30.439165403413732 | 29.620494243784062 | 31.300975094296746 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.003581248849043031 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.001_null | fixed_small_bad_mass | null | 0.001 | 0.001 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.178776333869504 | 17.178776333869507 | 17.178776333869504 | 17.178776333869504 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.001_positive | fixed_small_bad_mass | positive | 0.001 | 0.001 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.178776333869507 | 17.178776333869507 | 17.178776333869507 | 17.178776333869507 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.001_cancelling | fixed_small_bad_mass | cancelling | 0.001 | 0.001 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.178776333869507 | 17.178776333869507 | 17.178776333869507 | 17.178776333869507 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.005_null | fixed_small_bad_mass | null | 0.005 | 0.005 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.19036278951808 | 17.190362789518076 | 17.19036278951808 | 17.19036278951808 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.005_positive | fixed_small_bad_mass | positive | 0.005 | 0.005 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.190362789518076 | 17.190362789518076 | 17.190362789518076 | 17.190362789518083 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.005_cancelling | fixed_small_bad_mass | cancelling | 0.005 | 0.005 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.190362789518076 | 17.190362789518076 | 17.190362789518076 | 17.190362789518083 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.02_null | fixed_small_bad_mass | null | 0.02 | 0.02 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.840779461746692 | 17.8407794617467 | 17.840779461746692 | 17.840779461746692 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.02_positive | fixed_small_bad_mass | positive | 0.02 | 0.02 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.840779461746692 | 17.8407794617467 | 17.840779461746692 | 17.840779461746692 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.02_cancelling | fixed_small_bad_mass | cancelling | 0.02 | 0.02 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 17.840779461746692 | 17.8407794617467 | 17.840779461746692 | 17.840779461746692 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.1_null | fixed_small_bad_mass | null | 0.1 | 0.1 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 31.669602012986356 | 31.669602012986346 | 31.669602012986356 | 31.669602012986356 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.1_positive | fixed_small_bad_mass | positive | 0.1 | 0.1 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 31.669602012986356 | 31.669602012986346 | 31.669602012986356 | 31.669602012986356 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.1_cancelling | fixed_small_bad_mass | cancelling | 0.1 | 0.1 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 31.669602012986356 | 31.669602012986346 | 31.669602012986356 | 31.669602012986356 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.5_null | fixed_small_bad_mass | null | 0.5 | 0.5 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 192.35272730565455 | 174.8452288245764 | 144.9726599491236 | 192.35272730565455 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.5_positive | fixed_small_bad_mass | positive | 0.5 | 0.5 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 187.21740469386836 | 168.46618366012373 | 137.76795524441889 | 189.9701574466211 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |
| fixed_badmass_0.5_cancelling | fixed_small_bad_mass | cancelling | 0.5 | 0.5 | 1000 | 1000 | 1.0 | 0.0 | 1000 | 0 | 1.0 | 0.0 | 1.0 | 0.0 | 1000 | 1.0 | 0.0 | 148.85404133050503 | 169.16853909828166 | 144.875062351526 | 192.35272730565455 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 1000 | 1000 | 1.0 | 0.0 | 0.0 | Population-truth comparisons are target-mismatch diagnostics, not coverage claims for this conditional interval. |

## Supplementary Table 42. Numerical design inventory for δ_s and Δ_w weighted-summary validation

| Design | Patients | Records per patient: value/probability | Latent Gaussian dependence parameter | Score values | P(group0,score) | P(group1,score) | Primary risk vector | Never-primary risk vector | Prespecified support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | 1000 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.1, 0.2, 0.3, 0.4] | [0, 1, 2, 3] |
| null_heterogeneous_iid | 1200 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.1, 0.4, 0.3] | [0, 1, 2, 3] |
| heterogeneous_random_weights | 1200 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0.32, 0.1, 0.05, 0.03] | [0.05, 0.1, 0.12, 0.23] | [0.1, 0.4, 0.15, 0.35] | [0.3, 0.2, 0.25, 0.1] | [0, 1, 2, 3] |
| repeated_admissions_cross_group | 900 | [[3, 1.0]] | 0.3 | [0, 1, 2, 3] | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.25, 0.35, 0.5] | [0, 1, 2, 3] |
| unequal_cluster_sizes | 800 | [[1, 0.55], [2, 0.25], [4, 0.15], [8, 0.05]] | 0.35 | [0, 1, 2, 3] | [0.2, 0.15, 0.1, 0.05] | [0.05, 0.1, 0.15, 0.2] | [0.08, 0.2, 0.35, 0.5] | [0.18, 0.3, 0.25, 0.6] | [0, 1, 2, 3] |
| near_boundary_risks | 1800 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.005, 0.02, 0.65, 0.85] | [0.01, 0.025, 0.7, 0.8] | [0, 1, 2, 3] |
| partial_structural_support | 1000 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3, 4, 5] | [0.1, 0.1, 0.15, 0.15, 0.0, 0.0] | [0.0, 0.0, 0.1, 0.1, 0.15, 0.15] | [0.1, 0.15, 0.2, 0.25, 0.3, 0.35] | [0.08, 0.1, 0.4, 0.45, 0.3, 0.5] | [2, 3] |
| rare_common_support_holdout | 800 | [[1, 1.0]] | 0.0 | [0, 1, 2] | [0.249, 0.249, 0.002] | [0.249, 0.249, 0.002] | [0.1, 0.2, 0.3] | [0.15, 0.25, 0.35] | [0, 1, 2] |
| few_large_clusters | 16 | [[10, 1.0]] | 0.4 | [0, 1, 2, 3] | [0.125, 0.125, 0.125, 0.125] | [0.125, 0.125, 0.125, 0.125] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.25, 0.35, 0.5] | [0, 1, 2, 3] |
| no_common_support | 1000 | [[1, 1.0]] | 0.0 | [0, 1, 2, 3] | [0.25, 0.25, 0.0, 0.0] | [0.0, 0.0, 0.25, 0.25] | [0.1, 0.2, 0.3, 0.4] | [0.2, 0.25, 0.35, 0.5] | [] |
| high_icc_unbalanced_holdout | 800 | [[1, 0.7], [10, 0.3]] | 0.6 | [0, 1, 2, 3] | [0.25, 0.15, 0.07, 0.03] | [0.03, 0.07, 0.15, 0.25] | [0.15, 0.3, 0.45, 0.6] | [0.2, 0.2, 0.5, 0.55] | [0, 1, 2, 3] |

## Supplementary Table 43. Full simulation simulation policy results

| Design | Policy | Weight mode | Replicates | Point output (%) | Interval output (%) | Target support match (%) | Off-target interval output (%) | On-target population coverage (%) | On-target denominator | Population coverage MCSE (pp) | Valid-target coverage among emitted (%) | Emitted interval denominator | Valid-target coverage MCSE (pp) | Observed-weight coverage (%) | Observed-weight denominator | Observed-weight MCSE (pp) | Unconditional noncoverage events | Unconditional noncoverage (%) | Unconditional noncoverage MCSE (pp) | Mean point bias on target | Refusal counts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.4 | 1000 | 0.727 | 94.39999999999999 | 1000 | 0.7270763371201131 | 94.4 | 1000 | 0.727 | 56 | 5.6 | 0.727 | -0.000989 | {} |
| null_balanced_iid | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.4 | 1000 | 0.727 | 94.39999999999999 | 1000 | 0.7270763371201131 | 94.4 | 1000 | 0.727 | 56 | 5.6 | 0.727 | -0.000989 | {} |
| null_balanced_iid | C | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.4 | 1000 | 0.727 | 94.39999999999999 | 1000 | 0.7270763371201131 | 94.4 | 1000 | 0.727 | 56 | 5.6 | 0.727 | -0.000989 | {} |
| null_balanced_iid | D | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.4 | 1000 | 0.727 | 94.39999999999999 | 1000 | 0.7270763371201131 | 94.4 | 1000 | 0.727 | 56 | 5.6 | 0.727 | -0.000989 | {} |
| null_balanced_iid | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.4 | 1000 | 0.727 | 94.39999999999999 | 1000 | 0.7270763371201131 | 94.4 | 1000 | 0.727 | 56 | 5.6 | 0.727 | -0.000989 | {} |
| null_balanced_iid | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.1 | 1000 | 0.745 | 94.1 | 1000 | 0.7451107300260817 |  | 0 |  | 59 | 5.9 | 0.745 | -0.001 | {} |
| null_heterogeneous_iid | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.9 | 1000 | 0.757 | 93.89999999999999 | 1000 | 0.7568289106528638 | 94.3 | 1000 | 0.733 | 61 | 6.1 | 0.757 | -0.000792 | {} |
| null_heterogeneous_iid | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.9 | 1000 | 0.757 | 93.89999999999999 | 1000 | 0.7568289106528638 | 94.3 | 1000 | 0.733 | 61 | 6.1 | 0.757 | -0.000792 | {} |
| null_heterogeneous_iid | C | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.9 | 1000 | 0.757 | 93.89999999999999 | 1000 | 0.7568289106528638 | 94.3 | 1000 | 0.733 | 61 | 6.1 | 0.757 | -0.000792 | {} |
| null_heterogeneous_iid | D | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.9 | 1000 | 0.757 | 93.89999999999999 | 1000 | 0.7568289106528638 | 94.3 | 1000 | 0.733 | 61 | 6.1 | 0.757 | -0.000792 | {} |
| null_heterogeneous_iid | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.5 | 1000 | 0.78 | 93.5 | 1000 | 0.7795832219846701 | 94.0 | 1000 | 0.751 | 65 | 6.5 | 0.78 | -0.000792 | {} |
| null_heterogeneous_iid | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.8 | 1000 | 0.763 | 93.8 | 1000 | 0.762600813007697 |  | 0 |  | 62 | 6.2 | 0.763 | -0.000696 | {} |
| heterogeneous_random_weights | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.5 | 1000 | 0.721 | 94.5 | 1000 | 0.7209368904418753 | 94.4 | 1000 | 0.727 | 55 | 5.5 | 0.721 | 0.000261 | {} |
| heterogeneous_random_weights | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.5 | 1000 | 0.721 | 94.5 | 1000 | 0.7209368904418753 | 94.4 | 1000 | 0.727 | 55 | 5.5 | 0.721 | 0.000261 | {} |
| heterogeneous_random_weights | C | estimated_pooled_record | 1,000 | 100.0 | 99.7 | 100.0 | 0.0 | 94.48 | 997 | 0.723 | 94.48345035105315 | 997 | 0.7230428880219668 | 94.38 | 997 | 0.729 | 55 | 5.5 | 0.721 | 0.000261 | {"too_few_distinct_patients_per_score_definition_cell": 3} |
| heterogeneous_random_weights | D | estimated_pooled_record | 1,000 | 100.0 | 99.7 | 100.0 | 0.0 | 94.48 | 997 | 0.723 | 94.48345035105315 | 997 | 0.7230428880219668 | 94.38 | 997 | 0.729 | 55 | 5.5 | 0.721 | 0.000261 | {"too_few_distinct_patients_per_score_definition_cell": 3} |
| heterogeneous_random_weights | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.7 | 1000 | 0.768 | 93.7 | 1000 | 0.7683163410991593 | 93.9 | 1000 | 0.757 | 63 | 6.3 | 0.768 | 0.000261 | {} |
| heterogeneous_random_weights | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.8 | 1000 | 0.763 | 93.8 | 1000 | 0.762600813007697 |  | 0 |  | 62 | 6.2 | 0.763 | 0.000552 | {} |
| repeated_admissions_cross_group | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.1 | 1000 | 0.745 | 94.1 | 1000 | 0.7451107300260817 | 94.2 | 1000 | 0.739 | 59 | 5.9 | 0.745 | 0.000263 | {} |
| repeated_admissions_cross_group | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.1 | 1000 | 0.745 | 94.1 | 1000 | 0.7451107300260817 | 94.2 | 1000 | 0.739 | 59 | 5.9 | 0.745 | 0.000263 | {} |
| repeated_admissions_cross_group | C | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.1 | 1000 | 0.745 | 94.1 | 1000 | 0.7451107300260817 | 94.2 | 1000 | 0.739 | 59 | 5.9 | 0.745 | 0.000263 | {} |
| repeated_admissions_cross_group | D | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.1 | 1000 | 0.745 | 94.1 | 1000 | 0.7451107300260817 | 94.2 | 1000 | 0.739 | 59 | 5.9 | 0.745 | 0.000263 | {} |
| repeated_admissions_cross_group | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.1 | 1000 | 0.745 | 94.1 | 1000 | 0.7451107300260817 | 94.1 | 1000 | 0.745 | 59 | 5.9 | 0.745 | 0.000263 | {} |
| repeated_admissions_cross_group | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.0 | 1000 | 0.751 | 94.0 | 1000 | 0.7509993342207438 |  | 0 |  | 60 | 6.0 | 0.751 | 0.000306 | {} |
| unequal_cluster_sizes | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 95.8 | 1000 | 0.634 | 48 | 4.8 | 0.676 | 0.000595 | {} |
| unequal_cluster_sizes | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 95.8 | 1000 | 0.634 | 48 | 4.8 | 0.676 | 0.000595 | {} |
| unequal_cluster_sizes | C | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 95.8 | 1000 | 0.634 | 48 | 4.8 | 0.676 | 0.000595 | {} |
| unequal_cluster_sizes | D | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 95.8 | 1000 | 0.634 | 48 | 4.8 | 0.676 | 0.000595 | {} |
| unequal_cluster_sizes | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 95.6 | 1000 | 0.649 | 48 | 4.8 | 0.676 | 0.000595 | {} |
| unequal_cluster_sizes | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.5 | 1000 | 0.656 | 95.5 | 1000 | 0.655553201502365 |  | 0 |  | 45 | 4.5 | 0.656 | 0.000557 | {} |
| near_boundary_risks | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.7 | 1000 | 0.641 | 95.7 | 1000 | 0.6414904519944161 | 95.6 | 1000 | 0.649 | 43 | 4.3 | 0.641 | -0.00024 | {} |
| near_boundary_risks | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.7 | 1000 | 0.641 | 95.7 | 1000 | 0.6414904519944161 | 95.6 | 1000 | 0.649 | 43 | 4.3 | 0.641 | -0.00024 | {} |
| near_boundary_risks | C | estimated_pooled_record | 1,000 | 100.0 | 61.7 | 100.0 | 0.0 | 95.95 | 617 | 0.794 | 95.9481361426256 | 617 | 0.793785409009966 | 95.79 | 617 | 0.809 | 25 | 2.5 | 0.494 | -0.00024 | {"degenerate_outcome_cell": 383} |
| near_boundary_risks | D | estimated_pooled_record | 1,000 | 100.0 | 61.7 | 100.0 | 0.0 | 95.95 | 617 | 0.794 | 95.9481361426256 | 617 | 0.793785409009966 | 95.79 | 617 | 0.809 | 25 | 2.5 | 0.494 | -0.00024 | {"degenerate_outcome_cell": 383} |
| near_boundary_risks | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.7 | 1000 | 0.641 | 95.7 | 1000 | 0.6414904519944161 | 95.5 | 1000 | 0.656 | 43 | 4.3 | 0.641 | -0.00024 | {} |
| near_boundary_risks | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.3 | 1000 | 0.669 | 95.3 | 1000 | 0.669260786241059 |  | 0 |  | 47 | 4.7 | 0.669 | -0.000189 | {} |
| partial_structural_support | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.3 | 1000 | 0.733 | 94.3 | 1000 | 0.7331507348424336 | 94.3 | 1000 | 0.733 | 57 | 5.7 | 0.733 | -0.000967 | {} |
| partial_structural_support | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.3 | 1000 | 0.733 | 94.3 | 1000 | 0.7331507348424336 | 94.3 | 1000 | 0.733 | 57 | 5.7 | 0.733 | -0.000967 | {} |
| partial_structural_support | C | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.3 | 1000 | 0.733 | 94.3 | 1000 | 0.7331507348424336 | 94.3 | 1000 | 0.733 | 57 | 5.7 | 0.733 | -0.000967 | {} |
| partial_structural_support | D | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.3 | 1000 | 0.733 | 94.3 | 1000 | 0.7331507348424336 | 94.3 | 1000 | 0.733 | 57 | 5.7 | 0.733 | -0.000967 | {} |
| partial_structural_support | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.3 | 1000 | 0.733 | 94.3 | 1000 | 0.7331507348424336 | 94.3 | 1000 | 0.733 | 57 | 5.7 | 0.733 | -0.000967 | {} |
| partial_structural_support | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.5 | 1000 | 0.721 | 94.5 | 1000 | 0.7209368904418753 |  | 0 |  | 55 | 5.5 | 0.721 | -0.000951 | {} |
| rare_common_support_holdout | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 69.1 | 30.9 | 95.37 | 691 | 0.799 | 65.9 | 1000 | 1.4990630407024248 | 95.37 | 691 | 0.799 | 341 | 34.1 | 1.499 | -0.000224 | {} |
| rare_common_support_holdout | B | estimated_pooled_record | 1,000 | 100.0 | 0.0 | 69.1 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 | 0.0 | 0.0 | -0.000224 | {"below_10_records_per_score_definition_cell": 1000} |
| rare_common_support_holdout | C | estimated_pooled_record | 1,000 | 100.0 | 0.0 | 69.1 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 | 0.0 | 0.0 | -0.000224 | {"degenerate_outcome_cell": 617, "target_support_lost": 309, "too_few_distinct_patients_per_score_definition_cell": 691, "too_few_records_per_score_definition_cell": 691, "too_few_records_per_score_level": 691} |
| rare_common_support_holdout | D | estimated_pooled_record | 1,000 | 100.0 | 30.9 | 69.1 | 30.9 |  | 0 |  | 0.0 | 309 | 0.0 |  | 0 |  | 309 | 30.9 | 1.461 | -0.000224 | {"degenerate_outcome_cell": 617, "too_few_distinct_patients_per_score_definition_cell": 691} |
| rare_common_support_holdout | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 69.1 | 30.9 | 95.37 | 691 | 0.799 | 65.9 | 1000 | 1.4990630407024248 | 95.37 | 691 | 0.799 | 341 | 34.1 | 1.499 | -0.000224 | {} |
| rare_common_support_holdout | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 69.1 | 69.1 | 69.1 | 0.0 | 95.37 | 691 | 0.799 | 95.36903039073806 | 691 | 0.799467153773554 |  | 0 |  | 32 | 3.2 | 0.557 | -0.000162 | {"target_support_lost": 309} |
| few_large_clusters | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.3 | 1000 | 0.791 | 93.30000000000001 | 1000 | 0.7906389820898028 | 93.6 | 1000 | 0.774 | 67 | 6.7 | 0.791 | 0.002375 | {} |
| few_large_clusters | B | estimated_pooled_record | 1,000 | 100.0 | 97.5 | 100.0 | 0.0 | 93.33 | 975 | 0.799 | 93.33333333333333 | 975 | 0.7988595860203707 | 93.64 | 975 | 0.781 | 65 | 6.5 | 0.78 | 0.002375 | {"below_10_records_per_score_definition_cell": 25} |
| few_large_clusters | C | estimated_pooled_record | 1,000 | 100.0 | 0.0 | 100.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 | 0.0 | 0.0 | 0.002375 | {"degenerate_outcome_cell": 236, "too_few_distinct_patients_per_score_definition_cell": 1000, "too_few_distinct_patients_total": 1000, "too_few_records_per_score_definition_cell": 25} |
| few_large_clusters | D | estimated_pooled_record | 1,000 | 100.0 | 0.0 | 100.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 | 0.0 | 0.0 | 0.002375 | {"degenerate_outcome_cell": 236, "too_few_distinct_patients_per_score_definition_cell": 1000} |
| few_large_clusters | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 93.3 | 1000 | 0.791 | 93.30000000000001 | 1000 | 0.7906389820898028 | 93.5 | 1000 | 0.78 | 67 | 6.7 | 0.791 | 0.002375 | {} |
| few_large_clusters | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 92.7 | 1000 | 0.823 | 92.7 | 1000 | 0.8226238508577294 |  | 0 |  | 73 | 7.3 | 0.823 | 0.002262 | {} |
| no_common_support | A | estimated_pooled_record | 1,000 | 0.0 | 0.0 | 0.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  |  | {"no_common_support": 1000} |
| no_common_support | B | estimated_pooled_record | 1,000 | 0.0 | 0.0 | 0.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  |  | {"no_common_support": 1000} |
| no_common_support | C | estimated_pooled_record | 1,000 | 0.0 | 0.0 | 0.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  |  | {"no_common_support": 1000} |
| no_common_support | D | estimated_pooled_record | 1,000 | 0.0 | 0.0 | 0.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  |  | {"no_common_support": 1000} |
| no_common_support | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 0.0 | 0.0 | 0.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  |  | {"no_common_support": 1000} |
| no_common_support | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 0.0 | 0.0 | 0.0 | 0.0 |  | 0 |  |  | 0 |  |  | 0 |  | 0 |  |  |  | {"no_estimand": 1000} |
| high_icc_unbalanced_holdout | A | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 94.8 | 1000 | 0.702 | 48 | 4.8 | 0.676 | -0.000415 | {} |
| high_icc_unbalanced_holdout | B | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 94.8 | 1000 | 0.702 | 48 | 4.8 | 0.676 | -0.000415 | {} |
| high_icc_unbalanced_holdout | C | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 94.8 | 1000 | 0.702 | 48 | 4.8 | 0.676 | -0.000415 | {} |
| high_icc_unbalanced_holdout | D | estimated_pooled_record | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.2 | 1000 | 0.676 | 95.19999999999999 | 1000 | 0.6759881655768838 | 94.8 | 1000 | 0.702 | 48 | 4.8 | 0.676 | -0.000415 | {} |
| high_icc_unbalanced_holdout | A_legacy_fixed_weight_IF | legacy_fixed_weight_variance | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 95.1 | 1000 | 0.683 | 95.1 | 1000 | 0.6826346021115546 | 94.7 | 1000 | 0.708 | 49 | 4.9 | 0.683 | -0.000415 | {} |
| high_icc_unbalanced_holdout | A_fixed_true_weights | fixed_population_weight_sensitivity | 1,000 | 100.0 | 100.0 | 100.0 | 0.0 | 94.9 | 1000 | 0.696 | 94.89999999999999 | 1000 | 0.6956938982052382 |  | 0 |  | 51 | 5.1 | 0.696 | -0.000446 | {} |

**Notes.**

- All eleven confirmatory designs and every reported policy are retained. Population-truth coverage, conditional observed-weight coverage, and valid-target coverage among emitted intervals are separate fields. Off-target output is not folded into conditional on-target coverage.

## Supplementary Table 44. Paired simulation strategy comparisons

| design | first_policy | second_policy | contrast | paired_replicates | emission_difference | emission_difference_mcse | unconditional_miss_difference | unconditional_miss_difference_mcse | conditional_coverage_difference | conditional_coverage_difference_mcse | paired_coverage_n_min | conditional_observed_weight_coverage_difference | conditional_observed_weight_coverage_difference_mcse | paired_conditional_observed_weight_n_min | mean_width_difference_on_jointly_emitted | mean_width_difference_mcse | width_joint_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_balanced_iid | A | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_balanced_iid | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_balanced_iid | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_balanced_iid | A | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_balanced_iid | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.00014378681627378643 | 3.8420686524389285e-06 | 1000 |
| null_heterogeneous_iid | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_heterogeneous_iid | A | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_heterogeneous_iid | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_heterogeneous_iid | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_heterogeneous_iid | A | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| null_heterogeneous_iid | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | -0.004 | 0.0019969947390987264 | 0.0039999999999998925 | 0.0019969947390987264 | 1000 | 0.0030000000000000027 | 0.0017303161543469432 | 1000 | 0.0008066067426938873 | 1.0939946501039823e-05 | 1000 |
| heterogeneous_random_weights | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| heterogeneous_random_weights | A | C | first minus second | 1000 | 0.003 | 0.0017303161543469432 | 0.0 | 0.0 | 0.00016549648946839746 | 9.788974020870458e-05 | 997 | 0.00016850551654956636 | 9.962324946266189e-05 | 997 | 0.0 | 0.0 | 997 |
| heterogeneous_random_weights | B | C | first minus second | 1000 | 0.003 | 0.0017303161543469432 | 0.0 | 0.0 | 0.00016549648946839746 | 9.788974020870458e-05 | 997 | 0.00016850551654956636 | 9.962324946266189e-05 | 997 | 0.0 | 0.0 | 997 |
| heterogeneous_random_weights | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 997 | 0.0 | 0.0 | 997 | 0.0 | 0.0 | 997 |
| heterogeneous_random_weights | A | D | first minus second | 1000 | 0.003 | 0.0017303161543469432 | 0.0 | 0.0 | 0.00016549648946839746 | 9.788974020870458e-05 | 997 | 0.00016850551654956636 | 9.962324946266189e-05 | 997 | 0.0 | 0.0 | 997 |
| heterogeneous_random_weights | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | -0.008 | 0.0028185003005044974 | 0.007999999999999896 | 0.0028185003005044974 | 1000 | 0.0050000000000000044 | 0.00223158687484489 | 1000 | 0.0020449274242903465 | 2.19320073485593e-05 | 1000 |
| repeated_admissions_cross_group | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| repeated_admissions_cross_group | A | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| repeated_admissions_cross_group | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| repeated_admissions_cross_group | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| repeated_admissions_cross_group | A | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| repeated_admissions_cross_group | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0010000000000000009 | 0.001 | 1000 | 6.402220033325218e-05 | 3.0222593601001657e-06 | 1000 |
| unequal_cluster_sizes | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| unequal_cluster_sizes | A | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| unequal_cluster_sizes | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| unequal_cluster_sizes | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| unequal_cluster_sizes | A | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| unequal_cluster_sizes | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0020000000000000018 | 0.0014135055705578234 | 1000 | 0.0004494872917853243 | 1.325064470463329e-05 | 1000 |
| near_boundary_risks | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| near_boundary_risks | A | C | first minus second | 1000 | 0.383 | 0.015380102325652699 | 0.018 | 0.00420638724961144 | -0.0024813614262561012 | 0.005141323152236118 | 617 | -0.0018606158833063269 | 0.005175199134799819 | 617 | 0.0 | 0.0 | 617 |
| near_boundary_risks | B | C | first minus second | 1000 | 0.383 | 0.015380102325652699 | 0.018 | 0.00420638724961144 | -0.0024813614262561012 | 0.005141323152236118 | 617 | -0.0018606158833063269 | 0.005175199134799819 | 617 | 0.0 | 0.0 | 617 |
| near_boundary_risks | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 617 | 0.0 | 0.0 | 617 | 0.0 | 0.0 | 617 |
| near_boundary_risks | A | D | first minus second | 1000 | 0.383 | 0.015380102325652699 | 0.018 | 0.00420638724961144 | -0.0024813614262561012 | 0.005141323152236118 | 617 | -0.0018606158833063269 | 0.005175199134799819 | 617 | 0.0 | 0.0 | 617 |
| near_boundary_risks | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0010000000000000009 | 0.0010000000000000002 | 1000 | 0.000149383675925227 | 3.9321254236331635e-06 | 1000 |
| partial_structural_support | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| partial_structural_support | A | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| partial_structural_support | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| partial_structural_support | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| partial_structural_support | A | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| partial_structural_support | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.00016538295371332692 | 7.712821795168623e-06 | 1000 |
| rare_common_support_holdout | A | B | first minus second | 1000 | 1.0 | 0.0 | 0.341 | 0.014998131348402837 |  |  | 0 |  |  | 0 |  |  | 0 |
| rare_common_support_holdout | A | C | first minus second | 1000 | 1.0 | 0.0 | 0.341 | 0.014998131348402837 |  |  | 0 |  |  | 0 |  |  | 0 |
| rare_common_support_holdout | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 |  |  | 0 |  |  | 0 |  |  | 0 |
| rare_common_support_holdout | C | D | first minus second | 1000 | -0.309 | 0.014619600977206347 | -0.309 | 0.014619600977206347 |  |  | 0 |  |  | 0 |  |  | 0 |
| rare_common_support_holdout | A | D | first minus second | 1000 | 0.691 | 0.014619600977206345 | 0.032 | 0.005568393575081328 |  |  | 0 |  |  | 0 |  |  | 0 |
| rare_common_support_holdout | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 691 | 0.0 | 0.0 | 691 | 0.0001746733552973398 | 5.7825647648193045e-06 | 691 |
| few_large_clusters | A | B | first minus second | 1000 | 0.025 | 0.004939574819698493 | 0.002 | 0.0014135055705578234 | -0.0003333333333332966 | 0.0013733555543624057 | 975 | -0.00041025641025638215 | 0.0013735433350106157 | 975 | 0.0 | 0.0 | 975 |
| few_large_clusters | A | C | first minus second | 1000 | 1.0 | 0.0 | 0.067 | 0.007910345983177575 |  |  | 0 |  |  | 0 |  |  | 0 |
| few_large_clusters | B | C | first minus second | 1000 | 0.975 | 0.004939574819698493 | 0.065 | 0.0077997330618320435 |  |  | 0 |  |  | 0 |  |  | 0 |
| few_large_clusters | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 |  |  | 0 |  |  | 0 |  |  | 0 |
| few_large_clusters | A | D | first minus second | 1000 | 1.0 | 0.0 | 0.067 | 0.007910345983177575 |  |  | 0 |  |  | 0 |  |  | 0 |
| few_large_clusters | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0031638599858416633 | 0.0 | 0.0031638599858416633 | 1000 | 0.0010000000000000009 | 0.0026468860961526104 | 1000 | 0.002641780750568798 | 0.00031531492639307133 | 1000 |
| no_common_support | A | B | first minus second | 1000 | 0.0 | 0.0 |  |  |  |  | 0 |  |  | 0 |  |  | 0 |
| no_common_support | A | C | first minus second | 1000 | 0.0 | 0.0 |  |  |  |  | 0 |  |  | 0 |  |  | 0 |
| no_common_support | B | C | first minus second | 1000 | 0.0 | 0.0 |  |  |  |  | 0 |  |  | 0 |  |  | 0 |
| no_common_support | C | D | first minus second | 1000 | 0.0 | 0.0 |  |  |  |  | 0 |  |  | 0 |  |  | 0 |
| no_common_support | A | D | first minus second | 1000 | 0.0 | 0.0 |  |  |  |  | 0 |  |  | 0 |  |  | 0 |
| no_common_support | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 |  |  |  |  | 0 |  |  | 0 |  |  | 0 |
| high_icc_unbalanced_holdout | A | B | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| high_icc_unbalanced_holdout | A | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| high_icc_unbalanced_holdout | B | C | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| high_icc_unbalanced_holdout | C | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| high_icc_unbalanced_holdout | A | D | first minus second | 1000 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 | 0.0 | 0.0 | 1000 |
| high_icc_unbalanced_holdout | A | A_legacy_fixed_weight_IF | first minus second | 1000 | 0.0 | 0.0 | -0.001 | 0.0010000000000000002 | 0.0010000000000000009 | 0.0010000000000000002 | 1000 | 0.0010000000000000009 | 0.0010000000000000002 | 1000 | 0.00016404188051007818 | 8.702907902560982e-06 | 1000 |

**Notes.**

- Paired differences are descriptive simulation contrasts over the recorded paired replicate sets.

## Supplementary Table 45. Full sparse-boundary strategy results

| design | strategy | replicates | point_output_rate | interval_output_rate | n_intervals | conditional_coverage | coverage_mcse | unconditional_missed_intervals | median_width | bias | bias_mcse | refusal_evaluation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fine_cells | A | 1000 | 1.0 | 1.0 | 1000 | 0.952 | 0.006759881655768837 | 48 | 0.041971547050085066 | -0.00015436733692476273 | 0.0003424164358940989 | shared numerical estimate and explicit count rule |
| fine_cells | B | 1000 | 1.0 | 0.0 | 0 |  |  | 0 |  | -0.00015436733692476273 | 0.0003424164358940989 | shared numerical estimate and explicit count rule |
| fine_cells | C | 1000 | 1.0 | 0.0 | 0 |  |  | 0 |  | -0.00015436733692476273 | 0.0003424164358940989 | actual C example plus deterministic count gate on every replicate |
| fine_cells | D | 1000 | 1.0 | 0.0 | 0 |  |  | 0 |  | -0.00015436733692476273 | 0.0003424164358940989 | shared numerical estimate and explicit count rule |
| tiny_arm | A | 1000 | 1.0 | 1.0 | 1000 | 0.636 | 0.015215255502291114 | 364 | 0.03668816181107842 | -0.00025124017490491034 | 0.0006459457598154097 | shared numerical estimate and explicit count rule |
| tiny_arm | B | 1000 | 1.0 | 0.0 | 0 |  |  | 0 |  | -0.00025124017490491034 | 0.0006459457598154097 | shared numerical estimate and explicit count rule |
| tiny_arm | C | 1000 | 1.0 | 0.0 | 0 |  |  | 0 |  | -0.00025124017490491034 | 0.0006459457598154097 | actual C example plus deterministic count gate on every replicate |
| tiny_arm | D | 1000 | 1.0 | 0.0 | 0 |  |  | 0 |  | -0.00025124017490491034 | 0.0006459457598154097 | shared numerical estimate and explicit count rule |

**Notes.**

- The sparse validation holds the score-specific risk difference constant, so the population and observed record-weight targets coincide. B/C/D emit no interval for these structures; conditional coverage is undefined when no interval is emitted.

## Supplementary Table 46. Full selected audit-strategy and sparse-boundary interval results

| Design | Strategy | Point output (% of replicates) | Interval output (% of replicates) | Target support matched (% of replicates) | Off-target interval output (% of replicates) | Population-truth coverage on target (n; MCSE, pp) | Valid-target coverage among emitted intervals (n; MCSE, pp) | Emitted-interval population-truth noncoverage / all replicates | Output / refusal state |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | A | 100.00% | 100.00% | 100.00% | 0.00% | 94.40% (n=1,000; 0.727 pp) | 94.40% (n=1,000; 0.727 pp) | 56 / 1,000 (5.60%; 0.727 pp) | point and interval emitted in all replicates |
| null_balanced_iid | B | 100.00% | 100.00% | 100.00% | 0.00% | 94.40% (n=1,000; 0.727 pp) | 94.40% (n=1,000; 0.727 pp) | 56 / 1,000 (5.60%; 0.727 pp) | point and interval emitted in all replicates |
| null_balanced_iid | C | 100.00% | 100.00% | 100.00% | 0.00% | 94.40% (n=1,000; 0.727 pp) | 94.40% (n=1,000; 0.727 pp) | 56 / 1,000 (5.60%; 0.727 pp) | point and interval emitted in all replicates |
| repeated_admissions_cross_group | A | 100.00% | 100.00% | 100.00% | 0.00% | 94.10% (n=1,000; 0.745 pp) | 94.10% (n=1,000; 0.745 pp) | 59 / 1,000 (5.90%; 0.745 pp) | point and interval emitted in all replicates |
| repeated_admissions_cross_group | B | 100.00% | 100.00% | 100.00% | 0.00% | 94.10% (n=1,000; 0.745 pp) | 94.10% (n=1,000; 0.745 pp) | 59 / 1,000 (5.90%; 0.745 pp) | point and interval emitted in all replicates |
| repeated_admissions_cross_group | C | 100.00% | 100.00% | 100.00% | 0.00% | 94.10% (n=1,000; 0.745 pp) | 94.10% (n=1,000; 0.745 pp) | 59 / 1,000 (5.90%; 0.745 pp) | point and interval emitted in all replicates |
| rare_common_support_holdout | A | 100.00% | 100.00% | 69.10% | 30.90% | 95.37% (n=691; 0.799 pp) | 65.90% (n=1,000; 1.499 pp) | 341 / 1,000 (34.10%; 1.499 pp) | point and interval emitted in all replicates |
| rare_common_support_holdout | B | 100.00% | 0.00% | 69.10% | 0.00% | — (0 on-target intervals) | — (no emitted intervals) | 0 / 1,000 (0.00%; 0.000 pp) | point only; no interval emitted; refusals: below_10_records_per_score_definition_cell=1000 |
| rare_common_support_holdout | C | 100.00% | 0.00% | 69.10% | 0.00% | — (0 on-target intervals) | — (no emitted intervals) | 0 / 1,000 (0.00%; 0.000 pp) | point only; no interval emitted; refusals: degenerate_outcome_cell=617, target_support_lost=309, too_few_distinct_patients_per_score_definition_cell=691, too_few_records_per_score_definition_cell=691, too_few_records_per_score_level=691 |
| near_boundary_risks | A | 100.00% | 100.00% | 100.00% | 0.00% | 95.70% (n=1,000; 0.641 pp) | 95.70% (n=1,000; 0.641 pp) | 43 / 1,000 (4.30%; 0.641 pp) | point and interval emitted in all replicates |
| near_boundary_risks | B | 100.00% | 100.00% | 100.00% | 0.00% | 95.70% (n=1,000; 0.641 pp) | 95.70% (n=1,000; 0.641 pp) | 43 / 1,000 (4.30%; 0.641 pp) | point and interval emitted in all replicates |
| near_boundary_risks | C | 100.00% | 61.70% | 100.00% | 0.00% | 95.95% (n=617; 0.794 pp) | 95.95% (n=617; 0.794 pp) | 25 / 1,000 (2.50%; 0.494 pp) | point output; interval emitted in a subset of replicates; refusals: degenerate_outcome_cell=383 |
| few_large_clusters | A | 100.00% | 100.00% | 100.00% | 0.00% | 93.30% (n=1,000; 0.791 pp) | 93.30% (n=1,000; 0.791 pp) | 67 / 1,000 (6.70%; 0.791 pp) | point and interval emitted in all replicates |
| few_large_clusters | B | 100.00% | 97.50% | 100.00% | 0.00% | 93.33% (n=975; 0.799 pp) | 93.33% (n=975; 0.799 pp) | 65 / 1,000 (6.50%; 0.780 pp) | point output; interval emitted in a subset of replicates; refusals: below_10_records_per_score_definition_cell=25 |
| few_large_clusters | C | 100.00% | 0.00% | 100.00% | 0.00% | — (0 on-target intervals) | — (no emitted intervals) | 0 / 1,000 (0.00%; 0.000 pp) | point only; no interval emitted; refusals: degenerate_outcome_cell=236, too_few_distinct_patients_per_score_definition_cell=1000, too_few_distinct_patients_total=1000, too_few_records_per_score_definition_cell=25 |
| fine_cells | A | 100.00% | 100.00% | not separately summarized | not separately summarized | 95.20% (n=1,000; 0.676 pp) | not separately summarized | 48 / 1,000 | A emits a point/interval; B/C apply deterministic count rules |
| fine_cells | B | 100.00% | 0.00% | not separately summarized | not separately summarized | — (no emitted intervals) | not separately summarized | 0 / 1,000 | point output; interval refused by sparse-cell count rule |
| fine_cells | C | 100.00% | 0.00% | not separately summarized | not separately summarized | — (no emitted intervals) | not separately summarized | 0 / 1,000 | point output; interval refused by sparse-cell count rule |
| tiny_arm | A | 100.00% | 100.00% | not separately summarized | not separately summarized | 63.60% (n=1,000; 1.522 pp) | not separately summarized | 364 / 1,000 | A emits a point/interval; B/C apply deterministic count rules |
| tiny_arm | B | 100.00% | 0.00% | not separately summarized | not separately summarized | — (no emitted intervals) | not separately summarized | 0 / 1,000 | point output; interval refused by sparse-cell count rule |
| tiny_arm | C | 100.00% | 0.00% | not separately summarized | not separately summarized | — (no emitted intervals) | not separately summarized | 0 / 1,000 | point output; interval refused by sparse-cell count rule |

Complete row-level data are also supplied in S46.csv.

## Supplementary Table 47. Score-level simultaneous coverage diagnostics

| design | family | family_defined | n_defined_group_risk_intervals | n_defined_delta_s_intervals | n_eligible_datasets | n_complete_output_families | complete_family_output_rate | complete_family_output_rate_mcse | n_complete_families_covering_all_truths | conditional_simultaneous_containment | conditional_simultaneous_containment_mcse | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 1000 | 1.0 | 0.0 | 635 | 0.635 | 0.015224158433227107 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| null_heterogeneous_iid | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 1000 | 1.0 | 0.0 | 602 | 0.602 | 0.015478888849009803 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| heterogeneous_random_weights | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 998 | 0.998 | 0.0014127986409959495 | 603 | 0.6042084168336673 | 0.015479659090307024 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| repeated_admissions_cross_group | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 1000 | 1.0 | 0.0 | 626 | 0.626 | 0.015301111070768685 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| unequal_cluster_sizes | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 1000 | 1.0 | 0.0 | 611 | 0.611 | 0.015416841440450765 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| near_boundary_risks | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 590 | 0.59 | 0.01555313473226539 | 368 | 0.6237288135593221 | 0.019944464449948473 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| partial_structural_support | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 2 | 1000 | 1000 | 1.0 | 0.0 | 672 | 0.672 | 0.014846413708367418 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| rare_common_support_holdout | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 6 | 3 | 1000 | 0 | 0.0 | 0.0 | 0 |  |  | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| few_large_clusters | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 0 | 0.0 | 0.0 | 0 |  |  | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |
| no_common_support | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | False | 4 | 0 | 0 | 0 |  |  | 0 |  |  | Undefined: design has no population common-support delta_s estimand. |
| high_icc_unbalanced_holdout | all_defined_group_risk_and_common_support_delta_s_pointwise_intervals | True | 8 | 4 | 1000 | 1000 | 1.0 | 0.0 | 602 | 0.602 | 0.015478888849009803 | Descriptive simultaneous containment of emitted pointwise intervals; no 95% familywise claim. |

## Supplementary Table 48. Score-level interval validation by design and method

| design | method | truth_defined | n_defined_score_arm_intervals_per_dataset | n_design_replicates | n_eligible_intervals | n_ci_emitted | n_withheld | output_rate | output_rate_mcse_clustered_by_dataset | n_covered_issued_rounded_ci | conditional_coverage_issued_rounded_ci | conditional_coverage_mcse_issued_clustered_by_dataset | n_covered_fullprecision_ci | conditional_coverage_fullprecision_ci | conditional_coverage_mcse_fullprecision_clustered_by_dataset | coverage_difference_fullprecision_minus_issued | n_coverage_discordant_due_to_rounding | n_emitted_endpoint_rounding_mismatches | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | group_risk | True | 8 | 1000 | 8000 | 8000 | 0 | 1.0 | 0.0 | 7643 | 0.955375 | 0.0023515450536060628 | 7640 | 0.955 | 0.0023610007040075877 | -0.0003750000000000142 | 3 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| null_balanced_iid | delta_s | True | 4 | 1000 | 4000 | 4000 | 0 | 1.0 | 0.0 | 3787 | 0.94675 | 0.0035516970664813256 | 3786 | 0.9465 | 0.0035567401367544976 | -0.00024999999999997247 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| null_heterogeneous_iid | group_risk | True | 8 | 1000 | 8000 | 8000 | 0 | 1.0 | 0.0 | 7597 | 0.949625 | 0.0023814188062015744 | 7597 | 0.949625 | 0.0023814188062015744 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| null_heterogeneous_iid | delta_s | True | 4 | 1000 | 4000 | 4000 | 0 | 1.0 | 0.0 | 3788 | 0.947 | 0.0035466291853785024 | 3786 | 0.9465 | 0.003556740136754498 | -0.0004999999999999449 | 2 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| heterogeneous_random_weights | group_risk | True | 8 | 1000 | 8000 | 7998 | 2 | 0.99975 | 0.00017668819631972793 | 7615 | 0.9521130282570642 | 0.002407326450230684 | 7613 | 0.9518629657414354 | 0.002415320891347233 | -0.0002500625156288683 | 2 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| heterogeneous_random_weights | delta_s | True | 4 | 1000 | 4000 | 3998 | 2 | 0.9995 | 0.00035337639263945586 | 3759 | 0.9402201100550275 | 0.0036764557966868358 | 3758 | 0.9399699849924963 | 0.0036808869410930307 | -0.0002501250625311924 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| repeated_admissions_cross_group | group_risk | True | 8 | 1000 | 8000 | 8000 | 0 | 1.0 | 0.0 | 7624 | 0.953 | 0.0023417907643476575 | 7624 | 0.953 | 0.0023417907643476575 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| repeated_admissions_cross_group | delta_s | True | 4 | 1000 | 4000 | 4000 | 0 | 1.0 | 0.0 | 3802 | 0.9505 | 0.0034185430283143192 | 3802 | 0.9505 | 0.0034185430283143192 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| unequal_cluster_sizes | group_risk | True | 8 | 1000 | 8000 | 8000 | 0 | 1.0 | 0.0 | 7615 | 0.951875 | 0.002408144209455392 | 7613 | 0.951625 | 0.0024161067747405012 | -0.00024999999999997247 | 2 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| unequal_cluster_sizes | delta_s | True | 4 | 1000 | 4000 | 4000 | 0 | 1.0 | 0.0 | 3791 | 0.94775 | 0.0035312756062657316 | 3791 | 0.94775 | 0.0035312756062657316 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| near_boundary_risks | group_risk | True | 8 | 1000 | 8000 | 7544 | 456 | 0.943 | 0.0023130283396664425 | 7191 | 0.9532078472958643 | 0.002347339207435091 | 7190 | 0.9530752916224814 | 0.002348623940411873 | -0.00013255567338288365 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| near_boundary_risks | delta_s | True | 4 | 1000 | 4000 | 3585 | 415 | 0.89625 | 0.003976713687424801 | 3431 | 0.9570432357043236 | 0.0033657217829643066 | 3430 | 0.9567642956764296 | 0.003373415455322115 | -0.0002789400278939702 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| partial_structural_support | group_risk | True | 8 | 1000 | 8000 | 8000 | 0 | 1.0 | 0.0 | 7650 | 0.95625 | 0.0022632520429262423 | 7650 | 0.95625 | 0.0022632520429262423 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| partial_structural_support | delta_s | True | 2 | 1000 | 2000 | 2000 | 0 | 1.0 | 0.0 | 1906 | 0.953 | 0.004670418911919231 | 1906 | 0.953 | 0.004670418911919231 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| rare_common_support_holdout | group_risk | True | 6 | 1000 | 6000 | 4000 | 2000 | 0.6666666666666666 | 0.0 | 3802 | 0.9505 | 0.0035968997327820644 | 3801 | 0.95025 | 0.0036021400462659574 | -0.00024999999999997247 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| rare_common_support_holdout | delta_s | True | 3 | 1000 | 3000 | 2000 | 1000 | 0.6666666666666666 | 0.0 | 1899 | 0.9495 | 0.004766809464670523 | 1900 | 0.95 | 0.004745789978762495 | 0.0004999999999999449 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| few_large_clusters | group_risk | True | 8 | 1000 | 8000 | 0 | 8000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| few_large_clusters | delta_s | True | 4 | 1000 | 4000 | 0 | 4000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| no_common_support | group_risk | True | 4 | 1000 | 4000 | 4000 | 0 | 1.0 | 0.0 | 3809 | 0.95225 | 0.003360614710321794 | 3808 | 0.952 | 0.0033663529720355133 | -0.0002500000000000835 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| no_common_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. |
| high_icc_unbalanced_holdout | group_risk | True | 8 | 1000 | 8000 | 8000 | 0 | 1.0 | 0.0 | 7606 | 0.95075 | 0.002589622297487347 | 7606 | 0.95075 | 0.002589622297487347 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |
| high_icc_unbalanced_holdout | delta_s | True | 4 | 1000 | 4000 | 4000 | 0 | 1.0 | 0.0 | 3776 | 0.944 | 0.003623137746087931 | 3776 | 0.944 | 0.003623137746087931 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. |

## Supplementary Table 49. Score-level interval precision sensitivity

| design | method | truth_defined | n_defined_score_arm_intervals_per_dataset | n_design_replicates | n_eligible_intervals | n_ci_emitted | n_withheld | output_rate | output_rate_mcse_clustered_by_dataset | n_covered_issued_rounded_ci | conditional_coverage_issued_rounded_ci | conditional_coverage_mcse_issued_clustered_by_dataset | n_covered_fullprecision_ci | conditional_coverage_fullprecision_ci | conditional_coverage_mcse_fullprecision_clustered_by_dataset | coverage_difference_fullprecision_minus_issued | n_coverage_discordant_due_to_rounding | n_emitted_endpoint_rounding_mismatches | interpretation | level | arm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 961 | 0.961 | 0.006125072776426131 | 961 | 0.961 | 0.006125072776426131 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 959 | 0.959 | 0.006273624021118765 | 959 | 0.959 | 0.006273624021118765 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| null_balanced_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 955 | 0.955 | 0.006558812241406064 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 959 | 0.959 | 0.006273624021118764 | 957 | 0.957 | 0.006418114379799739 | -0.0020000000000000018 | 2 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 949 | 0.949 | 0.006960420062571471 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| null_balanced_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.0068954729748979164 | 949 | 0.949 | 0.006960420062571471 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 952 | 0.952 | 0.006763264133666651 | 952 | 0.952 | 0.006763264133666651 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 951 | 0.951 | 0.00682976175614096 | 951 | 0.951 | 0.00682976175614096 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| null_balanced_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 946 | 0.946 | 0.007150883521295472 | 946 | 0.946 | 0.007150883521295472 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 946 | 0.946 | 0.007150883521295473 | 946 | 0.946 | 0.007150883521295473 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| null_balanced_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 965 | 0.965 | 0.005814534272734903 | 965 | 0.965 | 0.005814534272734903 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| null_balanced_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 936 | 0.936 | 0.007743640226919377 | 936 | 0.936 | 0.007743640226919377 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 949 | 0.949 | 0.006960420062571471 | 949 | 0.949 | 0.006960420062571471 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.0068954729748979164 | 950 | 0.95 | 0.0068954729748979164 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| null_heterogeneous_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 957 | 0.957 | 0.006418114379799739 | 957 | 0.957 | 0.006418114379799739 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 946 | 0.946 | 0.007150883521295473 | 946 | 0.946 | 0.007150883521295473 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 942 | 0.942 | 0.0073953154557929906 | 942 | 0.942 | 0.0073953154557929906 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| null_heterogeneous_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 939 | 0.939 | 0.007572076091557476 | 937 | 0.937 | 0.007687007876286461 | -0.0019999999999998908 | 2 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 956 | 0.956 | 0.0064889217984273875 | 956 | 0.956 | 0.0064889217984273875 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 957 | 0.957 | 0.006418114379799739 | 957 | 0.957 | 0.006418114379799739 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| null_heterogeneous_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 942 | 0.942 | 0.0073953154557929906 | 942 | 0.942 | 0.0073953154557929906 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 953 | 0.953 | 0.006695956678163012 | 953 | 0.953 | 0.006695956678163012 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| null_heterogeneous_iid | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 944 | 0.944 | 0.007274401481697097 | 944 | 0.944 | 0.007274401481697097 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| null_heterogeneous_iid | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.0068954729748979164 | 950 | 0.95 | 0.0068954729748979164 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 936 | 0.936 | 0.007743640226919378 | 936 | 0.936 | 0.007743640226919378 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 954 | 0.954 | 0.006627814717380679 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| heterogeneous_random_weights | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 942 | 0.942 | 0.0073953154557929906 | 942 | 0.942 | 0.0073953154557929906 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 954 | 0.954 | 0.006627814717380679 | 954 | 0.954 | 0.006627814717380679 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 950 | 0.95 | 0.006895472974897917 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| heterogeneous_random_weights | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 949 | 0.949 | 0.006960420062571471 | 948 | 0.948 | 0.007024624213817089 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 962 | 0.962 | 0.0060491811505849775 | 962 | 0.962 | 0.0060491811505849775 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.007024624213817089 | 948 | 0.948 | 0.007024624213817089 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| heterogeneous_random_weights | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 928 | 0.928 | 0.008178195576218687 | 928 | 0.928 | 0.008178195576218687 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 998 | 2 | 0.998 | 0.0014135055705578234 | 956 | 0.9579158316633266 | 0.006358798092643493 | 955 | 0.9569138276553106 | 0.0064306867897348996 | -0.0010020040080159776 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| heterogeneous_random_weights | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 954 | 0.954 | 0.006627814717380679 | 954 | 0.954 | 0.006627814717380679 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| heterogeneous_random_weights | delta_s | True | 1 | 1000 | 1000 | 998 | 2 | 0.998 | 0.0014135055705578234 | 940 | 0.9418837675350702 | 0.0074096785484197925 | 940 | 0.9418837675350702 | 0.0074096785484197925 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 955 | 0.955 | 0.006558812241406064 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 950 | 0.95 | 0.006895472974897917 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| repeated_admissions_cross_group | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 959 | 0.959 | 0.006273624021118765 | 959 | 0.959 | 0.006273624021118765 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 952 | 0.952 | 0.006763264133666652 | 952 | 0.952 | 0.006763264133666652 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 942 | 0.942 | 0.0073953154557929906 | 942 | 0.942 | 0.0073953154557929906 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| repeated_admissions_cross_group | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 947 | 0.947 | 0.007088105617246489 | 947 | 0.947 | 0.007088105617246489 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 961 | 0.961 | 0.006125072776426131 | 961 | 0.961 | 0.006125072776426131 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 950 | 0.95 | 0.006895472974897917 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| repeated_admissions_cross_group | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 945 | 0.945 | 0.007212976294639199 | 945 | 0.945 | 0.007212976294639199 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 961 | 0.961 | 0.006125072776426131 | 961 | 0.961 | 0.006125072776426131 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| repeated_admissions_cross_group | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 953 | 0.953 | 0.006695956678163012 | 953 | 0.953 | 0.006695956678163012 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| repeated_admissions_cross_group | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 951 | 0.951 | 0.006829761756140959 | 951 | 0.951 | 0.006829761756140959 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.007024624213817089 | 947 | 0.947 | 0.007088105617246489 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 960 | 0.96 | 0.006199874066337029 | 960 | 0.96 | 0.006199874066337029 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| unequal_cluster_sizes | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 939 | 0.939 | 0.007572076091557476 | 939 | 0.939 | 0.007572076091557476 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 949 | 0.949 | 0.00696042006257147 | 949 | 0.949 | 0.00696042006257147 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 952 | 0.952 | 0.006763264133666652 | 952 | 0.952 | 0.006763264133666652 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| unequal_cluster_sizes | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 950 | 0.95 | 0.006895472974897917 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 955 | 0.955 | 0.006558812241406064 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 959 | 0.959 | 0.006273624021118764 | 959 | 0.959 | 0.006273624021118764 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| unequal_cluster_sizes | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 963 | 0.963 | 0.005972157622389639 | 963 | 0.963 | 0.005972157622389639 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 944 | 0.944 | 0.007274401481697097 | 944 | 0.944 | 0.007274401481697097 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| unequal_cluster_sizes | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.007024624213817089 | 947 | 0.947 | 0.007088105617246489 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| unequal_cluster_sizes | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 939 | 0.939 | 0.007572076091557475 | 939 | 0.939 | 0.007572076091557475 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 672 | 328 | 0.672 | 0.01485384248727031 | 649 | 0.9657738095238095 | 0.007016969885982307 | 649 | 0.9657738095238095 | 0.007016969885982307 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 885 | 115 | 0.885 | 0.010093407594904551 | 858 | 0.9694915254237289 | 0.005783994560305087 | 858 | 0.9694915254237289 | 0.005783994560305087 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| near_boundary_risks | delta_s | True | 1 | 1000 | 1000 | 598 | 402 | 0.598 | 0.015512467135714957 | 597 | 0.9983277591973244 | 0.0016716780711055904 | 597 | 0.9983277591973244 | 0.0016716780711055904 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 993 | 7 | 0.993 | 0.0026377941462437807 | 954 | 0.9607250755287009 | 0.006167368155362001 | 954 | 0.9607250755287009 | 0.006167368155362001 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 994 | 6 | 0.994 | 0.002443352199329841 | 956 | 0.9617706237424547 | 0.006084969752230649 | 956 | 0.9617706237424547 | 0.006084969752230649 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| near_boundary_risks | delta_s | True | 1 | 1000 | 1000 | 987 | 13 | 0.987 | 0.0035838308894036615 | 941 | 0.9533941236068896 | 0.006712978471976059 | 941 | 0.9533941236068896 | 0.006712978471976059 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 944 | 0.944 | 0.007274401481697097 | 944 | 0.944 | 0.007274401481697097 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 940 | 0.94 | 0.007513751157474972 | 940 | 0.94 | 0.007513751157474972 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| near_boundary_risks | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 946 | 0.946 | 0.007150883521295473 | 945 | 0.945 | 0.0072129762946392 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 946 | 0.946 | 0.007150883521295473 | 945 | 0.945 | 0.007212976294639199 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| near_boundary_risks | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 944 | 0.944 | 0.007274401481697097 | 944 | 0.944 | 0.007274401481697097 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| near_boundary_risks | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 947 | 0.947 | 0.007088105617246489 | 947 | 0.947 | 0.007088105617246489 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 959 | 0.959 | 0.006273624021118765 | 959 | 0.959 | 0.006273624021118765 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| partial_structural_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 0.0 | never |
| partial_structural_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 0.0 | never_minus_principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 956 | 0.956 | 0.0064889217984273875 | 956 | 0.956 | 0.0064889217984273875 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| partial_structural_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 1.0 | never |
| partial_structural_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 1.0 | never_minus_principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 960 | 0.96 | 0.006199874066337029 | 960 | 0.96 | 0.006199874066337029 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 961 | 0.961 | 0.006125072776426131 | 961 | 0.961 | 0.006125072776426131 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| partial_structural_support | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 955 | 0.955 | 0.006558812241406064 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 939 | 0.939 | 0.007572076091557476 | 939 | 0.939 | 0.007572076091557476 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 962 | 0.962 | 0.0060491811505849775 | 962 | 0.962 | 0.0060491811505849775 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| partial_structural_support | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 951 | 0.951 | 0.006829761756140959 | 951 | 0.951 | 0.006829761756140959 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| partial_structural_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 4.0 | principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 965 | 0.965 | 0.005814534272734904 | 965 | 0.965 | 0.005814534272734904 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 4.0 | never |
| partial_structural_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 4.0 | never_minus_principal |
| partial_structural_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 5.0 | principal |
| partial_structural_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.00702462421381709 | 948 | 0.948 | 0.00702462421381709 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 5.0 | never |
| partial_structural_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 5.0 | never_minus_principal |
| rare_common_support_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 954 | 0.954 | 0.006627814717380679 | 954 | 0.954 | 0.006627814717380679 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| rare_common_support_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.00702462421381709 | 947 | 0.947 | 0.007088105617246489 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| rare_common_support_holdout | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 950 | 0.95 | 0.006895472974897917 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| rare_common_support_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 952 | 0.952 | 0.006763264133666652 | 952 | 0.952 | 0.006763264133666652 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| rare_common_support_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.007024624213817089 | 948 | 0.948 | 0.007024624213817089 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| rare_common_support_holdout | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 949 | 0.949 | 0.006960420062571471 | 950 | 0.95 | 0.0068954729748979164 | 0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| rare_common_support_holdout | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| rare_common_support_holdout | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| rare_common_support_holdout | delta_s | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| few_large_clusters | delta_s | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| few_large_clusters | delta_s | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| few_large_clusters | delta_s | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| few_large_clusters | group_risk | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| few_large_clusters | delta_s | True | 1 | 1000 | 1000 | 0 | 1000 | 0.0 | 0.0 | 0 |  |  | 0 |  |  |  | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |
| no_common_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 959 | 0.959 | 0.006273624021118764 | 959 | 0.959 | 0.006273624021118764 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| no_common_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 0.0 | never |
| no_common_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 0.0 | never_minus_principal |
| no_common_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 954 | 0.954 | 0.006627814717380679 | -0.0010000000000000009 | 1 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| no_common_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 1.0 | never |
| no_common_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 1.0 | never_minus_principal |
| no_common_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 2.0 | principal |
| no_common_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 949 | 0.949 | 0.006960420062571471 | 949 | 0.949 | 0.006960420062571471 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| no_common_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 2.0 | never_minus_principal |
| no_common_support | group_risk | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 3.0 | principal |
| no_common_support | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 946 | 0.946 | 0.007150883521295472 | 946 | 0.946 | 0.007150883521295472 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| no_common_support | delta_s | False | 0 | 1000 | 0 | 0 | 0 |  |  | 0 |  |  | 0 |  |  |  | 0 | 0 | Undefined: no population-defined target intervals in this design. | 3.0 | never_minus_principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 956 | 0.956 | 0.006488921798427387 | 956 | 0.956 | 0.006488921798427387 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 955 | 0.955 | 0.006558812241406064 | 955 | 0.955 | 0.006558812241406064 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never |
| high_icc_unbalanced_holdout | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 940 | 0.94 | 0.007513751157474971 | 940 | 0.94 | 0.007513751157474971 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 0.0 | never_minus_principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 942 | 0.942 | 0.0073953154557929906 | 942 | 0.942 | 0.0073953154557929906 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 953 | 0.953 | 0.006695956678163012 | 953 | 0.953 | 0.006695956678163012 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never |
| high_icc_unbalanced_holdout | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 937 | 0.937 | 0.007687007876286461 | 937 | 0.937 | 0.007687007876286461 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 1.0 | never_minus_principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 953 | 0.953 | 0.006695956678163012 | 953 | 0.953 | 0.006695956678163012 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 948 | 0.948 | 0.007024624213817089 | 948 | 0.948 | 0.007024624213817089 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never |
| high_icc_unbalanced_holdout | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 958 | 0.958 | 0.006346359293033784 | 958 | 0.958 | 0.006346359293033784 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 2.0 | never_minus_principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 949 | 0.949 | 0.006960420062571471 | 949 | 0.949 | 0.006960420062571471 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | principal |
| high_icc_unbalanced_holdout | group_risk | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 950 | 0.95 | 0.006895472974897917 | 950 | 0.95 | 0.006895472974897917 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never |
| high_icc_unbalanced_holdout | delta_s | True | 1 | 1000 | 1000 | 1000 | 0 | 1.0 | 0.0 | 941 | 0.941 | 0.007454835650406693 | 941 | 0.941 | 0.007454835650406693 | 0.0 | 0 | 0 | Coverage is conditional on emitted pointwise intervals; MCSE resamples whole datasets. | 3.0 | never_minus_principal |

## Supplementary Table 50. Score-level interval refusal frequencies

| design | level | estimand | arm | truth_defined | support_type | ci_status | replicate_count | eligible_replicate_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_balanced_iid | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| null_heterogeneous_iid | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 3.0 | group_risk | principal | True | common_support | computed | 998 | 1000 |
| heterogeneous_random_weights | 3.0 | group_risk | principal | True | common_support | too few distinct patients | 2 | 1000 |
| heterogeneous_random_weights | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| heterogeneous_random_weights | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 998 | 1000 |
| heterogeneous_random_weights | 3.0 | delta_s | never_minus_principal | True | common_support | too few distinct patients in a definition | 2 | 1000 |
| repeated_admissions_cross_group | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| repeated_admissions_cross_group | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| unequal_cluster_sizes | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| near_boundary_risks | 0.0 | group_risk | principal | True | common_support | computed | 672 | 1000 |
| near_boundary_risks | 0.0 | group_risk | principal | True | common_support | degenerate outcome: point estimate only | 328 | 1000 |
| near_boundary_risks | 0.0 | group_risk | never | True | common_support | computed | 885 | 1000 |
| near_boundary_risks | 0.0 | group_risk | never | True | common_support | degenerate outcome: point estimate only | 115 | 1000 |
| near_boundary_risks | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 598 | 1000 |
| near_boundary_risks | 0.0 | delta_s | never_minus_principal | True | common_support | degenerate outcome: point estimate only | 402 | 1000 |
| near_boundary_risks | 1.0 | group_risk | principal | True | common_support | computed | 993 | 1000 |
| near_boundary_risks | 1.0 | group_risk | principal | True | common_support | degenerate outcome: point estimate only | 7 | 1000 |
| near_boundary_risks | 1.0 | group_risk | never | True | common_support | computed | 994 | 1000 |
| near_boundary_risks | 1.0 | group_risk | never | True | common_support | degenerate outcome: point estimate only | 6 | 1000 |
| near_boundary_risks | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 987 | 1000 |
| near_boundary_risks | 1.0 | delta_s | never_minus_principal | True | common_support | degenerate outcome: point estimate only | 13 | 1000 |
| near_boundary_risks | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| near_boundary_risks | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| near_boundary_risks | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| near_boundary_risks | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| near_boundary_risks | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| near_boundary_risks | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 0.0 | group_risk | principal | True | one_definition_support | computed | 1000 | 1000 |
| partial_structural_support | 0.0 | group_risk | never | False | one_definition_support | no records | 1000 | 0 |
| partial_structural_support | 0.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| partial_structural_support | 1.0 | group_risk | principal | True | one_definition_support | computed | 1000 | 1000 |
| partial_structural_support | 1.0 | group_risk | never | False | one_definition_support | no records | 1000 | 0 |
| partial_structural_support | 1.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| partial_structural_support | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| partial_structural_support | 4.0 | group_risk | principal | False | one_definition_support | no records | 1000 | 0 |
| partial_structural_support | 4.0 | group_risk | never | True | one_definition_support | computed | 1000 | 1000 |
| partial_structural_support | 4.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| partial_structural_support | 5.0 | group_risk | principal | False | one_definition_support | no records | 1000 | 0 |
| partial_structural_support | 5.0 | group_risk | never | True | one_definition_support | computed | 1000 | 1000 |
| partial_structural_support | 5.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| rare_common_support_holdout | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| rare_common_support_holdout | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| rare_common_support_holdout | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| rare_common_support_holdout | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| rare_common_support_holdout | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| rare_common_support_holdout | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| rare_common_support_holdout | 2.0 | group_risk | principal | True | common_support | no records | 194 | 1000 |
| rare_common_support_holdout | 2.0 | group_risk | principal | True | common_support | too few distinct patients | 806 | 1000 |
| rare_common_support_holdout | 2.0 | group_risk | never | True | common_support | no records | 204 | 1000 |
| rare_common_support_holdout | 2.0 | group_risk | never | True | common_support | too few distinct patients | 796 | 1000 |
| rare_common_support_holdout | 2.0 | delta_s | never_minus_principal | True | common_support | no shared support | 357 | 1000 |
| rare_common_support_holdout | 2.0 | delta_s | never_minus_principal | True | common_support | too few distinct patients in a definition | 643 | 1000 |
| few_large_clusters | 0.0 | group_risk | principal | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 0.0 | group_risk | never | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 0.0 | delta_s | never_minus_principal | True | common_support | too few distinct patients in a definition | 1000 | 1000 |
| few_large_clusters | 1.0 | group_risk | principal | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 1.0 | group_risk | never | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 1.0 | delta_s | never_minus_principal | True | common_support | too few distinct patients in a definition | 1000 | 1000 |
| few_large_clusters | 2.0 | group_risk | principal | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 2.0 | group_risk | never | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 2.0 | delta_s | never_minus_principal | True | common_support | too few distinct patients in a definition | 1000 | 1000 |
| few_large_clusters | 3.0 | group_risk | principal | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 3.0 | group_risk | never | True | common_support | too few distinct patients | 1000 | 1000 |
| few_large_clusters | 3.0 | delta_s | never_minus_principal | True | common_support | too few distinct patients in a definition | 1000 | 1000 |
| no_common_support | 0.0 | group_risk | principal | True | one_definition_support | computed | 1000 | 1000 |
| no_common_support | 0.0 | group_risk | never | False | one_definition_support | no records | 1000 | 0 |
| no_common_support | 0.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| no_common_support | 1.0 | group_risk | principal | True | one_definition_support | computed | 1000 | 1000 |
| no_common_support | 1.0 | group_risk | never | False | one_definition_support | no records | 1000 | 0 |
| no_common_support | 1.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| no_common_support | 2.0 | group_risk | principal | False | one_definition_support | no records | 1000 | 0 |
| no_common_support | 2.0 | group_risk | never | True | one_definition_support | computed | 1000 | 1000 |
| no_common_support | 2.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| no_common_support | 3.0 | group_risk | principal | False | one_definition_support | no records | 1000 | 0 |
| no_common_support | 3.0 | group_risk | never | True | one_definition_support | computed | 1000 | 1000 |
| no_common_support | 3.0 | delta_s | never_minus_principal | False | one_definition_support | no shared support | 1000 | 0 |
| high_icc_unbalanced_holdout | 0.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 0.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 0.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 1.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 1.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 1.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 2.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 2.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 2.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 3.0 | group_risk | principal | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 3.0 | group_risk | never | True | common_support | computed | 1000 | 1000 |
| high_icc_unbalanced_holdout | 3.0 | delta_s | never_minus_principal | True | common_support | computed | 1000 | 1000 |

## Supplementary Table 51. Score-level coverage sensitivity to rounding

| design | replicate | level | method | arm | truth_pp | issued_lower_pp | issued_upper_pp | fullprecision_lower_pp | fullprecision_upper_pp | issued_rounded_covered | fullprecision_covered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | 210 | 1.0 | group_risk | never | 20.0 | 20.0 | 36.37 | 20.00177004500231 | 36.37139895166396 | True | False |
| null_balanced_iid | 346 | 1.0 | group_risk | principal | 20.0 | 20.0 | 35.19 | 20.000286037856004 | 35.18810216285135 | True | False |
| null_balanced_iid | 467 | 1.0 | group_risk | principal | 20.0 | 20.0 | 35.19 | 20.000286037856004 | 35.18810216285135 | True | False |
| null_balanced_iid | 803 | 1.0 | delta_s | never_minus_principal | 0.0 | -20.34 | -0.0 | -20.341793365570993 | -0.004816546256308785 | True | False |
| null_heterogeneous_iid | 712 | 1.0 | delta_s | never_minus_principal | -10.0 | -10.0 | 4.66 | -9.996206400971925 | 4.657195591931639 | True | False |
| null_heterogeneous_iid | 905 | 1.0 | delta_s | never_minus_principal | -10.0 | -10.0 | 5.37 | -9.996870651386303 | 5.373826554657995 | True | False |
| heterogeneous_random_weights | 607 | 3.0 | group_risk | principal | 35.0 | 8.4 | 35.0 | 8.401045210359566 | 34.99882037531024 | True | False |
| heterogeneous_random_weights | 663 | 1.0 | delta_s | never_minus_principal | -20.0 | -20.0 | 2.21 | -19.99843805929319 | 2.2134136017489743 | True | False |
| heterogeneous_random_weights | 772 | 0.0 | group_risk | never | 30.0 | 30.0 | 52.03 | 30.000851592871285 | 52.03070244915082 | True | False |
| unequal_cluster_sizes | 690 | 3.0 | group_risk | never | 60.0 | 60.0 | 70.66 | 60.001015768397245 | 70.66457242813767 | True | False |
| unequal_cluster_sizes | 939 | 0.0 | group_risk | principal | 8.0 | 8.0 | 15.58 | 8.004386316423723 | 15.578628732321102 | True | False |
| near_boundary_risks | 10 | 3.0 | group_risk | principal | 85.0 | 74.69 | 85.0 | 74.69151794267927 | 84.99641105209966 | True | False |
| near_boundary_risks | 648 | 2.0 | delta_s | never_minus_principal | 4.999999999999993 | -12.5 | 5.0 | -12.498311780242878 | 4.9956842436594835 | True | False |
| rare_common_support_holdout | 379 | 1.0 | delta_s | never_minus_principal | 4.999999999999999 | 5.0 | 21.34 | 4.998639449603635 | 21.341562138122704 | False | True |
| rare_common_support_holdout | 626 | 0.0 | group_risk | never | 15.0 | 6.25 | 15.0 | 6.248541427963481 | 14.995769433376394 | True | False |
| no_common_support | 25 | 1.0 | group_risk | principal | 20.0 | 11.05 | 20.0 | 11.048253231829237 | 19.99578976654123 | True | False |

## Supplementary Table 52. Score-level δ_s validation results

| design | level | estimand | arm | support_type | truth_defined | truth_pp | n_design_replicates | n_eligible_replicates | n_point_available | point_available_rate | n_ci_emitted | output_rate | output_rate_mcse | n_covered | conditional_coverage | conditional_coverage_mcse | bias_pp_point_available | bias_pp_ci_emitted | refusal_counts_json | principal_records_mean | principal_records_median | principal_records_min | principal_records_max | never_records_mean | never_records_median | never_records_min | never_records_max | principal_patients_mean | principal_patients_median | principal_patients_min | principal_patients_max | never_patients_mean | never_patients_median | never_patients_min | never_patients_max | principal_events_mean | principal_events_median | principal_events_min | principal_events_max | never_events_mean | never_events_median | never_events_min | never_events_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_balanced_iid | 0.0 | group_risk | principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 961 | 0.961 | 0.006122009474020767 | 0.14981999999999995 | 0.14981999999999995 | {} | 124.472 | 125.0 | 88.0 | 160.0 | 125.651 | 126.0 | 91.0 | 166.0 | 124.472 | 125.0 | 88.0 | 160.0 | 125.651 | 126.0 | 91.0 | 166.0 | 12.625 | 13.0 | 3.0 | 25.0 | 12.749 | 13.0 | 3.0 | 24.0 |
| null_balanced_iid | 0.0 | group_risk | never | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 959 | 0.959 | 0.006270486424512857 | 0.13634000000000004 | 0.13634000000000004 | {} | 124.472 | 125.0 | 88.0 | 160.0 | 125.651 | 126.0 | 91.0 | 166.0 | 124.472 | 125.0 | 88.0 | 160.0 | 125.651 | 126.0 | 91.0 | 166.0 | 12.625 | 13.0 | 3.0 | 25.0 | 12.749 | 13.0 | 3.0 | 24.0 |
| null_balanced_iid | 0.0 | delta_s | never_minus_principal | common_support | True | 0.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | -0.013579999999999995 | -0.013579999999999995 | {} | 124.472 | 125.0 | 88.0 | 160.0 | 125.651 | 126.0 | 91.0 | 166.0 | 124.472 | 125.0 | 88.0 | 160.0 | 125.651 | 126.0 | 91.0 | 166.0 | 12.625 | 13.0 | 3.0 | 25.0 | 12.749 | 13.0 | 3.0 | 24.0 |
| null_balanced_iid | 1.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 959 | 0.959 | 0.006270486424512857 | 0.12644 | 0.12644 | {} | 124.679 | 124.0 | 92.0 | 157.0 | 124.412 | 124.0 | 93.0 | 159.0 | 124.679 | 124.0 | 92.0 | 157.0 | 124.412 | 124.0 | 93.0 | 159.0 | 25.086 | 25.0 | 12.0 | 41.0 | 24.427 | 24.0 | 10.0 | 40.0 |
| null_balanced_iid | 1.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | -0.36587000000000003 | -0.36587000000000003 | {} | 124.679 | 124.0 | 92.0 | 157.0 | 124.412 | 124.0 | 93.0 | 159.0 | 124.679 | 124.0 | 92.0 | 157.0 | 124.412 | 124.0 | 93.0 | 159.0 | 25.086 | 25.0 | 12.0 | 41.0 | 24.427 | 24.0 | 10.0 | 40.0 |
| null_balanced_iid | 1.0 | delta_s | never_minus_principal | common_support | True | 0.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | -0.4920799999999999 | -0.4920799999999999 | {} | 124.679 | 124.0 | 92.0 | 157.0 | 124.412 | 124.0 | 93.0 | 159.0 | 124.679 | 124.0 | 92.0 | 157.0 | 124.412 | 124.0 | 93.0 | 159.0 | 25.086 | 25.0 | 12.0 | 41.0 | 24.427 | 24.0 | 10.0 | 40.0 |
| null_balanced_iid | 2.0 | group_risk | principal | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 952 | 0.952 | 0.006759881655768837 | -0.17482999999999999 | -0.17482999999999999 | {} | 125.077 | 125.0 | 94.0 | 158.0 | 125.397 | 125.0 | 91.0 | 157.0 | 125.077 | 125.0 | 94.0 | 158.0 | 125.397 | 125.0 | 91.0 | 157.0 | 37.299 | 37.0 | 21.0 | 56.0 | 37.387 | 37.0 | 20.0 | 55.0 |
| null_balanced_iid | 2.0 | group_risk | never | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 951 | 0.951 | 0.006826346021115546 | -0.19487 | -0.19487 | {} | 125.077 | 125.0 | 94.0 | 158.0 | 125.397 | 125.0 | 91.0 | 157.0 | 125.077 | 125.0 | 94.0 | 158.0 | 125.397 | 125.0 | 91.0 | 157.0 | 37.299 | 37.0 | 21.0 | 56.0 | 37.387 | 37.0 | 20.0 | 55.0 |
| null_balanced_iid | 2.0 | delta_s | never_minus_principal | common_support | True | 0.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 946 | 0.946 | 0.0071473071852271785 | -0.02014 | -0.02014 | {} | 125.077 | 125.0 | 94.0 | 158.0 | 125.397 | 125.0 | 91.0 | 157.0 | 125.077 | 125.0 | 94.0 | 158.0 | 125.397 | 125.0 | 91.0 | 157.0 | 37.299 | 37.0 | 21.0 | 56.0 | 37.387 | 37.0 | 20.0 | 55.0 |
| null_balanced_iid | 3.0 | group_risk | principal | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 946 | 0.946 | 0.0071473071852271785 | -0.19423999999999997 | -0.19423999999999997 | {} | 125.284 | 125.0 | 96.0 | 159.0 | 125.028 | 125.0 | 89.0 | 162.0 | 125.284 | 125.0 | 96.0 | 159.0 | 125.028 | 125.0 | 89.0 | 162.0 | 49.861 | 50.0 | 29.0 | 79.0 | 49.762 | 50.0 | 29.0 | 73.0 |
| null_balanced_iid | 3.0 | group_risk | never | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 965 | 0.965 | 0.005811626278418119 | -0.22406 | -0.22406 | {} | 125.284 | 125.0 | 96.0 | 159.0 | 125.028 | 125.0 | 89.0 | 162.0 | 125.284 | 125.0 | 96.0 | 159.0 | 125.028 | 125.0 | 89.0 | 162.0 | 49.861 | 50.0 | 29.0 | 79.0 | 49.762 | 50.0 | 29.0 | 73.0 |
| null_balanced_iid | 3.0 | delta_s | never_minus_principal | common_support | True | 0.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 936 | 0.936 | 0.007739767438366605 | -0.02958000000000004 | -0.02958000000000004 | {} | 125.284 | 125.0 | 96.0 | 159.0 | 125.028 | 125.0 | 89.0 | 162.0 | 125.284 | 125.0 | 96.0 | 159.0 | 125.028 | 125.0 | 89.0 | 162.0 | 49.861 | 50.0 | 29.0 | 79.0 | 49.762 | 50.0 | 29.0 | 73.0 |
| null_heterogeneous_iid | 0.0 | group_risk | principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 949 | 0.949 | 0.006956938982052382 | -0.22676 | -0.22676 | {} | 149.675 | 149.5 | 114.0 | 188.0 | 149.689 | 149.0 | 117.0 | 183.0 | 149.675 | 149.5 | 114.0 | 188.0 | 149.689 | 149.0 | 117.0 | 183.0 | 14.632 | 14.5 | 4.0 | 28.0 | 29.953 | 30.0 | 12.0 | 46.0 |
| null_heterogeneous_iid | 0.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | -0.003200000000000074 | -0.003200000000000074 | {} | 149.675 | 149.5 | 114.0 | 188.0 | 149.689 | 149.0 | 117.0 | 183.0 | 149.675 | 149.5 | 114.0 | 188.0 | 149.689 | 149.0 | 117.0 | 183.0 | 14.632 | 14.5 | 4.0 | 28.0 | 29.953 | 30.0 | 12.0 | 46.0 |
| null_heterogeneous_iid | 0.0 | delta_s | never_minus_principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 957 | 0.957 | 0.006414904519944161 | 0.22317 | 0.22317 | {} | 149.675 | 149.5 | 114.0 | 188.0 | 149.689 | 149.0 | 117.0 | 183.0 | 149.675 | 149.5 | 114.0 | 188.0 | 149.689 | 149.0 | 117.0 | 183.0 | 14.632 | 14.5 | 4.0 | 28.0 | 29.953 | 30.0 | 12.0 | 46.0 |
| null_heterogeneous_iid | 1.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 946 | 0.946 | 0.0071473071852271785 | 0.19086999999999996 | 0.19086999999999996 | {} | 149.83 | 150.0 | 113.0 | 185.0 | 150.427 | 150.0 | 114.0 | 185.0 | 149.83 | 150.0 | 113.0 | 185.0 | 150.427 | 150.0 | 114.0 | 185.0 | 30.263 | 30.0 | 15.0 | 48.0 | 15.112 | 15.0 | 5.0 | 28.0 |
| null_heterogeneous_iid | 1.0 | group_risk | never | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 942 | 0.942 | 0.007391616873188169 | 0.05421 | 0.05421 | {} | 149.83 | 150.0 | 113.0 | 185.0 | 150.427 | 150.0 | 114.0 | 185.0 | 149.83 | 150.0 | 113.0 | 185.0 | 150.427 | 150.0 | 114.0 | 185.0 | 30.263 | 30.0 | 15.0 | 48.0 | 15.112 | 15.0 | 5.0 | 28.0 |
| null_heterogeneous_iid | 1.0 | delta_s | never_minus_principal | common_support | True | -10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 939 | 0.939 | 0.007568289106528638 | -0.13636 | -0.13636 | {} | 149.83 | 150.0 | 113.0 | 185.0 | 150.427 | 150.0 | 114.0 | 185.0 | 149.83 | 150.0 | 113.0 | 185.0 | 150.427 | 150.0 | 114.0 | 185.0 | 30.263 | 30.0 | 15.0 | 48.0 | 15.112 | 15.0 | 5.0 | 28.0 |
| null_heterogeneous_iid | 2.0 | group_risk | principal | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 956 | 0.956 | 0.006485676526007139 | 0.040569999999999974 | 0.040569999999999974 | {} | 149.621 | 150.0 | 115.0 | 184.0 | 150.327 | 150.0 | 115.0 | 187.0 | 149.621 | 150.0 | 115.0 | 184.0 | 150.327 | 150.0 | 115.0 | 187.0 | 44.958 | 45.0 | 25.0 | 73.0 | 60.181 | 60.0 | 34.0 | 87.0 |
| null_heterogeneous_iid | 2.0 | group_risk | never | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 957 | 0.957 | 0.006414904519944161 | 0.01796999999999988 | 0.01796999999999988 | {} | 149.621 | 150.0 | 115.0 | 184.0 | 150.327 | 150.0 | 115.0 | 187.0 | 149.621 | 150.0 | 115.0 | 184.0 | 150.327 | 150.0 | 115.0 | 187.0 | 44.958 | 45.0 | 25.0 | 73.0 | 60.181 | 60.0 | 34.0 | 87.0 |
| null_heterogeneous_iid | 2.0 | delta_s | never_minus_principal | common_support | True | 10.000000000000004 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 942 | 0.942 | 0.007391616873188169 | -0.02254000000000355 | -0.02254000000000355 | {} | 149.621 | 150.0 | 115.0 | 184.0 | 150.327 | 150.0 | 115.0 | 187.0 | 149.621 | 150.0 | 115.0 | 184.0 | 150.327 | 150.0 | 115.0 | 187.0 | 44.958 | 45.0 | 25.0 | 73.0 | 60.181 | 60.0 | 34.0 | 87.0 |
| null_heterogeneous_iid | 3.0 | group_risk | principal | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 953 | 0.953 | 0.00669260786241059 | 0.20584999999999998 | 0.20584999999999998 | {} | 150.717 | 151.0 | 113.0 | 182.0 | 149.714 | 150.0 | 110.0 | 187.0 | 150.717 | 151.0 | 113.0 | 182.0 | 149.714 | 150.0 | 110.0 | 187.0 | 60.567 | 61.0 | 35.0 | 84.0 | 45.189 | 45.0 | 26.0 | 69.0 |
| null_heterogeneous_iid | 3.0 | group_risk | never | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 944 | 0.944 | 0.007270763371201131 | 0.16851999999999998 | 0.16851999999999998 | {} | 150.717 | 151.0 | 113.0 | 182.0 | 149.714 | 150.0 | 110.0 | 187.0 | 150.717 | 151.0 | 113.0 | 182.0 | 149.714 | 150.0 | 110.0 | 187.0 | 60.567 | 61.0 | 35.0 | 84.0 | 45.189 | 45.0 | 26.0 | 69.0 |
| null_heterogeneous_iid | 3.0 | delta_s | never_minus_principal | common_support | True | -10.000000000000004 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | -0.03715999999999643 | -0.03715999999999643 | {} | 150.717 | 151.0 | 113.0 | 182.0 | 149.714 | 150.0 | 110.0 | 187.0 | 150.717 | 151.0 | 113.0 | 182.0 | 149.714 | 150.0 | 110.0 | 187.0 | 60.567 | 61.0 | 35.0 | 84.0 | 45.189 | 45.0 | 26.0 | 69.0 |
| heterogeneous_random_weights | 0.0 | group_risk | principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 936 | 0.936 | 0.007739767438366605 | 0.03504999999999998 | 0.03504999999999998 | {} | 384.324 | 384.0 | 332.0 | 434.0 | 59.967 | 60.0 | 36.0 | 82.0 | 384.324 | 384.0 | 332.0 | 434.0 | 59.967 | 60.0 | 36.0 | 82.0 | 38.568 | 38.0 | 22.0 | 57.0 | 18.026 | 18.0 | 8.0 | 32.0 |
| heterogeneous_random_weights | 0.0 | group_risk | never | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | 0.03829999999999998 | 0.03829999999999998 | {} | 384.324 | 384.0 | 332.0 | 434.0 | 59.967 | 60.0 | 36.0 | 82.0 | 384.324 | 384.0 | 332.0 | 434.0 | 59.967 | 60.0 | 36.0 | 82.0 | 38.568 | 38.0 | 22.0 | 57.0 | 18.026 | 18.0 | 8.0 | 32.0 |
| heterogeneous_random_weights | 0.0 | delta_s | never_minus_principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 942 | 0.942 | 0.007391616873188169 | 0.0032199999999999703 | 0.0032199999999999703 | {} | 384.324 | 384.0 | 332.0 | 434.0 | 59.967 | 60.0 | 36.0 | 82.0 | 384.324 | 384.0 | 332.0 | 434.0 | 59.967 | 60.0 | 36.0 | 82.0 | 38.568 | 38.0 | 22.0 | 57.0 | 18.026 | 18.0 | 8.0 | 32.0 |
| heterogeneous_random_weights | 1.0 | group_risk | principal | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 954 | 0.954 | 0.006624499981130654 | -0.23717999999999995 | -0.23717999999999995 | {} | 120.085 | 120.0 | 89.0 | 155.0 | 119.48 | 119.0 | 85.0 | 149.0 | 120.085 | 120.0 | 89.0 | 155.0 | 119.48 | 119.0 | 85.0 | 149.0 | 47.767 | 48.0 | 31.0 | 75.0 | 24.061 | 24.0 | 9.0 | 43.0 |
| heterogeneous_random_weights | 1.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | 0.13823000000000002 | 0.13823000000000002 | {} | 120.085 | 120.0 | 89.0 | 155.0 | 119.48 | 119.0 | 85.0 | 149.0 | 120.085 | 120.0 | 89.0 | 155.0 | 119.48 | 119.0 | 85.0 | 149.0 | 47.767 | 48.0 | 31.0 | 75.0 | 24.061 | 24.0 | 9.0 | 43.0 |
| heterogeneous_random_weights | 1.0 | delta_s | never_minus_principal | common_support | True | -20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 949 | 0.949 | 0.006956938982052382 | 0.37549 | 0.37549 | {} | 120.085 | 120.0 | 89.0 | 155.0 | 119.48 | 119.0 | 85.0 | 149.0 | 120.085 | 120.0 | 89.0 | 155.0 | 119.48 | 119.0 | 85.0 | 149.0 | 47.767 | 48.0 | 31.0 | 75.0 | 24.061 | 24.0 | 9.0 | 43.0 |
| heterogeneous_random_weights | 2.0 | group_risk | principal | common_support | True | 15.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 962 | 0.962 | 0.006046155803483734 | -0.20686000000000007 | -0.20686000000000007 | {} | 59.718 | 60.0 | 37.0 | 80.0 | 144.088 | 144.0 | 112.0 | 178.0 | 59.718 | 60.0 | 37.0 | 80.0 | 144.088 | 144.0 | 112.0 | 178.0 | 8.823 | 9.0 | 1.0 | 19.0 | 35.904 | 36.0 | 19.0 | 59.0 |
| heterogeneous_random_weights | 2.0 | group_risk | never | common_support | True | 25.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | -0.09979000000000006 | -0.09979000000000006 | {} | 59.718 | 60.0 | 37.0 | 80.0 | 144.088 | 144.0 | 112.0 | 178.0 | 59.718 | 60.0 | 37.0 | 80.0 | 144.088 | 144.0 | 112.0 | 178.0 | 8.823 | 9.0 | 1.0 | 19.0 | 35.904 | 36.0 | 19.0 | 59.0 |
| heterogeneous_random_weights | 2.0 | delta_s | never_minus_principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 928 | 0.928 | 0.00817410545564467 | 0.10697999999999996 | 0.10697999999999996 | {} | 59.718 | 60.0 | 37.0 | 80.0 | 144.088 | 144.0 | 112.0 | 178.0 | 59.718 | 60.0 | 37.0 | 80.0 | 144.088 | 144.0 | 112.0 | 178.0 | 8.823 | 9.0 | 1.0 | 19.0 | 35.904 | 36.0 | 19.0 | 59.0 |
| heterogeneous_random_weights | 3.0 | group_risk | principal | common_support | True | 35.0 | 1000 | 1000 | 1000 | 1.0 | 998 | 0.998 | 0.0014127986409959495 | 956 | 0.9579158316633266 | 0.006355617898349741 | 0.0021499999999999774 | 0.013627254509018001 | {"too few distinct patients": 2} | 35.796 | 36.0 | 16.0 | 57.0 | 276.542 | 277.0 | 230.0 | 329.0 | 35.796 | 36.0 | 16.0 | 57.0 | 276.542 | 277.0 | 230.0 | 329.0 | 12.534 | 12.0 | 3.0 | 28.0 | 27.453 | 27.0 | 13.0 | 44.0 |
| heterogeneous_random_weights | 3.0 | group_risk | never | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 954 | 0.954 | 0.006624499981130654 | -0.07694000000000002 | -0.07694000000000002 | {} | 35.796 | 36.0 | 16.0 | 57.0 | 276.542 | 277.0 | 230.0 | 329.0 | 35.796 | 36.0 | 16.0 | 57.0 | 276.542 | 277.0 | 230.0 | 329.0 | 12.534 | 12.0 | 3.0 | 28.0 | 27.453 | 27.0 | 13.0 | 44.0 |
| heterogeneous_random_weights | 3.0 | delta_s | never_minus_principal | common_support | True | -25.0 | 1000 | 1000 | 1000 | 1.0 | 998 | 0.998 | 0.0014127986409959495 | 940 | 0.9418837675350702 | 0.007405972782472367 | -0.07906000000000012 | -0.09320641282565134 | {"too few distinct patients in a definition": 2} | 35.796 | 36.0 | 16.0 | 57.0 | 276.542 | 277.0 | 230.0 | 329.0 | 35.796 | 36.0 | 16.0 | 57.0 | 276.542 | 277.0 | 230.0 | 329.0 | 12.534 | 12.0 | 3.0 | 28.0 | 27.453 | 27.0 | 13.0 | 44.0 |
| repeated_admissions_cross_group | 0.0 | group_risk | principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | 0.06295000000000005 | 0.06295000000000005 | {} | 337.704 | 338.0 | 289.0 | 385.0 | 337.424 | 338.0 | 291.0 | 393.0 | 297.265 | 297.0 | 255.0 | 339.0 | 297.028 | 297.0 | 258.0 | 340.0 | 33.977 | 34.0 | 17.0 | 55.0 | 67.609 | 68.0 | 42.0 | 99.0 |
| repeated_admissions_cross_group | 0.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | 0.037509999999999946 | 0.037509999999999946 | {} | 337.704 | 338.0 | 289.0 | 385.0 | 337.424 | 338.0 | 291.0 | 393.0 | 297.265 | 297.0 | 255.0 | 339.0 | 297.028 | 297.0 | 258.0 | 340.0 | 33.977 | 34.0 | 17.0 | 55.0 | 67.609 | 68.0 | 42.0 | 99.0 |
| repeated_admissions_cross_group | 0.0 | delta_s | never_minus_principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 959 | 0.959 | 0.006270486424512857 | -0.025219999999999965 | -0.025219999999999965 | {} | 337.704 | 338.0 | 289.0 | 385.0 | 337.424 | 338.0 | 291.0 | 393.0 | 297.265 | 297.0 | 255.0 | 339.0 | 297.028 | 297.0 | 258.0 | 340.0 | 33.977 | 34.0 | 17.0 | 55.0 | 67.609 | 68.0 | 42.0 | 99.0 |
| repeated_admissions_cross_group | 1.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 952 | 0.952 | 0.006759881655768837 | -0.04908999999999996 | -0.04908999999999996 | {} | 338.056 | 338.0 | 288.0 | 400.0 | 338.781 | 339.0 | 286.0 | 395.0 | 297.362 | 297.0 | 253.0 | 345.0 | 298.077 | 298.0 | 257.0 | 344.0 | 67.444 | 67.0 | 46.0 | 91.0 | 85.125 | 85.0 | 52.0 | 123.0 |
| repeated_admissions_cross_group | 1.0 | group_risk | never | common_support | True | 25.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 942 | 0.942 | 0.007391616873188169 | 0.12389000000000006 | 0.12389000000000006 | {} | 338.056 | 338.0 | 288.0 | 400.0 | 338.781 | 339.0 | 286.0 | 395.0 | 297.362 | 297.0 | 253.0 | 345.0 | 298.077 | 298.0 | 257.0 | 344.0 | 67.444 | 67.0 | 46.0 | 91.0 | 85.125 | 85.0 | 52.0 | 123.0 |
| repeated_admissions_cross_group | 1.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 947 | 0.947 | 0.007084560677981384 | 0.1727100000000009 | 0.1727100000000009 | {} | 338.056 | 338.0 | 288.0 | 400.0 | 338.781 | 339.0 | 286.0 | 395.0 | 297.362 | 297.0 | 253.0 | 345.0 | 298.077 | 298.0 | 257.0 | 344.0 | 67.444 | 67.0 | 46.0 | 91.0 | 85.125 | 85.0 | 52.0 | 123.0 |
| repeated_admissions_cross_group | 2.0 | group_risk | principal | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 961 | 0.961 | 0.006122009474020767 | 0.09365999999999995 | 0.09365999999999995 | {} | 337.533 | 337.0 | 281.0 | 389.0 | 336.863 | 336.0 | 284.0 | 393.0 | 297.245 | 297.0 | 254.0 | 339.0 | 296.253 | 296.0 | 246.0 | 339.0 | 101.591 | 101.0 | 65.0 | 132.0 | 117.568 | 117.0 | 88.0 | 152.0 |
| repeated_admissions_cross_group | 2.0 | group_risk | never | common_support | True | 35.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | -0.09658000000000001 | -0.09658000000000001 | {} | 337.533 | 337.0 | 281.0 | 389.0 | 336.863 | 336.0 | 284.0 | 393.0 | 297.245 | 297.0 | 254.0 | 339.0 | 296.253 | 296.0 | 246.0 | 339.0 | 101.591 | 101.0 | 65.0 | 132.0 | 117.568 | 117.0 | 88.0 | 152.0 |
| repeated_admissions_cross_group | 2.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 945 | 0.945 | 0.007209368904418752 | -0.1899299999999991 | -0.1899299999999991 | {} | 337.533 | 337.0 | 281.0 | 389.0 | 336.863 | 336.0 | 284.0 | 393.0 | 297.245 | 297.0 | 254.0 | 339.0 | 296.253 | 296.0 | 246.0 | 339.0 | 101.591 | 101.0 | 65.0 | 132.0 | 117.568 | 117.0 | 88.0 | 152.0 |
| repeated_admissions_cross_group | 3.0 | group_risk | principal | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 961 | 0.961 | 0.006122009474020767 | -0.06484999999999999 | -0.06484999999999999 | {} | 336.944 | 336.5 | 278.0 | 384.0 | 336.695 | 337.0 | 285.0 | 389.0 | 296.721 | 297.0 | 253.0 | 339.0 | 296.492 | 297.0 | 252.0 | 335.0 | 134.55 | 134.0 | 97.0 | 183.0 | 168.311 | 168.0 | 132.0 | 204.0 |
| repeated_admissions_cross_group | 3.0 | group_risk | never | common_support | True | 50.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 953 | 0.953 | 0.00669260786241059 | -0.011459999999999994 | -0.011459999999999994 | {} | 336.944 | 336.5 | 278.0 | 384.0 | 336.695 | 337.0 | 285.0 | 389.0 | 296.721 | 297.0 | 253.0 | 339.0 | 296.492 | 297.0 | 252.0 | 335.0 | 134.55 | 134.0 | 97.0 | 183.0 | 168.311 | 168.0 | 132.0 | 204.0 |
| repeated_admissions_cross_group | 3.0 | delta_s | never_minus_principal | common_support | True | 9.999999999999998 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 951 | 0.951 | 0.006826346021115546 | 0.053600000000001785 | 0.053600000000001785 | {} | 336.944 | 336.5 | 278.0 | 384.0 | 336.695 | 337.0 | 285.0 | 389.0 | 296.721 | 297.0 | 253.0 | 339.0 | 296.492 | 297.0 | 252.0 | 335.0 | 134.55 | 134.0 | 97.0 | 183.0 | 168.311 | 168.0 | 132.0 | 204.0 |
| unequal_cluster_sizes | 0.0 | group_risk | principal | common_support | True | 8.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | 0.03105999999999999 | 0.03105999999999999 | {} | 328.41 | 328.0 | 264.0 | 400.0 | 82.03 | 82.0 | 51.0 | 114.0 | 264.317 | 264.0 | 219.0 | 312.0 | 77.152 | 77.0 | 49.0 | 105.0 | 26.364 | 26.0 | 12.0 | 51.0 | 14.83 | 15.0 | 3.0 | 32.0 |
| unequal_cluster_sizes | 0.0 | group_risk | never | common_support | True | 18.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 960 | 0.96 | 0.00619677335393187 | 0.09332000000000004 | 0.09332000000000004 | {} | 328.41 | 328.0 | 264.0 | 400.0 | 82.03 | 82.0 | 51.0 | 114.0 | 264.317 | 264.0 | 219.0 | 312.0 | 77.152 | 77.0 | 49.0 | 105.0 | 26.364 | 26.0 | 12.0 | 51.0 | 14.83 | 15.0 | 3.0 | 32.0 |
| unequal_cluster_sizes | 0.0 | delta_s | never_minus_principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 939 | 0.939 | 0.007568289106528638 | 0.06245999999999999 | 0.06245999999999999 | {} | 328.41 | 328.0 | 264.0 | 400.0 | 82.03 | 82.0 | 51.0 | 114.0 | 264.317 | 264.0 | 219.0 | 312.0 | 77.152 | 77.0 | 49.0 | 105.0 | 26.364 | 26.0 | 12.0 | 51.0 | 14.83 | 15.0 | 3.0 | 32.0 |
| unequal_cluster_sizes | 1.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 949 | 0.949 | 0.006956938982052382 | -0.17468999999999993 | -0.17468999999999993 | {} | 245.878 | 246.0 | 196.0 | 317.0 | 164.319 | 164.0 | 117.0 | 209.0 | 207.866 | 208.0 | 173.0 | 249.0 | 146.234 | 146.0 | 110.0 | 186.0 | 48.745 | 49.0 | 28.0 | 73.0 | 49.258 | 49.0 | 28.0 | 73.0 |
| unequal_cluster_sizes | 1.0 | group_risk | never | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 952 | 0.952 | 0.006759881655768837 | -0.025360000000000056 | -0.025360000000000056 | {} | 245.878 | 246.0 | 196.0 | 317.0 | 164.319 | 164.0 | 117.0 | 209.0 | 207.866 | 208.0 | 173.0 | 249.0 | 146.234 | 146.0 | 110.0 | 186.0 | 48.745 | 49.0 | 28.0 | 73.0 | 49.258 | 49.0 | 28.0 | 73.0 |
| unequal_cluster_sizes | 1.0 | delta_s | never_minus_principal | common_support | True | 9.999999999999998 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | 0.14911000000000182 | 0.14911000000000182 | {} | 245.878 | 246.0 | 196.0 | 317.0 | 164.319 | 164.0 | 117.0 | 209.0 | 207.866 | 208.0 | 173.0 | 249.0 | 146.234 | 146.0 | 110.0 | 186.0 | 48.745 | 49.0 | 28.0 | 73.0 | 49.258 | 49.0 | 28.0 | 73.0 |
| unequal_cluster_sizes | 2.0 | group_risk | principal | common_support | True | 35.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | -0.1641900000000001 | -0.1641900000000001 | {} | 163.596 | 164.0 | 112.0 | 204.0 | 246.974 | 247.0 | 200.0 | 304.0 | 145.865 | 146.0 | 101.0 | 181.0 | 208.483 | 208.0 | 169.0 | 252.0 | 56.981 | 57.0 | 34.0 | 82.0 | 61.931 | 62.0 | 40.0 | 86.0 |
| unequal_cluster_sizes | 2.0 | group_risk | never | common_support | True | 25.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 959 | 0.959 | 0.006270486424512857 | 0.06912000000000003 | 0.06912000000000003 | {} | 163.596 | 164.0 | 112.0 | 204.0 | 246.974 | 247.0 | 200.0 | 304.0 | 145.865 | 146.0 | 101.0 | 181.0 | 208.483 | 208.0 | 169.0 | 252.0 | 56.981 | 57.0 | 34.0 | 82.0 | 61.931 | 62.0 | 40.0 | 86.0 |
| unequal_cluster_sizes | 2.0 | delta_s | never_minus_principal | common_support | True | -9.999999999999998 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 963 | 0.963 | 0.005969170796685251 | 0.23325999999999825 | 0.23325999999999825 | {} | 163.596 | 164.0 | 112.0 | 204.0 | 246.974 | 247.0 | 200.0 | 304.0 | 145.865 | 146.0 | 101.0 | 181.0 | 208.483 | 208.0 | 169.0 | 252.0 | 56.981 | 57.0 | 34.0 | 82.0 | 61.931 | 62.0 | 40.0 | 86.0 |
| unequal_cluster_sizes | 3.0 | group_risk | principal | common_support | True | 50.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 944 | 0.944 | 0.007270763371201131 | -0.10603999999999997 | -0.10603999999999997 | {} | 82.194 | 82.0 | 51.0 | 123.0 | 328.301 | 327.0 | 275.0 | 390.0 | 77.428 | 77.0 | 49.0 | 114.0 | 264.03 | 264.0 | 224.0 | 304.0 | 41.02 | 41.0 | 23.0 | 61.0 | 197.157 | 196.0 | 154.0 | 250.0 |
| unequal_cluster_sizes | 3.0 | group_risk | never | common_support | True | 60.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | 0.055539999999999964 | 0.055539999999999964 | {} | 82.194 | 82.0 | 51.0 | 123.0 | 328.301 | 327.0 | 275.0 | 390.0 | 77.428 | 77.0 | 49.0 | 114.0 | 264.03 | 264.0 | 224.0 | 304.0 | 41.02 | 41.0 | 23.0 | 61.0 | 197.157 | 196.0 | 154.0 | 250.0 |
| unequal_cluster_sizes | 3.0 | delta_s | never_minus_principal | common_support | True | 9.999999999999998 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 939 | 0.939 | 0.007568289106528638 | 0.1617800000000017 | 0.1617800000000017 | {} | 82.194 | 82.0 | 51.0 | 123.0 | 328.301 | 327.0 | 275.0 | 390.0 | 77.428 | 77.0 | 49.0 | 114.0 | 264.03 | 264.0 | 224.0 | 304.0 | 41.02 | 41.0 | 23.0 | 61.0 | 197.157 | 196.0 | 154.0 | 250.0 |
| near_boundary_risks | 0.0 | group_risk | principal | common_support | True | 0.5 | 1000 | 1000 | 1000 | 1.0 | 672 | 0.672 | 0.014846413708367418 | 649 | 0.9657738095238095 | 0.007013460523479246 | -0.017920000000000002 | 0.21738095238095237 | {"degenerate outcome: point estimate only": 328} | 224.058 | 224.0 | 181.0 | 264.0 | 224.777 | 225.0 | 178.0 | 268.0 | 224.058 | 224.0 | 181.0 | 264.0 | 224.777 | 225.0 | 178.0 | 268.0 | 1.081 | 1.0 | 0.0 | 5.0 | 2.238 | 2.0 | 0.0 | 8.0 |
| near_boundary_risks | 0.0 | group_risk | never | common_support | True | 1.0 | 1000 | 1000 | 1000 | 1.0 | 885 | 0.885 | 0.010088359628799917 | 858 | 0.9694915254237289 | 0.005781101839663886 | -0.003930000000000006 | 0.12550282485875705 | {"degenerate outcome: point estimate only": 115} | 224.058 | 224.0 | 181.0 | 264.0 | 224.777 | 225.0 | 178.0 | 268.0 | 224.058 | 224.0 | 181.0 | 264.0 | 224.777 | 225.0 | 178.0 | 268.0 | 1.081 | 1.0 | 0.0 | 5.0 | 2.238 | 2.0 | 0.0 | 8.0 |
| near_boundary_risks | 0.0 | delta_s | never_minus_principal | common_support | True | 0.5 | 1000 | 1000 | 1000 | 1.0 | 598 | 0.598 | 0.015504708962118573 | 597 | 0.9983277591973244 | 0.0016708420230057335 | 0.014090000000000002 | -0.08705685618729098 | {"degenerate outcome: point estimate only": 402} | 224.058 | 224.0 | 181.0 | 264.0 | 224.777 | 225.0 | 178.0 | 268.0 | 224.058 | 224.0 | 181.0 | 264.0 | 224.777 | 225.0 | 178.0 | 268.0 | 1.081 | 1.0 | 0.0 | 5.0 | 2.238 | 2.0 | 0.0 | 8.0 |
| near_boundary_risks | 1.0 | group_risk | principal | common_support | True | 2.0 | 1000 | 1000 | 1000 | 1.0 | 993 | 0.993 | 0.002636474919281427 | 954 | 0.9607250755287009 | 0.006164283699977599 | 0.03258 | 0.046908358509566976 | {"degenerate outcome: point estimate only": 7} | 224.951 | 224.0 | 168.0 | 268.0 | 225.609 | 226.0 | 186.0 | 284.0 | 224.951 | 224.0 | 168.0 | 268.0 | 225.609 | 226.0 | 186.0 | 284.0 | 4.576 | 4.0 | 0.0 | 13.0 | 5.622 | 5.0 | 0.0 | 15.0 |
| near_boundary_risks | 1.0 | group_risk | never | common_support | True | 2.5 | 1000 | 1000 | 1000 | 1.0 | 994 | 0.994 | 0.002442130217658347 | 956 | 0.9617706237424547 | 0.006081926506352768 | -0.010780000000000005 | 0.004245472837022128 | {"degenerate outcome: point estimate only": 6} | 224.951 | 224.0 | 168.0 | 268.0 | 225.609 | 226.0 | 186.0 | 284.0 | 224.951 | 224.0 | 168.0 | 268.0 | 225.609 | 226.0 | 186.0 | 284.0 | 4.576 | 4.0 | 0.0 | 13.0 | 5.622 | 5.0 | 0.0 | 15.0 |
| near_boundary_risks | 1.0 | delta_s | never_minus_principal | common_support | True | 0.5000000000000001 | 1000 | 1000 | 1000 | 1.0 | 987 | 0.987 | 0.0035820385257559714 | 941 | 0.9533941236068896 | 0.006709621143197935 | -0.043470000000000085 | -0.04114488348530912 | {"degenerate outcome: point estimate only": 13} | 224.951 | 224.0 | 168.0 | 268.0 | 225.609 | 226.0 | 186.0 | 284.0 | 224.951 | 224.0 | 168.0 | 268.0 | 225.609 | 226.0 | 186.0 | 284.0 | 4.576 | 4.0 | 0.0 | 13.0 | 5.622 | 5.0 | 0.0 | 15.0 |
| near_boundary_risks | 2.0 | group_risk | principal | common_support | True | 65.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 944 | 0.944 | 0.007270763371201131 | 0.06412000000000004 | 0.06412000000000004 | {} | 225.075 | 225.0 | 179.0 | 272.0 | 225.035 | 225.0 | 186.0 | 272.0 | 225.075 | 225.0 | 179.0 | 272.0 | 225.035 | 225.0 | 186.0 | 272.0 | 146.458 | 147.0 | 112.0 | 190.0 | 157.823 | 158.0 | 124.0 | 201.0 |
| near_boundary_risks | 2.0 | group_risk | never | common_support | True | 70.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 940 | 0.94 | 0.007509993342207438 | 0.13671000000000008 | 0.13671000000000008 | {} | 225.075 | 225.0 | 179.0 | 272.0 | 225.035 | 225.0 | 186.0 | 272.0 | 225.075 | 225.0 | 179.0 | 272.0 | 225.035 | 225.0 | 186.0 | 272.0 | 146.458 | 147.0 | 112.0 | 190.0 | 157.823 | 158.0 | 124.0 | 201.0 |
| near_boundary_risks | 2.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999993 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 946 | 0.946 | 0.0071473071852271785 | 0.07274000000000716 | 0.07274000000000716 | {} | 225.075 | 225.0 | 179.0 | 272.0 | 225.035 | 225.0 | 186.0 | 272.0 | 225.075 | 225.0 | 179.0 | 272.0 | 225.035 | 225.0 | 186.0 | 272.0 | 146.458 | 147.0 | 112.0 | 190.0 | 157.823 | 158.0 | 124.0 | 201.0 |
| near_boundary_risks | 3.0 | group_risk | principal | common_support | True | 85.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 946 | 0.946 | 0.0071473071852271785 | -0.055589999999999876 | -0.055589999999999876 | {} | 225.325 | 225.0 | 178.0 | 269.0 | 225.17 | 225.0 | 182.0 | 268.0 | 225.325 | 225.0 | 178.0 | 269.0 | 225.17 | 225.0 | 182.0 | 268.0 | 191.407 | 191.0 | 150.0 | 235.0 | 180.143 | 180.0 | 146.0 | 218.0 |
| near_boundary_risks | 3.0 | group_risk | never | common_support | True | 80.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 944 | 0.944 | 0.007270763371201131 | 0.0022300000000003307 | 0.0022300000000003307 | {} | 225.325 | 225.0 | 178.0 | 269.0 | 225.17 | 225.0 | 182.0 | 268.0 | 225.325 | 225.0 | 178.0 | 269.0 | 225.17 | 225.0 | 182.0 | 268.0 | 191.407 | 191.0 | 150.0 | 235.0 | 180.143 | 180.0 | 146.0 | 218.0 |
| near_boundary_risks | 3.0 | delta_s | never_minus_principal | common_support | True | -4.999999999999993 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 947 | 0.947 | 0.007084560677981384 | 0.057869999999992885 | 0.057869999999992885 | {} | 225.325 | 225.0 | 178.0 | 269.0 | 225.17 | 225.0 | 182.0 | 268.0 | 225.325 | 225.0 | 178.0 | 269.0 | 225.17 | 225.0 | 182.0 | 268.0 | 191.407 | 191.0 | 150.0 | 235.0 | 180.143 | 180.0 | 146.0 | 218.0 |
| partial_structural_support | 0.0 | group_risk | principal | one_definition_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 959 | 0.959 | 0.006270486424512857 | 0.17760000000000004 | 0.17760000000000004 | {} | 99.996 | 99.0 | 70.0 | 139.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.996 | 99.0 | 70.0 | 139.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10.191 | 10.0 | 2.0 | 21.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| partial_structural_support | 0.0 | group_risk | never | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 0.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 1.0 | group_risk | principal | one_definition_support | True | 15.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 956 | 0.956 | 0.006485676526007139 | -0.20705999999999994 | -0.20705999999999994 | {} | 100.226 | 100.0 | 71.0 | 131.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.226 | 100.0 | 71.0 | 131.0 | 0.0 | 0.0 | 0.0 | 0.0 | 14.83 | 15.0 | 4.0 | 27.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| partial_structural_support | 1.0 | group_risk | never | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 1.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 2.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 960 | 0.96 | 0.00619677335393187 | -0.08763000000000001 | -0.08763000000000001 | {} | 150.274 | 150.0 | 115.0 | 190.0 | 99.829 | 100.0 | 72.0 | 135.0 | 150.274 | 150.0 | 115.0 | 190.0 | 99.829 | 100.0 | 72.0 | 135.0 | 29.924 | 30.0 | 16.0 | 48.0 | 40.01 | 40.0 | 21.0 | 61.0 |
| partial_structural_support | 2.0 | group_risk | never | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 961 | 0.961 | 0.006122009474020767 | 0.09996999999999998 | 0.09996999999999998 | {} | 150.274 | 150.0 | 115.0 | 190.0 | 99.829 | 100.0 | 72.0 | 135.0 | 150.274 | 150.0 | 115.0 | 190.0 | 99.829 | 100.0 | 72.0 | 135.0 | 29.924 | 30.0 | 16.0 | 48.0 | 40.01 | 40.0 | 21.0 | 61.0 |
| partial_structural_support | 2.0 | delta_s | never_minus_principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | 0.18785000000000002 | 0.18785000000000002 | {} | 150.274 | 150.0 | 115.0 | 190.0 | 99.829 | 100.0 | 72.0 | 135.0 | 150.274 | 150.0 | 115.0 | 190.0 | 99.829 | 100.0 | 72.0 | 135.0 | 29.924 | 30.0 | 16.0 | 48.0 | 40.01 | 40.0 | 21.0 | 61.0 |
| partial_structural_support | 3.0 | group_risk | principal | common_support | True | 25.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 939 | 0.939 | 0.007568289106528638 | 0.011219999999999942 | 0.011219999999999942 | {} | 149.886 | 150.0 | 117.0 | 185.0 | 100.384 | 100.0 | 69.0 | 129.0 | 149.886 | 150.0 | 117.0 | 185.0 | 100.384 | 100.0 | 69.0 | 129.0 | 37.492 | 37.0 | 20.0 | 57.0 | 45.423 | 45.0 | 27.0 | 65.0 |
| partial_structural_support | 3.0 | group_risk | never | common_support | True | 45.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 962 | 0.962 | 0.006046155803483734 | 0.24308 | 0.24308 | {} | 149.886 | 150.0 | 117.0 | 185.0 | 100.384 | 100.0 | 69.0 | 129.0 | 149.886 | 150.0 | 117.0 | 185.0 | 100.384 | 100.0 | 69.0 | 129.0 | 37.492 | 37.0 | 20.0 | 57.0 | 45.423 | 45.0 | 27.0 | 65.0 |
| partial_structural_support | 3.0 | delta_s | never_minus_principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 951 | 0.951 | 0.006826346021115546 | 0.23221000000000006 | 0.23221000000000006 | {} | 149.886 | 150.0 | 117.0 | 185.0 | 100.384 | 100.0 | 69.0 | 129.0 | 149.886 | 150.0 | 117.0 | 185.0 | 100.384 | 100.0 | 69.0 | 129.0 | 37.492 | 37.0 | 20.0 | 57.0 | 45.423 | 45.0 | 27.0 | 65.0 |
| partial_structural_support | 4.0 | group_risk | principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 4.0 | group_risk | never | one_definition_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 965 | 0.965 | 0.005811626278418119 | -0.15082000000000004 | -0.15082000000000004 | {} | 0.0 | 0.0 | 0.0 | 0.0 | 149.854 | 150.0 | 115.0 | 190.0 | 0.0 | 0.0 | 0.0 | 0.0 | 149.854 | 150.0 | 115.0 | 190.0 | 0.0 | 0.0 | 0.0 | 0.0 | 44.734 | 45.0 | 22.0 | 65.0 |
| partial_structural_support | 4.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 5.0 | group_risk | principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| partial_structural_support | 5.0 | group_risk | never | one_definition_support | True | 50.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | -0.07708999999999995 | -0.07708999999999995 | {} | 0.0 | 0.0 | 0.0 | 0.0 | 149.551 | 149.0 | 117.0 | 185.0 | 0.0 | 0.0 | 0.0 | 0.0 | 149.551 | 149.0 | 117.0 | 185.0 | 0.0 | 0.0 | 0.0 | 0.0 | 74.68 | 74.0 | 49.0 | 105.0 |
| partial_structural_support | 5.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| rare_common_support_holdout | 0.0 | group_risk | principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 954 | 0.954 | 0.006624499981130654 | 0.011140000000000014 | 0.011140000000000014 | {} | 199.636 | 199.0 | 158.0 | 239.0 | 199.352 | 199.0 | 166.0 | 237.0 | 199.636 | 199.0 | 158.0 | 239.0 | 199.352 | 199.0 | 166.0 | 237.0 | 19.988 | 20.0 | 9.0 | 42.0 | 29.974 | 30.0 | 16.0 | 50.0 |
| rare_common_support_holdout | 0.0 | group_risk | never | common_support | True | 15.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | 0.03098999999999998 | 0.03098999999999998 | {} | 199.636 | 199.0 | 158.0 | 239.0 | 199.352 | 199.0 | 166.0 | 237.0 | 199.636 | 199.0 | 158.0 | 239.0 | 199.352 | 199.0 | 166.0 | 237.0 | 19.988 | 20.0 | 9.0 | 42.0 | 29.974 | 30.0 | 16.0 | 50.0 |
| rare_common_support_holdout | 0.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | 0.01975000000000089 | 0.01975000000000089 | {} | 199.636 | 199.0 | 158.0 | 239.0 | 199.352 | 199.0 | 166.0 | 237.0 | 199.636 | 199.0 | 158.0 | 239.0 | 199.352 | 199.0 | 166.0 | 237.0 | 19.988 | 20.0 | 9.0 | 42.0 | 29.974 | 30.0 | 16.0 | 50.0 |
| rare_common_support_holdout | 1.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 952 | 0.952 | 0.006759881655768837 | -0.05674999999999999 | -0.05674999999999999 | {} | 199.471 | 199.0 | 157.0 | 235.0 | 198.364 | 198.0 | 157.0 | 238.0 | 199.471 | 199.0 | 157.0 | 235.0 | 198.364 | 198.0 | 157.0 | 238.0 | 39.784 | 39.0 | 22.0 | 59.0 | 49.55 | 49.0 | 21.0 | 74.0 |
| rare_common_support_holdout | 1.0 | group_risk | never | common_support | True | 25.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | -0.027549999999999967 | -0.027549999999999967 | {} | 199.471 | 199.0 | 157.0 | 235.0 | 198.364 | 198.0 | 157.0 | 238.0 | 199.471 | 199.0 | 157.0 | 235.0 | 198.364 | 198.0 | 157.0 | 238.0 | 39.784 | 39.0 | 22.0 | 59.0 | 49.55 | 49.0 | 21.0 | 74.0 |
| rare_common_support_holdout | 1.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 949 | 0.949 | 0.006956938982052382 | 0.029130000000000905 | 0.029130000000000905 | {} | 199.471 | 199.0 | 157.0 | 235.0 | 198.364 | 198.0 | 157.0 | 238.0 | 199.471 | 199.0 | 157.0 | 235.0 | 198.364 | 198.0 | 157.0 | 238.0 | 39.784 | 39.0 | 22.0 | 59.0 | 49.55 | 49.0 | 21.0 | 74.0 |
| rare_common_support_holdout | 2.0 | group_risk | principal | common_support | True | 30.0 | 1000 | 1000 | 806 | 0.806 | 0 | 0.0 | 0.0 | 0 |  |  | 0.06107940446650098 |  | {"no records": 194, "too few distinct patients": 806} | 1.575 | 1.0 | 0.0 | 7.0 | 1.602 | 1.0 | 0.0 | 6.0 | 1.575 | 1.0 | 0.0 | 7.0 | 1.602 | 1.0 | 0.0 | 6.0 | 0.473 | 0.0 | 0.0 | 4.0 | 0.585 | 0.0 | 0.0 | 4.0 |
| rare_common_support_holdout | 2.0 | group_risk | never | common_support | True | 35.0 | 1000 | 1000 | 796 | 0.796 | 0 | 0.0 | 0.0 | 0 |  |  | 1.5429899497487434 |  | {"no records": 204, "too few distinct patients": 796} | 1.575 | 1.0 | 0.0 | 7.0 | 1.602 | 1.0 | 0.0 | 6.0 | 1.575 | 1.0 | 0.0 | 7.0 | 1.602 | 1.0 | 0.0 | 6.0 | 0.473 | 0.0 | 0.0 | 4.0 | 0.585 | 0.0 | 0.0 | 4.0 |
| rare_common_support_holdout | 2.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 643 | 0.643 | 0 | 0.0 | 0.0 | 0 |  |  | 1.2011508553654746 |  | {"no shared support": 357, "too few distinct patients in a definition": 643} | 1.575 | 1.0 | 0.0 | 7.0 | 1.602 | 1.0 | 0.0 | 6.0 | 1.575 | 1.0 | 0.0 | 7.0 | 1.602 | 1.0 | 0.0 | 6.0 | 0.473 | 0.0 | 0.0 | 4.0 | 0.585 | 0.0 | 0.0 | 4.0 |
| few_large_clusters | 0.0 | group_risk | principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.011080000000000183 |  | {"too few distinct patients": 1000} | 19.872 | 20.0 | 8.0 | 34.0 | 19.699 | 19.0 | 8.0 | 33.0 | 11.762 | 12.0 | 6.0 | 16.0 | 11.595 | 12.0 | 6.0 | 16.0 | 2.012 | 2.0 | 0.0 | 10.0 | 3.945 | 4.0 | 0.0 | 13.0 |
| few_large_clusters | 0.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | 0.02601999999999989 |  | {"too few distinct patients": 1000} | 19.872 | 20.0 | 8.0 | 34.0 | 19.699 | 19.0 | 8.0 | 33.0 | 11.762 | 12.0 | 6.0 | 16.0 | 11.595 | 12.0 | 6.0 | 16.0 | 2.012 | 2.0 | 0.0 | 10.0 | 3.945 | 4.0 | 0.0 | 13.0 |
| few_large_clusters | 0.0 | delta_s | never_minus_principal | common_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | 0.03714000000000007 |  | {"too few distinct patients in a definition": 1000} | 19.872 | 20.0 | 8.0 | 34.0 | 19.699 | 19.0 | 8.0 | 33.0 | 11.762 | 12.0 | 6.0 | 16.0 | 11.595 | 12.0 | 6.0 | 16.0 | 2.012 | 2.0 | 0.0 | 10.0 | 3.945 | 4.0 | 0.0 | 13.0 |
| few_large_clusters | 1.0 | group_risk | principal | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | 0.7439799999999998 |  | {"too few distinct patients": 1000} | 20.096 | 20.0 | 5.0 | 34.0 | 19.877 | 20.0 | 7.0 | 34.0 | 11.81 | 12.0 | 4.0 | 16.0 | 11.74 | 12.0 | 5.0 | 16.0 | 4.172 | 4.0 | 0.0 | 16.0 | 4.997 | 5.0 | 0.0 | 14.0 |
| few_large_clusters | 1.0 | group_risk | never | common_support | True | 25.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | 0.13909999999999997 |  | {"too few distinct patients": 1000} | 20.096 | 20.0 | 5.0 | 34.0 | 19.877 | 20.0 | 7.0 | 34.0 | 11.81 | 12.0 | 4.0 | 16.0 | 11.74 | 12.0 | 5.0 | 16.0 | 4.172 | 4.0 | 0.0 | 16.0 | 4.997 | 5.0 | 0.0 | 14.0 |
| few_large_clusters | 1.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.6048199999999995 |  | {"too few distinct patients in a definition": 1000} | 20.096 | 20.0 | 5.0 | 34.0 | 19.877 | 20.0 | 7.0 | 34.0 | 11.81 | 12.0 | 4.0 | 16.0 | 11.74 | 12.0 | 5.0 | 16.0 | 4.172 | 4.0 | 0.0 | 16.0 | 4.997 | 5.0 | 0.0 | 14.0 |
| few_large_clusters | 2.0 | group_risk | principal | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.03171000000000004 |  | {"too few distinct patients": 1000} | 20.016 | 20.0 | 8.0 | 35.0 | 20.231 | 20.0 | 9.0 | 34.0 | 11.812 | 12.0 | 6.0 | 16.0 | 11.855 | 12.0 | 7.0 | 16.0 | 6.023 | 6.0 | 0.0 | 18.0 | 7.02 | 7.0 | 0.0 | 18.0 |
| few_large_clusters | 2.0 | group_risk | never | common_support | True | 35.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.37771000000000016 |  | {"too few distinct patients": 1000} | 20.016 | 20.0 | 8.0 | 35.0 | 20.231 | 20.0 | 9.0 | 34.0 | 11.812 | 12.0 | 6.0 | 16.0 | 11.855 | 12.0 | 7.0 | 16.0 | 6.023 | 6.0 | 0.0 | 18.0 | 7.02 | 7.0 | 0.0 | 18.0 |
| few_large_clusters | 2.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.34583999999999937 |  | {"too few distinct patients in a definition": 1000} | 20.016 | 20.0 | 8.0 | 35.0 | 20.231 | 20.0 | 9.0 | 34.0 | 11.812 | 12.0 | 6.0 | 16.0 | 11.855 | 12.0 | 7.0 | 16.0 | 6.023 | 6.0 | 0.0 | 18.0 | 7.02 | 7.0 | 0.0 | 18.0 |
| few_large_clusters | 3.0 | group_risk | principal | common_support | True | 40.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | 0.13122999999999993 |  | {"too few distinct patients": 1000} | 20.049 | 20.0 | 8.0 | 37.0 | 20.16 | 20.0 | 8.0 | 35.0 | 11.803 | 12.0 | 5.0 | 16.0 | 11.807 | 12.0 | 6.0 | 16.0 | 8.047 | 8.0 | 0.0 | 20.0 | 10.004 | 10.0 | 1.0 | 23.0 |
| few_large_clusters | 3.0 | group_risk | never | common_support | True | 50.0 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.35963 |  | {"too few distinct patients": 1000} | 20.049 | 20.0 | 8.0 | 37.0 | 20.16 | 20.0 | 8.0 | 35.0 | 11.803 | 12.0 | 5.0 | 16.0 | 11.807 | 12.0 | 6.0 | 16.0 | 8.047 | 8.0 | 0.0 | 20.0 | 10.004 | 10.0 | 1.0 | 23.0 |
| few_large_clusters | 3.0 | delta_s | never_minus_principal | common_support | True | 9.999999999999998 | 1000 | 1000 | 1000 | 1.0 | 0 | 0.0 | 0.0 | 0 |  |  | -0.4908699999999983 |  | {"too few distinct patients in a definition": 1000} | 20.049 | 20.0 | 8.0 | 37.0 | 20.16 | 20.0 | 8.0 | 35.0 | 11.803 | 12.0 | 5.0 | 16.0 | 11.807 | 12.0 | 6.0 | 16.0 | 8.047 | 8.0 | 0.0 | 20.0 | 10.004 | 10.0 | 1.0 | 23.0 |
| no_common_support | 0.0 | group_risk | principal | one_definition_support | True | 10.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 959 | 0.959 | 0.006270486424512857 | -0.04726000000000003 | -0.04726000000000003 | {} | 250.041 | 250.0 | 200.0 | 291.0 | 0.0 | 0.0 | 0.0 | 0.0 | 250.041 | 250.0 | 200.0 | 291.0 | 0.0 | 0.0 | 0.0 | 0.0 | 24.885 | 25.0 | 10.0 | 45.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| no_common_support | 0.0 | group_risk | never | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 0.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 1.0 | group_risk | principal | one_definition_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | -0.07612 | -0.07612 | {} | 249.413 | 249.0 | 209.0 | 294.0 | 0.0 | 0.0 | 0.0 | 0.0 | 249.413 | 249.0 | 209.0 | 294.0 | 0.0 | 0.0 | 0.0 | 0.0 | 49.692 | 49.0 | 32.0 | 75.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| no_common_support | 1.0 | group_risk | never | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 1.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 2.0 | group_risk | principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 2.0 | group_risk | never | one_definition_support | True | 35.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 949 | 0.949 | 0.006956938982052382 | -0.04602000000000008 | -0.04602000000000008 | {} | 0.0 | 0.0 | 0.0 | 0.0 | 250.221 | 250.0 | 206.0 | 298.0 | 0.0 | 0.0 | 0.0 | 0.0 | 250.221 | 250.0 | 206.0 | 298.0 | 0.0 | 0.0 | 0.0 | 0.0 | 87.469 | 87.0 | 59.0 | 122.0 |
| no_common_support | 2.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 3.0 | group_risk | principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| no_common_support | 3.0 | group_risk | never | one_definition_support | True | 50.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 946 | 0.946 | 0.0071473071852271785 | 0.12864000000000006 | 0.12864000000000006 | {} | 0.0 | 0.0 | 0.0 | 0.0 | 250.325 | 250.5 | 204.0 | 293.0 | 0.0 | 0.0 | 0.0 | 0.0 | 250.325 | 250.5 | 204.0 | 293.0 | 0.0 | 0.0 | 0.0 | 0.0 | 125.486 | 126.0 | 92.0 | 158.0 |
| no_common_support | 3.0 | delta_s | never_minus_principal | one_definition_support | False |  | 1000 | 0 | 0 |  | 0 |  |  | 0 |  |  |  |  | {} |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| high_icc_unbalanced_holdout | 0.0 | group_risk | principal | common_support | True | 15.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 956 | 0.956 | 0.006485676526007139 | 0.028800000000000048 | 0.028800000000000048 | {} | 739.333 | 738.0 | 607.0 | 875.0 | 88.295 | 88.0 | 61.0 | 119.0 | 366.496 | 366.0 | 324.0 | 409.0 | 79.422 | 79.0 | 55.0 | 109.0 | 111.132 | 110.0 | 73.0 | 153.0 | 17.672 | 17.0 | 6.0 | 33.0 |
| high_icc_unbalanced_holdout | 0.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 955 | 0.955 | 0.00655553201502365 | 0.022340000000000054 | 0.022340000000000054 | {} | 739.333 | 738.0 | 607.0 | 875.0 | 88.295 | 88.0 | 61.0 | 119.0 | 366.496 | 366.0 | 324.0 | 409.0 | 79.422 | 79.0 | 55.0 | 109.0 | 111.132 | 110.0 | 73.0 | 153.0 | 17.672 | 17.0 | 6.0 | 33.0 |
| high_icc_unbalanced_holdout | 0.0 | delta_s | never_minus_principal | common_support | True | 5.000000000000002 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 940 | 0.94 | 0.007509993342207438 | -0.006720000000001781 | -0.006720000000001781 | {} | 739.333 | 738.0 | 607.0 | 875.0 | 88.295 | 88.0 | 61.0 | 119.0 | 366.496 | 366.0 | 324.0 | 409.0 | 79.422 | 79.0 | 55.0 | 109.0 | 111.132 | 110.0 | 73.0 | 153.0 | 17.672 | 17.0 | 6.0 | 33.0 |
| high_icc_unbalanced_holdout | 1.0 | group_risk | principal | common_support | True | 30.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 942 | 0.942 | 0.007391616873188169 | -0.038420000000000044 | -0.038420000000000044 | {} | 442.474 | 441.0 | 369.0 | 519.0 | 206.964 | 207.0 | 159.0 | 263.0 | 275.928 | 276.0 | 227.0 | 312.0 | 162.716 | 163.0 | 132.0 | 196.0 | 132.583 | 133.0 | 83.0 | 186.0 | 41.296 | 41.0 | 20.0 | 66.0 |
| high_icc_unbalanced_holdout | 1.0 | group_risk | never | common_support | True | 20.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 953 | 0.953 | 0.00669260786241059 | -0.03531000000000004 | -0.03531000000000004 | {} | 442.474 | 441.0 | 369.0 | 519.0 | 206.964 | 207.0 | 159.0 | 263.0 | 275.928 | 276.0 | 227.0 | 312.0 | 162.716 | 163.0 | 132.0 | 196.0 | 132.583 | 133.0 | 83.0 | 186.0 | 41.296 | 41.0 | 20.0 | 66.0 |
| high_icc_unbalanced_holdout | 1.0 | delta_s | never_minus_principal | common_support | True | -9.999999999999998 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 937 | 0.937 | 0.007683163410991592 | 0.0028799999999982047 | 0.0028799999999982047 | {} | 442.474 | 441.0 | 369.0 | 519.0 | 206.964 | 207.0 | 159.0 | 263.0 | 275.928 | 276.0 | 227.0 | 312.0 | 162.716 | 163.0 | 132.0 | 196.0 | 132.583 | 133.0 | 83.0 | 186.0 | 41.296 | 41.0 | 20.0 | 66.0 |
| high_icc_unbalanced_holdout | 2.0 | group_risk | principal | common_support | True | 45.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 953 | 0.953 | 0.00669260786241059 | -0.09829000000000004 | -0.09829000000000004 | {} | 206.143 | 205.0 | 156.0 | 262.0 | 442.43 | 442.0 | 367.0 | 530.0 | 162.566 | 162.0 | 129.0 | 205.0 | 275.99 | 276.0 | 232.0 | 315.0 | 92.58 | 92.5 | 58.0 | 128.0 | 221.197 | 221.0 | 171.0 | 297.0 |
| high_icc_unbalanced_holdout | 2.0 | group_risk | never | common_support | True | 50.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 948 | 0.948 | 0.007021111023192843 | -0.0013600000000000706 | -0.0013600000000000706 | {} | 206.143 | 205.0 | 156.0 | 262.0 | 442.43 | 442.0 | 367.0 | 530.0 | 162.566 | 162.0 | 129.0 | 205.0 | 275.99 | 276.0 | 232.0 | 315.0 | 92.58 | 92.5 | 58.0 | 128.0 | 221.197 | 221.0 | 171.0 | 297.0 |
| high_icc_unbalanced_holdout | 2.0 | delta_s | never_minus_principal | common_support | True | 4.999999999999999 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 958 | 0.958 | 0.006343185319695463 | 0.09706000000000083 | 0.09706000000000083 | {} | 206.143 | 205.0 | 156.0 | 262.0 | 442.43 | 442.0 | 367.0 | 530.0 | 162.566 | 162.0 | 129.0 | 205.0 | 275.99 | 276.0 | 232.0 | 315.0 | 92.58 | 92.5 | 58.0 | 128.0 | 221.197 | 221.0 | 171.0 | 297.0 |
| high_icc_unbalanced_holdout | 3.0 | group_risk | principal | common_support | True | 60.0 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 949 | 0.949 | 0.006956938982052382 | -0.20829999999999996 | -0.20829999999999996 | {} | 88.317 | 89.0 | 61.0 | 116.0 | 737.008 | 735.0 | 629.0 | 856.0 | 79.383 | 79.0 | 57.0 | 104.0 | 365.57 | 365.0 | 319.0 | 410.0 | 52.807 | 53.0 | 21.0 | 78.0 | 405.597 | 405.0 | 315.0 | 503.0 |
| high_icc_unbalanced_holdout | 3.0 | group_risk | never | common_support | True | 55.00000000000001 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 950 | 0.95 | 0.006892024376045114 | 0.03382999999999281 | 0.03382999999999281 | {} | 88.317 | 89.0 | 61.0 | 116.0 | 737.008 | 735.0 | 629.0 | 856.0 | 79.383 | 79.0 | 57.0 | 104.0 | 365.57 | 365.0 | 319.0 | 410.0 | 52.807 | 53.0 | 21.0 | 78.0 | 405.597 | 405.0 | 315.0 | 503.0 |
| high_icc_unbalanced_holdout | 3.0 | delta_s | never_minus_principal | common_support | True | -4.999999999999993 | 1000 | 1000 | 1000 | 1.0 | 1000 | 1.0 | 0.0 | 941 | 0.941 | 0.007451107300260817 | 0.24207999999999294 | 0.24207999999999294 | {} | 88.317 | 89.0 | 61.0 | 116.0 | 737.008 | 735.0 | 629.0 | 856.0 | 79.383 | 79.0 | 57.0 | 104.0 | 365.57 | 365.0 | 319.0 | 410.0 | 52.807 | 53.0 | 21.0 | 78.0 | 405.597 | 405.0 | 315.0 | 503.0 |

## Supplementary Table 53. Adapted PEER-cohort weighted summary Δ_w

| analysis | estimand | n | n_patients | n_inference_clusters | delta_w_pp | numerical_se_pp | lo_pp | hi_pp | support_share | levels | state | interval_status | weight_target | n_eligible | n_complete | primary_eligible | never_eligible | instrument |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adapted published PEER population | Delta_w weighted summary | 3565 | 3365 | 3365 | 1.640331494904508 | 1.0883563361778859 |  |  | 1.0 | 6 | interval withheld: too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell | not computed (too_few_distinct_patients_per_score_definition_cell, degenerate_outcome_cell) | observed pooled record shares within common support | 5883 | 3565 | 1717 | 4166 | adapted CURB-65, same definition in both position groups |

## Supplementary Table 54. Amsterdam weighted summary Δ_w by GCS definition and interval method

| score | interval_type | estimate_pp | ci_lower_pp | ci_upper_pp | interval_status |
| --- | --- | --- | --- | --- | --- |
| GCS ≤13 | normal_influence_function | 18.91 |  |  | not computed (too_few_distinct_patients_per_score_definition_cell) |
| GCS ≤13 | patient_cluster_percentile_bootstrap | 18.91 |  |  | not computed (too_few_distinct_patients_per_score_definition_cell) |
| GCS <15 | normal_influence_function | 18.43 | 3.2 | 33.67 | computed |
| GCS <15 | patient_cluster_percentile_bootstrap | 18.43 | -1.51 | 33.24 | computed |

## Supplementary Table 55. Amsterdam score-level δ_s for GCS ≤13

| level | n | n_never | n_primary | patients_never | patients_primary | events_never | events_primary | risk_never | risk_primary | diff_pp | risk_never_ci_pp | risk_primary_ci_pp | delta_ci_pp | risk_never_ci_status | risk_primary_ci_status | delta_ci_status | weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2.0 | 157 | 28 | 129 | 28 | 125 | 10.0 | 30.0 | 35.71 | 23.26 | 12.46 | [20.38, 54.66] | [16.76, 31.33] | [-6.72, 31.64] | computed | computed | computed | 0.6205533596837944 |
| 3.0 | 96 | 19 | 77 | 19 | 74 | 13.0 | 30.0 | 68.42 | 38.96 | 29.46 |  | [28.51, 50.53] |  | too few distinct patients | computed | too few distinct patients in a definition | 0.3794466403162055 |

## Supplementary Table 56. Amsterdam score-level δ_s for GCS <15

| level | n | n_never | n_primary | patients_never | patients_primary | events_never | events_primary | risk_never | risk_primary | diff_pp | risk_never_ci_pp | risk_primary_ci_pp | delta_ci_pp | risk_never_ci_status | risk_primary_ci_status | delta_ci_status | weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2.0 | 131 | 24 | 107 | 24 | 105 | 9.0 | 27.0 | 37.5 | 25.23 | 12.27 | [20.77, 57.87] | [17.86, 34.38] | [-8.84, 33.37] | computed | computed | computed | 0.515748031496063 |
| 3.0 | 123 | 24 | 99 | 24 | 94 | 14.0 | 33.0 | 58.33 | 33.33 | 25.0 | [38.3, 75.94] | [24.56, 43.44] | [2.95, 47.05] | computed | computed | computed | 0.484251968503937 |

## Supplementary Table 57. Amsterdam observed mortality by reconstructed qSOFA

| group | qsofa_main | n_admissions | n_patients | icu_mcu_discharge_deaths | mortality_pct |
| --- | --- | --- | --- | --- | --- |
| primary | 2 | 129 | 125 | 30 | 23.26 |
| primary | 3 | 77 | 74 | 30 | 38.96 |
| secondary_only | 1 | 1 | 1 | 0 | 0.0 |
| secondary_only | 2 | 28 | 28 | 10 | 35.71 |
| secondary_only | 3 | 19 | 19 | 13 | 68.42 |


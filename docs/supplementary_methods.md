# Supplementary methods for the diagnosis position audit

## Targets and units

The primary audit concerns hospital-admission records indexed to the earliest eligible ICU episode. A patient can contribute several admissions and can appear in both diagnosis groups. The target weights records; patient clustering handles dependence without changing that target. Database-specific grouping and score reconstruction rules are those in the manuscript. The analysis population has known diagnosis group, known hospital outcome and every required score component. Results do not automatically describe incomplete records or an external population.

Let c index independently sampled patient clusters within a source, and let j index records within a patient. Selection indicator R retains records satisfying the stated rules. Define A(c,g,s) as the number of selected records in diagnosis group g and score s within patient c; define B(c,g,s) as their death count. Population cell risk is p(g,s)=E[B(c,g,s)]/E[A(c,g,s)]. This ratio weights records rather than giving each patient equal mass. The score-specific target is δ(s)=p(N,s)−p(P,s), with N denoting never-primary and P primary under the relevant source definition.

For a declared support S*, let A(c,s)=A(c,N,s)+A(c,P,s) and A(c,S*) be its sum over S*. Population record weights are w(s)=E[A(c,s)]/E[A(c,S*)]. The population weighted summary Δ_w is Σ over S* of w(s)δ(s). This is a within-source target, not an external standard population. Finite expected cluster contributions and positive target cell probabilities are needed for this ratio parameter. Large-sample influence-function inference additionally requires a stable support and regularity of the clustered contributions.

Sample cell means and pooled record proportions estimate these quantities. The finite dataset's observed δ_s and weighted summary Δ_w are descriptive statistics even when an interval is refused. In clinical data the population support is not fully known: the implemented point estimator uses observed common score support. Clinical interval statements therefore do not establish uniform validity under unobserved rare support. In simulations, S* is supplied by the design; loss of any positive-probability target cell is explicitly detected. A point retained after target-support loss describes observed support and is not a replacement estimate for the original population target.

## Estimated weight influence contributions

For a supported record i with score s, define its cell-risk contribution r_i. In the formulas below, n denotes record counts, Y is binary hospital death, and hats indicate sample quantities.

\[
r_i=\frac{I_{N,i}(Y_i-\widehat p_{N,s})}{n_{N,s}}-\frac{I_{P,i}(Y_i-\widehat p_{P,s})}{n_{P,s}}.
\]

The record contribution includes the estimated pooled-weight term. Here N_S is the number of records on the chosen common support.

\[
a_i=\widehat w_s r_i+\frac{\widehat\delta_s-\widehat\Delta_w}{N_S}.
\]

Unsupported records have zero contribution. Contributions are combined within patient before squaring, allowing repeated admissions and cross-group records to covary.

\[
U_c=\sum_{i\in c}a_i,\qquad \widehat V=\frac{G}{G-1}\sum_c U_c^2.
\]

G is the number of distinct patients in the complete-case input universe before restriction to common support. Patients with no supported records contribute zero but remain in that finite-sample correction. If fixed reference weights are deliberately supplied for a sensitivity, the weight-estimation term is omitted. This is a different weighting analysis and is labelled accordingly. The primary weighted-summary interval uses the normal approximation with this variance; it is not the percentile interval from the small bootstrap gate.

Score-level δ_s intervals use the analogous two-cell patient contributions. Group-risk intervals are transformed logit-Wald intervals. A sparse level can withhold that level's interval without removing intervals at other levels. Bonferroni intervals are an asymptotic sensitivity across the declared family, with the same reporting gates; selective emission and sparse data do not supply a universal finite-sample familywise guarantee.

## Operational reporting policy

The software states concern policy output. Invalid required input or no common score yields no point estimate. Other gates may retain a point and withhold its interval. Passing every applicable gate permits an interval under the policy; it does not establish that all inferential assumptions hold.

Strategy A adds no refusal rule. B requires ten records in every target score-by-group cell. C additionally requires target-support stability, twenty distinct patients overall and per target cell, twenty records per score level, nondegenerate outcomes in every cell, and at least twenty usable draws from sixty patient-cluster bootstrap draws. A usable draw retains every target score and has at least ten events in each diagnosis group across support. D retains C's distinct-patient and nondegenerate-cell thresholds on observed support, but omits its bootstrap and prespecified support-stability checks.

These are operational safeguards, not optimized or universally valid thresholds. Increasing refusals can reduce the number of emitted failures without improving conditional coverage or useful inference. We report emission, support match, off-target output, and coverage among emitted on-target intervals. Supplementary Table 44 reports paired interval-width differences on replicates in which both strategies emitted an interval. The full A/B/C/D results remain in the aggregate supplement; no global strategy ranking is asserted.

Pneumonia summary refusals illustrate the distinction between policy output and estimability. A small zero-score cell can suppress the policy's interval for the entire weighted summary Δ_w. The supplementary perturbation ranges fix all other empirical risks and weights while allowing refused-layer differences to vary over their full possible range. They omit sampling uncertainty and are neither confidence intervals nor proof of statistical significance. We did not remove rare levels and reuse the original target label.

## Numerical simulation design

Supplementary Table 42 gives all numerical specifications of the eleven weighted-summary simulation designs. Vectors align with the stated score order. The joint group-score probabilities sum to one; cluster-size probabilities describe patients. Conditional on these category draws, outcomes use thresholded latent Gaussian variables with a shared patient component. The parameter named outcome_icc in the stored configuration is a latent Gaussian correlation parameter, not generally the binary outcome intraclass correlation.

Each design used one thousand outer datasets. Population truth and population record weights follow the supplied marginal probabilities and risks on S*. A separate observed-weight diagnostic conditions on each dataset's weight realization and does not replace population-target coverage. The no-common-support design has no corresponding population contrast. Rare-common-support loss is counted as off-target interval emission, not as successful coverage of a new target. Few-large-cluster and sparse-boundary structures expose the cost of refusal. The separate deterministic fine-cell and tiny-arm checks are retained with their own denominators.

Aggregate outcomes had been inspected before the exploratory extensions. Configurations were specified before their respective runs, but the overall study was not prospectively preregistered. The numerical inventory makes existing results assessable; it does not extend their coverage guarantee to every clinical structure or to crossed hospital dependence.

## Missing score and outcome restrictions

Missing components are unknown rather than normal. The separate score-assignment bounds use records with known group, binary outcome and valid lower and upper compatible scores. They can assign optional known deaths and survivors differently to maximize or minimize a single level's risk contrast. Extremes can differ across levels, so they are not generally jointly attainable across all scores. These are identification bounds with no sampling interval. They do not incorporate unknown outcomes, unknown group semantics or all missingness mechanisms.

The primary target can remain the complete-component, known-outcome population. Generalizing to all disease-eligible admissions would require additional assumptions about missing scores and outcomes. Existing bounds and completeness by group are retained so the selection restriction is visible.

## Diagnosis field qualification

eICU diagnoses have a clinical priority field over linked ICU stays. A matching Primary-priority row at any linked stay defines the primary disease group. MIMIC uses minimum billing sequence among matching disease codes; it is assigned after the clinical course and is not an onset time. These source constructs were not pooled into one harmonized exposure.

Zigong is an infection-selected single-center dataset. The official source describes diagnosis codes, descriptions and diagnosis discharge status, but the public description and descriptor article did not establish principal-diagnosis meaning for Diagnosis_seq. The official release dictionary describes Diagnosis_seq only as “the sequence of diagnosis”, without defining principal-diagnosis rank . The field was not interpreted as principal-diagnosis rank from its name alone. Sequence-one and other-sequence contrasts are retained as unqualified field-audit examples, not as verified principal-diagnosis associations. The discharge-status outcome remains distinct from follow-up death. Its principal-diagnosis semantics remain unresolved.

Official sources consulted: https://physionet.org/content/icu-infection-zigong-fourth/1.1/ and https://pmc.ncbi.nlm.nih.gov/articles/PMC8968758/ . The source description is evidence for the endpoint field, not proof of diagnosis-rank semantics.

## Composition audit

The composition tables describe the same four complete-component, known-outcome populations as the main analysis. All percentages use admission records as denominators, including records with unknown characteristics.

Demographic descriptions include the age threshold and recorded sex with missing denominators shown. Age top-coding does not change the threshold at sixty-five. eICU describes the index ICU admission source; MIMIC describes hospital admission type, which is not treated as the same field. eICU Primary-priority diagnostic labels are nonexclusive over linked ICU stays. MIMIC billing sequence-one is one diagnosis per admission. Missing qualifying diagnoses are reported. A record can therefore contribute to multiple eICU diagnosis rows; their percentages need not sum to one hundred. The shared denominator remains the complete-record disease group, not a sum of diagnosis rows.

The indicator of also appearing in the other complete main disease cohort describes overlap of these analytic cohorts, not the prevalence of all comorbidity diagnoses. These descriptions explain selected records but do not identify the cause of source differences or remove unmeasured severity heterogeneity.

## Exploratory mapping evaluation

Supplementary Tables 23–26 report all retained paired Brier contrasts, subgroup metrics, eligibility counts and split details. The original integer score is the sole numeric predictor in a logistic intercept-and-slope mapping. Primary-only and broad training share the same downstream test records. Different training sizes are part of the policies, not an isolated diagnosis-composition effect.

eICU uses deterministic hospital buckets for training, independent recalibration and test roles, excluding patients with multihospital or cross-role records. MIMIC uses entire possible calendar intervals inferred from anchor-year groups and admission-year offsets. Intervals wholly ending by 2013 enter training; intervals wholly within 2014–2016 enter recalibration; intervals wholly within 2017–2022 enter testing. Ambiguous or out-of-window intervals and cross-role patients are excluded. The panel-level exclusions and disease-specific flow have different denominators and are not added together.

Independent broad-population intercept recalibration fixes the original linear predictor as an offset. Test calibration intercepts and slopes are diagnostic point estimates, never used to update predictions. Patient-cluster and hospital-cluster resampling preserve record weighting and are reported separately. Paired intervals condition on the realized trained and recalibrated maps; they are not the uncertainty of repeatedly developing a new model. Analyses are exploratory and pointwise. Overall and diagnosis-subgroup results are reported together, including opposite directions, failed advantages and hospital sensitivities. Intervals including zero do not establish equivalence.

## Supplementary applications

The PEER-defined application adapts its public cohort inclusion and exclusion logic, admission index and present score reconstruction. It does not reproduce the original prediction model. Amsterdam is a supplemental unit-discharge application with different endpoints and a prior outcome pilot; both GCS thresholds and the larger bootstrap precision comparison remain in the supplementary tables. It is not an untouched external validation of the hospital-admission target.

The conditional-Hoeffding construction targets the mean of a weighted outcome sum conditional on the complete observed design, including empirical weights and support. It assumes independent patient clusters conditional on that design, an unverified assumption in these clinical data. That parameter differs from the primary source-population weighted summary Δ_w. Its intervals do not replace refused primary intervals. A finite-sample population guarantee would require an a priori bound on patient-cluster contributions, which was unavailable for this population target.

Imaging linkage for pancreatitis remains unvalidated against independent local clinician labels. Missing reports and absent mentions are not absence of pleural effusion. Imaging and score windows differ, and SIRS remains adapted. We report no reconstructed standard complete BISAP outcome analysis from these unvalidated rules.

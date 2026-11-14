# v2 benchmark protocol and source reconciliation

## Contract locked before confirmatory outcomes

The target support `S*` is supplied by each simulated population. In applications without an externally prespecified support, the tool uses observed shared score levels, labels the target as observed common support, and makes no extrapolation claim.

For each score level `s`, define `delta_s = p_1s - p_0s`, where group 1 is never-principal and group 0 is principal, and each `p_gs` is the binary outcome risk per admission record. The main estimand is `Delta_w = sum_{s in S*} w_s delta_s`, where `w_s` is the population pooled-record frequency conditional on `S*`. Each admission record contributes equally to `w_s`; repeated records are clustered by patient for uncertainty.

With sample pooled-record weights and complete fixed support, the row-level influence contribution is

```text
phi_i = I(s_i in S*) / N_support * (delta_{s_i} - Delta_w)
        + sum_s w_s * [ I(g_i=1,s_i=s) * (Y_i-p_1s)/N_1s
                      - I(g_i=0,s_i=s) * (Y_i-p_0s)/N_0s ]
```

Patient contributions are summed across all score and definition cells before squaring. The empirical cluster sandwich uses the finite-sample correction `M/(M-1)` with `M` equal to the number of independent patient clusters in the audit sample. The legacy comparator omits the first, weight-estimation term while retaining the same observed-weight point estimate. The fixed-weight sensitivity instead uses the known population weights in both point estimate and IF and therefore targets the same parameter under a different information condition.

All main A/B/C policies use the corrected estimated-weight estimator. A and B use the observed common support when a target cell is absent, so any interval from them is marked off-target against the population truth. C uses known `S*`; if any prespecified cell is lost, C withholds the population-target interval, reports `target_support_lost`, and retains an observed-supported point estimate with that changed-target label.

## Simulation design

The frozen JSON config specifies 11 scenarios: null with homogeneous risks; null with score-specific effects that average to zero; heterogeneous effects with unequal estimated weights; repeated admissions with cross-definition clusters; unequal cluster sizes; near-boundary risks; partial structural support; rare positive common support; few large clusters; no common support; and high-ICC, unbalanced-size holdout data. Main and stress scenarios are identified in the configuration; holdouts are not used to alter any threshold.

For each of 1,000 replicates per scenario, each patient's admissions share a latent normal effect. An admission outcome is generated through a Gaussian copula with the requested marginal risk. The configured `outcome_icc` is the latent Gaussian correlation parameter; the resulting binary ICC depends on marginal risk. This gives genuine within-patient outcome dependence while preserving each score-by-definition marginal risk. Admissions independently draw score and group from the fixed joint population distribution, so the pooled record weights are random across replicates. Cluster sizes vary by scenario and include patients with admissions in both definition groups and multiple score levels.

Every rule is evaluated on the same generated dataset. B checks all prespecified target cells, so a missing positive-probability target cell is below its 10-record threshold. C's patient bootstrap is only attempted after deterministic refusal rules pass. It uses 60 replicates, with the original requirement of at least 20 usable draws and at least 10 events in each definition per draw. D is supplementary and isolates the matched threshold of at least 20 distinct patients per score-definition cell plus exact outcome variation; D has no bootstrap or support-stability gate.

The frozen seed is `27112026`; it is independent from the old m112/m103 seed `20261103`. The run config SHA-256 is captured in the output manifest. Results are descriptive and will not be used to change thresholds.

The first launch was stopped at 700/1,000 replicates in the first design after a boundary audit found that C's interval was reconstructed from rounded display fields, while A/B/D used full precision. Those incomplete metrics were moved to `outputs/v2/audit/superseded_rounding_pilot_20261112_2049/` and are excluded. The restarted driver uses the same policies, DGPs, and seed, but C's emission decision alone comes from `audit_v2`; all emitted intervals are formed from the shared full-precision estimate and SE. A boundary regression requires exact equality of A/B/C/D intervals when all four emit.

## Metrics

- Point-estimate availability and interval-emission rates use all outer replicates.
- Conditional coverage is computed among emitted intervals whose sample support equals `S*`; its denominator and binomial MCSE are reported.
- An unconditional missed interval is an emitted interval that fails to cover the population truth or is emitted on changed support. Its rate, count, and MCSE use all outer replicates. Refusals and support mismatch are reported separately.
- Median and mean interval widths are reported among emitted on-target intervals. Widths for off-target intervals remain visible in replicate metrics but do not contribute to the on-target width summary.
- A/B/C/D are paired on the same replicate. Paired MCSEs use replicate-wise differences for emission and misses. The conditional-coverage contrast uses the paired ratio-estimator influence function. Width contrasts use datasets where both policies emitted on-target intervals.
- A legacy fixed-observed-weight IF comparator and an oracle fixed-population-weight sensitivity are separated from the main rule comparison.
- A secondary per-replicate conditional target is calculated as `sum(observed pooled-record weight_s * known delta_s)` only when observed common support equals `S*`. Conditional observed-weight coverage is reported in separate columns (including for the legacy fixed-observed-weight IF) and never replaces population-truth coverage. When support is lost, this target and its coverage are missing rather than mixed with the changed-support parameter.
- The restart adds only output-schema fields for that conditional target/coverage and its version marker. The random seed, DGP definitions, thresholds, policy logic, and 1,000 outer replicates per design are unchanged.

With 1,000 emitted intervals and 95% coverage, the binomial MCSE is about 0.69 percentage points. If refusal lowers emission, the reported MCSE uses the actual eligible denominator and becomes larger.

## Source audit and repaired defects

The frozen workspace snapshot is 38,219 bytes and the newer F: source is 39,660 bytes. The newer copy adds the per-cell distinct-patient threshold and explicitly identifies pooled weights as record counts. v2 adopts both changes.

The old `m112_refusal_strategies.py` directly called low-level estimators for A/B and called the full `audit()` path for C. That is intentional for policy comparison but meant A/B bypassed the shipped gates. The v2 benchmark implements A/B as explicit policies and calls `audit_v2()` for C. The old `m103_failure_boundary.py` used independent Bernoulli outcomes and one-row patients; m112's few-clusters case recycled IDs across independent rows. Neither tests genuine patient outcome dependence. Both used fixed cell sizes, so neither evaluates random pooled-weight uncertainty. They used 200 outer replicates and 60 bootstrap draws, leaving conditional coverage MCSE near 1.5 pp even at full emission.

The newer audit variance treated estimated pooled-record weights as fixed and omitted their IF term. C's `min_arm_n` counted records despite help text saying patients; the newer per-cell patient threshold is a distinct rule. Degeneracy was checked using rounded percentage strings, which could falsely flag rare nonzero risks as 0%. The Markdown report embedded historical coverage ranges as if they were guarantees. The v2 tool checks raw event counts, records each threshold and unit in structured output, separates missingness assumptions from complete-case handling, and removes historical coverage claims.

Regression tests cover the estimated-weight IF term, fixed-weight estimator, cross-definition patient cancellation, target-support loss, exact degeneracy detection, independent per-level interval gates, finite-sample cluster correction, and a normal CLI run with structured metadata.

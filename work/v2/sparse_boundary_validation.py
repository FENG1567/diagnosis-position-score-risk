"""Re-evaluate the two original sparse-cell structures with the revised IF.

C/B/D interval refusal is deterministic from fixed cell counts in these
designs. Verify the actual tool once per design, and verify the count gate on
every replicate. No repeated expensive bootstrap is needed after that gate.
"""
import json
import hashlib
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from analyse_panels import audit_module, clean_json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/v2/sparse_boundary_validation'
REPLICATES = 1000
SEED = 27112028


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    specifications = {}
    for name in ['fine_cells', 'tiny_arm']:
        if name == 'fine_cells':
            n0, n1 = rng.integers(3, 20, size=200), rng.integers(3, 20, size=200)
        else:
            n0, n1 = rng.integers(1, 3, size=200), rng.integers(20, 60, size=200)
        specifications[name] = dict(n_primary=n0.tolist(), n_never=n1.tolist(),
                                     p_primary=0.10, p_never=0.18)
    config = dict(seed=SEED, outer_replicates=REPLICATES, designs=specifications,
                  rule_evaluation='C/B/D refusal determined by per-cell counts, actual C API verified once per design',
                  truth='constant delta_s=0.08, therefore all pooled-record-weighted summary targets equal0.08',
                  shared_tool=hashlib.sha256((ROOT / 'work/v2/audit/cohort_definition_audit.py').read_bytes()).hexdigest())
    (OUT / 'frozen_config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    module = audit_module()
    z = norm.ppf(0.975)
    records, tool_examples = [], {}
    for design, spec in specifications.items():
        score, group = [], []
        for level, (n0, n1) in enumerate(zip(spec['n_primary'], spec['n_never'])):
            score.extend([level] * (n0 + n1))
            group.extend([0] * n0 + [1] * n1)
        score, group = np.asarray(score, float), np.asarray(group, int)
        pid = np.arange(len(score))
        probability = np.where(group == 1, spec['p_never'], spec['p_primary'])
        truth = 0.08
        for replicate in range(REPLICATES):
            y = rng.binomial(1, probability).astype(float)
            d = pd.DataFrame(dict(pid=pid, score=score, grp=group, y=y))
            estimate = module.stratified_rd(score, y, group)[0]
            se = module.stratified_rd_se(score, y, group, pid)[0]
            # Both count rules fail on every draw, independently of outcomes.
            count_matrix = pd.crosstab(d.score, d.grp)
            assert count_matrix.min().min() < 10
            assert count_matrix.min().min() < 20
            if replicate == 0:
                actual = module.audit_v2(d, expected_levels=list(range(200)),
                                          config=dict(reps=60, seed=SEED, min_events=10, min_level_n=20,
                                                      min_arm_n=10, min_clusters=20, min_usable_bootstrap=20,
                                                      model_check=False))
                assert actual.get('delta_ci_pp') is None
                assert actual.get('stratified_rd_pp') is not None
                tool_examples[design] = actual
            emitted = bool(np.isfinite(se) and se > 0)
            records.append(dict(design=design, replicate=replicate, estimate=estimate,
                                truth=truth, se=se, emitted_A=emitted,
                                covered_A=bool(emitted and abs(estimate - truth) <= z * se),
                                width_A=2 * z * se if emitted else np.nan))
        print(f'Completed {design}, {REPLICATES} replicates', flush=True)
    details = pd.DataFrame(records)
    details.to_csv(OUT / 'replicate_results.csv', index=False)
    rows = []
    for design, data in details.groupby('design'):
        emit = data.emitted_A
        coverage = data.loc[emit, 'covered_A'].mean()
        for strategy in ['A', 'B', 'C', 'D']:
            produced = int(emit.sum()) if strategy == 'A' else 0
            c = coverage if produced else np.nan
            rows.append(dict(design=design, strategy=strategy, replicates=len(data), point_output_rate=1.0,
                             interval_output_rate=produced / len(data), n_intervals=produced,
                             conditional_coverage=c,
                             coverage_mcse=np.sqrt(c * (1 - c) / produced) if produced else np.nan,
                             unconditional_missed_intervals=int((emit & ~data.covered_A).sum()) if strategy == 'A' else 0,
                             median_width=data.loc[emit, 'width_A'].median() if produced else np.nan,
                             bias=float((data.estimate - data.truth).mean()),
                             bias_mcse=float(data.estimate.std(ddof=1) / np.sqrt(len(data))),
                             refusal_evaluation='actual C example plus deterministic count gate on every replicate' if strategy == 'C'
                                                else 'shared numerical estimate and explicit count rule'))
    pd.DataFrame(rows).to_csv(OUT / 'strategy_summary.csv', index=False)
    (OUT / 'actual_tool_examples.json').write_text(json.dumps(clean_json(tool_examples), indent=2,
                                                             allow_nan=False), encoding='utf-8')
    provenance = dict(config_sha256=hashlib.sha256((OUT / 'frozen_config.json').read_bytes()).hexdigest(),
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      tool_sha256=config['shared_tool'], numpy=np.__version__, pandas=pd.__version__,
                      thread_limits={name: os.environ.get(name) for name in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']})
    (OUT / 'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

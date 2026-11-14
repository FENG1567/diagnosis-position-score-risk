"""Make the coverage denominator and target-mismatch penalty explicit."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'outputs/v2/audit/confirmatory_v2/benchmark_replicate_metrics.csv'


def main():
    frame = pd.read_csv(SOURCE, low_memory=False)
    rows = []
    for (design, policy), data in frame.groupby(['design', 'policy'], sort=False):
        emitted = data.interval_emitted.astype(bool)
        matching = data.target_support_match.astype(bool)
        numerical = emitted & ((data.point - data.truth).abs() <= 1.96 * data.se)
        valid = numerical & matching
        n_emit = int(emitted.sum())
        n_on_target = int((emitted & matching).sum())
        coverage = valid.sum() / n_emit if n_emit else np.nan
        rows.append(dict(design=design, policy=policy, datasets=len(data), n_emitted=n_emit,
                         interval_output_pct=100 * n_emit / len(data),
                         n_emitted_on_declared_target=n_on_target,
                         off_target_output_pct=100 * (emitted & ~matching).sum() / len(data),
                         numerical_coverage_all_emitted_pct=100 * numerical.sum() / n_emit if n_emit else np.nan,
                         valid_target_coverage_all_emitted_pct=100 * coverage,
                         valid_target_coverage_mcse_pp=100 * np.sqrt(coverage * (1 - coverage) / n_emit) if n_emit else np.nan,
                         numerical_coverage_on_target_pct=100 * valid.sum() / n_on_target if n_on_target else np.nan,
                         definition='valid-target coverage counts wrong-target intervals as failures; numerical coverage alone can include accidental coverage of a different target'))
    pd.DataFrame(rows).to_csv(SOURCE.parent / 'benchmark_target_and_coverage_denominators.csv', index=False)


if __name__ == '__main__':
    main()

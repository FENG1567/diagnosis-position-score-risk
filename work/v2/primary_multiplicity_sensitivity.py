"""Adjusted normal intervals over the twenty planned primary score comparisons."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy.stats import norm

from analyse_panels import analysis_frame, audit_module, file_hash, normalize_panel


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/v2/measurement_sensitivity'
SOURCES = {
    'eICU-CRD': (ROOT / 'work/v2/eicu/eicu_disease_panel.csv.gz', 'eicu'),
    'MIMIC-IV': (Path('F:/分析专用/meta_measurement_20261103/work/paperB_v2/mimic/mimic_iv_v2_score_panel.csv.gz'), 'mimic_iv'),
}


def main():
    family_size = 20
    alpha = 0.05
    critical = norm.ppf(1 - alpha / (2 * family_size))
    module = audit_module()
    rows, inputs = [], []
    for database, (path, folder) in SOURCES.items():
        panel = normalize_panel(path)
        level_path = ROOT / 'outputs/v2/analysis' / folder / 'levels.csv'
        issued = pd.read_csv(level_path)
        inputs.extend([dict(path=str(p), sha256=file_hash(p)) for p in [path, level_path]])
        for disease, score, maximum in [('sepsis', 'qsofa', 3), ('pneumonia', 'curb65', 5)]:
            frame = analysis_frame(panel.loc[panel.disease.eq(disease) & panel.grp.notna()], score)
            for level in range(maximum + 1):
                cell = frame.loc[frame.score.eq(level)]
                source = issued.loc[issued.disease.eq(disease) & issued.level.eq(level)].iloc[0]
                point_only = source.delta_ci_status != 'computed'
                never, primary = cell.loc[cell.grp.eq(1)], cell.loc[cell.grp.eq(0)]
                p1, p0 = never.y.mean(), primary.y.mean()
                delta = p1 - p0
                lower = upper = se = np.nan
                if not point_only:
                    contribution = np.concatenate(((never.y.to_numpy() - p1) / len(never),
                                                   -(primary.y.to_numpy() - p0) / len(primary)))
                    patient = np.concatenate((never.pid.to_numpy(), primary.pid.to_numpy()))
                    se = np.sqrt(module._cluster_variance(contribution, patient,
                                                         total_clusters=frame.pid.nunique()))
                    pointwise = np.round(100 * np.array([delta - 1.96 * se, delta + 1.96 * se]), 2)
                    assert np.allclose(pointwise, [source.delta_ci_pp_lo, source.delta_ci_pp_hi])
                    lower, upper = delta - critical * se, delta + critical * se
                rows.append(dict(database=database, disease=disease, level=level,
                                 estimand='delta_s observed mortality difference', family_size=family_size,
                                 family_alpha=alpha, critical_value=critical,
                                 delta_pp=100 * delta, se_pp=100 * se,
                                 pointwise_lower_pp=source.delta_ci_pp_lo,
                                 pointwise_upper_pp=source.delta_ci_pp_hi,
                                 adjusted_lower_pp=100 * lower, adjusted_upper_pp=100 * upper,
                                 adjusted_excludes_zero=bool(lower > 0 or upper < 0) if not point_only else False,
                                 interval_status='point only under primary audit gate' if point_only else 'adjusted normal interval',
                                 interpretation='Bonferroni adjustment over all planned primary levels; asymptotic sensitivity with primary interval gates retained'))
    assert len(rows) == family_size
    OUT.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(rows)
    table.to_csv(OUT / 'primary_multiplicity_intervals.csv', index=False)
    summaries = []
    groups = list(table.groupby(['database', 'disease'], sort=False))
    groups.append((('all primary sources', 'all primary conditions'), table))
    for (database, disease), group in groups:
        summaries.append(dict(database=database, disease=disease, family_size=family_size,
                              planned_levels=len(group),
                              issued_intervals=int(group.interval_status.eq('adjusted normal interval').sum()),
                              pointwise_excludes_zero=int(((group.pointwise_lower_pp > 0)
                                                           | (group.pointwise_upper_pp < 0)).sum()),
                              adjusted_excludes_zero=int(group.adjusted_excludes_zero.sum()),
                              point_only_levels=int(group.interval_status.ne('adjusted normal interval').sum())))
    pd.DataFrame(summaries).to_csv(OUT / 'primary_multiplicity_summary.csv', index=False)
    provenance = dict(amendment='secondary multiplicity method specified after revised primary results',
                      inputs=inputs, script_sha256=file_hash(__file__),
                      audit_sha256=file_hash(ROOT / 'work/v2/audit/cohort_definition_audit.py'),
                      analysis_driver_sha256=file_hash(ROOT / 'work/v2/analyse_panels.py'))
    (OUT / 'primary_multiplicity_provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(table.to_string(index=False), flush=True)


if __name__ == '__main__':
    main()

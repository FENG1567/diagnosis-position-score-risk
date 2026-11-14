"""Regressions for actual source schemas and benchmark-policy alignment."""
from types import SimpleNamespace

import numpy as np
import pandas as pd

from analyse_panels import audited, normalize_panel
from robustness import analyze_robustness, variant_frame


def test_eicu_score_and_disease_aliases(tmp_path):
    path = tmp_path / 'panel.csv'
    pd.DataFrame(dict(disease=['acute pancreatitis', 'heart_failure'], admission_id=[1, 2],
                      pid=[1, 2], grp=[0, 1], died=[0, 1], qsofa_score=[0, 1],
                      curb65_score=[0, 1], bisap4_score=[0, 1], qsofa_gcs15_score=[0, 1])).to_csv(path, index=False)
    panel = normalize_panel(path)
    assert panel.disease.tolist() == ['pancreatitis', 'heart failure']
    assert panel.qsofa.tolist() == [0, 1]


def test_mimic_age_alias_and_breadth_position(tmp_path):
    path = tmp_path / 'panel.csv'
    pd.DataFrame(dict(disease=['sepsis', 'sepsis'], hadm_id=[1, 2], subject_id=[1, 2],
                      grp=[0, 1], died=[0, 1], qsofa=[1, 1], age_at_admit=[44, 75],
                      pos_narrow=[2, np.nan], pos_broad=[1, 2])).to_csv(path, index=False)
    panel = normalize_panel(path)
    assert panel.age.tolist() == [44, 75]
    narrow = variant_frame(panel, 'sepsis', 'qsofa', 'narrow')
    broad = variant_frame(panel, 'sepsis', 'qsofa', 'broad')
    assert len(narrow) == 1 and narrow.grp.tolist() == [1]
    assert broad.grp.tolist() == [0, 1]


def test_mixed_boolean_source_flags_are_normalized(tmp_path):
    path = tmp_path / 'panel.csv'
    pd.DataFrame(dict(disease=['sepsis'] * 2, admission_id=[1, 2], pid=[1, 2], grp=[0, 1],
                      died=[0, 1], qsofa=[0, 1], sepsis_narrow_member=['True', '1.0'],
                      sepsis_narrow_primary_all_icu=['True', '0'])).to_csv(path, index=False)
    panel = normalize_panel(path)
    variant = variant_frame(panel, 'sepsis', 'qsofa', 'narrow')
    assert variant.grp.tolist() == [0, 1]


def test_empirical_gate_matches_confirmatory_policy():
    captured = {}
    def fake_audit(frame, **kwargs):
        captured.update(kwargs['config'])
        return {'stratified_rd_pp': None, 'per_level': [], 'interval_status': 'not computed'}
    frame = pd.DataFrame(dict(pid=[1, 2, 3, 4], admission_id=[1, 2, 3, 4],
                              grp=[0, 0, 1, 1], y=[0, 1, 0, 1], score=[0, 0, 0, 0]))
    audited(SimpleNamespace(audit_v2=fake_audit), frame, 'synthetic', 'sepsis', 'test')
    assert captured['reps'] == 60
    assert captured['min_events'] == 10
    assert captured['min_usable_bootstrap'] == 20
    assert captured['min_clusters'] == 20


def test_refinement_identical_components_gives_zero_paired_change():
    source = pd.DataFrame(dict(pid=np.arange(80), admission_id=np.arange(80),
                               grp=np.tile([0, 1], 40), died=np.tile([0, 0, 1, 1], 20),
                               qsofa=np.ones(80), q_rr=np.ones(80), q_sbp=np.zeros(80),
                               q_gcs13=np.zeros(80), age=np.full(80, 60), gender=['M'] * 80,
                               pos_narrow=np.tile([1, 2], 40), pos_broad=np.tile([1, 2], 40)))
    rows, cells, timing = analyze_robustness(source, 'MIMIC-IV', 'sepsis', 'qsofa')
    changes = [row for row in rows if 'fine minus score-only' in row['analysis']]
    assert len(changes) == 2
    assert all(np.isclose(row['difference_pp'], 0) for row in changes)
    assert all(np.isclose(row['numerical_se_pp'], 0) for row in changes)
    assert cells and timing == []


def test_version_comparison_normal_entry_preserves_admission_matching(tmp_path, monkeypatch):
    import compare_versions
    import sys
    old_rows, new_rows = [], []
    for disease in ['sepsis', 'pneumonia']:
        for admission, outcome in zip(range(1, 5), [0, 1, 1, 0]):
            old_group = (admission + 1) % 2
            for stay in [admission * 10, admission * 10 + 1]:
                old_rows.append(dict(disease=disease, admission_id=str(admission), pid=admission,
                                     index_stay_id=str(stay), grp=old_group, y=outcome,
                                     qsofa=1.0, curb65=0.0, rr=22.0, gcs=15.0,
                                     sbp_min=120.0, dbp_min=80.0, age=60.0, bun=14.0))
            new_group = outcome if disease == 'sepsis' else old_group
            new_rows.append(dict(disease=disease, admission_id=admission, pid=admission,
                                 index_patientunitstayid=admission * 10, grp=new_group,
                                 died=outcome, qsofa=float(admission > 2), curb65=0.0))
    panel_path = tmp_path / 'new.csv'
    pd.DataFrame(new_rows).to_csv(panel_path, index=False)
    # Public fixture: provenance fingerprints must use synthetic files too.
    monkeypatch.setattr(compare_versions, 'PROJECT', tmp_path)
    (tmp_path / 'incoming').mkdir()
    pd.DataFrame(old_rows).to_csv(tmp_path / 'incoming/eicu_score_panel.csv.gz', index=False)
    pd.DataFrame({'synthetic_fixture': [True]}).to_csv(tmp_path / 'incoming/eicu_patient.csv.gz', index=False)
    monkeypatch.setattr(compare_versions, 'old_panel', lambda database: pd.DataFrame(old_rows))
    output = tmp_path / 'comparison'
    monkeypatch.setattr(sys, 'argv', ['compare_versions', '--panel', str(panel_path),
                                     '--database', 'eICU-CRD', '--outdir', str(output)])
    compare_versions.main()
    stages = pd.read_csv(output / 'version_comparison.csv')
    sepsis = stages.loc[stages.disease == 'sepsis']
    assert sepsis.iloc[0].n_input_records == 8
    assert sepsis.iloc[-1].n_input_records == 4
    changes = pd.read_csv(output / 'paired_version_changes.csv')
    position = changes.loc[(changes.disease == 'sepsis') & changes.comparison.str.startswith('G minus F')]
    assert np.isclose(position.iloc[0].difference_pp, 100)

"""Descriptive eICU uncertainty sensitivity to crossed patient and hospital clusters."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy.stats import t

from analyse_panels import SCORES, analysis_frame, file_hash, normalize_panel
from estimands import direct_contrast


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / 'work/v2/eicu/eicu_disease_panel.csv.gz'
OUT = ROOT / 'outputs/v2/measurement_sensitivity'


def main():
    panel = normalize_panel(PANEL)
    rows = []
    for disease, (score, _) in SCORES.items():
        source = panel.loc[panel.disease.eq(disease) & panel.grp.notna()].copy()
        frame = analysis_frame(source, score)
        if frame.hospitalid.isna().any():
            raise ValueError('Hospital identifiers are required for the matched clustering comparison')
        patient = direct_contrast(frame)
        hospital = direct_contrast(frame.assign(pid=frame.hospitalid))
        intersections = pd.factorize(pd.MultiIndex.from_frame(frame[['pid', 'hospitalid']]))[0]
        intersection = direct_contrast(frame.assign(pid=intersections))
        assert np.isclose(patient.estimate, hospital.estimate)
        assert np.isclose(patient.estimate, intersection.estimate)
        n_hospitals = frame.hospitalid.nunique()
        degrees_freedom = min(frame.pid.nunique(), n_hospitals) - 1
        critical = t.ppf(0.975, degrees_freedom)
        two_way_variance = patient.se**2 + hospital.se**2 - intersection.se**2
        patient_hospitals = frame.groupby('pid').hospitalid.nunique()
        for label, variance, formula in [
                ('hospital', hospital.se**2, 'V_hospital'),
                ('patient and hospital, two-way inclusion-exclusion', two_way_variance,
                 'V_patient + V_hospital - V_patient_hospital_intersection')]:
            valid = np.isfinite(variance) and variance > 0 and degrees_freedom > 0
            se = np.sqrt(variance) if valid else np.nan
            rows.append(dict(database='eICU-CRD', disease=disease,
                             analysis='clustering sensitivity after revised primary results',
                             estimand='Delta_w record-weighted summary on identical complete-case records',
                             cluster_definition=label, n_input_records=len(frame),
                             n_supported_records=patient.n_records, n_patients=frame.pid.nunique(),
                             n_hospitals=n_hospitals,
                             n_patients_across_hospitals=int(patient_hospitals.gt(1).sum()),
                             delta_w_pp=100 * patient.estimate, primary_patient_se_pp=100 * patient.se,
                             sensitivity_se_pp=100 * se, degrees_freedom=degrees_freedom,
                             lower_pp=100 * (patient.estimate - critical * se),
                             upper_pp=100 * (patient.estimate + critical * se),
                             interval_status='descriptive asymptotic t interval' if valid else 'invalid variance, point only',
                             variance_formula=formula,
                             limitation='crossed-cluster asymptotic sensitivity; calibration unverified for these empirical structures'))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / 'hospital_cluster_comparison.csv', index=False)
    dependencies = [Path(__file__), ROOT / 'work/v2/analyse_panels.py', ROOT / 'work/v2/estimands.py']
    provenance = dict(panel_sha256=file_hash(PANEL),
                      dependencies=[dict(path=str(path), sha256=file_hash(path)) for path in dependencies],
                      amendment='initiated after inspection of revised primary results',
                      interval='t critical value with minimum(patient count, hospital count) minus one degrees of freedom')
    (OUT / 'hospital_cluster_provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(pd.DataFrame(rows).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()

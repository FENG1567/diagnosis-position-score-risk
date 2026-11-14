# Release adaptations and verification boundary

The statistical estimators, reporting thresholds, simulation configurations, clinical reconstruction code and held-out model algorithms are unchanged. The new reproduce.py invokes the existing aggregate table builders and final numbering transform, compares all 59 output CSVs, and rerenders the two figures. It adds no clinical result.

The new run_private.py makes working copies, translates historical absolute path constants in runtime copies and refreshes executable copies when mappings/source change. Public source files and published results remain untouched. register_private_inputs.py records a new private rerun's protocol/code/input hashes without calling it preregistration. Three temporary-script regressions verify absolute-path isolation, mapping/source refresh and rejection of a public output root.

One original integration test mocked clinical input rows but still fingerprinted historical private files. Its public test fixture now creates synthetic provenance inputs and points only that test to its temporary directory. This changes the test fixture, not the estimator or clinical inputs.

One original bootstrap-precision smoke test additionally hashes a restricted Amsterdam patient panel. It remains included but is explicitly deselected from public CI. This is a documented unexecuted clinical-source check, not a passed test. All remaining selected tests use synthetic data or public metadata. No patient-level analysis or full 11,000-replicate benchmark was rerun for this packaging task; the complete frozen benchmark configuration and driver are included for independent reruns.

The final plotting labels use the existing v4 policy wording. Missing Arial on another platform can affect glyphs and PDF bytes. Scientific source values, interval statuses and the policy source table are checked separately from byte identity.

README and citation metadata use the current Journal of Intensive Care target and Liwei Liu as corresponding author. No repository URL, article DOI or clinical-source access entitlement is invented.

The original per-level pilot test wrote into outputs/v2; its public test output location is redirected to _generated/tests so repeated CI runs do not add simulated pilot files to the frozen source-input tree. The statistical test and pilot configuration are unchanged.

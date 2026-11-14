# Restricted-source patient-level reanalysis

This guide is for researchers who have independently obtained lawful access to the applicable source datasets. It supplements the public aggregate reproduction instructions in README.md; it does not distribute or grant access to restricted data.

## Scope and limits

The commands in reproduce.py reconstruct the included author-created aggregate tables and figures. They do not read patient records or independently recalculate patient-level confidence intervals. The private modules below are separate stages with dataset-specific inputs, prerequisites, and output locations. **There is no one-command end-to-end clinical reanalysis.** Follow each module's dependencies and review its --help output before running it.

Do not place raw source files, patient-level extracts, row-level caches, or clinical text in the public repository. The configured private working directory defaults to private/reanalysis, and generated private/ content is excluded from version control. Keep access credentials outside this package; the example configuration contains placeholders only.

## Data access and versions

Obtain source files directly from the data providers and confirm the current data use agreement and required training/access approvals. The analyses refer to eICU-CRD 2.0, MIMIC-IV 3.1, MIMIC-III 1.4, Zigong 1.1, and AmsterdamUMCdb. Provider pages:

- eICU-CRD: <https://physionet.org/content/eicu-crd/>
- MIMIC-IV: <https://physionet.org/content/mimiciv/>
- MIMIC-III: <https://physionet.org/content/mimiciii/>
- Zigong 1.1: <https://physionet.org/content/icu-infection-zigong-fourth/1.1/>
- AmsterdamUMCdb: <https://amsterdammedicaldatascience.nl/>

The database names and versions describe the source releases used by this project; they do not guarantee that a newly acquired copy, local extraction, or newer provider release is identical. Preserve source checksums and record any version differences in your private provenance.

## Private path configuration

Copy config/paths.example.json to config/paths.local.json and replace every destination placeholder with a path to your own authorized data and private work area. Do not commit paths.local.json. from_prefix values below are the historical source-code path prefixes; to_prefix values are local placeholders. Longer matching prefixes take precedence over shorter prefixes. The mapping is applied to copied code at execution time; public source files are left unchanged.

Example structure:

    {
      "run_root": "private/reanalysis",
      "environment": {
        "EICU_ROOT": "D:/authorized-data/eicu-crd"
      },
      "path_mappings": [
        {
          "from_prefix": "F:/分析专用/meta_measurement_20261103",
          "to_prefix": "private/reanalysis/legacy_private"
        },
        {
          "from_prefix": "D:/数据库集合/eicu数据库",
          "to_prefix": "D:/authorized-data/eicu-crd"
        },
        {
          "from_prefix": "D:/数据库集合/mimic数据/mimic-iv_3.1.0.zip",
          "to_prefix": "D:/authorized-data/mimic-iv/mimic-iv-3.1.0.zip"
        },
        {
          "from_prefix": "D:/数据库集合/mimic3/mimic-iii-clinical-database-1.4.zip",
          "to_prefix": "D:/authorized-data/mimic-iii/mimic-iii-clinical-database-1.4.zip"
        },
        {
          "from_prefix": "F:/分析专用/meta_measurement_20261103/incoming/zigong",
          "to_prefix": "D:/authorized-data/zigong"
        },
        {
          "from_prefix": "F:/分析专用/meta_measurement_20261103/work/paperB_v2/amsterdam/archive",
          "to_prefix": "D:/authorized-data/amsterdam/archive"
        }
      ]
    }

All D:/authorized-data/... destinations above are examples. Set EICU_ROOT and source-specific mappings to the real locations on your machine. If an input path is under a more specific source folder, add a longer from_prefix for that folder before relying on the broad historical F: project-root mapping. Do not map a restricted source to a public package folder.

The private runner interface is:

    python run_private.py --config config/paths.local.json work/v2/...py -- [original script arguments]

Pass each script's existing parameters after --. The runner is a path/working-copy helper; it is not a workflow orchestrator and does not infer missing data dependencies.

An older F:/.../work/02_code/run_all.sh belongs to a different paper package and is not an entry point for this audit.

## Source reconstruction modules

Run the source-specific reconstruction stages only after their licensed raw files are present and the path mappings resolve to those files. The actual interfaces below were checked against the corresponding script argument parsers; paths in the examples are placeholders.

### eICU

work/v2/eicu/build_eicu_v2.py reads the eICU source tables. It uses EICU_ROOT, which can be set through the environment object in the config. A full run has no required CLI arguments; --postprocess-only rebuilds scores and aggregates from an existing private cache without rereading raw tables:

    python run_private.py --config config/paths.local.json work/v2/eicu/build_eicu_v2.py
    python run_private.py --config config/paths.local.json work/v2/eicu/build_eicu_v2.py -- --postprocess-only

### MIMIC-IV

work/v2/mimic/m58_mimic_rebuild.py accepts --zip, --out-dir, --private-dir, and --cache-dir. It also supports --index-only, --aggregate-only, --force-rescan, --chart-chunksize, and --lab-chunksize. For example, after filling in local paths:

    python run_private.py --config config/paths.local.json work/v2/mimic/m58_mimic_rebuild.py -- --zip D:/authorized-data/mimic-iv/mimic-iv-3.1.0.zip --out-dir private/reanalysis/mimic_iv/output --private-dir private/reanalysis/mimic_iv/private --cache-dir private/reanalysis/mimic_iv/cache

--index-only limits a run to the admission index; --aggregate-only requires verified private index/event caches; --force-rescan ignores filtered event caches. Review the source and available storage before a full event-table scan.

### MIMIC-III

work/v2/mimic3/m58_mimic3_rebuild.py accepts --zip, --out-dir, --private-dir, and --cache-dir; additional options include --index-only, --allow-event-scan, --force-rescan, --chart-chunksize, and --lab-chunksize. A full event scan is explicitly gated by --allow-event-scan:

    python run_private.py --config config/paths.local.json work/v2/mimic3/m58_mimic3_rebuild.py -- --zip D:/authorized-data/mimic-iii/mimic-iii-clinical-database-1.4.zip --out-dir private/reanalysis/mimic_iii/output --private-dir private/reanalysis/mimic_iii/private --cache-dir private/reanalysis/mimic_iii/cache --allow-event-scan

Use --index-only for an index-only run. Do not add --allow-event-scan unless you intend and are authorized to process the full event tables.

### Zigong

work/v2/zigong/rebuild.py has no command-line argument parser. Its source and output paths are module constants, so configure them through path mappings before invoking it:

    python run_private.py --config config/paths.local.json work/v2/zigong/rebuild.py

The source's diagnosis fields must be described using their documented source meaning. Do not label its groups as primary versus secondary diagnoses unless that interpretation is independently established.

### AmsterdamUMCdb

work/v2/amsterdam/run_amsterdam_audit.py requires --phase preoutcome or --phase outcome; it also accepts --reps (default 400) and --seed (default 20261112). Configure its private/archive paths first:

    python run_private.py --config config/paths.local.json work/v2/amsterdam/run_amsterdam_audit.py -- --phase preoutcome
    python run_private.py --config config/paths.local.json work/v2/amsterdam/run_amsterdam_audit.py -- --phase outcome --reps 400 --seed 20261112

Those commands describe the earlier strict-unit reference. The final supplementary application uses `work/v2/amsterdam/run_amsterdam_dictionary_unit_repair.py` after the strict private intermediates exist. This module also requires `--phase preoutcome` or `--phase outcome`, with final policy defaults `--reps 60 --seed 20261112`. Its official dictionary (SHA256 recorded in the source) and pinned SQL references are supplied as third-party metadata/code; they contain no patient rows. Run the preoutcome repair and the repaired outcome stage in that order, retaining the separate strict and repaired provenance. Do not substitute the strict 400-draw reference for the final repaired analysis.

## Downstream analyses

The following modules consume reconstructed panels, frozen manifests, or source-specific private derivatives; they are not substitutes for the reconstruction steps above.

- work/v2/analyse_panels.py requires --panel, --database, and --outdir and produces the per-panel analysis outputs.
- work/v2/conditional_validation/run_final_clinical.py has no CLI options. It consumes the registered validated input panels and requires the expected validation manifest and Amsterdam repair output; the code stops if a source repair is still pending. Do not invoke it until those prerequisites have been created and reviewed.
- work/v3/validation/count_eligibility.py accepts --eicu-panel, --mimic-panel, and --outdir to create aggregate eligibility tables for the held-out migration evaluation.
- work/v3/validation/fit_and_validate.py accepts the same panel/output arguments plus --bootstrap-reps, which is fixed by the protocol constant. Its frozen eligibility manifest must be present and pass integrity checks before fitting.
- work/v4/composition.py reads the defined source panels and source tables to rebuild aggregate composition outputs. Its data paths are module constants; configure them in the local mapping.

Review each module's documented protocol, dependencies, and input hash checks before proceeding. These stages have not been wrapped into a verified, one-command patient-level workflow. Do not infer that public aggregate reproduction demonstrates successful full patient-level reanalysis.

Path-adapted runtime code has different file hashes from the historical study. Before running the held-out fitting stage in a staged working copy, explicitly register its protocol, code and authorized input-panel hashes:

    python register_private_inputs.py --run-root private/reanalysis --eicu-panel /absolute/path/to/authorized/eicu_panel.csv.gz --mimic-panel /absolute/path/to/authorized/mimic_panel.csv.gz

First create the private working copy through run_private.py (the eligibility stage is suitable). The registration helper preserves the original study manifest and writes a new private rerun manifest, labeled as a reproduction attempt rather than preregistration. It refuses panel-byte differences from the original inputs unless the researcher explicitly supplies --allow-input-differences after inspecting them; such a run must not be described as original-file-identical. Regenerated gzip timestamps can also change file hashes, so investigate rather than silently relaxing this check. The registration helper does not fit models or certify equivalence of changed inputs.

The original bootstrap-precision `test_real_adapter_and_report_smoke` additionally verifies the hash of an actual restricted Amsterdam panel. Public CI explicitly deselects this one test. It is not counted as a passed clinical-source verification. Authorized users may run the full test after configuring the relevant source panel and matching manifest in their private run root.

## Interpretation and reporting

δ_s is a direct difference between observed mortality proportions within a score stratum, without adjustment by a fitted model. Δ_w is a record-weighted summary and has a different interpretation. Keep them distinct in tables and prose. The primary comparison is limited to the specified eICU and MIMIC-IV sepsis and pneumonia cohorts. The Zigong grouping semantics remain unverified, and BISAP-4 is a distinct score definition from BISAP. Report the exact dataset release, code version, source-file hashes, exclusions, unavailable estimates, and any deviation from the frozen protocol. Never copy patient identifiers, records, or clinical text into public outputs.

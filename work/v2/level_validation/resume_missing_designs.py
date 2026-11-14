#!/usr/bin/env python3
"""Resume absent per-design checkpoints without changing the frozen runner."""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import run_per_level_validation as frozen_runner


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parents[2]
OUTPUT_DIR = WORK_ROOT / "outputs" / "v2" / "level_validation"
CHECKPOINT_DIR = OUTPUT_DIR / "replicate_checkpoints"
FREEZE_PATH = OUTPUT_DIR / "pre_run_freeze.json"
MANIFEST_PATH = OUTPUT_DIR / "recovery_resume_manifest.json"
EXPECTED_FREEZE = {
    "config_sha256": "7e7abd7406148a2cc53b7d1e8cab9119291cf6bf21263c905481acbf21908dff",
    "shared_inference_tool_sha256": "8b074a3b3adf808311cc42e7f3fdf7d24427e31aab421569ea3460b07c184994",
    "dgp_generator_sha256": "43dc393dbd804a29c9948a9245b4125537061408f57d72a1268b603bd852eb14",
    "runner_sha256": "d0ab55e070292bd650dc6b6a7f80632567dd02f67523ee5413c8028b34809421",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkpoint_path(index: int, design: dict) -> Path:
    return CHECKPOINT_DIR / f"replicates_{index + 1:02d}_{design['name']}.csv"


def validate_checkpoint(path: Path, index: int, design: dict, reps: int) -> dict:
    frame = pd.read_csv(path)
    expected_rows = reps * len(design["scores"]) * 3
    observed_replicates = sorted(map(int, frame["replicate"].unique()))
    if len(frame) != expected_rows or observed_replicates != list(range(reps)):
        raise ValueError(
            f"{path.name} has {len(frame)} rows and replicate IDs "
            f"{observed_replicates[:3]}..{observed_replicates[-3:]}; expected "
            f"{expected_rows} rows and 0..{reps - 1}"
        )
    if set(frame["design"].astype(str).unique()) != {design["name"]}:
        raise ValueError(f"{path.name} contains an unexpected design label")
    if frame.groupby("replicate", sort=False).size().ne(len(design["scores"]) * 3).any():
        raise ValueError(f"{path.name} does not contain three rows per score and replicate")
    expected_estimands = {"group_risk", "delta_s"}
    if set(frame["estimand"].astype(str).unique()) != expected_estimands:
        raise ValueError(f"{path.name} has unexpected estimand labels")
    return {
        "design_index": index,
        "design": design["name"],
        "path": str(path.relative_to(OUTPUT_DIR)),
        "rows": len(frame),
        "replicates": len(observed_replicates),
        "sha256": sha256(path),
    }


def write_manifest(manifest: dict) -> None:
    manifest["updated_utc"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    config_path = frozen_runner.DEFAULT_CONFIG.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    frozen_runner.validate_config(config)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    audit_path = frozen_runner.AUDIT_DIR / "cohort_definition_audit.py"
    benchmark_path = frozen_runner.AUDIT_DIR / "benchmark.py"
    actual_hashes = {
        "config_sha256": sha256(config_path),
        "shared_inference_tool_sha256": sha256(audit_path),
        "dgp_generator_sha256": sha256(benchmark_path),
        "runner_sha256": sha256(Path(frozen_runner.__file__).resolve()),
    }
    if actual_hashes != EXPECTED_FREEZE:
        raise RuntimeError(f"frozen input hash mismatch: {actual_hashes}")

    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    for key, value in EXPECTED_FREEZE.items():
        if freeze.get(key) != value:
            raise RuntimeError(f"pre-run freeze mismatch for {key}")

    reps = int(config["outer_replicates_per_design"])
    initial_checkpoints = []
    missing_designs = []
    for index, design in enumerate(config["designs"]):
        path = checkpoint_path(index, design)
        if path.exists():
            initial_checkpoints.append(validate_checkpoint(path, index, design, reps))
        else:
            missing_designs.append((index, design))

    manifest = {
        "record_type": "missing_design_checkpoint_recovery",
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "config_sha256": actual_hashes["config_sha256"],
        "runner_path": str(Path(frozen_runner.__file__).resolve()),
        "runner_sha256": actual_hashes["runner_sha256"],
        "shared_inference_tool_sha256": actual_hashes["shared_inference_tool_sha256"],
        "dgp_generator_sha256": actual_hashes["dgp_generator_sha256"],
        "seed": int(config["seed"]),
        "replicates_per_design": reps,
        "design_count": len(config["designs"]),
        "recovery_method": (
            "Separate adapter imports the frozen runner's load_sources/validation helpers; "
            "it applies the identical per-design seed formula and row construction for missing "
            "designs only. The frozen runner source, original config, DGP, and inference tool "
            "are not modified. Final aggregation is performed by the frozen runner in "
            "aggregate-only mode against the complete original checkpoint set."
        ),
        "preexisting_validated_checkpoints": initial_checkpoints,
        "missing_designs_at_start": [
            {"design_index": index, "design": design["name"]}
            for index, design in missing_designs
        ],
        "newly_generated_checkpoints": [],
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "thread_limits": {
            key: os.environ.get(key)
            for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
    }
    write_manifest(manifest)

    simulate_dataset, per_level_inference = frozen_runner.load_sources()
    thresholds = config["inference_validation"]
    min_patients = int(thresholds["min_patients"])
    min_records_per_arm = int(thresholds["min_records_per_arm"])
    min_records_per_level = int(thresholds["min_records_per_level"])
    start = time.monotonic()

    try:
        for design_index, design in missing_designs:
            design_name = design["name"]
            scores = list(map(float, design["scores"]))
            joint = np.asarray(design["joint_probabilities_group_score"], dtype=float)
            risks = np.asarray([design["risks_principal"], design["risks_never"]], dtype=float)
            common_levels = set(map(float, design["expected_support"]))
            group_truth_defined = {
                (float(score), int(group)): bool(joint[group, j] > 0)
                for j, score in enumerate(scores) for group in (0, 1)
            }
            delta_truth_defined = {
                float(score): bool(joint[0, j] > 0 and joint[1, j] > 0)
                for j, score in enumerate(scores)
            }
            base_seed = int(config["seed"]) + design_index * 1_000_003
            replicate_rows: list[dict] = []

            for rep in range(reps):
                rng = np.random.default_rng(base_seed + rep * 10_007)
                frame = simulate_dataset(design, rng)
                input_df = frame.rename(columns={"y": "outcome"})
                results = per_level_inference(
                    input_df, scores, min_patients=min_patients,
                    min_records_per_arm=min_records_per_arm,
                    min_records_per_level=min_records_per_level,
                )
                if len(results) != len(scores):
                    raise RuntimeError(
                        f"unexpected per-level output length in {design_name} rep {rep}"
                    )

                for j, result in enumerate(results):
                    score = float(result["level"])
                    if score != scores[j]:
                        raise RuntimeError(f"level order changed in {design_name} rep {rep}")
                    n0, n1 = int(result["n_primary"]), int(result["n_never"])
                    patients0, patients1 = int(result["patients_primary"]), int(result["patients_never"])
                    events0, events1 = int(result["events_primary"]), int(result["events_never"])
                    is_common = score in common_levels
                    support_type = (
                        "common_support" if is_common else
                        "one_definition_support" if (joint[0, j] > 0 or joint[1, j] > 0)
                        else "structurally_absent"
                    )
                    shared_counts = {
                        "design": design_name,
                        "replicate": rep,
                        "level": score,
                        "support_type": support_type,
                        "n_principal": n0,
                        "n_never": n1,
                        "patients_principal": patients0,
                        "patients_never": patients1,
                        "events_principal": events0,
                        "events_never": events1,
                    }

                    for group, arm, risk_field, ci_field, status_field, n in (
                        (0, "principal", "risk_primary", "risk_primary_ci_pp",
                         "risk_primary_ci_status", n0),
                        (1, "never", "risk_never", "risk_never_ci_pp",
                         "risk_never_ci_status", n1),
                    ):
                        truth_defined = group_truth_defined[(score, group)]
                        point = result[risk_field]
                        lo, hi = frozen_runner._ci_bounds(result, ci_field)
                        status = result[status_field]
                        truth = 100 * float(risks[group, j]) if truth_defined else None
                        covered = (
                            bool(lo <= truth <= hi)
                            if truth_defined and status == "computed" else None
                        )
                        replicate_rows.append({
                            **shared_counts,
                            "estimand": "group_risk",
                            "arm": arm,
                            "truth_defined": truth_defined,
                            "target_common_support": is_common,
                            "truth_pp": truth,
                            "point_pp": point,
                            "ci_lower_pp": lo,
                            "ci_upper_pp": hi,
                            "ci_status": status,
                            "observed_cell_present": n > 0,
                            "covered": covered,
                        })

                    truth_defined = delta_truth_defined[score]
                    delta_point = result["diff_pp"]
                    lo, hi = frozen_runner._ci_bounds(result, "delta_ci_pp")
                    status = result["delta_ci_status"]
                    truth = (
                        100 * (float(risks[1, j]) - float(risks[0, j]))
                        if truth_defined else None
                    )
                    replicate_rows.append({
                        **shared_counts,
                        "estimand": "delta_s",
                        "arm": "never_minus_principal",
                        "truth_defined": truth_defined,
                        "target_common_support": is_common,
                        "truth_pp": truth,
                        "point_pp": delta_point,
                        "ci_lower_pp": lo,
                        "ci_upper_pp": hi,
                        "ci_status": status,
                        "observed_cell_present": bool(n0 > 0 and n1 > 0),
                        "covered": (
                            bool(lo <= truth <= hi)
                            if truth_defined and status == "computed" else None
                        ),
                    })

            expected_rows = reps * len(scores) * 3
            if len(replicate_rows) != expected_rows:
                raise RuntimeError(
                    f"row-count mismatch for {design_name}: {len(replicate_rows)} != {expected_rows}"
                )
            destination = checkpoint_path(design_index, design)
            fd, temporary_name = tempfile.mkstemp(
                prefix=f".{destination.stem}.", suffix=".tmp", dir=CHECKPOINT_DIR
            )
            os.close(fd)
            temporary_path = Path(temporary_name)
            try:
                pd.DataFrame.from_records(replicate_rows).to_csv(
                    temporary_path, index=False, encoding="utf-8"
                )
                # Re-open and validate before atomically installing a complete file.
                validate_checkpoint(temporary_path, design_index, design, reps)
                temporary_path.replace(destination)
            finally:
                if temporary_path.exists():
                    temporary_path.unlink()
            record = validate_checkpoint(destination, design_index, design, reps)
            manifest["newly_generated_checkpoints"].append(record)
            manifest["elapsed_seconds"] = round(time.monotonic() - start, 3)
            write_manifest(manifest)
            print(
                f"[per-level-recovery] completed {design_index + 1}/{len(config['designs'])}: "
                f"{design_name}; checkpoint={destination.name}",
                flush=True,
            )
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["failure"] = f"{type(exc).__name__}: {exc}"
        manifest["elapsed_seconds"] = round(time.monotonic() - start, 3)
        write_manifest(manifest)
        raise

    # Revalidate every checkpoint after recovery before reporting completion.
    all_checkpoints = [
        validate_checkpoint(checkpoint_path(index, design), index, design, reps)
        for index, design in enumerate(config["designs"])
    ]
    manifest["all_checkpoints"] = all_checkpoints
    manifest["status"] = "complete_checkpoints_ready_for_frozen_aggregation"
    manifest["elapsed_seconds"] = round(time.monotonic() - start, 3)
    write_manifest(manifest)
    print(
        f"[per-level-recovery] all {len(all_checkpoints)} frozen design checkpoints validated; "
        "run the frozen runner with --aggregate-only",
        flush=True,
    )


if __name__ == "__main__":
    main()

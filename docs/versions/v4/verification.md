# V4 Verification

## Checks Performed
- Verified MLflow tracking config loads from `configs/training.yaml`.
- Verified invalid MLflow tracking config fails safely.
- Verified MLflow params include model type, split config, dataset version, checksum, and pipeline version.
- Verified numeric metrics are logged while non-numeric metric structures are skipped.
- Verified training and evaluation durations are included in MLflow metrics.
- Verified MLflow artifacts are logged through the helper.
- Verified dedicated confusion matrix artifact path is built from config.
- Verified dedicated confusion matrix artifact is logged to MLflow.
- Verified failed errors inside an active MLflow run are tagged with failure details.
- Verified timed evaluation returns normal metrics and a non-negative duration.
- Verified Decision Tree and Random Forest model construction.
- Verified experiment candidate config parsing and per-candidate artifact directories.
- Verified champion selection prefers highest F1 and applies tie-breakers.
- Verified different dataset checksum candidates are rejected.
- Verified MLflow run tags can be set on existing runs.
- Verified previous champion tags are cleared before a new champion is selected.
- Verified single-model `app.train` still works.
- Verified multi-model `app.run_experiments` creates candidate runs and a champion report.
- Verified local `reports/champion_run.json` is written.
- Verified MLflow shows exactly one active `champion=true` run after the latest candidate sweep.
- Verified validation and reproducibility commands still pass after V4 changes.

## Commands Executed
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c7_baseline_model_training.py`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c6_champion_selection.py`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c6_experiment_candidates.py`
- `.\vir_env\Scripts\python.exe -m pytest -q`
- `.\vir_env\Scripts\python.exe -m app.run_experiments`
- `.\vir_env\Scripts\python.exe -m app.train`
- `.\vir_env\Scripts\python.exe -m app.validate_data`
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility`
- `.\vir_env\Scripts\python.exe -c "import mlflow; ..."`
- `Get-Content reports\champion_run.json`

## Expected Output
- Focused V4 and trainer tests pass.
- Full test suite passes.
- Single-model training still creates a finished MLflow run.
- Multi-model experiment command creates one MLflow run per candidate.
- Candidate runs include `candidate_name` tags.
- Exactly one latest active run is tagged `champion=true`.
- Champion report records champion run, eligible runs, metrics, dataset checksum, and selection rule.
- Validation and reproducibility still pass.

## Actual Output
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c7_baseline_model_training.py` returned `7 passed in 1.74s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `10 passed in 0.46s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c6_champion_selection.py` returned `4 passed in 0.02s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c6_experiment_candidates.py` returned `4 passed in 1.43s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `160 passed in 2.16s`.
- `.\vir_env\Scripts\python.exe -m app.run_experiments` completed successfully.
- Latest candidate run IDs were `94b658840cbc447b85eeb31086d89378`, `39b6d1a8b63b46c58709b06d6e711cb2`, and `fa64772b235f4fc68540e1efc9d65401`.
- Latest champion run ID was `39b6d1a8b63b46c58709b06d6e711cb2`.
- Latest champion model type was `decision_tree`.
- Latest champion report selected the run by F1-first rule with tie-breakers and same dataset checksum.
- MLflow query showed exactly `1` active `champion=true` run after champion cleanup.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and created MLflow run `1f1001937f324071b0533ee05d1d58de`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed with `status=passed` and `issues=0`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed with `status=passed`.

## Outcome
V4 now supports real multi-model experiment comparison and champion selection, not just manual single-model tracking.

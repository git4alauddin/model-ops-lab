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
- Verified training creates a real MLflow run.
- Verified training metadata includes `mlflow_run_id`.
- Verified training metadata includes `evaluation_duration_seconds`.
- Verified local `artifacts/confusion_matrix.json` is written.
- Verified latest MLflow run contains `confusion_matrix.json` in artifact listing.
- Verified validation and reproducibility commands still pass after V4 tracking changes.

## Commands Executed
- `.\vir_env\Scripts\python.exe -m pip install -r requirements.txt`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c10_artifact_persistence.py`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c9_evaluation_metrics.py`
- `.\vir_env\Scripts\python.exe -m pytest -q`
- `.\vir_env\Scripts\python.exe -m app.train`
- `.\vir_env\Scripts\python.exe -m app.validate_data`
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility`
- `.\vir_env\Scripts\python.exe -c "import mlflow; ..."`

## Expected Output
- V4 focused tests pass.
- Existing V1, V2, and V3 tests continue passing.
- Training completes after validation.
- MLflow creates a finished run.
- Training metadata stores the MLflow run ID.
- Training metadata stores evaluation duration.
- Local `artifacts/confusion_matrix.json` is created.
- MLflow run contains parameters, metrics, duration metrics, and the confusion matrix artifact.
- Failed in-run errors are visible as MLflow tags.

## Actual Output
- `.\vir_env\Scripts\python.exe -m pip install -r requirements.txt` installed `mlflow 3.13.0` during V4-C1 setup.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c10_artifact_persistence.py` returned `4 passed in 1.34s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `8 passed in 0.05s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c9_evaluation_metrics.py` returned `6 passed in 1.37s` during V4-C2 verification.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `148 passed in 2.05s`.
- First real V4-C1 training run with `file:./mlruns` failed because MLflow 3 blocks the filesystem tracking backend by default.
- Switched local tracking to `sqlite:///mlflow.db`.
- During V4-C2 runtime verification, the first training run exposed a missing `_load_mlflow()` helper.
- Restored `_load_mlflow()` with a safe `ExperimentTrackingError` for missing MLflow installations.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and created MLflow run `4d269974b64147cda439311170bf8d35`.
- Generated `artifacts/training_metadata.json` includes `mlflow_run_id` and `evaluation_duration_seconds`.
- Generated `artifacts/confusion_matrix.json` contains `labels=[0, 1]` and `matrix=[[3, 0], [0, 1]]`.
- Latest MLflow run query showed `status=FINISHED`, `metrics.accuracy=1.0`, `metrics.f1=1.0`, and `params.pipeline_version=v4-c3`.
- Latest MLflow artifact listing showed `config_snapshot.json`, `confusion_matrix.json`, `metrics.json`, `model.pkl`, and `training_metadata.json`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed with `status=passed` and `issues=0`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed with `status=passed`.

## Outcome
V4-C3 dedicated confusion matrix artifact is operational and visible through MLflow artifacts.

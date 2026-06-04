# V4 Commit Log

This file records meaningful V4 commits and the operational purpose of each change.

## Pending - v4-c2: add failed-run tracking and evaluation duration

### What Changed
- Added timed evaluation helper.
- Persisted `evaluation_duration_seconds` in training metadata.
- Logged evaluation duration in the formatted training logs.
- Logged training and evaluation durations to MLflow metrics.
- Added failed-run tags for errors raised inside an active MLflow run.
- Preserved the original training-body exception when run tracking records a failure.
- Restored real MLflow module loading for production runtime commands.
- Added focused tests for timed evaluation, duration metric building, and failed-run tagging.
- Updated V4 implementation, verification, lessons, and issues docs.
- Updated README V4 status.

### What Problem It Solved
- Makes run timing visible in MLflow for experiment comparison.
- Makes failed training runs easier to inspect from MLflow tags.
- Keeps local training metadata aligned with tracked experiment metrics.
- Ensures the real training command exercises the production MLflow loader path.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `8 passed in 0.04s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c9_evaluation_metrics.py` returned `6 passed in 1.37s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `148 passed in 2.01s`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and created MLflow run `172efc2f2a704d469d65f98451d5c8ec`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed with `status=passed` and `issues=0`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed with `status=passed`.
- Generated `artifacts/training_metadata.json` includes `mlflow_run_id` and `evaluation_duration_seconds`.
- Latest MLflow run query showed `status=FINISHED`, `metrics.accuracy=1.0`, `metrics.f1=1.0`, `metrics.training_duration_seconds=0.009198`, `metrics.evaluation_duration_seconds=0.009016`, and `params.pipeline_version=v4-c2`.

## e519049 - v4-c1: add MLflow tracking foundation

### What Changed
- Added MLflow dependency.
- Added MLflow tracking config.
- Added experiment tracking helper module.
- Integrated MLflow run creation into training.
- Logged core training parameters to MLflow.
- Logged numeric evaluation metrics to MLflow.
- Logged training artifacts to MLflow.
- Persisted `mlflow_run_id` in training metadata.
- Added focused V4-C1 MLflow tracking tests.
- Added V4 documentation files.
- Updated README with V4 status and MLflow UI instructions.
- Corrected the V3-C6 commit log entry from `Pending` to `f5f1881`.

### What Problem It Solved
- Makes each training run inspectable from MLflow.
- Links training metadata to an MLflow run ID.
- Records dataset version context with experiment parameters.
- Creates the foundation for experiment comparison.

### Verification
- `.\vir_env\Scripts\python.exe -m pip install -r requirements.txt` installed `mlflow 3.13.0`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `5 passed in 0.04s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `144 passed in 3.97s`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after switching local MLflow tracking to `sqlite:///mlflow.db`.
- Generated `artifacts/training_metadata.json` includes `mlflow_run_id`.
- MLflow run query showed `status=FINISHED`, `metrics.accuracy=1.0`, `metrics.f1=1.0`, `params.model_type=logistic_regression`, and `params.dataset_version=v1`.

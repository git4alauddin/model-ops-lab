# V4 Commit Log

This file records meaningful V4 commits and the operational purpose of each change.

## Pending - v4-c1: add MLflow tracking foundation

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

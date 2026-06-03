# V4 Verification

## Checks Performed
- Verified MLflow tracking config loads from `configs/training.yaml`.
- Verified invalid MLflow tracking config fails safely.
- Verified MLflow params include model type, split config, dataset version, and checksum.
- Verified numeric metrics are logged while non-numeric metric structures are skipped.
- Verified MLflow artifacts are logged through the helper.
- Verified training creates a real MLflow run.
- Verified training metadata includes `mlflow_run_id`.
- Verified MLflow run contains accuracy, F1, model type, and dataset version.

## Commands Executed
- `.\vir_env\Scripts\python.exe -m pip install -r requirements.txt`
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py`
- `.\vir_env\Scripts\python.exe -m pytest -q`
- `.\vir_env\Scripts\python.exe -m app.train`
- `.\vir_env\Scripts\python.exe -c "import mlflow; ..."`

## Expected Output
- V4-C1 focused tests pass.
- Existing V1, V2, and V3 tests continue passing.
- Training completes after validation.
- MLflow creates a finished run.
- Training metadata stores the MLflow run ID.
- MLflow run contains parameters and metrics.

## Actual Output
- `.\vir_env\Scripts\python.exe -m pip install -r requirements.txt` installed `mlflow 3.13.0`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `5 passed in 0.04s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `144 passed in 3.97s`.
- First real training run with `file:./mlruns` failed because MLflow 3 blocks the filesystem tracking backend by default.
- Switched local tracking to `sqlite:///mlflow.db`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and created MLflow run `0685cc7ef377427283aae5499b3f2185`.
- Generated `artifacts/training_metadata.json` includes `mlflow_run_id`.
- MLflow run query showed `status=FINISHED`, `metrics.accuracy=1.0`, `metrics.f1=1.0`, `params.model_type=logistic_regression`, and `params.dataset_version=v1`.

## Outcome
V4-C1 MLflow tracking foundation is operational.

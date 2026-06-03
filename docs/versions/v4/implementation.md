# V4 Implementation

## Scope
Chunk V4-C1: MLflow tracking foundation.

## V4-C1 Additions
- `requirements.txt`
  - added `mlflow>=3.0.0`
- `.gitignore`
  - ignores local MLflow runtime stores
  - ignores `mlflow.db*`, `mlruns/`, and `mlartifacts/`
- `configs/training.yaml`
  - added `experiment_tracking.experiment_name`
  - added `experiment_tracking.tracking_uri`
  - uses `sqlite:///mlflow.db` for local tracking
- `app/experiment_tracking.py`
  - added `ExperimentTrackingError`
  - added config parsing with defaults
  - added MLflow run context helper
  - added run ID extraction helper
  - added flat parameter construction
  - added metric and artifact logging
- `app/train.py`
  - starts an MLflow run after validation passes
  - persists `mlflow_run_id` in `artifacts/training_metadata.json`
  - logs model, split, dataset version, and checksum parameters
  - logs numeric evaluation metrics
  - logs model, metrics, config snapshot, and metadata artifacts
  - writes `[EXPERIMENT]` section with MLflow run ID
- `tests/test_v4_c1_mlflow_tracking_foundation.py`
  - validates MLflow tracking config parsing
  - validates MLflow parameter construction
  - validates MLflow run setup using a fake MLflow module
  - validates params, metrics, and artifact logging using a fake MLflow module
  - validates invalid tracking config failure
- `README.md`
  - added V4 status
  - added MLflow UI command
- `docs/versions/v4/`
  - added V4 overview, implementation notes, verification notes, lessons, issues, and commit log

## Current V4-C1 Workflow
```text
python -m app.train
  -> run validation gate
  -> start MLflow run
  -> train baseline model
  -> evaluate held-out test set
  -> persist local artifacts
  -> log MLflow params
  -> log MLflow metrics
  -> log MLflow artifacts
  -> persist mlflow_run_id in training metadata
```

## Remaining V4 Gaps
- Failed-run tracking is not explicit yet.
- Evaluation duration is not logged yet.
- Confusion matrix is not logged as a dedicated MLflow artifact yet.
- Multiple experiment comparison docs are not added yet.
- Best-run selection rule is not added yet.

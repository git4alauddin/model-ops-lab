# V4 Implementation

## Scope
V4 adds experiment tracking and training observability on top of the V1-V3 pipeline.

Implemented chunks:
- V4-C1: MLflow tracking foundation.
- V4-C2: failed-run tracking and evaluation duration.

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

## V4-C2 Additions
- `app/evaluate.py`
  - added `evaluate_model_with_duration`
  - returns normal evaluation metrics plus elapsed evaluation time
- `app/experiment_tracking.py`
  - added `build_mlflow_metrics`
  - logs `training_duration_seconds`
  - logs `evaluation_duration_seconds`
  - tags failed in-run errors with `run_outcome=failed`
  - tags failed in-run errors with `failure_type`
  - tags failed in-run errors with `failure_message`
  - preserves the original exception from the training body instead of replacing it with a run-start error
- `app/train.py`
  - uses timed evaluation
  - persists `evaluation_duration_seconds` in training metadata
  - writes evaluation duration in the `[EVALUATION]` log section
  - logs evaluation duration to MLflow as a metric
- `tests/test_v1_c9_evaluation_metrics.py`
  - validates timed evaluation returns metrics and a duration
- `tests/test_v4_c1_mlflow_tracking_foundation.py`
  - validates MLflow duration metric construction
  - validates failed body errors are tagged on the active run

## Current V4 Workflow
```text
python -m app.train
  -> run validation gate
  -> start MLflow run
  -> train baseline model
  -> evaluate held-out test set with duration timing
  -> persist local artifacts
  -> log MLflow params
  -> log MLflow metrics, including training and evaluation duration
  -> log MLflow artifacts
  -> persist mlflow_run_id and evaluation duration in training metadata
```

If an error happens after the MLflow run starts:

```text
active MLflow run
  -> tag run_outcome=failed
  -> tag failure_type=<exception class>
  -> tag failure_message=<exception message>
  -> re-raise the original exception
```

## Remaining V4 Gaps
- Confusion matrix is not logged as a dedicated MLflow artifact yet.
- Multiple experiment comparison docs are not added yet.
- Best-run selection rule is not added yet.

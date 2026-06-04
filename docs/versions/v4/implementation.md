# V4 Implementation

## Scope
V4 adds experiment tracking and training observability on top of the V1-V3 pipeline.

Implemented chunks:
- V4-C1: MLflow tracking foundation.
- V4-C2: failed-run tracking and evaluation duration.
- V4-C3: dedicated confusion matrix MLflow artifact.
- V4-C4: MLflow experiment comparison guide.
- V4-C5: best-run selection rule.

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

## V4-C3 Additions
- `configs/training.yaml`
  - added `artifacts.confusion_matrix_file`
- `app/utils/artifacts.py`
  - added `confusion_matrix` artifact path construction
- `app/experiment_tracking.py`
  - bumped tracked `pipeline_version` to `v4-c3`
- `app/train.py`
  - persists `artifacts/confusion_matrix.json`
  - writes labels and matrix in a self-contained JSON structure
  - includes `confusion_matrix` in the formatted `[ARTIFACTS]` log section
  - logs the dedicated confusion matrix file to MLflow with the other artifacts
- `tests/test_v1_c10_artifact_persistence.py`
  - validates confusion matrix artifact path construction
- `tests/test_v4_c1_mlflow_tracking_foundation.py`
  - validates MLflow artifact logging includes the dedicated confusion matrix artifact

## V4-C4 Additions
- `docs/experiments/mlflow_comparison_guide.md`
  - added manual MLflow run comparison workflow
  - documents params, metrics, artifacts, and tags to inspect
  - explains duration-vs-quality tradeoffs
  - adds a manual comparison checklist
  - clarifies when to use UI vs SQL
- `docs/experiments/README.md`
  - added guide pointer

## V4-C5 Additions
- `docs/experiments/best_run_selection_rule.md`
  - added eligible-run requirements
  - defines same-data comparison using dataset name, version, and checksum
  - selects `f1` as the primary ranking metric
  - defines secondary metric checks using precision, recall, accuracy, and confusion matrix
  - defines tie-breakers: recall, precision, accuracy, runtime, simplicity, pipeline version
  - defines rejection rules for incomplete or invalid runs
  - adds manual selection checklist and decision record format
- `docs/experiments/mlflow_comparison_guide.md`
  - links comparison workflow to the best-run selection rule
- `docs/experiments/README.md`
  - indexes the best-run selection rule

## Current V4 Workflow
```text
python -m app.train
  -> run validation gate
  -> start MLflow run
  -> train baseline model
  -> evaluate held-out test set with duration timing
  -> persist local artifacts
  -> persist dedicated confusion_matrix.json
  -> log MLflow params
  -> log MLflow metrics, including training and evaluation duration
  -> log MLflow artifacts, including confusion_matrix.json
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

Manual experiment workflow:

```text
MLflow UI
  -> compare eligible runs
  -> confirm same dataset checksum
  -> rank by F1
  -> inspect precision, recall, accuracy, and confusion matrix
  -> apply tie-breakers
  -> record selected run ID and reason
```

## Remaining V4 Gaps
None. V4 experiment tracking and observability scope is complete.

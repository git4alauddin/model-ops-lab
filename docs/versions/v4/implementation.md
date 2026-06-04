# V4 Implementation

## Scope
V4 adds experiment tracking, training observability, model comparison, and champion selection on top of the V1-V3 pipeline.

Implemented chunks:
- V4-C1: MLflow tracking foundation.
- V4-C2: failed-run tracking and evaluation duration.
- V4-C3: dedicated confusion matrix MLflow artifact.
- V4-C4: MLflow experiment comparison guide.
- V4-C5: best-run selection rule.
- V4-C6: multi-model experiment candidates and champion selection.

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

## V4-C2 Additions
- `app/evaluate.py`
  - added `evaluate_model_with_duration`
  - returns normal evaluation metrics plus elapsed evaluation time
- `app/experiment_tracking.py`
  - added `build_mlflow_metrics`
  - logs `training_duration_seconds`
  - logs `evaluation_duration_seconds`
  - tags failed in-run errors with `run_outcome=failed`, `failure_type`, and `failure_message`
  - preserves the original exception from the training body
- `app/train.py`
  - uses timed evaluation
  - persists `evaluation_duration_seconds` in training metadata
  - writes evaluation duration in the `[EVALUATION]` log section
  - logs evaluation duration to MLflow as a metric

## V4-C3 Additions
- `configs/training.yaml`
  - added `artifacts.confusion_matrix_file`
- `app/utils/artifacts.py`
  - added `confusion_matrix` artifact path construction
- `app/train.py`
  - persists `artifacts/confusion_matrix.json`
  - writes labels and matrix in a self-contained JSON structure
  - includes `confusion_matrix` in the formatted `[ARTIFACTS]` log section
  - logs the dedicated confusion matrix file to MLflow with the other artifacts

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

## V4-C6 Additions
- `configs/training.yaml`
  - added `experiment_candidates`
  - added Logistic Regression, Decision Tree, and Random Forest candidates
  - added `champion_selection.report_path`
- `app/pipeline/trainer.py`
  - added `decision_tree` model support
  - added `random_forest` model support
- `app/champion_selection.py`
  - added pure champion selection logic
  - validates eligible runs
  - enforces same dataset name, version, and checksum
  - ranks by F1 and documented tie-breakers
  - returns champion, eligible runs, and rejected runs
- `app/run_experiments.py`
  - added multi-model experiment runner command
  - validates data once before candidate training
  - trains each candidate as a separate MLflow run
  - uses one shared train/test split for fair comparison
  - builds a fresh preprocessing pipeline per candidate to avoid fitted-state leakage
  - stores candidate artifacts under `artifacts/experiments/<candidate_name>/`
  - tags runs with `candidate_name` and `candidate_model_type`
  - clears previous `champion=true` tags before selecting a new champion
  - tags the selected run with `champion=true`
  - writes `reports/champion_run.json`
- `app/experiment_tracking.py`
  - bumped `pipeline_version` to `v4-c6`
  - added `set_run_tags`
  - added `clear_champion_tags`
- Tests
  - added model factory coverage for Decision Tree and Random Forest
  - added champion selection tests
  - added experiment candidate config tests
  - added MLflow run-tag and champion-tag cleanup tests

## Single-Model Workflow
```text
python -m app.train
  -> run validation gate
  -> start one MLflow run
  -> train configured model
  -> evaluate held-out test set with duration timing
  -> persist local artifacts
  -> persist dedicated confusion_matrix.json
  -> log MLflow params, metrics, and artifacts
  -> persist mlflow_run_id and evaluation duration in training metadata
```

## Multi-Model Champion Workflow
```text
python -m app.run_experiments
  -> run validation gate once
  -> load dataset and create one shared train/test split
  -> build a fresh preprocessor for each candidate
  -> train logistic_regression_baseline as one MLflow run
  -> train decision_tree_baseline as one MLflow run
  -> train random_forest_baseline as one MLflow run
  -> log candidate params, metrics, tags, and artifacts
  -> apply best-run selection rule
  -> clear older champion=true tags
  -> tag selected run champion=true
  -> save reports/champion_run.json
```

## Failure Behavior
If an error happens after an MLflow run starts:

```text
active MLflow run
  -> tag run_outcome=failed
  -> tag failure_type=<exception class>
  -> tag failure_message=<exception message>
  -> re-raise the original exception
```

## Remaining V4 Gaps
None. V4 experiment tracking, observability, multi-model comparison, and champion selection scope is complete.

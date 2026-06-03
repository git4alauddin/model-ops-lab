# V4 Issues Faced

## Open
- Failed-run tracking is not explicit yet.
- Evaluation duration is not logged yet.
- Confusion matrix is not logged as a dedicated MLflow artifact yet.
- Experiment comparison documentation is not added yet.

## Resolved

## V4-C1 MLflow File Store Blocked

### Symptom
The first real training run failed while starting the MLflow run.

### Root Cause
MLflow 3 blocks the local filesystem tracking backend by default unless `MLFLOW_ALLOW_FILE_STORE=true` is set.

### Investigation Process
The training stack trace pointed to `mlflow.set_experiment` and reported that the filesystem backend is in maintenance mode.

### Fix Applied
Changed `experiment_tracking.tracking_uri` from `file:./mlruns` to `sqlite:///mlflow.db`.

### Why The Fix Worked
SQLite is a supported local tracking backend and allows MLflow to create experiments and runs without opting into the deprecated file store.

### Prevention Strategy
Use SQLite for local MLflow tracking by default and keep generated MLflow stores ignored by git.

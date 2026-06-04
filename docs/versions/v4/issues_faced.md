# V4 Issues Faced

## Open
- Experiment comparison documentation is not added yet.
- Best-run selection rule is not added yet.

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

## V4-C2 Missing MLflow Loader

### Symptom
The first V4-C2 runtime training verification failed with `NameError: name '_load_mlflow' is not defined`.

### Root Cause
The tracking helper referenced `_load_mlflow()` when no fake MLflow module was passed, but that loader function was missing from the module.

### Investigation Process
Focused tests passed because they inject `FakeMlflow`. The real `python -m app.train` command exercised the production path and exposed the missing loader.

### Fix Applied
Added `_load_mlflow()` using `importlib.import_module("mlflow")` and wrapped missing dependency failures in `ExperimentTrackingError`.

### Why The Fix Worked
The production path can now load MLflow normally, while tests can still inject a fake module without depending on a live tracking backend.

### Prevention Strategy
For helper modules with dependency injection, test both the injected fake path and at least one real runtime command.

## V4-C3 Confusion Matrix Was Buried In Metrics JSON

### Symptom
The confusion matrix existed only inside `metrics.json`, so it was less obvious in the MLflow UI artifact list.

### Root Cause
The training flow logged `metrics.json` as one combined artifact and did not create a dedicated confusion matrix artifact.

### Investigation Process
Reviewing the MLflow UI artifact model showed that important evaluation outputs should be visible as first-class run artifacts when they are useful to inspect directly.

### Fix Applied
Added `artifacts/confusion_matrix.json` with labels and matrix, then logged it to MLflow with the other run artifacts.

### Why The Fix Worked
The MLflow run artifact list now exposes `confusion_matrix.json` directly, while `metrics.json` remains unchanged for backward compatibility.

### Prevention Strategy
Keep high-value evaluation outputs as dedicated artifacts when they are commonly inspected on their own.

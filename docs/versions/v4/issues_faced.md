# V4 Issues Faced

## Open
- Confusion matrix is not logged as a dedicated MLflow artifact yet.
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

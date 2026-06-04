# V4 Issues Faced

## Open
None. V4 experiment tracking, observability, multi-model comparison, and champion selection scope is complete.

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

## V4-C4 Run Comparison Workflow Was Not Documented

### Symptom
MLflow could track multiple runs, but there was no clear project guide for comparing those runs consistently.

### Root Cause
The tracking foundation existed before a documented comparison workflow.

### Investigation Process
Reviewed the MLflow UI workflow and the project's logged params, metrics, tags, and artifacts.

### Fix Applied
Added `docs/experiments/mlflow_comparison_guide.md` with UI steps, comparison fields, artifact inspection guidance, duration tradeoffs, and a manual checklist.

### Why The Fix Worked
The project now has a repeatable manual process for comparing MLflow runs before adding a formal best-run rule.

### Prevention Strategy
Document manual interpretation before automating model selection rules.

## V4-C5 Best-Run Selection Rule Was Missing

### Symptom
Runs could be compared manually, but there was no documented rule for selecting the best run.

### Root Cause
Comparison guidance existed before a decision policy.

### Investigation Process
Reviewed the current metrics, artifacts, dataset version fields, and churn-classification tradeoffs.

### Fix Applied
Added `docs/experiments/best_run_selection_rule.md` with eligibility requirements, F1-first ranking, tie-breakers, rejection rules, and decision record format.

### Why The Fix Worked
Run selection now follows a consistent documented policy instead of ad hoc metric inspection.

### Prevention Strategy
Define model-selection criteria before adding automated selection or registry promotion.

## V4-C6 Single-Model Tracking Was Not Enough

### Symptom
V4 had MLflow tracking and a selection rule, but only one model family was actually being trained by default.

### Root Cause
The project tracked repeated Logistic Regression runs instead of a real candidate set.

### Investigation Process
Reviewed the V4 output and confirmed that experiment tracking was technically correct but did not yet demonstrate realistic model comparison.

### Fix Applied
Added configurable experiment candidates for Logistic Regression, Decision Tree, and Random Forest. Added `app.run_experiments` to train each candidate as a separate MLflow run and select a champion.

### Why The Fix Worked
The project now produces multiple comparable MLflow runs and a concrete champion report instead of relying only on manual comparison documentation.

### Prevention Strategy
Experiment tracking should include real challenger candidates before moving into orchestration or registry work.

## V4-C6 Old Champion Tags Could Remain Active

### Symptom
After repeated experiment sweeps, older runs could still retain `champion=true`, causing multiple champion runs in MLflow.

### Root Cause
The first champion-tag implementation marked the selected run but did not clear previous champion tags.

### Investigation Process
Queried MLflow run tags after repeated `app.run_experiments` executions and saw an older run still tagged as champion.

### Fix Applied
Added `clear_champion_tags` and called it before tagging the current champion. The runner now tags current batch candidates as `champion=false` before marking the selected run as `champion=true`.

### Why The Fix Worked
The latest MLflow query showed exactly one active `champion=true` run after cleanup.

### Prevention Strategy
Stateful tags that represent a current global status must be cleared before assigning a new owner.

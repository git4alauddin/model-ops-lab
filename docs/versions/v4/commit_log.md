# V4 Commit Log

This file records meaningful V4 commits and the operational purpose of each change.

## Pending - v4-c6: add multi-model champion selection

### What Changed
- Added Decision Tree and Random Forest model support.
- Added configurable experiment candidates in `configs/training.yaml`.
- Added `app.run_experiments` for multi-model candidate sweeps.
- Added `app.champion_selection` for deterministic champion selection.
- Added one shared train/test split with a fresh preprocessing pipeline per candidate.
- Added candidate-specific artifact directories under `artifacts/experiments/<candidate_name>/`.
- Added `reports/champion_run.json` as the champion selection report.
- Added MLflow candidate tags.
- Added MLflow champion tagging.
- Added cleanup for older `champion=true` tags before selecting a new champion.
- Bumped tracked pipeline version to `v4-c6`.
- Added focused tests for model candidates, champion selection, candidate config parsing, run tagging, and champion tag cleanup.
- Updated V4 docs, experiment guides, and README.

### What Problem It Solved
- Makes V4 real experiment management instead of repeated runs of one model family.
- Produces comparable MLflow candidate runs.
- Selects and explains a champion run using the documented selection rule.
- Prevents stale champion tags from making multiple runs look active.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c7_baseline_model_training.py` returned `7 passed in 1.74s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `10 passed in 0.46s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c6_champion_selection.py` returned `4 passed in 0.02s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c6_experiment_candidates.py` returned `4 passed in 1.43s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `160 passed in 2.16s`.
- `.\vir_env\Scripts\python.exe -m app.run_experiments` created three candidate MLflow runs and wrote `reports/champion_run.json`.
- Latest champion run ID was `39b6d1a8b63b46c58709b06d6e711cb2`.
- Latest champion model type was `decision_tree`.
- MLflow query showed exactly `1` active `champion=true` run after champion cleanup.
- `.\vir_env\Scripts\python.exe -m app.train` still completed successfully and created MLflow run `1f1001937f324071b0533ee05d1d58de`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed with `status=passed` and `issues=0`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed with `status=passed`.

## 7fa5001 - v4-c5: add best-run selection rule

### What Changed
- Added `docs/experiments/best_run_selection_rule.md`.
- Defined eligible-run requirements for best-run selection.
- Defined same-data comparison using dataset name, version, and checksum.
- Selected `f1` as the primary ranking metric.
- Added secondary checks using precision, recall, accuracy, and confusion matrix.
- Added tie-breakers for recall, precision, accuracy, runtime, model simplicity, and pipeline version.
- Added rejection rules for incomplete or invalid runs.
- Added manual selection checklist and decision record format.
- Linked the comparison guide to the best-run selection rule.
- Indexed the best-run rule in `docs/experiments/README.md`.
- Marked V4 as complete in README and V4 docs.
- Finalized the V4-C4 commit log hash as `c316826`.

### What Problem It Solved
- Removes ad hoc best-run selection.
- Establishes a consistent manual model-selection policy before automation.
- Closes the final V4 experiment tracking and observability gap.

### Verification
- `Get-Content docs\experiments\best_run_selection_rule.md` confirmed the rule exists.
- `Get-Content docs\experiments\mlflow_comparison_guide.md` confirmed the guide links to the rule.
- `Get-Content docs\experiments\README.md` confirmed both guides are indexed.
- `git diff --check` passed with only normal Windows CRLF warnings.

## c316826 - v4-c4: add MLflow experiment comparison guide

### What Changed
- Added `docs/experiments/mlflow_comparison_guide.md`.
- Documented how to start MLflow UI and open the baseline experiment.
- Documented how to select and compare multiple runs.
- Listed params, metrics, tags, and artifacts to inspect during comparison.
- Added duration-vs-quality interpretation guidance.
- Added a manual comparison checklist.
- Clarified when to use MLflow UI vs SQL.
- Updated `docs/experiments/README.md` with a guide pointer.
- Updated V4 overview, implementation, verification, issues, and lessons docs.
- Updated README with the comparison-guide pointer.

### What Problem It Solved
- Gives a repeatable manual process for comparing MLflow runs.
- Connects metrics, params, artifacts, and dataset checksums into one comparison workflow.
- Prepares the project for a future best-run selection rule.

### Verification
- `Get-Content docs\experiments\mlflow_comparison_guide.md` confirmed the guide exists.
- `Get-Content docs\experiments\README.md` confirmed the guide is indexed.
- `git diff --check` passed with only normal Windows CRLF warnings.

## fc66039 - v4-c3: log confusion matrix as MLflow artifact

### What Changed
- Added `artifacts.confusion_matrix_file` to training config.
- Added `confusion_matrix` artifact path construction.
- Bumped tracked pipeline version to `v4-c3`.
- Persisted `artifacts/confusion_matrix.json` during training.
- Stored confusion matrix labels and matrix in a self-contained JSON artifact.
- Logged the dedicated confusion matrix file to MLflow with the other run artifacts.
- Included the confusion matrix artifact in the formatted training artifact log section.
- Added focused tests for confusion matrix artifact path construction and MLflow artifact logging.
- Updated V4 implementation, verification, issues, and lessons docs.
- Updated README runtime outputs.

### What Problem It Solved
- Makes confusion matrix inspection easier from the MLflow UI artifact list.
- Keeps `metrics.json` unchanged while promoting a high-value evaluation output to a first-class artifact.
- Improves run explainability without changing model behavior.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c10_artifact_persistence.py` returned `4 passed in 1.34s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `8 passed in 0.05s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `148 passed in 2.05s`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and created MLflow run `4d269974b64147cda439311170bf8d35`.
- Generated `artifacts/confusion_matrix.json` contains `labels=[0, 1]` and `matrix=[[3, 0], [0, 1]]`.
- Latest MLflow run query showed `status=FINISHED`, `metrics.accuracy=1.0`, `metrics.f1=1.0`, and `params.pipeline_version=v4-c3`.
- Latest MLflow artifact listing showed `config_snapshot.json`, `confusion_matrix.json`, `metrics.json`, `model.pkl`, and `training_metadata.json`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed with `status=passed` and `issues=0`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed with `status=passed`.

## 70d38c4 - v4-c2: add failed-run tracking and evaluation duration

### What Changed
- Added timed evaluation helper.
- Persisted `evaluation_duration_seconds` in training metadata.
- Logged evaluation duration in the formatted training logs.
- Logged training and evaluation durations to MLflow metrics.
- Added failed-run tags for errors raised inside an active MLflow run.
- Preserved the original training-body exception when run tracking records a failure.
- Restored real MLflow module loading for production runtime commands.
- Added focused tests for timed evaluation, duration metric building, and failed-run tagging.
- Updated V4 implementation, verification, lessons, and issues docs.
- Updated README V4 status.

### What Problem It Solved
- Makes run timing visible in MLflow for experiment comparison.
- Makes failed training runs easier to inspect from MLflow tags.
- Keeps local training metadata aligned with tracked experiment metrics.
- Ensures the real training command exercises the production MLflow loader path.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v4_c1_mlflow_tracking_foundation.py` returned `8 passed in 0.04s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v1_c9_evaluation_metrics.py` returned `6 passed in 1.37s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `148 passed in 2.01s`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and created MLflow run `172efc2f2a704d469d65f98451d5c8ec`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed with `status=passed` and `issues=0`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed with `status=passed`.
- Generated `artifacts/training_metadata.json` includes `mlflow_run_id` and `evaluation_duration_seconds`.
- Latest MLflow run query showed `status=FINISHED`, `metrics.accuracy=1.0`, `metrics.f1=1.0`, `metrics.training_duration_seconds=0.009198`, `metrics.evaluation_duration_seconds=0.009016`, and `params.pipeline_version=v4-c2`.

## e519049 - v4-c1: add MLflow tracking foundation

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

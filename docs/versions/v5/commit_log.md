# V5 Commit Log

This file records meaningful V5 commits and the operational purpose of each change.

## Pending - v5-c4: remove duplicate pipeline validation

### What Changed
- Extracted reusable `run_experiment_workflow()` from `app.run_experiments`.
- Kept standalone `python -m app.run_experiments` validation enabled by default.
- Added explicit `validate_before_run` control for experiment workflow reuse.
- Updated `app.run_training_pipeline` to call experiments with `validate_before_run=False`.
- Updated pipeline execution to use the returned champion report.
- Updated V5 pipeline tests to use temporary log paths for expected failure scenarios.
- Bumped pipeline metadata version to `v5-c4`.
- Added focused validation ownership tests.
- Updated V5-C3 pipeline entrypoint tests for returned champion report behavior.
- Updated README and V5 docs.
- Finalized the V5-C3 commit hash as `32e7653`.

### What Problem It Solved
- Removes duplicate validation from `python -m app.run_training_pipeline`.
- Keeps the standalone experiment command safe when it is run directly.
- Gives the future Prefect layer a cleaner reusable experiment function.
- Keeps expected test failure traces out of `logs/modelopslab.log`.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c2_pipeline_run_metadata.py tests\test_v5_c3_training_pipeline_entrypoint.py tests\test_v5_c4_pipeline_validation_ownership.py` returned `17 passed in 1.71s`.
- `.\vir_env\Scripts\python.exe -m app.run_experiments` completed successfully and logged a standalone `[VALIDATION]` section.
- `.\vir_env\Scripts\python.exe -m app.run_training_pipeline` completed successfully and created pipeline run `pipeline_20260604T181245710980Z_3db9b1f0`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `177 passed in 2.46s`.
- `Select-String -Path logs\modelopslab.log -Pattern "ERROR|Traceback|pipeline_test_"` returned no matches after the clean pipeline run.

## 32e7653 - v5-c3: add training pipeline entrypoint

### What Changed
- Added `app/run_training_pipeline.py`.
- Added `python -m app.run_training_pipeline`.
- Added validation stage status tracking.
- Added experiment stage status tracking.
- Added champion report loading and validation.
- Added MLflow run ID extraction from eligible champion report runs.
- Added champion run ID persistence in pipeline metadata.
- Added failed-stage metadata persistence for validation and experiment failures.
- Bumped pipeline metadata version to `v5-c3`.
- Added focused V5-C3 pipeline entrypoint tests.
- Updated README and V5 docs.
- Finalized the V5-C2 commit hash as `45b10b2`.

### What Problem It Solved
- Turns the V5 metadata contract into a real executable pipeline command.
- Creates pipeline-level metadata for successful and failed workflow runs.
- Proves the orchestration flow before introducing Prefect.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c2_pipeline_run_metadata.py tests\test_v5_c3_training_pipeline_entrypoint.py` returned `13 passed in 1.53s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `173 passed in 2.34s`.
- `.\vir_env\Scripts\python.exe -m app.run_training_pipeline` completed successfully and created pipeline run `pipeline_20260604T174409840205Z_e66818f3`.
- `git diff --check` passed with only normal Windows CRLF warnings.

## 45b10b2 - v5-c2: add pipeline run metadata

### What Changed
- Added `app/pipeline_run_metadata.py`.
- Added filesystem-safe pipeline run ID generation.
- Added canonical pipeline run metadata creation.
- Added stage status update helper.
- Added pass/fail completion helper.
- Added safe metadata path building.
- Added JSON persistence to `pipeline_runs/<pipeline_run_id>.json`.
- Added focused V5-C2 tests.
- Updated V5 docs and README.
- Finalized the V5-C1 commit hash as `3c8beb8`.

### What Problem It Solved
- Defines the pipeline run metadata contract before orchestration code is added.
- Separates pipeline-level run status from model metrics, training metadata, and MLflow run metadata.
- Gives future Prefect tasks one stable output shape to update.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c2_pipeline_run_metadata.py` returned `8 passed in 0.18s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `168 passed in 2.38s`.
- `git diff --check` passed with only normal Windows CRLF warnings.

## 3c8beb8 - v5-c1: add orchestration foundation

### What Changed
- Added V5 documentation scaffold.
- Added `pipeline_runs/.gitkeep` for future pipeline metadata outputs.
- Added `.gitignore` rules for future pipeline run metadata outputs.
- Added Prefect vs Airflow decision record.
- Added V5 status to README.
- Finalized the V4 diagram commit hash as `bd57557`.

### What Problem It Solved
- Establishes the orchestration boundary before runtime code is added.
- Creates the documentation structure required for V5.
- Defines where pipeline run metadata will live.
- Keeps generated pipeline run metadata out of git.
- Records the orchestration tool decision before dependency changes.

### Verification
- `Get-ChildItem docs\versions\v5` confirmed V5 docs exist.
- `Get-ChildItem pipeline_runs` confirmed `.gitkeep` exists.
- `Get-Content docs\decisions\adr_prefect_for_v5_orchestration.md` confirmed the ADR exists.
- `git diff --check` passed with only normal Windows CRLF warnings.

# V5 Commit Log

This file records meaningful V5 commits and the operational purpose of each change.

## Pending - v5-c9: extract pipeline stage helpers

### What Changed
- Added `app/tasks/validation_task.py`.
- Added `app/tasks/experiment_task.py`.
- Added `app/tasks/__init__.py`.
- Delegated validation execution from `run_training_pipeline()` to `run_validation_stage()`.
- Delegated experiment execution from `run_training_pipeline()` to `run_experiment_stage()`.
- Kept pipeline metadata and stage status ownership inside `run_training_pipeline()`.
- Bumped pipeline metadata version to `v5-c9`.
- Added focused stage helper tests.
- Updated README, V5 diagram, and V5 docs.
- Finalized the V5-C8 commit hash as `61eeb5a`.

### What Problem It Solved
- Creates clearer pipeline stage boundaries.
- Prepares future Prefect task decomposition without changing runtime behavior.
- Keeps the existing plain Python and Prefect pipeline commands stable.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c3_training_pipeline_entrypoint.py tests\test_v5_c4_pipeline_validation_ownership.py tests\test_v5_c6_prefect_orchestration.py tests\test_v5_c7_prefect_retry_policy.py tests\test_v5_c8_prefect_failure_visibility.py tests\test_v5_c9_pipeline_stage_tasks.py` returned `23 passed in 3.52s`.
- `.\vir_env\Scripts\python.exe -m app.run_prefect_pipeline` completed successfully and created pipeline run `pipeline_20260604T192411531526Z_764769dc`.
- Generated V5-C9 pipeline metadata had `pipeline_version=v5-c9`, `status=passed`, `stage_statuses.validation=passed`, `stage_statuses.experiments=passed`, `mlflow_run_ids=3`, and `champion_run_id=bb579b6839af402980d57e91580346b3`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `191 passed in 4.39s`.
- `Select-String -Path logs\modelopslab.log -Pattern "ERROR|Traceback|pipeline_test_"` returned no matches after the V5-C9 verification run.
- `git diff --check` passed with only normal Windows CRLF warnings.

## 61eeb5a - v5-c8: expose Prefect failure context

### What Changed
- Attached failed pipeline metadata to `TrainingPipelineError`.
- Exposed `pipeline_run_id` and `failed_stage` on pipeline failures.
- Preserved nested pipeline failure metadata inside `PrefectPipelineError`.
- Added failed run context to the Prefect command error/log boundary.
- Bumped pipeline metadata version to `v5-c8`.
- Added focused failure visibility tests.
- Kept expected pipeline success and failure logs silent in focused tests.
- Updated README, V5 diagram, and V5 docs.
- Finalized the V5-C7 commit hash as `dfea121`.

### What Problem It Solved
- Makes failed Prefect-wrapped pipeline runs easier to inspect.
- Points users to the exact failed pipeline run metadata file.
- Keeps pipeline metadata as the source of truth while improving command-level visibility.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c3_training_pipeline_entrypoint.py tests\test_v5_c4_pipeline_validation_ownership.py tests\test_v5_c6_prefect_orchestration.py tests\test_v5_c7_prefect_retry_policy.py tests\test_v5_c8_prefect_failure_visibility.py` returned `17 passed in 3.53s`.
- `.\vir_env\Scripts\python.exe -m app.run_prefect_pipeline` completed successfully and created pipeline run `pipeline_20260604T190942672811Z_7c46b02f`.
- Generated V5-C8 pipeline metadata had `pipeline_version=v5-c8`, `status=passed`, `stage_statuses.validation=passed`, `stage_statuses.experiments=passed`, `mlflow_run_ids=3`, and `champion_run_id=e8d6814b81624d208fc53c8621710f6e`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `185 passed in 4.61s`.
- `Select-String -Path logs\modelopslab.log -Pattern "ERROR|Traceback|pipeline_test_"` returned no matches after the V5-C8 verification run.
- `git diff --check` passed with only normal Windows CRLF warnings.

## dfea121 - v5-c7: add Prefect retry policy

### What Changed
- Added `PIPELINE_TASK_RETRIES = 2`.
- Added `PIPELINE_TASK_RETRY_DELAY_SECONDS = 5`.
- Configured `run_training_pipeline_task` with Prefect retries.
- Bumped pipeline metadata version to `v5-c7`.
- Added focused retry policy tests.
- Updated README, V5 diagram, and V5 docs.
- Finalized the V5-C6 commit hash as `6d9997f`.

### What Problem It Solved
- Adds controlled retry behavior to the local Prefect task.
- Keeps retry policy explicit and conservative.
- Preserves the existing plain Python pipeline behavior.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c6_prefect_orchestration.py tests\test_v5_c7_prefect_retry_policy.py` returned `6 passed in 3.67s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c2_pipeline_run_metadata.py tests\test_v5_c3_training_pipeline_entrypoint.py tests\test_v5_c4_pipeline_validation_ownership.py tests\test_v5_c6_prefect_orchestration.py tests\test_v5_c7_prefect_retry_policy.py` returned `23 passed in 4.00s`.
- `.\vir_env\Scripts\python.exe -m app.run_prefect_pipeline` completed successfully and created pipeline run `pipeline_20260604T190037406517Z_bb1af1de`.
- Generated V5-C7 pipeline metadata had `pipeline_version=v5-c7`, `status=passed`, `stage_statuses.validation=passed`, `stage_statuses.experiments=passed`, `mlflow_run_ids=3`, and `champion_run_id=64a4bbb3123f4a309a2f528f19b418dc`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `183 passed in 5.45s`.
- `Select-String -Path logs\modelopslab.log -Pattern "ERROR|Traceback|pipeline_test_"` returned no matches after the V5-C7 verification run.

## 6d9997f - v5-c6: add Prefect orchestration wrapper

### What Changed
- Added `prefect>=3.0.0` to `requirements.txt`.
- Added `app/orchestration/prefect_pipeline.py`.
- Added local Prefect flow `modelopslab-training-pipeline`.
- Added local Prefect task `run-training-pipeline`.
- Added `python -m app.run_prefect_pipeline`.
- Bumped pipeline metadata version to `v5-c6`.
- Updated V5 training pipeline diagram to include the local Prefect wrapper.
- Added focused Prefect orchestration tests.
- Updated README and V5 docs.
- Finalized the V5-C5 commit hash as `1f12a25`.

### What Problem It Solved
- Moves Prefect from an ADR decision into an executable local orchestration wrapper.
- Preserves the proven plain Python pipeline command.
- Avoids introducing scheduling or deployment complexity before the local flow is stable.

### Verification
- `.\vir_env\Scripts\python.exe -c "import prefect; print(prefect.__version__)"` returned `3.7.3`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c2_pipeline_run_metadata.py tests\test_v5_c3_training_pipeline_entrypoint.py tests\test_v5_c4_pipeline_validation_ownership.py tests\test_v5_c6_prefect_orchestration.py` returned `21 passed in 3.88s`.
- `.\vir_env\Scripts\python.exe -m app.run_prefect_pipeline` completed successfully and created pipeline run `pipeline_20260604T183142304402Z_84df64f1`.
- Generated V5-C6 pipeline metadata had `pipeline_version=v5-c6`, `status=passed`, `stage_statuses.validation=passed`, `stage_statuses.experiments=passed`, `mlflow_run_ids=3`, and `champion_run_id=9e2615eea1f9449db118b4e5dc4efbe0`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `181 passed in 4.95s`.
- `git diff --check` passed with only normal Windows CRLF warnings.

## 1f12a25 - v5-c5: add training pipeline flow diagram

### What Changed
- Added `docs/diagrams/v5_training_pipeline_flow.md`.
- Documented the plain Python training pipeline command.
- Documented validation ownership.
- Documented `run_experiment_workflow(..., validate_before_run=false)`.
- Documented MLflow candidate runs and champion selection.
- Documented passed and failed pipeline metadata outputs.
- Linked the V5 diagram from README.
- Updated V5 docs.
- Finalized the V5-C4 commit hash as `b166db6`.

### What Problem It Solved
- Makes the current V5 orchestration behavior easier to explain visually.
- Clarifies the difference between pipeline metadata, MLflow metadata, and champion reports.
- Creates a clean reference point before Prefect is introduced.

### Verification
- `Get-Content docs\diagrams\v5_training_pipeline_flow.md` confirmed the diagram exists.
- `Select-String -Path README.md -Pattern "v5_training_pipeline_flow"` confirmed README links the diagram.
- `git diff --check` passed with only normal Windows CRLF warnings.

## b166db6 - v5-c4: remove duplicate pipeline validation

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

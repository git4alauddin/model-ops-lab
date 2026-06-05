# V5 Implementation

## Scope
V5 adds training pipeline automation and workflow orchestration.

The first chunk is intentionally small: define the orchestration direction, document the boundary, and create the pipeline run output location before introducing orchestration code.

Implemented chunks:
- V5-C1: orchestration foundation and documentation scaffold.
- V5-C2: pipeline run metadata contract and persistence helper.
- V5-C3: plain Python training pipeline entrypoint.
- V5-C4: single validation ownership for the training pipeline.
- V5-C5: training pipeline flow diagram.
- V5-C6: local Prefect orchestration wrapper.
- V5-C7: Prefect task retry policy.
- V5-C8: Prefect failure context visibility.
- V5-C9: pipeline stage task helpers.
- V5-C10: Prefect local deployment scaffold.
- V5-C11: stage-level Prefect tasks.

## V5-C1 Additions
- `docs/versions/v5/`
  - added V5 overview, implementation, verification, issues, lessons, and commit log files
- `docs/decisions/adr_prefect_for_v5_orchestration.md`
  - records the decision to use Prefect over Airflow for the initial orchestration layer
- `pipeline_runs/.gitkeep`
  - creates the future pipeline metadata output folder
- `.gitignore`
  - ignores future pipeline run metadata while keeping `pipeline_runs/.gitkeep`
- `README.md`
  - adds V5 status
  - adds `pipeline_runs/` to the structure
  - documents that V5 orchestration is starting
- `docs/versions/v4/commit_log.md`
  - finalizes the V4 diagram commit hash

## V5-C2 Additions
- `app/pipeline_run_metadata.py`
  - builds filesystem-safe pipeline run IDs
  - builds the canonical pipeline run metadata payload
  - validates pipeline-level statuses
  - validates stage-level statuses
  - updates stage status without mutating the original metadata
  - marks pipeline runs as passed or failed
  - persists metadata to `pipeline_runs/<pipeline_run_id>.json`
- `tests/test_v5_c2_pipeline_run_metadata.py`
  - covers run ID format
  - covers metadata field contract
  - covers stage status updates
  - covers success completion metadata
  - covers failed-run validation
  - covers safe output path validation
  - covers JSON persistence
- `README.md`
  - records the metadata helper in V5 status and project structure
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C1 commit hash as `3c8beb8`

## V5-C3 Additions
- `app/run_training_pipeline.py`
  - adds `python -m app.run_training_pipeline`
  - initializes pipeline run metadata
  - persists running metadata at command start
  - marks validation as running, passed, or failed
  - runs the validation gate before experiments
  - marks experiments as running, passed, or failed
  - calls the existing `app.run_experiments.main()` workflow
  - reads `reports/champion_run.json`
  - copies eligible MLflow run IDs into pipeline metadata
  - copies champion run ID into pipeline metadata
  - persists final passed or failed pipeline metadata
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c3`
- `tests/test_v5_c3_training_pipeline_entrypoint.py`
  - covers successful pipeline metadata lifecycle
  - covers validation failure metadata
  - covers experiment failure metadata
  - covers experiment `SystemExit` failure metadata
  - covers champion and MLflow run ID extraction
- `README.md`
  - documents the V5 pipeline command
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C2 commit hash as `45b10b2`

## V5-C4 Additions
- `app/run_experiments.py`
  - extracts `run_experiment_workflow()`
  - keeps `python -m app.run_experiments` behavior unchanged
  - validates by default for standalone experiment runs
  - allows validation to be skipped for pipeline-owned execution
  - returns the champion report to callers
- `app/run_training_pipeline.py`
  - calls `run_experiment_workflow(..., validate_before_run=False)`
  - keeps validation ownership in the pipeline command
  - uses the returned champion report instead of re-reading the report file
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c4`
- `tests/test_v5_c4_pipeline_validation_ownership.py`
  - proves standalone experiments validate
  - proves experiment workflow can skip validation for pipeline ownership
  - proves the training pipeline validates once
- `tests/test_v5_c3_training_pipeline_entrypoint.py`
  - updates pipeline entrypoint tests for returned champion report behavior
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C3 commit hash as `32e7653`

## V5-C5 Additions
- `docs/diagrams/v5_training_pipeline_flow.md`
  - documents the plain Python pipeline command
  - shows validation ownership
  - shows `run_experiment_workflow(..., validate_before_run=false)`
  - shows MLflow candidate runs
  - shows champion selection output
  - shows passed and failed pipeline metadata output
- `README.md`
  - links the V5 training pipeline flow diagram
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C4 commit hash as `b166db6`

## V5-C6 Additions
- `requirements.txt`
  - adds `prefect>=3.0.0`
- `app/orchestration/prefect_pipeline.py`
  - adds `training_pipeline_flow`
  - adds `run_training_pipeline_task`
  - wraps the existing plain Python pipeline in local Prefect orchestration
- `app/run_prefect_pipeline.py`
  - adds `python -m app.run_prefect_pipeline`
  - runs the local Prefect flow
  - preserves `python -m app.run_training_pipeline`
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c6`
- `tests/test_v5_c6_prefect_orchestration.py`
  - covers task delegation to the plain pipeline
  - covers flow delegation to the task
  - covers command wrapper success and failure behavior
- `docs/diagrams/v5_training_pipeline_flow.md`
  - updates the diagram to show the local Prefect wrapper
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C5 commit hash as `1f12a25`

## V5-C7 Additions
- `app/orchestration/prefect_pipeline.py`
  - adds `PIPELINE_TASK_RETRIES = 2`
  - adds `PIPELINE_TASK_RETRY_DELAY_SECONDS = 5`
  - configures retry behavior on `run_training_pipeline_task`
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c7`
- `tests/test_v5_c7_prefect_retry_policy.py`
  - proves the Prefect task exposes the retry policy
  - proves the task still delegates to `run_training_pipeline`
- `README.md`
  - documents the Prefect retry policy at a high level
- `docs/diagrams/v5_training_pipeline_flow.md`
  - shows the retry-enabled Prefect task
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C6 commit hash as `6d9997f`

## V5-C8 Additions
- `app/run_training_pipeline.py`
  - attaches failed pipeline metadata to `TrainingPipelineError`
  - exposes `pipeline_run_id` and `failed_stage` on failed pipeline exceptions
- `app/run_prefect_pipeline.py`
  - preserves nested pipeline failure metadata when wrapping flow failures
  - includes failed `pipeline_run_id` and `failed_stage` in Prefect command errors when available
  - logs failed pipeline run context at the command boundary
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c8`
- `tests/test_v5_c8_prefect_failure_visibility.py`
  - proves failed pipeline exceptions expose metadata context
  - proves Prefect command errors preserve nested pipeline failure metadata
- `tests/test_v5_c3_training_pipeline_entrypoint.py`
  - keeps expected pipeline success and failure logs silent during focused tests
- `tests/test_v5_c4_pipeline_validation_ownership.py`
  - keeps expected pipeline success logs silent during focused tests
- `README.md`
  - documents Prefect failure context visibility
- `docs/diagrams/v5_training_pipeline_flow.md`
  - shows command-level failure context from failed pipeline metadata
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C7 commit hash as `dfea121`

## V5-C9 Additions
- `app/tasks/validation_task.py`
  - adds `run_validation_stage()`
  - runs the configured validation runner
  - enforces the training validation gate
- `app/tasks/experiment_task.py`
  - adds `run_experiment_stage()`
  - runs the experiment workflow with `validate_before_run=False`
  - validates champion report shape
  - keeps champion and MLflow run ID extraction helpers
- `app/run_training_pipeline.py`
  - delegates validation execution to `run_validation_stage()`
  - delegates experiment execution to `run_experiment_stage()`
  - keeps orchestration, stage status updates, and metadata persistence in the pipeline command
  - keeps existing helper imports compatible for callers
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c9`
- `tests/test_v5_c9_pipeline_stage_tasks.py`
  - proves validation stage helper behavior
  - proves experiment stage helper behavior
  - proves the training pipeline delegates to the extracted helpers
- `README.md`
  - documents the new `app/tasks/` structure
- `docs/diagrams/v5_training_pipeline_flow.md`
  - shows validation and experiment stage helpers in the current V5 flow
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C8 commit hash as `61eeb5a`

## V5-C10 Additions
- `prefect.yaml`
  - defines `local-training-pipeline`
  - points to `app/orchestration/prefect_pipeline.py:training_pipeline_flow`
  - uses local process work pool `modelopslab-local-process-pool`
  - includes an inactive daily schedule in `Asia/Kolkata`
- `tests/test_v5_c10_prefect_deployment_scaffold.py`
  - proves the deployment entrypoint, parameters, work pool, and inactive schedule are defined
- `docs/deployment/prefect_local_deployment.md`
  - explains deployment concepts
  - documents CLI setup
  - documents GUI learning flow
  - records guardrails for local use
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c10`
- `README.md`
  - links the deployment scaffold guide
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C9 commit hash as `6f82997`

## V5-C11 Additions
- `app/orchestration/prefect_pipeline.py`
  - replaces the one-big Prefect task with stage-level Prefect tasks
  - adds `initialize_pipeline_run_task`
  - adds `validation_stage_task`
  - adds `experiment_stage_task`
  - adds `finalize_pipeline_run_task`
  - preserves failed metadata on stage-level Prefect errors
  - keeps retries on validation only
  - disables experiment retries to avoid duplicate MLflow candidate runs
- `app/pipeline_run_metadata.py`
  - bumps pipeline metadata version to `v5-c11`
- `app/run_training_pipeline.py`
  - remains the plain Python fallback path
- `prefect.yaml`
  - bumps deployment version to `v5-c11`
- `tests/test_v5_c6_prefect_orchestration.py`
  - verifies the flow delegates through stage-level Prefect tasks
- `tests/test_v5_c7_prefect_retry_policy.py`
  - verifies validation retries and experiment no-retry behavior
- `tests/test_v5_c11_prefect_stage_tasks.py`
  - verifies initialization, validation, experiment, finalization, and failed metadata behavior
- `README.md`
  - documents stage-level Prefect task behavior
- `docs/diagrams/v5_training_pipeline_flow.md`
  - shows stage-level Prefect tasks
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C10 commit hash as `937e33e`

## Orchestration Boundary
V5 should not rewrite the working V1-V4 behavior in one step.

Current stable commands remain:

```powershell
python -m app.train
python -m app.run_experiments
python -m app.run_training_pipeline
python -m app.run_prefect_pipeline
```

V5 orchestration will wrap or extract stage behavior carefully instead of duplicating everything blindly.

## Planned V5 Runtime Direction
Future V5 chunks should introduce:

```text
safe schedule activation after local worker behavior is understood
```

Expected pipeline flow:

```text
training pipeline
  -> Prefect flow
  -> initialize pipeline run task
  -> validation stage task
  -> experiment stage task
  -> finalize pipeline run task
```

## Pipeline Metadata Output
Pipeline run metadata is persisted under:

```text
pipeline_runs/
```

Runtime metadata files in this folder remain local run outputs. The repository tracks only `.gitkeep`.

Expected metadata fields:

```text
pipeline_run_id
pipeline_version
started_at
completed_at
status
stage_statuses
failed_stage
dataset_version
config_path
mlflow_run_ids
champion_run_id
```

## Design Guardrail
The first orchestration implementation should preserve these facts:

```text
app.train = one configured model
app.run_experiments = configured candidate sweep + champion selection
app.run_training_pipeline = controlled workflow wrapper around proven behavior
app.run_prefect_pipeline = local Prefect wrapper around app.run_training_pipeline
```

## Remaining V5 Gaps
- Prefect deployment schedule exists but remains inactive by default.

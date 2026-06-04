# V5 Implementation

## Scope
V5 adds training pipeline automation and workflow orchestration.

The first chunk is intentionally small: define the orchestration direction, document the boundary, and create the pipeline run output location before introducing orchestration code.

Implemented chunks:
- V5-C1: orchestration foundation and documentation scaffold.
- V5-C2: pipeline run metadata contract and persistence helper.
- V5-C3: plain Python training pipeline entrypoint.
- V5-C4: single validation ownership for the training pipeline.

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

## Orchestration Boundary
V5 should not rewrite the working V1-V4 behavior in one step.

Current stable commands remain:

```powershell
python -m app.train
python -m app.run_experiments
python -m app.run_training_pipeline
```

V5 orchestration will wrap or extract stage behavior carefully instead of duplicating everything blindly.

## Planned V5 Runtime Direction
Future V5 chunks should introduce:

```text
app/tasks/validation_task.py
app/tasks/training_task.py
app/tasks/experiment_task.py
app/orchestration/prefect_config.py
```

Expected pipeline flow:

```text
training pipeline
  -> validation task
  -> experiment task
  -> champion report read
  -> metadata persistence task
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
```

## Remaining V5 Gaps
- Prefect dependency is not added yet.
- Stage task modules are not added yet.
- Retry behavior is not implemented yet.
- Pipeline diagram is not added yet.

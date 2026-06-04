# V5 Implementation

## Scope
V5 adds training pipeline automation and workflow orchestration.

The first chunk is intentionally small: define the orchestration direction, document the boundary, and create the pipeline run output location before introducing orchestration code.

Implemented chunks:
- V5-C1: orchestration foundation and documentation scaffold.
- V5-C2: pipeline run metadata contract and persistence helper.

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

## Orchestration Boundary
V5 should not rewrite the working V1-V4 behavior in one step.

Current stable commands remain:

```powershell
python -m app.train
python -m app.run_experiments
```

V5 orchestration will wrap or extract stage behavior carefully instead of duplicating everything blindly.

## Planned V5 Runtime Direction
Future V5 chunks should introduce:

```text
app/pipelines/training_pipeline.py
app/tasks/validation_task.py
app/tasks/training_task.py
app/tasks/experiment_task.py
app/orchestration/prefect_config.py
```

Expected pipeline flow:

```text
training pipeline
  -> validation task
  -> training or experiment task
  -> artifact verification task
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
V5 pipeline = controlled workflow wrapper around proven behavior
```

## Remaining V5 Gaps
- Prefect dependency is not added yet.
- Runtime pipeline command is not added yet.
- Stage task modules are not added yet.
- Pipeline metadata persistence is implemented as a helper but is not wired into an orchestration command yet.
- Retry behavior is not implemented yet.
- Pipeline diagram is not added yet.

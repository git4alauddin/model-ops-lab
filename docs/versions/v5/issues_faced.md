# V5 Issues Faced

## Open
- Prefect scheduling and deployment configuration are not added yet.

## Resolved

## V5-C1 Orchestration Boundary Needed Before Code

### Symptom
V5 introduces a new orchestration layer, but the project already has stable commands for training and experiment sweeps.

### Root Cause
Adding orchestration code immediately could duplicate or destabilize working V1-V4 behavior.

### Investigation Process
Reviewed the V5 plan and current commands: `app.train` and `app.run_experiments`.

### Fix Applied
Started V5 with documentation, an ADR, and `pipeline_runs/` output structure before adding runtime orchestration code.

### Why The Fix Worked
The project now has a clear boundary: orchestration should wrap or extract proven behavior carefully instead of rewriting it blindly.

### Prevention Strategy
For new operational layers, document architecture boundaries before implementation.

## V5-C2 Metadata Contract Needed Before Orchestration

### Symptom
Prefect orchestration will need to record pipeline status, stage status, MLflow run IDs, and champion output, but those fields did not have a code-level contract yet.

### Root Cause
V1-V4 metadata focused on model training, validation, dataset versions, and MLflow runs. Pipeline-level execution metadata is a separate concern.

### Investigation Process
Reviewed existing artifact persistence, training metadata, experiment candidate outputs, and V5 planning docs.

### Fix Applied
Added `app/pipeline_run_metadata.py` with run ID generation, metadata building, stage updates, completion marking, safe path creation, and JSON persistence.

### Why The Fix Worked
The orchestration layer can now target one stable metadata shape instead of inventing fields inside each future pipeline task.

### Prevention Strategy
Define the metadata contract before connecting orchestration tools or runtime stage execution.

## V5-C3 Plain Pipeline Needed Before Prefect

### Symptom
The project had pipeline metadata helpers, but no runtime command created a real pipeline run record.

### Root Cause
V5-C2 intentionally stopped at the metadata contract. The next operational gap was proving the stage lifecycle without adding Prefect yet.

### Investigation Process
Reviewed the existing validation command, experiment sweep command, champion report format, and pipeline metadata helper.

### Fix Applied
Added `app/run_training_pipeline.py` as a plain Python wrapper that runs validation, runs the existing experiment sweep, reads the champion report, and persists final pipeline metadata.

### Why The Fix Worked
The project now has an executable orchestration path without introducing orchestration-tool complexity.

### Prevention Strategy
Keep orchestration behavior testable in plain Python before wrapping it with Prefect flows and tasks.

## V5-C3 Duplicate Validation Is Accepted Temporarily

### Symptom
`python -m app.run_training_pipeline` validates the dataset, then `app.run_experiments.main()` validates it again internally.

### Root Cause
The V5-C3 command wraps stable V4 behavior instead of refactoring experiment internals during the same chunk.

### Fix Applied
Kept the duplicate validation temporarily in V5-C3 to avoid destabilizing the proven experiment command.

### Prevention Strategy
Future V5 task extraction should split experiment execution from validation so the pipeline controls validation exactly once.

### V5-C4 Resolution
Extracted `run_experiment_workflow()` with `validate_before_run=True` by default. The standalone experiment command still validates, while `app.run_training_pipeline` calls the workflow with `validate_before_run=False`.

## V5-C4 Expected Failure Tests Polluted Runtime Log

### Symptom
Focused failure-path tests passed, but `logs/modelopslab.log` contained expected test exceptions from validation and experiment failure scenarios.

### Root Cause
The tests loaded the real `configs/training.yaml`, so the app logger attached to the real project log file.

### Fix Applied
Updated V5 pipeline tests to use temporary config files with temporary log directories.

### Why The Fix Worked
Expected failure traces remain inside pytest temporary paths instead of the project runtime log.

### Prevention Strategy
Failure-path tests should use temporary runtime output locations unless the test is explicitly verifying production log output.

## V5-C6 Prefect Wrapper Should Not Replace Pipeline Logic

### Symptom
Prefect needed to be introduced without moving validation, experiment execution, champion selection, and metadata persistence into a new untested structure.

### Root Cause
The plain Python pipeline was already proven. Rebuilding the same behavior directly inside Prefect would create duplicate orchestration logic.

### Fix Applied
Added a local Prefect flow and task that delegate to `run_training_pipeline`.

### Why The Fix Worked
Prefect now orchestrates the existing pipeline while the core behavior remains testable and runnable without Prefect.

### Prevention Strategy
Keep orchestration tools as wrappers around stable application behavior until there is a clear need to split individual tasks.

## V5-C7 Retry Policy Needed Guardrails

### Symptom
Prefect was available as a local wrapper, but task retries were not configured.

### Root Cause
V5-C6 introduced orchestration first and intentionally avoided retry behavior during the initial Prefect integration.

### Fix Applied
Added a conservative retry policy to the Prefect pipeline task: two retries with a five-second delay.

### Why The Fix Worked
Transient task failures can be retried by Prefect while the underlying pipeline code remains unchanged.

### Prevention Strategy
Keep retry policy small and explicit until the pipeline has more granular task modules and stronger failure classification.

## V5-C8 Failed Prefect Runs Needed Metadata Context

### Symptom
The plain pipeline persisted failed run metadata, but the Prefect command wrapped failures with a generic command-level exception.

### Root Cause
`run_prefect_pipeline()` did not preserve the `pipeline_run_id` or `failed_stage` from the underlying pipeline failure.

### Fix Applied
Attached failed metadata to `TrainingPipelineError`, then made `PrefectPipelineError` extract and expose that metadata from the exception chain.

### Why The Fix Worked
The pipeline metadata file remains the source of truth, while the command-level error now points directly to the failed run and failed stage.

### Prevention Strategy
When wrapping lower-level workflow errors, preserve structured failure context instead of replacing it with only a generic message.

## V5-C9 Stage Boundaries Needed Without Behavior Change

### Symptom
The training pipeline worked, but validation and experiment execution were still embedded directly inside `run_training_pipeline()`.

### Root Cause
Earlier V5 chunks intentionally prioritized a stable plain pipeline and Prefect wrapper before extracting stage-level boundaries.

### Fix Applied
Added small validation and experiment stage helper modules, then made `run_training_pipeline()` delegate execution to those helpers while keeping metadata ownership in the pipeline command.

### Why The Fix Worked
The pipeline behavior stays the same, but the stage responsibilities are now easier to test and easier to map to future Prefect task decomposition.

### Prevention Strategy
Extract orchestration boundaries incrementally after behavior is proven, not while the base pipeline is still unstable.

# V5 Issues Faced

## Open
- Prefect dependency is not added yet.
- Stage task modules are not added yet.
- The plain Python pipeline currently wraps `app.run_experiments.main()`, so validation runs twice during the full pipeline command.
- Prefect orchestration is not added yet.

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
Kept the duplicate validation for now to avoid destabilizing the proven experiment command.

### Prevention Strategy
Future V5 task extraction should split experiment execution from validation so the pipeline controls validation exactly once.

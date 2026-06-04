# V5 Issues Faced

## Open
- Prefect dependency is not added yet.
- Runtime orchestration command is not added yet.
- Pipeline metadata persistence is implemented as a helper but not wired into a runtime orchestration command yet.

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

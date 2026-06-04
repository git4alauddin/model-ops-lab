# V5 Issues Faced

## Open
- Prefect dependency is not added yet.
- Runtime orchestration command is not added yet.
- Pipeline metadata persistence is not implemented yet.

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

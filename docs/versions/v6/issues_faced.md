# V6 Issues Faced

## Open
- Registry storage folder is not added yet.
- Model registry runtime code is not added yet.
- Register and promote commands are not added yet.

## Resolved

## V6-C1 Registry Boundary Needed Before Code

### Symptom
The project can select a champion run, but it does not yet have a separate model version lifecycle.

### Root Cause
V4 focused on MLflow experiment tracking and champion selection. V5 focused on orchestration. Neither version defined a model registry contract.

### Fix Applied
Started V6 with documentation and an ADR before adding registry runtime code.

### Why The Fix Worked
The project now has a clear boundary between MLflow experiment tracking and project-level model version management.

### Prevention Strategy
Define lifecycle states and ownership before writing model registry code.

# V6 Issues Faced

## Open
- Register and promote commands are not added yet.
- Rollback behavior is not added yet.

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

## V6-C2 Contract Before Persistence

### Symptom
The project needed model registry runtime code, but persistence and promotion behavior would be unclear without a metadata contract.

### Root Cause
Registration, promotion, and rollback all depend on the same model version fields and lifecycle state vocabulary.

### Fix Applied
Added `app/model_registry.py` with a validated model version metadata contract and focused tests.

### Why The Fix Worked
Future registry commands can now build on one shared contract instead of inventing metadata shape independently.

### Prevention Strategy
Add persistence and promotion only after the contract is covered by tests.

## V6-C3 Safe Registry Persistence

### Symptom
Validated model registry metadata could be created, but there was no safe way to store or reload it.

### Root Cause
The registry did not yet have path-building, JSON persistence, or load-time validation behavior.

### Fix Applied
Added safe metadata path construction, save/load helpers, and focused persistence tests.

### Why The Fix Worked
Registry records now round-trip through local JSON storage while preserving the same contract validation.

### Prevention Strategy
Keep generated registry records ignored by git and validate path inputs before writing files.

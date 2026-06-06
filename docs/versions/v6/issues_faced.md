# V6 Issues Faced

## Open
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

## V6-C4 Registration From Champion Report

### Symptom
The project could select a champion run and persist registry records, but there was no command connecting those two capabilities.

### Root Cause
Champion selection belonged to V4 experiment tracking. Registry persistence belonged to V6. No registration step translated champion output into model registry metadata.

### Fix Applied
Added `app/register_model.py` to read the champion report, build candidate model metadata, and save it through the registry persistence layer.

### Why The Fix Worked
The selected champion run can now become a managed candidate model version without automatically promoting it.

### Prevention Strategy
Keep registration and promotion as separate commands so lifecycle changes remain intentional.

## V6-C5 Explicit Champion Promotion

### Symptom
Registered candidate model versions existed, but there was no controlled lifecycle transition to champion.

### Root Cause
Registration and persistence did not yet define how a candidate becomes the active winner.

### Fix Applied
Added `app/promote_model.py` to load a candidate record, validate its current state, update it to `champion`, and persist promotion metadata.

### Why The Fix Worked
The project now separates candidate registration from champion promotion while keeping the transition auditable.

### Prevention Strategy
Reject promotion attempts for non-candidate records and keep rollback as a separate future behavior.

## V6-C6 Multiple Champion Risk

### Symptom
The registry could promote a candidate to champion, but it did not prevent another champion for the same model name from staying active.

### Root Cause
Promotion updated only the selected model record. It did not inspect the registry for existing champions.

### Fix Applied
Added registry listing, champion lookup, and archive behavior before promoting the selected candidate.

### Why The Fix Worked
Promotion now keeps one active champion per model name while leaving unrelated model champions untouched.

### Prevention Strategy
Keep champion replacement scoped by model name and test lifecycle transitions with multiple records.

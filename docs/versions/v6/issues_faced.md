# V6 Issues Faced

## Open
- No open V6 issues.

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

## V6-C7 Manual Registry Inspection

### Symptom
Registry state existed locally, but checking it required opening JSON files manually.

### Root Cause
The registry had write and lifecycle operations, but no read-oriented command for operational inspection.

### Fix Applied
Added `app/query_model_registry.py` to validate records, find the current champion, and print a compact summary.

### Why The Fix Worked
Registry state can now be inspected through a command-level workflow that uses the same validation layer as persistence.

### Prevention Strategy
Keep future lifecycle operations paired with simple inspection commands or reports.

## V6-C8 Lifecycle Needed Visual Closure

### Symptom
V6 behavior was implemented across registration, promotion, single champion enforcement, and querying, but the lifecycle required reading multiple files.

### Root Cause
The implementation had no focused flow diagram for the model registry lifecycle.

### Fix Applied
Added a concise Mermaid diagram for the implemented V6 registry flow.

### Why The Fix Worked
The diagram shows how champion reports become candidate records, how promotion creates one champion, how old champions are archived, and how registry query inspection works.

### Prevention Strategy
Add version-specific diagrams only after the behavior is stable enough to avoid speculative documentation.

## V6-C9 Rollback Needed Guardrails Before Code

### Symptom
Rollback was still the remaining lifecycle gap, but implementing it directly would risk unclear behavior.

### Root Cause
Rollback changes which model is champion and which model is archived. Without explicit rules, rollback could create multiple champions or modify the wrong records.

### Fix Applied
Added an ADR defining rollback as an explicit manual transition from archived model version to champion.

### Why The Fix Worked
Rollback now has clear constraints before code is added: target must be archived, current champion must be archived, reason is required, and one champion remains active.

### Prevention Strategy
Implement rollback only after guardrails are documented and test cases are clear.

## V6-C10 Rollback Command Safety

### Symptom
Rollback rules existed, but there was no command that safely restored an archived model version.

### Root Cause
The registry needed a dedicated rollback path separate from candidate promotion.

### Fix Applied
Added `app/rollback_model.py` with archived-only rollback, required reason, current champion archival, and focused tests.

### Why The Fix Worked
Rollback now follows the documented guardrails and preserves one active champion for the model name.

### Prevention Strategy
Keep rollback separate from promotion so candidate promotion and archived rollback stay distinct lifecycle operations.

## V6-C11 Closure Needed Before V7

### Symptom
The V6 lifecycle was implemented, but the project needed an explicit closure check before moving to V7.

### Root Cause
Without closure checks, it is easy to move forward while missing a command, diagram, ADR, or completion status.

### Fix Applied
Added focused V6 closure tests and marked V6 complete in the version docs.

### Why The Fix Worked
The closure test verifies the lifecycle states, registry commands, support docs, and completion marker.

### Prevention Strategy
Close each major version with a small test that verifies the version's operational components and documentation anchors.

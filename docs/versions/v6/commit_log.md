# V6 Commit Log

This file records meaningful V6 commits and the operational purpose of each change.

## 3de8e69 - v6-c1: add model registry foundation

### What Changed
- Added V6 documentation scaffold.
- Added model registry overview.
- Added model registry implementation plan.
- Added V6 verification, issues, lessons, and commit log files.
- Added ADR for starting with a local model registry.
- Added V6 status to README.
- Finalized the V5-C12 commit hash as `e8cd385`.

### What Problem It Solved
- Defines the model registry boundary before runtime code is added.
- Separates experiment tracking from model version lifecycle management.
- Records the initial decision to start with local project registry metadata.

### Verification
- Verified V6 documentation scaffold exists.
- Verified README includes V6 status.
- Verified V5-C12 commit hash is finalized as `e8cd385`.
- Ran `git diff --check`; it passed with normal LF-to-CRLF working-copy warnings only.

## 94e9291 - v6-c2: add model registry metadata contract

### What Changed
- Added model registry metadata contract module.
- Added supported lifecycle states: `candidate`, `champion`, `archived`.
- Added local `model_registry/` placeholder.
- Added focused tests for valid records, missing fields, invalid lifecycle state, supported lifecycle states, and numeric metrics.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Defines the required shape of a registered model version before persistence, registration, or promotion logic is added.
- Creates one shared lifecycle vocabulary for future V6 commands.

### Verification
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `203 passed in 8.27s`.

## 0ac6a45 - v6-c3: add model registry persistence

### What Changed
- Added safe model registry metadata path construction.
- Added model registry metadata save and load helpers.
- Added load-time validation for persisted registry JSON.
- Ignored generated `model_registry/` runtime JSON files while keeping `.gitkeep` tracked.
- Added focused persistence tests.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Moves registry metadata from in-memory records to validated local JSON records.
- Creates a persistence layer that future registration and promotion commands can use.

### Verification
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.16s`.
- `python -m pytest -q` passed: `209 passed in 5.27s`.

## e8c10b4 - v6-c4: add model registration command

### What Changed
- Added model registration command.
- Connected `reports/champion_run.json` to local model registry metadata.
- Registered selected champion runs as `candidate` model versions.
- Added clear failures for missing or incomplete champion reports.
- Added focused registration command tests.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Converts experiment champion output into a managed local model registry record.
- Keeps promotion explicit by registering the model as a candidate first.

### Verification
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.15s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.17s`.
- `python -m app.register_model` registered `customer_churn_model` candidate version `v1-7ab8f00a`.
- `python -m pytest -q` passed: `214 passed in 4.70s`.

## 9911132 - v6-c5: add champion promotion command

### What Changed
- Added lifecycle status update helper.
- Added champion promotion command.
- Added candidate-only promotion guard.
- Added promotion reason persistence.
- Added focused promotion command tests.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Adds the explicit lifecycle transition from `candidate` to `champion`.
- Prevents accidental promotion of already promoted or archived model records.

### Verification
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.19s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.14s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.18s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.18s`.
- `python -m app.promote_model` promoted `customer_churn_model` version `v1-7ab8f00a` to champion.
- `python -m pytest -q` passed: `219 passed in 4.46s`.

## dba8fd5 - v6-c6: enforce single champion model

### What Changed
- Added registry record listing.
- Added champion lookup by model name.
- Added archive behavior for existing champions.
- Updated promotion to archive prior champions before promoting a new candidate.
- Added focused single-champion tests.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Keeps the active champion unambiguous for each model name.
- Prevents multiple champion records for the same model from staying active after promotion.

### Verification
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `4 passed in 0.23s`.
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.21s`.
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `5 passed in 0.23s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.15s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.18s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.16s`.
- `python -m app.register_model` registered `customer_churn_model` candidate version `v1-7ab8f00a`.
- `python -m app.promote_model` promoted `customer_churn_model` version `v1-7ab8f00a` to champion.
- `python -m pytest -q` passed: `224 passed in 4.59s`.

## 845ebc8 - v6-c7: add model registry query command

### What Changed
- Added model registry query command.
- Added compact registry summary formatting.
- Added model-name record lookup helper.
- Added current champion display.
- Added focused query command tests.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Makes local registry state inspectable without manually opening JSON files.
- Provides a command-level way to identify the current champion and registered versions.

### Verification
- `python -m pytest -q tests\test_v6_c7_model_registry_query.py` passed: `5 passed in 0.19s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.15s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.19s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.18s`.
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `5 passed in 0.23s`.
- `python -m app.query_model_registry` printed champion `v1-7ab8f00a` for `customer_churn_model`.
- `python -m pytest -q` passed: `229 passed in 4.71s`.

## 8c9a1a4 - v6-c8: add model registry flow diagram

### What Changed
- Added V6 model registry Mermaid flow diagram.
- Documented registration from champion report to candidate record.
- Documented promotion from candidate to champion.
- Documented previous champion archival.
- Documented query command inspection.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Makes the implemented V6 lifecycle understandable without reading multiple code files.
- Keeps lifecycle documentation outside the main README.

### Verification
- `Get-Content docs\diagrams\v6_model_registry_flow.md` confirmed the V6 registry diagram exists.
- `Select-String -Path docs\diagrams\v6_model_registry_flow.md -Pattern "flowchart TD|app.register_model|app.promote_model|app.query_model_registry|status=archived"` found the expected lifecycle nodes.
- `git diff --check` passed with normal LF-to-CRLF working-copy warnings only.
- No tests were run because V6-C8 is documentation-only.

## 578fbcc - v6-c9: define model rollback guardrails

### What Changed
- Added rollback ADR for V6 model registry.
- Defined rollback as `archived -> champion`.
- Defined current champion archival during rollback.
- Required rollback reason.
- Preserved single champion rule during rollback.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Defines rollback semantics before implementation.
- Prevents ambiguous lifecycle behavior when rollback code is added.

### Verification
- `Get-Content docs\decisions\adr_model_registry_rollback_for_v6.md` confirmed the rollback ADR exists.
- `Select-String -Path docs\decisions\adr_model_registry_rollback_for_v6.md -Pattern "archived -> champion|current champion -> archived|rollback reason|one active champion|python -m app.rollback_model"` found the expected rollback guardrails.
- `git diff --check` passed with normal LF-to-CRLF working-copy warnings only.
- No tests were run because V6-C9 is documentation-only.

## 0782776 - v6-c10: add model rollback command

### What Changed
- Added model rollback command.
- Required rollback target to be archived.
- Required rollback reason.
- Archived current champion during rollback.
- Promoted rollback target to champion.
- Added focused rollback command tests.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Implements the explicit rollback lifecycle transition.
- Restores an archived model version as champion while preserving one active champion.

### Verification
- `python -m pytest -q tests\test_v6_c10_rollback_model_command.py` passed: `7 passed in 0.21s`.
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `5 passed in 0.25s`.
- `python -m pytest -q tests\test_v6_c7_model_registry_query.py` passed: `5 passed in 0.25s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py tests\test_v6_c3_model_registry_persistence.py tests\test_v6_c4_register_model_command.py` passed: `16 passed in 0.28s`.
- `python -m app.rollback_model --model-version v1-previous --reason "Command-level rollback check" --output-dir <temp>` rolled back a temporary archived model version to champion.
- `python -m pytest -q` passed: `236 passed in 5.22s`.

## Pending - v6-c11: close model registry version

### What Changed
- Added V6 closure tests.
- Verified registry lifecycle states exist.
- Verified registry commands exist.
- Verified V6 registry diagram and ADRs exist.
- Marked V6 complete in version docs.
- Updated V6 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Provides explicit closure before moving to V7.
- Confirms the local model registry lifecycle is implemented and documented.

### Verification
- `python -m pytest -q tests\test_v6_c11_registry_closure.py` passed: `4 passed in 0.14s`.
- `python -m pytest -q tests\test_v6_*.py` failed in PowerShell because the wildcard was passed literally to pytest.
- PowerShell-expanded V6 suite command passed: `42 passed in 0.42s`.
- `python -m pytest -q` passed: `240 passed in 4.77s`.

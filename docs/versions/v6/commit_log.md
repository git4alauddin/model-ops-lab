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

## Pending - v6-c2: add model registry metadata contract

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

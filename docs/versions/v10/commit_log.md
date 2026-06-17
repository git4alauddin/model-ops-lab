# V10 Commit Log

## Uncommitted - v10-c1: add retraining governance foundation

### What Changed
- Added V10 documentation scaffold.
- Added a retraining governance guide.
- Updated README current scope and useful docs with V10.
- Added focused tests for the V10-C1 documentation contract.

### What Problem It Solved
- Defines V10 as the layer for governed retraining, regression protection, approval workflow, lineage, rollback, and portfolio packaging.
- Prevents retraining automation from starting as blind automatic promotion.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py` passed: `5 passed in 0.04s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `541 passed, 1 warning in 5.64s`.
- `git diff --check` passed with a CRLF normalization warning for `README.md`.

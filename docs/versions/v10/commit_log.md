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

## Uncommitted - v10-c2: add local retraining trigger decision

### What Changed
- Added a local retraining trigger decision builder.
- Added a command to generate `reports/retraining/retraining_trigger_decision.json`.
- Reads V9 monitoring alerts and data drift summary reports.
- Added decision states for recommended retraining, no retraining required, and insufficient monitoring data.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Connects V9 monitoring outputs to V10 retraining governance without running retraining or promoting models automatically.
- Makes the retraining trigger explainable through explicit reasons and source report freshness.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c2_retraining_trigger_decision.py` passed: `6 passed in 0.49s`.
- `vir_env\Scripts\python.exe -m py_compile app\observability\retraining_trigger.py app\evaluate_retraining_trigger.py` passed.
- `vir_env\Scripts\python.exe -m app.evaluate_retraining_trigger` generated `reports\retraining\retraining_trigger_decision.json` with `decision=retraining_recommended` and `reason_count=3`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py` passed: `11 passed in 0.48s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `547 passed, 1 warning in 5.51s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v10-c3: add candidate retraining run metadata

### What Changed
- Added a candidate retraining run metadata builder.
- Added a command to initialize `retraining_runs/<run_id>/retraining_metadata.json`.
- Added the `retraining_runs/` runtime directory placeholder and git ignore rules.
- Captures trigger context, data lineage, schema lineage, previous production champion, rollback target, pending approval, and pending promotion state.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Turns a retraining recommendation into a governed retraining run record before training starts.
- Creates audit and rollback context without changing production artifacts.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c3_candidate_retraining_run_metadata.py` passed: `6 passed in 0.70s`.
- `vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\start_candidate_retraining_run.py` passed.
- `vir_env\Scripts\python.exe -m app.start_candidate_retraining_run` generated `retraining_runs\retrain-20260617T184250573186Z\retraining_metadata.json` with `status=candidate_run_initialized` and `approval=pending`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py` passed: `17 passed in 0.59s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `598 passed, 1 warning in 7.37s`.
- `git diff --check` passed with CRLF normalization warnings only.

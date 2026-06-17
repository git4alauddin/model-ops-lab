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

## Uncommitted - v10-c4: add candidate retraining command

### What Changed
- Added a governed candidate retraining command.
- Trains a candidate model for a selected initialized retraining run.
- Writes candidate model, metrics, confusion matrix, config snapshot, and training metadata under `retraining_runs/<run_id>/candidate/`.
- Updates `retraining_runs/<run_id>/retraining_metadata.json` from `candidate_run_initialized` to `candidate_trained`.
- Keeps approval and promotion pending.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Turns a governed retraining run record into actual candidate model artifacts without touching production artifacts or the model registry.
- Preserves the human approval and promotion gate for later V10 chunks.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c4_candidate_retraining_command.py` passed: `4 passed in 1.74s`.
- `vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\candidate_training.py app\run_candidate_retraining.py` passed.
- `vir_env\Scripts\python.exe -m app.run_candidate_retraining --run-id retrain-20260617T184250573186Z` generated `retraining_runs\retrain-20260617T184250573186Z\candidate\model.pkl` and updated `status=candidate_trained`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py` passed: `21 passed in 1.75s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `602 passed, 1 warning in 7.12s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v10-c5: add candidate production comparison

### What Changed
- Added a candidate-vs-production comparison builder.
- Added a command to generate `retraining_runs/<run_id>/comparison_report.json`.
- Updates retraining metadata with comparison report path, regression gate results, and promotion recommendation.
- Moves candidate runs from `candidate_trained` to `candidate_compared`.
- Keeps approval and promotion decisions pending.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Creates a reviewable evidence layer between candidate training and any approval or promotion decision.
- Prevents a trained candidate from being treated as production-ready without explicit comparison against the current champion.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c5_candidate_production_comparison.py` passed: `6 passed in 0.59s`.
- `vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\candidate_comparison.py app\compare_candidate_to_production.py` passed.
- `vir_env\Scripts\python.exe -m app.compare_candidate_to_production --run-id retrain-20260617T184250573186Z` generated `retraining_runs\retrain-20260617T184250573186Z\comparison_report.json` with `status=passed` and `recommendation=ready_for_approval`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py tests\test_v10_c5_candidate_production_comparison.py` passed: `27 passed in 1.91s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `608 passed, 1 warning in 7.23s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v10-c6: add retraining approval gate

### What Changed
- Added a human approval gate.
- Added a command to write `retraining_runs/<run_id>/approval_record.json`.
- Supports `approved`, `rejected`, and `needs_review` decisions.
- Updates retraining metadata with the human decision and approval record path.
- Moves candidate runs from `candidate_compared` to `candidate_approval_recorded`.
- Keeps `promotion.decision` pending.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Adds the human-in-the-loop checkpoint between comparison evidence and production promotion.
- Prevents metric comparison from silently becoming production approval.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c6_retraining_approval_gate.py` passed: `5 passed in 0.56s`.
- `vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\approval_gate.py app\record_retraining_approval.py` passed.
- `vir_env\Scripts\python.exe -m app.record_retraining_approval --run-id retrain-20260617T184250573186Z --decision approved --approved-by alauddin --notes "Candidate passed comparison gate for local V10 walkthrough."` generated `retraining_runs\retrain-20260617T184250573186Z\approval_record.json` with `decision=approved` and kept `promotion.decision=pending`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py tests\test_v10_c5_candidate_production_comparison.py tests\test_v10_c6_retraining_approval_gate.py` passed: `32 passed in 1.91s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `613 passed, 1 warning in 6.51s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v10-c7: add candidate promotion record

### What Changed
- Added an approved candidate promotion record.
- Added a command to write `retraining_runs/<run_id>/promotion_record.json`.
- Updates retraining metadata from `candidate_approval_recorded` to `candidate_promoted`.
- Sets `promotion.decision = promoted`.
- Records promoter, reason, promotion timestamp, rollback target, approval record path, comparison report path, and candidate artifact paths.
- Explicitly records registry and serving updates as not performed.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Creates an auditable promotion decision after human approval without pretending live production changed.
- Separates promotion decision from model registry and serving runtime updates.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c7_candidate_promotion_record.py` passed: `6 passed in 0.57s`.
- `vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\promotion_record.py app\record_candidate_promotion.py` passed.
- `vir_env\Scripts\python.exe -m app.record_candidate_promotion --run-id retrain-20260617T184250573186Z --promoted-by alauddin --reason "Approved candidate selected for V10 promotion record walkthrough."` generated `retraining_runs\retrain-20260617T184250573186Z\promotion_record.json` with `decision=promoted`, `registry_update=not_performed`, and `serving_update=not_performed`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py tests\test_v10_c5_candidate_production_comparison.py tests\test_v10_c6_retraining_approval_gate.py tests\test_v10_c7_candidate_promotion_record.py` passed: `38 passed in 1.94s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `619 passed, 1 warning in 7.40s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v10-c8: add serving update handoff

### What Changed
- Added a serving update handoff validation command.
- Added `docs/retraining/serving_update_handoff.md`.
- Writes `retraining_runs/<run_id>/serving_handoff_report.json`.
- Updates retraining metadata with serving handoff status and report path.
- Moves candidate runs from `candidate_promoted` to `candidate_serving_handoff_validated`.
- Added focused tests and V10 documentation.

### What Problem It Solved
- Explains and validates the boundary between a promoted candidate record and an actual serving update.
- Prevents the project from pretending a model is live just because metadata says it was promoted.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c8_serving_handoff.py` passed: `5 passed in 0.61s`.
- `vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\serving_handoff.py app\validate_serving_handoff.py` passed.
- `vir_env\Scripts\python.exe -m app.validate_serving_handoff --run-id retrain-20260617T184250573186Z` generated `retraining_runs\retrain-20260617T184250573186Z\serving_handoff_report.json` with `status=ready` and no registry, serving, Cloud Run, or traffic change.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py tests\test_v10_c5_candidate_production_comparison.py tests\test_v10_c6_retraining_approval_gate.py tests\test_v10_c7_candidate_promotion_record.py tests\test_v10_c8_serving_handoff.py` passed: `43 passed in 3.01s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `624 passed, 1 warning in 8.25s`.
- `git diff --check` passed with CRLF normalization warnings only.

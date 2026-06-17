# V10 Verification

## V10-C1: Retraining Governance Foundation

Planned verification:

```powershell
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py
vir_env\Scripts\python.exe -m pytest -q
git diff --check
```

Actual verification:

```text
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py
5 passed in 0.04s

vir_env\Scripts\python.exe -m pytest -q
541 passed, 1 warning in 5.64s

git diff --check
passed with a CRLF normalization warning for README.md
```

## V10-C2: Local Retraining Trigger Decision

Planned verification:

```powershell
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c2_retraining_trigger_decision.py
vir_env\Scripts\python.exe -m py_compile app\observability\retraining_trigger.py app\evaluate_retraining_trigger.py
vir_env\Scripts\python.exe -m app.evaluate_retraining_trigger
vir_env\Scripts\python.exe -m pytest -q
git diff --check
```

Actual verification:

```text
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c2_retraining_trigger_decision.py
6 passed in 0.49s

vir_env\Scripts\python.exe -m py_compile app\observability\retraining_trigger.py app\evaluate_retraining_trigger.py
passed

vir_env\Scripts\python.exe -m app.evaluate_retraining_trigger
generated reports\retraining\retraining_trigger_decision.json with decision=retraining_recommended and reason_count=3

vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py
11 passed in 0.48s

vir_env\Scripts\python.exe -m pytest -q
547 passed, 1 warning in 5.51s

git diff --check
passed with CRLF normalization warnings only
```

## V10-C4: Candidate Retraining Command

Planned verification:

```powershell
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c4_candidate_retraining_command.py
vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\candidate_training.py app\run_candidate_retraining.py
vir_env\Scripts\python.exe -m app.run_candidate_retraining --run-id <run_id>
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py
vir_env\Scripts\python.exe -m pytest -q
git diff --check
```

Actual verification:

```text
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c4_candidate_retraining_command.py
4 passed in 1.74s

vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\retraining\candidate_training.py app\run_candidate_retraining.py
passed

vir_env\Scripts\python.exe -m app.run_candidate_retraining --run-id retrain-20260617T184250573186Z
generated retraining_runs\retrain-20260617T184250573186Z\candidate\model.pkl and updated status=candidate_trained

vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py tests\test_v10_c4_candidate_retraining_command.py
21 passed in 1.75s

vir_env\Scripts\python.exe -m pytest -q
602 passed, 1 warning in 7.12s

git diff --check
passed with CRLF normalization warnings only
```

## V10-C3: Candidate Retraining Run Metadata

Planned verification:

```powershell
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c3_candidate_retraining_run_metadata.py
vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\start_candidate_retraining_run.py
vir_env\Scripts\python.exe -m app.start_candidate_retraining_run
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py
vir_env\Scripts\python.exe -m pytest -q
git diff --check
```

Actual verification:

```text
vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c3_candidate_retraining_run_metadata.py
6 passed in 0.70s

vir_env\Scripts\python.exe -m py_compile app\retraining\candidate_run_metadata.py app\start_candidate_retraining_run.py
passed

vir_env\Scripts\python.exe -m app.start_candidate_retraining_run
generated retraining_runs\retrain-20260617T184250573186Z\retraining_metadata.json with status=candidate_run_initialized and approval=pending

vir_env\Scripts\python.exe -m pytest -q tests\test_v10_c1_retraining_governance_foundation.py tests\test_v10_c2_retraining_trigger_decision.py tests\test_v10_c3_candidate_retraining_run_metadata.py
17 passed in 0.59s

vir_env\Scripts\python.exe -m pytest -q
598 passed, 1 warning in 7.37s

git diff --check
passed with CRLF normalization warnings only
```

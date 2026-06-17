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

# V6 Verification

## Checks Performed
- Verified V6 documentation scaffold exists.
- Verified model registry ADR exists.
- Verified README includes V6 in the compact version scope table.
- Verified V5-C12 commit hash is finalized in V5 commit log.
- Verified V6-C2 model registry metadata contract tests.
- Verified V6-C3 model registry persistence tests.
- Verified V6-C4 model registration command tests.
- Verified V6-C5 champion promotion command tests.
- Verified V6-C6 single champion enforcement tests.
- Verified V6-C7 model registry query command tests.

## Commands Executed
- `Get-ChildItem docs\versions\v6`
- `Get-Content docs\decisions\adr_local_model_registry_for_v6.md`
- `Select-String -Path README.md -Pattern "V6"`
- `Select-String -Path docs\versions\v5\commit_log.md -Pattern "e8cd385"`
- `git diff --check`
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py`
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py`
- `python -m pytest -q tests\test_v6_c4_register_model_command.py`
- `python -m app.register_model`
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py`
- `python -m app.promote_model`
- `python -m pytest -q tests\test_v6_c6_single_champion.py`
- `python -m pytest -q tests\test_v6_c7_model_registry_query.py`
- `python -m app.query_model_registry`
- `python -m pytest -q`

## Expected Output
- V6 docs exist.
- ADR explains local registry decision and trade-offs.
- README exposes V6 as part of the compact project scope.
- V5-C12 is finalized with commit hash `e8cd385`.
- No runtime behavior changes are introduced in V6-C1.
- V6-C2 accepts valid model registry records and rejects invalid metadata.
- V6-C3 saves and loads validated local registry metadata records.
- V6-C4 registers the champion report as a local candidate model version.
- V6-C5 promotes a registered candidate model version to champion.
- V6-C6 archives previous champions when promoting a new champion for the same model name.
- V6-C7 prints a concise local registry summary and current champion.

## Actual Output
- `docs\versions\v6` contains overview, implementation, verification, issues, lessons, and commit log files.
- `README.md` contains V6 in the compact project scope table.
- `docs\versions\v5\commit_log.md` records V5-C12 as commit `e8cd385`.
- `git diff --check` passed. PowerShell reported normal LF-to-CRLF working-copy warnings only.
- No tests were run because V6-C1 is documentation and decision-record only.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `203 passed in 8.27s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.16s`.
- `python -m pytest -q` passed: `209 passed in 5.27s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.15s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.17s`.
- `python -m app.register_model` registered `customer_churn_model` candidate version `v1-7ab8f00a`.
- `python -m pytest -q` passed: `214 passed in 4.70s`.
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.19s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.14s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.18s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.18s`.
- `python -m app.promote_model` promoted `customer_churn_model` version `v1-7ab8f00a` to champion.
- `python -m pytest -q` passed: `219 passed in 4.46s`.
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `4 passed in 0.23s`.
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.21s`.
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `5 passed in 0.23s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.15s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.18s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.16s`.
- `python -m app.register_model` registered `customer_churn_model` candidate version `v1-7ab8f00a`.
- `python -m app.promote_model` promoted `customer_churn_model` version `v1-7ab8f00a` to champion.
- `python -m pytest -q` passed: `224 passed in 4.59s`.
- `python -m pytest -q tests\test_v6_c7_model_registry_query.py` passed: `5 passed in 0.19s`.
- `python -m pytest -q tests\test_v6_c2_model_registry_contract.py` passed: `5 passed in 0.15s`.
- `python -m pytest -q tests\test_v6_c3_model_registry_persistence.py` passed: `6 passed in 0.19s`.
- `python -m pytest -q tests\test_v6_c4_register_model_command.py` passed: `5 passed in 0.20s`.
- `python -m pytest -q tests\test_v6_c5_promote_model_command.py` passed: `5 passed in 0.18s`.
- `python -m pytest -q tests\test_v6_c6_single_champion.py` passed: `5 passed in 0.23s`.
- `python -m app.query_model_registry` printed champion `v1-7ab8f00a` for `customer_churn_model`.
- `python -m pytest -q` passed: `229 passed in 4.71s`.

## Outcome
V6-C1 establishes model registry planning and documentation foundations before runtime registry code is added.

V6-C2 establishes the model registry metadata contract before registration and promotion commands are added.

V6-C3 persists validated model registry metadata locally before registration and promotion commands are added.

V6-C4 registers the current champion report as a local candidate model version.

V6-C5 promotes a registered candidate model version to champion.

V6-C6 keeps one active champion per model name by archiving prior champions during promotion.

V6-C7 makes local registry state inspectable from a command instead of opening JSON files manually.

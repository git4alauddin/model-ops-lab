# V9 Commit Log

## Uncommitted - v9-c1: add production observability foundation

### What Changed
- Added V9 documentation scaffold.
- Added a production observability strategy document.
- Updated README current scope with V9.
- Added focused tests for the V9-C1 documentation contract.

### What Problem It Solved
- Defines V9 as the project layer for monitoring, drift detection, prediction telemetry, alert-ready metrics, and incident debugging.
- Prevents the monitoring version from starting with disconnected tools before the observability contract is clear.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py` passed: `5 passed in 0.04s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `479 passed, 1 warning in 5.66s`.
- `git diff --check` passed with a CRLF normalization warning for `README.md`.

## Uncommitted - v9-c2: add prediction telemetry contract

### What Changed
- Added a versioned prediction telemetry contract.
- Added prediction telemetry event builders.
- Wired `/predict` and `/predict/batch` success and failure logs to the V9 telemetry shape.
- Added validation failure telemetry while preserving normal FastAPI `422` responses.
- Added `DEPLOYMENT_VERSION` serving configuration.
- Added prediction telemetry documentation and focused tests.

### What Problem It Solved
- Turns prediction JSONL records into a stable telemetry source for monitoring, drift detection, debugging, dashboards, and alert-ready metrics.
- Links each prediction event to endpoint, serving environment, and deployment version.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c2_prediction_telemetry_contract.py` passed: `6 passed, 1 warning in 0.86s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v7_c7_prediction_logging.py tests\test_v7_c8_batch_prediction_endpoint.py tests\test_v8_c3_serving_environment_config.py` passed: `20 passed in 0.96s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `485 passed, 1 warning in 5.64s`.
- `git diff --check` passed with CRLF normalization warnings only.

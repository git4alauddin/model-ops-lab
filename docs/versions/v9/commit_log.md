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

## Uncommitted - v9-c3: add local prediction monitoring summary

### What Changed
- Added a local monitoring summary builder for prediction telemetry.
- Added a command to build `reports/monitoring/prediction_summary.json`.
- Summarized request counts, success/failure counts, failure rate, latency percentiles, prediction distribution, probability distribution, and failure categories.
- Updated README and V9 documentation.
- Added focused tests for the monitoring summary logic and report persistence.

### What Problem It Solved
- Converts V9 prediction telemetry into practical monitoring signals before adding Prometheus, Grafana, or drift tooling.
- Gives the project a local, testable observability report that can feed later dashboard and alerting work.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c3_local_monitoring_summary.py` passed: `7 passed in 0.06s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py tests\test_v9_c2_prediction_telemetry_contract.py tests\test_v9_c3_local_monitoring_summary.py` passed: `18 passed, 1 warning in 0.82s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `492 passed, 1 warning in 5.60s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v9-c4: filter monitoring summary telemetry events

### What Changed
- Updated the local prediction monitoring summary to use only supported V9 telemetry events.
- Added skipped-record accounting for legacy or unsupported telemetry records.
- Added focused tests for event filtering.
- Updated README and V9 documentation.

### What Problem It Solved
- Prevents older pre-V9 telemetry records from appearing as `None` buckets in event and endpoint summaries.
- Prevents legacy records from polluting request counts, failure rates, latency metrics, and prediction distributions.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c3_local_monitoring_summary.py tests\test_v9_c4_monitoring_summary_event_filtering.py` passed: `12 passed in 0.12s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py tests\test_v9_c2_prediction_telemetry_contract.py tests\test_v9_c3_local_monitoring_summary.py tests\test_v9_c4_monitoring_summary_event_filtering.py` passed: `23 passed, 1 warning in 1.07s`.
- `vir_env\Scripts\python.exe -m app.build_prediction_monitoring_summary` regenerated `reports\monitoring\prediction_summary.json` with `raw_event_count=263`, `total_events=92`, `skipped_event_count=171`, and no `None` metric buckets.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `497 passed, 1 warning in 5.54s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v9-c5: add monitoring alert rules foundation

### What Changed
- Added local alert evaluation from the prediction monitoring summary.
- Added an alert report command.
- Added default thresholds for missing telemetry, failure rate, p95 latency, skipped telemetry, and prediction distribution collapse.
- Added focused tests for alert rules and persistence.
- Updated README and V9 documentation.

### What Problem It Solved
- Converts local monitoring metrics into actionable alert states.
- Creates a file-based alert foundation before Prometheus, Grafana, Alertmanager, Cloud Monitoring, or notifications.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c5_monitoring_alert_rules.py` passed: `7 passed in 0.09s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py tests\test_v9_c2_prediction_telemetry_contract.py tests\test_v9_c3_local_monitoring_summary.py tests\test_v9_c4_monitoring_summary_event_filtering.py tests\test_v9_c5_monitoring_alert_rules.py` passed: `30 passed, 1 warning in 2.38s`.
- `vir_env\Scripts\python.exe -m app.build_monitoring_alerts` generated `reports\monitoring\alerts.json` with `overall_status=alerting` and `active_alert_count=3`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `504 passed, 1 warning in 18.71s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v9-c6: add data drift reference baseline foundation

### What Changed
- Added a reference baseline builder for future data drift detection.
- Added a command to generate `reports/drift/reference_baseline.json`.
- Summarized numeric, categorical, boolean, and target distributions from the training dataset.
- Updated README and V9 documentation.
- Added focused tests for baseline content and persistence.

### What Problem It Solved
- Establishes the reference distribution needed before comparing production inference traffic for drift.
- Keeps drift foundations dependency-free before introducing Evidently or dashboard tooling.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c6_drift_reference_baseline.py` passed: `7 passed in 0.59s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py tests\test_v9_c2_prediction_telemetry_contract.py tests\test_v9_c3_local_monitoring_summary.py tests\test_v9_c4_monitoring_summary_event_filtering.py tests\test_v9_c5_monitoring_alert_rules.py tests\test_v9_c6_drift_reference_baseline.py` passed: `37 passed, 1 warning in 1.54s`.
- `vir_env\Scripts\python.exe -m app.build_drift_reference_baseline` generated `reports\drift\reference_baseline.json` with `row_count=20` and `feature_count=7`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `511 passed, 1 warning in 8.64s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v9-c7: add production inference feature snapshot

### What Changed
- Added `input_features` to prediction telemetry for validated requests.
- Added an inference feature snapshot builder from prediction telemetry.
- Added a command to generate `reports/drift/inference_snapshot.json`.
- Updated the telemetry contract documentation.
- Added focused tests for feature snapshot extraction, skipped event accounting, and persistence.

### What Problem It Solved
- Creates the production inference distribution needed for future baseline-vs-inference drift comparison.
- Keeps feature telemetry bounded to validated serving features instead of identifiers, labels, or invalid raw payloads.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c7_inference_feature_snapshot.py` passed: `6 passed in 1.29s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v7_c7_prediction_logging.py tests\test_v9_c2_prediction_telemetry_contract.py` passed: `13 passed in 1.34s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py tests\test_v9_c2_prediction_telemetry_contract.py tests\test_v9_c3_local_monitoring_summary.py tests\test_v9_c4_monitoring_summary_event_filtering.py tests\test_v9_c5_monitoring_alert_rules.py tests\test_v9_c6_drift_reference_baseline.py tests\test_v9_c7_inference_feature_snapshot.py` passed: `43 passed, 1 warning in 1.40s`.
- `vir_env\Scripts\python.exe -m app.build_inference_snapshot` generated `reports\drift\inference_snapshot.json` with `row_count=0` and `skipped_event_count=297` because existing local telemetry predates `input_features`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `517 passed, 1 warning in 8.20s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Uncommitted - v9-c8: add local data drift comparison

### What Changed
- Added local baseline-vs-inference drift comparison.
- Added a command to generate `reports/drift/data_drift_summary.json`.
- Added numeric mean/range drift checks.
- Added categorical ratio drift checks.
- Added `insufficient_data` handling for empty inference snapshots.
- Updated README and V9 documentation.
- Added focused tests for drift comparison behavior and persistence.

### What Problem It Solved
- Turns the reference baseline and inference snapshot into a concrete local drift signal.
- Creates the final no-install bridge before introducing tool-based drift reporting with Evidently.

### Verification
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c8_local_data_drift_comparison.py` passed: `6 passed in 0.51s`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c6_drift_reference_baseline.py tests\test_v9_c7_inference_feature_snapshot.py tests\test_v9_c8_local_data_drift_comparison.py` passed: `19 passed in 0.64s`.
- `vir_env\Scripts\python.exe -m app.build_data_drift_summary` generated `reports\drift\data_drift_summary.json` with `overall_status=insufficient_data`, `inference_row_count=0`, and `insufficient_feature_count=7`.
- `vir_env\Scripts\python.exe -m pytest -q tests\test_v9_c1_observability_foundation.py tests\test_v9_c2_prediction_telemetry_contract.py tests\test_v9_c3_local_monitoring_summary.py tests\test_v9_c4_monitoring_summary_event_filtering.py tests\test_v9_c5_monitoring_alert_rules.py tests\test_v9_c6_drift_reference_baseline.py tests\test_v9_c7_inference_feature_snapshot.py tests\test_v9_c8_local_data_drift_comparison.py` passed: `49 passed, 1 warning in 1.36s`.
- `vir_env\Scripts\python.exe -m pytest -q` passed: `523 passed, 1 warning in 7.16s`.
- `git diff --check` passed with CRLF normalization warnings only.

# V9 Issues Faced

## V9-C1: Production Observability Foundation

No implementation issue yet.

The main design risk is scope control. Monitoring can expand into many tools quickly, so V9 starts by defining the telemetry and operational boundaries before adding Prometheus, Grafana, Evidently, or cloud-native monitoring.

## V9-C2: Prediction Telemetry Contract

The existing V7 prediction log was useful but too small for production observability. It did not include an explicit event version, event type, endpoint, serving environment, deployment version, error category, or failure stage.

V9-C2 changes that shape intentionally, so the older V7 tests had to be updated from the audit-log expectation to the telemetry-event expectation.

## V9-C3: Local Monitoring Summary From Prediction Telemetry

No external monitoring package was needed.

The main design choice was percentile calculation. V9-C3 uses a nearest-rank percentile because it is simple, deterministic, and dependency-free for local monitoring summaries.

## V9-C4: Monitoring Summary Event Filtering

The first local summary exposed a realistic issue: `logs/predictions.jsonl` contained older records from before V9-C2. Those records did not have `event_version`, `event_type`, or `endpoint`, so they appeared as `None` buckets and inflated failure metrics.

The fix was to treat the telemetry contract as a real boundary. Current metrics now use only supported V9 events and separately report skipped legacy records.

## V9-C5: Monitoring Alert Rules Foundation

No external alerting system was added.

The key design choice was to keep alert thresholds local and explicit. This lets the project learn alert behavior before adding Prometheus Alertmanager, Grafana alerts, Cloud Monitoring, or notification channels.

## V9-C6: Data Drift Reference Baseline Foundation

No external drift library was added.

The main design choice was to build the reference baseline from the existing training config and validation schema. That keeps the drift baseline aligned with the same dataset and feature roles already used by training, validation, and serving.

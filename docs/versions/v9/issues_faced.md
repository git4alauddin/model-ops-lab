# V9 Issues Faced

## V9-C1: Production Observability Foundation

No implementation issue yet.

The main design risk is scope control. Monitoring can expand into many tools quickly, so V9 starts by defining the telemetry and operational boundaries before adding Prometheus, Grafana, Evidently, or cloud-native monitoring.

## V9-C2: Prediction Telemetry Contract

The existing V7 prediction log was useful but too small for production observability. It did not include an explicit event version, event type, endpoint, serving environment, deployment version, error category, or failure stage.

V9-C2 changes that shape intentionally, so the older V7 tests had to be updated from the audit-log expectation to the telemetry-event expectation.

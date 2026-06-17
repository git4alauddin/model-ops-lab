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

## V9-C7: Production Inference Feature Snapshot

The existing V9 telemetry did not store input features, so it could support request monitoring but not feature drift checks.

The fix was to add a bounded `input_features` snapshot to validated prediction telemetry. Validation failures still avoid raw payload logging because failed payloads may be malformed or unsafe to treat as feature data.

## V9-C8: Local Data Drift Comparison

The current local inference snapshot can have zero feature rows because existing telemetry was generated before `input_features` existed.

V9-C8 handles that as `insufficient_data` instead of raising an error or reporting false `ok` status. This keeps the drift report honest until fresh feature-bearing prediction telemetry exists.

## V9-C9: Fresh Feature-Bearing Telemetry Workflow

Existing local reports initially showed `insufficient_data` because the telemetry file contained many events generated before V9-C7 added `input_features`.

Generating fresh valid prediction requests fixed the missing inference feature rows and allowed the drift summary to produce a real `drift_detected` result.

## V9-C10: Drift Alert Integration

No external alerting tool was added.

The main integration choice was to keep drift alerts in `reports/monitoring/alerts.json` instead of creating a separate alert report. That keeps operational and ML-specific alert states in one local place.

## V9-C11: Monitoring Dashboard Data Contract

No dashboard UI was added.

The key design choice was to create a dashboard-ready JSON contract first. This keeps the visualization layer simple later because it can consume one stable file instead of reinterpreting every raw monitoring and drift report.

## V9-C12: Local Monitoring Dashboard HTML

No external dashboard tool was added.

The main design choice was to render a static local HTML file from `reports/monitoring/dashboard_snapshot.json`. This gives the project an actual visible dashboard while keeping Grafana, Prometheus, servers, and new dependencies out of this chunk.

The dashboard renderer escapes snapshot values because monitoring reports are data inputs to HTML output.

## V9-C13: Prometheus Metrics Endpoint

The first design thought was to hand-render Prometheus text manually, but that would compromise the production learning goal.

The fix was to use `prometheus-client` explicitly and add it to `requirements.txt`. It was already installed transitively in the local virtual environment, but V9-C13 records it as a direct dependency because `/metrics` now relies on it.

The endpoint uses a local collector registry per response so tests and repeated app creation do not collide on metric names.

## V9-C14: Prometheus And Grafana Local Stack

The main local networking issue is that Prometheus runs in a container while the FastAPI API may run on the host machine.

The stack uses `host.docker.internal:8000/metrics` so Prometheus can scrape the host API from Docker Desktop.

The monitoring compose file is separate from the serving compose file so the project can start the API and monitoring stack independently while learning each tool.

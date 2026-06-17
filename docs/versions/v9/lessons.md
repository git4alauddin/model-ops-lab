# V9 Lessons

## V9-C1: Production Observability Foundation

- Deployment proves the service can run, but observability proves the service can be operated.
- ML systems need backend metrics and ML-specific metrics because healthy latency does not prove healthy predictions.
- Prediction telemetry is the raw material for drift detection, debugging, retention, and incident analysis.
- Data drift checks whether production inputs still resemble training inputs.
- Concept drift checks whether the relationship between inputs and outcomes has changed.
- Dashboards should come after telemetry contracts, otherwise they become disconnected charts.
- Alert-ready metrics should name thresholds, severity, ownership, and response behavior before automation is added.

## V9-C2: Prediction Telemetry Contract

- A prediction log should be a telemetry event, not only a debugging message.
- Stable event fields make downstream metrics, drift checks, dashboards, and alerts easier to build.
- Validation failures matter because bad input traffic can reveal broken clients or schema drift.
- `DEPLOYMENT_VERSION` links prediction behavior to the exact local run, image tag, Git SHA, or Cloud Run revision.
- Success, prediction failure, and validation failure events should be separated by `event_type` instead of inferred from message text.

## V9-C3: Local Monitoring Summary From Prediction Telemetry

- Telemetry becomes useful when it is converted into operational signals.
- Failure rate, latency percentiles, and prediction distribution are the first practical monitoring signals for a serving API.
- Local JSON summaries are a good bridge before Prometheus and dashboards because they prove the metrics are computable.
- Prediction probability buckets help detect confidence shifts before full drift detection exists.
- Monitoring commands should fail clearly when telemetry is missing or corrupted.

## V9-C4: Monitoring Summary Event Filtering

- Legacy telemetry should not pollute current monitoring metrics.
- Raw event count and valid event count are different when logs span multiple contract versions.
- Skipped-record accounting is better than silent filtering because it explains why the summary numbers may be smaller than the file line count.
- Versioned telemetry contracts make monitoring evolution safer.

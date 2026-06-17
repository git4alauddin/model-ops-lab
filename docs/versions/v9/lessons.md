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

## V9-C5: Monitoring Alert Rules Foundation

- Alert rules turn monitoring metrics into operational decisions.
- Local alert files are useful before notification systems because they make threshold logic visible and testable.
- Alerts should include recommended actions, not only metric values.
- High failure rate and missing telemetry are critical because they block trust in the serving system.
- Prediction distribution collapse is ML-specific; it can reveal behavior problems even when backend latency looks healthy.

## V9-C6: Data Drift Reference Baseline Foundation

- Drift detection needs a reference distribution before it can compare current production traffic.
- The training dataset is the first practical reference baseline for this project.
- Schema roles prevent identifiers and target columns from being mixed into feature drift checks.
- Numeric drift needs distribution statistics, not only min and max.
- Categorical drift needs value counts and value ratios so shifts can be measured later.
- Building the baseline before using Evidently makes the tool easier to understand when we add it.

## V9-C7: Production Inference Feature Snapshot

- Drift detection needs both a reference baseline and a current inference snapshot.
- Prediction telemetry must include validated input features before feature drift can be measured.
- Feature snapshots should be privacy-aware: keep useful feature values, but exclude identifiers, labels, and invalid raw payloads.
- Validation failures are useful operational telemetry, but they should not become drift rows because they did not pass the input schema.
- Snapshot builders should report skipped events so missing feature telemetry is visible.

## V9-C8: Local Data Drift Comparison

- Drift detection is a comparison between reference behavior and current inference behavior.
- Numeric feature drift can start with simple mean and range movement before advanced statistical tests.
- Categorical drift can start with category ratio changes.
- `insufficient_data` is a valid monitoring result; it is better than pretending a drift check passed.
- Local drift comparison makes later Evidently reports easier to understand because the basic math is visible.

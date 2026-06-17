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

## V9-C9: Fresh Feature-Bearing Telemetry Workflow

- Fresh feature-bearing telemetry turns drift comparison from missing-data reporting into real drift evaluation.
- Drift systems depend on data freshness; old telemetry can be structurally valid but incomplete for newer contracts.
- A local workflow should regenerate dependent reports in order: prediction summary, inference snapshot, drift summary, then alerts.
- Swagger UI is useful for learning the API interaction, while TestClient is useful for fast local refreshes.
- Report transitions are a good learning signal: `insufficient_data` means the pipeline is honest, not broken.

## V9-C10: Drift Alert Integration

- Drift alerts connect ML-specific monitoring to the same operational alert report.
- A drift detector is more useful when it produces actionable alert states, not only a standalone report.
- `drift_detected` and `insufficient_data` are different alert situations and need different recommended actions.
- Integrating drift alerts locally first keeps the alert logic visible before adding external notification systems.

## V9-C11: Monitoring Dashboard Data Contract

- Dashboards should read from a stable data contract instead of scraping many unrelated files directly.
- A dashboard snapshot separates report generation from visualization.
- Report freshness timestamps matter because stale monitoring data can be misleading.
- Source report paths make dashboard cards traceable back to the detailed JSON reports.

## V9-C12: Local Monitoring Dashboard HTML

- A dashboard should read from the dashboard snapshot instead of recomputing monitoring logic.
- Static HTML is a useful learning bridge before Grafana because it makes the monitoring surface visible without new services.
- Dashboard cards should show both backend health and ML-specific health.
- Escaping snapshot values matters because dashboards render report data into HTML.
- Report freshness belongs on the dashboard because stale observability can be worse than no observability.

## V9-C13: Prometheus Metrics Endpoint

- Prometheus gives Grafana a scrapeable metrics source instead of making Grafana read local JSON files directly.
- `prometheus-client` avoids hand-rolled text exposition and keeps the endpoint aligned with Prometheus conventions.
- A per-render collector registry prevents duplicate metric registration during tests and repeated app imports.
- Report availability metrics are useful because a working `/metrics` endpoint can still be missing local monitoring inputs.
- The metrics endpoint is a bridge from local file-based observability to production-style monitoring tools.

## V9-C14: Prometheus And Grafana Local Stack

- Grafana should visualize Prometheus metrics instead of reading application files directly.
- Prometheus needs a stable scrape target; in this local Windows/Docker setup that target is `host.docker.internal:8000/metrics`.
- Grafana provisioning makes dashboards reproducible instead of manually clicking them into existence.
- Keeping the monitoring compose file separate from the serving compose file makes learning and debugging easier.
- A starter dashboard is useful even if teams later refine panels in the Grafana UI.

## V9-C15: Monitoring Retention And Incident Debugging Workflow

- Incident debugging starts from the symptom, then moves backward through dashboards, metrics, reports, and raw telemetry.
- Retention is useful only when the retained files can reconstruct what happened.
- Generated logs and reports should stay out of Git because they are runtime evidence and may contain sensitive context.
- Report freshness matters during incidents because stale reports can point to the wrong cause.
- A clear regeneration order prevents inconsistent monitoring reports during local debugging.

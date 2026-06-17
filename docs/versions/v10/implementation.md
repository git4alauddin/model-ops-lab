# V10 Implementation

## V10-C1: Retraining Governance Foundation

### Files Added

```text
docs/retraining/retraining_governance.md
docs/versions/v10/
tests/test_v10_c1_retraining_governance_foundation.py
```

### Files Updated

```text
README.md
```

### Behavior
- Added the V10 documentation scaffold.
- Defined V10 as the continuous ML lifecycle management version.
- Recorded why monitoring alone is not enough after drift or model staleness is detected.
- Defined the governed retraining lifecycle.
- Documented retraining triggers, candidate model evaluation, regression protection, approval workflow, metadata, rollback, and portfolio packaging boundaries.
- Added focused static tests to protect the V10-C1 documentation contract.

### Important Boundary
V10-C1 is documentation and planning only.

It does not schedule retraining, run retraining, compare candidate models, promote models, install Airflow, or change production artifacts.

Those belong in later V10 chunks.

## V10-C2: Local Retraining Trigger Decision

### Files Added

```text
app/evaluate_retraining_trigger.py
app/observability/retraining_trigger.py
tests/test_v10_c2_retraining_trigger_decision.py
```

### Files Updated

```text
README.md
docs/versions/v10/
```

### Behavior
- Added a local retraining trigger decision builder.
- Reads:

```text
reports/monitoring/alerts.json
reports/drift/data_drift_summary.json
```

- Writes:

```text
reports/retraining/retraining_trigger_decision.json
```

- Added a command entry point:

```powershell
python -m app.evaluate_retraining_trigger
```

- Produces one of three decision states:

```text
retraining_recommended
retraining_not_required
insufficient_monitoring_data
```

- Treats drift, high failure rate, and prediction distribution collapse as retraining signals.
- Treats missing telemetry and insufficient drift rows as blockers before retraining.
- Records decision reasons, source report paths, source freshness, thresholds, and recommended next action.

### Important Boundary
V10-C2 evaluates whether retraining should be considered.

It does not run retraining, train a candidate model, compare models, promote artifacts, schedule jobs, or change production state.

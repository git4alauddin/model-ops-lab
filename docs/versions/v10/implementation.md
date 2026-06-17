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

## V10-C3: Candidate Retraining Run Metadata

### Files Added

```text
app/retraining/
app/start_candidate_retraining_run.py
retraining_runs/.gitkeep
tests/test_v10_c3_candidate_retraining_run_metadata.py
```

### Files Updated

```text
.gitignore
README.md
docs/versions/v10/
```

### Behavior
- Added a governed candidate retraining run initializer.
- Reads:

```text
reports/retraining/retraining_trigger_decision.json
configs/training.yaml
data_versions/customer_churn/v1.yaml
schema_versions/customer_churn_v1.yaml
model_registry/
```

- Writes:

```text
retraining_runs/<run_id>/retraining_metadata.json
```

- Added a command entry point:

```powershell
python -m app.start_candidate_retraining_run
```

- Requires the trigger decision to be `retraining_recommended`.
- Captures trigger reasons, source report freshness, dataset lineage, schema lineage, previous production champion, rollback target, pending approval state, pending promotion decision, and empty candidate artifact placeholders.
- Keeps generated retraining run records local and ignored by git.

### Important Boundary
V10-C3 initializes the governed candidate retraining record only.

It does not train a model, create candidate artifacts, compare candidate-vs-production metrics, approve promotion, promote artifacts, schedule retraining, or change production state.

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

## V10-C4: Candidate Retraining Command

### Files Added

```text
app/retraining/candidate_training.py
app/run_candidate_retraining.py
tests/test_v10_c4_candidate_retraining_command.py
```

### Files Updated

```text
README.md
app/retraining/candidate_run_metadata.py
docs/versions/v10/
```

### Behavior
- Added a governed candidate retraining command:

```powershell
python -m app.run_candidate_retraining --run-id <run_id>
```

- Reads:

```text
retraining_runs/<run_id>/retraining_metadata.json
configs/training.yaml
data/churn.csv
schema_versions/customer_churn_v1.yaml
data_versions/customer_churn/v1.yaml
```

- Writes candidate artifacts inside the selected retraining run:

```text
retraining_runs/<run_id>/candidate/model.pkl
retraining_runs/<run_id>/candidate/metrics.json
retraining_runs/<run_id>/candidate/confusion_matrix.json
retraining_runs/<run_id>/candidate/config_snapshot.json
retraining_runs/<run_id>/candidate/training_metadata.json
```

- Updates:

```text
retraining_runs/<run_id>/retraining_metadata.json
```

- Requires the run metadata status to be `candidate_run_initialized`.
- Moves the run status to `candidate_trained`.
- Stores candidate artifact paths, validation status, model type, metrics, and training metadata in the retraining metadata record.
- Keeps approval and promotion states as `pending`.

### Important Boundary
V10-C4 trains a candidate model only inside the governed retraining run folder.

It does not register the candidate model, compare it against production, approve it, promote it, overwrite production artifacts, update the serving model, schedule retraining, or change rollback state.

## V10-C5: Candidate vs Production Comparison Report

### Files Added

```text
app/retraining/candidate_comparison.py
app/compare_candidate_to_production.py
tests/test_v10_c5_candidate_production_comparison.py
```

### Files Updated

```text
README.md
app/retraining/candidate_run_metadata.py
docs/versions/v10/
```

### Behavior
- Added a governed comparison command:

```powershell
python -m app.compare_candidate_to_production --run-id <run_id>
```

- Reads:

```text
retraining_runs/<run_id>/retraining_metadata.json
```

- Writes:

```text
retraining_runs/<run_id>/comparison_report.json
```

- Updates:

```text
retraining_runs/<run_id>/retraining_metadata.json
```

- Requires run status `candidate_trained`.
- Compares candidate metrics against `previous_production_model.metrics`.
- Tracks accuracy, precision, recall, and F1 regression checks.
- Moves the run status to `candidate_compared`.
- Updates `candidate.comparison_report_path`, `regression_gates.status`, `regression_gates.results`, and `promotion.recommendation`.
- Keeps approval and promotion decisions as `pending`.

### Important Boundary
V10-C5 produces comparison evidence only.

It does not approve the candidate, promote it, register it, update the serving model, overwrite artifacts, or change rollback state.

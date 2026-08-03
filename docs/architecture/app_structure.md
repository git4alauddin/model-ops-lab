# App Structure Reference

This file maps the `app/` package to the project capabilities it implements.

Use it as a quick ownership guide before opening code. It is organized by package and command surface, with one short responsibility note per file.

## File-Level Directory Tree

```text
app/
|-- __init__.py                               # Marks app as the main Python package.
|-- build_dashboard_snapshot.py               # Command: builds dashboard_snapshot.json from monitoring, alert, and drift reports.
|-- build_data_drift_summary.py               # Command: compares reference and inference drift reports.
|-- build_drift_reference_baseline.py         # Command: builds the training-data drift reference baseline.
|-- build_inference_snapshot.py               # Command: builds inference feature distributions from prediction telemetry.
|-- build_monitoring_alerts.py                # Command: evaluates local monitoring and drift alert rules.
|-- build_monitoring_dashboard.py             # Command: renders the static local monitoring dashboard HTML.
|-- build_prediction_monitoring_summary.py    # Command: summarizes V9 prediction telemetry.
|-- champion_selection.py                     # Selects the best eligible experiment run and champion candidate.
|-- check_reproducibility.py                  # Command: verifies dataset checksum against dataset registry metadata.
|-- compare_candidate_to_production.py        # Command: compares retraining candidate metrics against production champion metrics.
|-- config.py                                 # Loads and validates training configuration.
|-- data.py                                   # Shared controlled CSV dataset loader.
|-- dataset_registry.py                       # Loads dataset version metadata and validates dataset checksums.
|-- evaluate.py                               # Computes model evaluation metrics and evaluation duration.
|-- evaluate_retraining_trigger.py            # Command: writes the retraining trigger decision report.
|-- experiment_tracking.py                    # Wraps MLflow run, params, metrics, artifacts, and tags.
|-- model_registry.py                         # Defines local model registry metadata, persistence, and lifecycle helpers.
|-- pipeline_run_metadata.py                  # Builds and persists V5 pipeline run metadata.
|-- promote_model.py                          # Command: promotes a registry candidate to champion.
|-- query_model_registry.py                   # Command: prints the local registry champion and version summary.
|-- record_candidate_promotion.py             # Command: records approved candidate promotion evidence.
|-- record_retraining_approval.py             # Command: records human approval for a retraining candidate.
|-- register_model.py                         # Command: registers the experiment champion as a registry candidate.
|-- rollback_local_retraining_model.py        # Command: rolls back a V10 local retraining serving update.
|-- rollback_model.py                         # Command: rolls back an archived registry model to champion.
|-- run_candidate_retraining.py               # Command: trains a retraining candidate inside a run folder.
|-- run_experiments.py                        # Command: runs multi-model experiment candidates and selects champion.
|-- run_prefect_pipeline.py                   # Command: runs the Prefect training pipeline wrapper.
|-- run_training_pipeline.py                  # Command: runs the plain Python training pipeline wrapper.
|-- schemas.py                                # Shared configuration contract constants.
|-- serve_api.py                              # Uvicorn entrypoint for the FastAPI serving API.
|-- start_candidate_retraining_run.py         # Command: initializes governed retraining run metadata.
|-- train.py                                  # Command: runs single-model training, evaluation, artifacts, and MLflow logging.
|-- update_local_serving_model.py             # Command: updates local registry champion from a validated retraining run.
|-- validate_data.py                          # Command: runs dataset validation and writes validation reports.
|-- validate_serving_handoff.py               # Command: validates readiness for local serving update.
|
|-- api/
|   |-- __init__.py                           # Marks the FastAPI API package.
|   |-- app.py                                # Creates the FastAPI app and registers routes plus validation handling.
|   |-- constants.py                          # Stores serving API identity constants.
|   |-- routes.py                             # Defines /health, /ready, /metrics, /predict, and /predict/batch.
|   |-- schemas.py                            # Defines Pydantic request and response schemas for inference.
|   `-- validation_handlers.py                # Logs validation-failure telemetry for invalid API requests.
|
|-- observability/
|   |-- __init__.py                           # Marks monitoring, drift, dashboard, and trigger helpers.
|   |-- dashboard_snapshot.py                 # Combines report files into one dashboard-ready JSON contract.
|   |-- drift_baseline.py                     # Builds training-data feature and target reference distributions.
|   |-- drift_comparison.py                   # Compares reference and inference distributions for data drift.
|   |-- inference_snapshot.py                 # Builds inference feature distributions from telemetry input_features.
|   |-- monitoring_alerts.py                  # Evaluates alert rules from monitoring and drift summaries.
|   |-- monitoring_dashboard.py               # Renders the local static monitoring dashboard.
|   |-- monitoring_summary.py                 # Summarizes request, latency, prediction, and telemetry quality metrics.
|   |-- prediction_telemetry.py               # Builds versioned prediction success, failure, and validation-failure events.
|   |-- prometheus_metrics.py                 # Renders local report values as Prometheus-compatible metrics.
|   `-- retraining_trigger.py                 # Converts monitoring and drift reports into retraining decisions.
|
|-- orchestration/
|   |-- __init__.py                           # Marks orchestration helpers.
|   `-- prefect_pipeline.py                   # Defines the local Prefect flow and stage-level tasks.
|
|-- pipeline/
|   |-- __init__.py                           # Marks reusable training pipeline helpers.
|   |-- preprocessing.py                      # Splits data, detects feature types, and builds preprocessing.
|   `-- trainer.py                            # Builds models, composes sklearn pipelines, and trains them.
|
|-- retraining/
|   |-- __init__.py                           # Marks governed retraining lifecycle helpers.
|   |-- approval_gate.py                      # Records and validates human approval decisions.
|   |-- candidate_comparison.py               # Builds candidate-vs-production comparison and regression gates.
|   |-- candidate_run_metadata.py             # Builds, validates, loads, saves, and updates retraining metadata.
|   |-- candidate_training.py                 # Trains isolated retraining candidates and records artifacts.
|   |-- local_serving_rollback.py             # Restores the recorded previous champion after local retraining update.
|   |-- local_serving_update.py               # Mutates local registry champion and validates local serving.
|   |-- promotion_record.py                   # Records approved promotion decisions before serving mutation.
|   `-- serving_handoff.py                    # Validates evidence required before local serving update.
|
|-- serving/
|   |-- __init__.py                           # Marks serving-layer helpers.
|   |-- model_loader.py                       # Loads the current registry champion model artifact.
|   |-- prediction_logging.py                 # Writes structured prediction telemetry JSONL.
|   |-- predictor.py                          # Converts requests to model inputs and returns prediction responses.
|   |-- readiness.py                          # Checks whether exactly one champion is available for serving.
|   |-- runtime_logging.py                    # Writes human-readable serving runtime logs.
|   `-- settings.py                           # Loads serving runtime settings from environment variables.
|
|-- tasks/
|   |-- __init__.py                           # Marks extracted pipeline stage helpers.
|   |-- experiment_task.py                    # Runs and validates the experiment stage for pipeline orchestration.
|   `-- validation_task.py                    # Runs validation and enforces the training validation gate.
|
|-- utils/
|   |-- __init__.py                           # Marks shared utility helpers.
|   |-- artifacts.py                          # Builds artifact paths and persists models/JSON outputs.
|   `-- logger.py                             # Configures console and file loggers without duplicate handlers.
|
`-- validation/
    |-- __init__.py                           # Marks reusable validation helpers.
    |-- checks.py                             # Runs schema, dtype, null, range, duplicate, and quality checks.
    `-- reports.py                            # Defines validation reports and persists validation outputs.
```

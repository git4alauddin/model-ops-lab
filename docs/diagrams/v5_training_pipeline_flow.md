# V5 Training Pipeline Flow

This diagram shows the current V5 training pipeline.

It is intentionally limited to the implemented V5 behavior: local Prefect orchestration, pipeline metadata, single validation ownership, reusable experiment workflow, MLflow candidate runs, champion selection, and failure-stage recording.

```mermaid
flowchart TD
    prefect_cmd["python -m app.run_prefect_pipeline"]
    prefect_flow["Prefect flow<br/>modelopslab-training-pipeline"]
    prefect_task["Prefect task<br/>run-training-pipeline<br/>retries=2"]
    pipeline_cmd["python -m app.run_training_pipeline"]
    config["configs/training.yaml"]
    metadata_start["Initialize pipeline metadata<br/>pipeline_version=v5-c7<br/>status=running"]
    validation["Validation stage<br/>validate_dataset_readiness"]
    validation_gate{"Validation passed?"}
    validation_failed["Mark validation failed<br/>failed_stage=validation"]

    experiment_workflow["run_experiment_workflow<br/>validate_before_run=false"]
    candidates["Configured candidates"]
    logreg["logistic_regression_baseline"]
    tree["decision_tree_baseline"]
    forest["random_forest_baseline"]

    run_a["MLflow candidate run"]
    run_b["MLflow candidate run"]
    run_c["MLflow candidate run"]
    mlflow["MLflow tracking store<br/>mlflow.db + mlruns/"]

    selection["Champion selection rule"]
    champion_report["reports/champion_run.json"]
    champion["Champion run ID"]
    metadata_passed["Finalize pipeline metadata<br/>status=passed<br/>mlflow_run_ids<br/>champion_run_id"]
    metadata_failed["Finalize pipeline metadata<br/>status=failed<br/>failed_stage=experiments"]
    pipeline_output["pipeline_runs/<pipeline_run_id>.json"]

    experiment_failed{"Experiment stage failed?"}

    prefect_cmd --> prefect_flow
    prefect_flow --> prefect_task
    prefect_task --> pipeline_cmd

    pipeline_cmd --> config
    pipeline_cmd --> metadata_start
    metadata_start --> pipeline_output
    config --> validation
    validation --> validation_gate

    validation_gate -- no --> validation_failed
    validation_failed --> pipeline_output

    validation_gate -- yes --> experiment_workflow
    experiment_workflow --> candidates
    candidates --> logreg
    candidates --> tree
    candidates --> forest

    logreg --> run_a
    tree --> run_b
    forest --> run_c

    run_a --> mlflow
    run_b --> mlflow
    run_c --> mlflow

    run_a --> selection
    run_b --> selection
    run_c --> selection
    selection --> champion_report
    selection --> champion

    experiment_workflow --> experiment_failed
    experiment_failed -- yes --> metadata_failed
    metadata_failed --> pipeline_output

    experiment_failed -- no --> metadata_passed
    champion_report --> metadata_passed
    champion --> metadata_passed
    metadata_passed --> pipeline_output
```

## Operational Meaning

V5 introduces a pipeline-level view of training.

The Prefect command wraps the existing plain Python pipeline in a local Prefect flow and task. The pipeline command owns validation once, then calls the reusable experiment workflow with validation disabled for that inner workflow. Candidate models still create MLflow runs, the champion selection logic still writes `reports/champion_run.json`, and the pipeline writes a separate run record under `pipeline_runs/`.

Pipeline metadata is not model metadata and it is not MLflow metadata. It records workflow-level state: stage status, failed stage, dataset version, MLflow run IDs, and champion run ID.

## Current Boundary

Prefect is active as a local wrapper.

Scheduled Prefect deployments are not active yet.

The current V5 pipeline can still run without Prefect through `python -m app.run_training_pipeline`. The Prefect command adds local flow/task orchestration around that proven behavior.

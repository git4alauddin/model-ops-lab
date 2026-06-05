# V5 Training Pipeline Flow

This diagram shows the current V5 training pipeline.

It is intentionally limited to the implemented V5 behavior: local Prefect stage-level orchestration, optional inactive deployment scaffold, pipeline metadata, extracted stage helpers, single validation ownership, reusable experiment workflow, MLflow candidate runs, champion selection, and failure-stage recording.

```mermaid
flowchart TD
    prefect_cmd["python -m app.run_prefect_pipeline"]
    fallback_cmd["python -m app.run_training_pipeline<br/>plain fallback"]
    prefect_yaml["prefect.yaml<br/>deployment scaffold<br/>schedule inactive"]

    subgraph prefect_layer["Prefect local orchestration"]
        prefect_flow["Flow<br/>modelopslab-training-pipeline"]
        init_task["Task<br/>initialize-pipeline-run"]
        validation_task["Task<br/>validation-stage<br/>retries=2"]
        experiment_task["Task<br/>experiment-stage<br/>retries=0"]
        finalize_task["Task<br/>finalize-pipeline-run"]
    end

    subgraph project_stage_helpers["Project stage helpers"]
        config["configs/training.yaml"]
        metadata_running["pipeline metadata<br/>v5-c11<br/>status=running"]
        validation_helper["app.tasks.validation_task<br/>validate_dataset_readiness"]
        validation_gate{"Validation passed?"}
        experiment_helper["app.tasks.experiment_task<br/>run_experiment_workflow<br/>validate_before_run=false"]
    end

    subgraph experiment_tracking["Experiment tracking"]
        candidates["Configured candidates"]
        logreg["logistic_regression_baseline"]
        tree["decision_tree_baseline"]
        forest["random_forest_baseline"]
        run_a["MLflow run"]
        run_b["MLflow run"]
        run_c["MLflow run"]
        mlflow["MLflow tracking store<br/>mlflow.db + mlruns/"]
        selection["Champion selection rule"]
        champion_report["reports/champion_run.json"]
        champion["Champion run ID"]
    end

    subgraph pipeline_records["Pipeline records"]
        metadata_passed["pipeline metadata<br/>status=passed<br/>mlflow_run_ids<br/>champion_run_id"]
        metadata_failed_validation["pipeline metadata<br/>status=failed<br/>failed_stage=validation"]
        metadata_failed_experiments["pipeline metadata<br/>status=failed<br/>failed_stage=experiments"]
        metadata_failed_finalization["pipeline metadata<br/>status=failed<br/>failed_stage=finalization"]
        pipeline_output["pipeline_runs/<pipeline_run_id>.json"]
        failure_context["Prefect command error<br/>pipeline_run_id + failed_stage"]
    end

    prefect_yaml -. optional deployment registration .-> prefect_flow
    prefect_cmd --> prefect_flow
    fallback_cmd -. uses same helpers without Prefect .-> config

    prefect_flow --> init_task
    init_task --> config
    init_task --> metadata_running
    metadata_running --> pipeline_output

    init_task --> validation_task
    validation_task --> validation_helper
    validation_helper --> validation_gate

    validation_gate -- no --> metadata_failed_validation
    metadata_failed_validation --> pipeline_output
    metadata_failed_validation --> failure_context

    validation_gate -- yes --> experiment_task
    experiment_task --> experiment_helper
    experiment_helper --> candidates
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

    experiment_task -- failure --> metadata_failed_experiments
    metadata_failed_experiments --> pipeline_output
    metadata_failed_experiments --> failure_context

    champion_report --> finalize_task
    champion --> finalize_task
    finalize_task --> metadata_passed
    metadata_passed --> pipeline_output

    finalize_task -- failure --> metadata_failed_finalization
    metadata_failed_finalization --> pipeline_output
    metadata_failed_finalization --> failure_context
```

## Operational Meaning

V5 introduces a pipeline-level view of training.

The Prefect command runs the training pipeline as local stage-level Prefect tasks. The plain Python pipeline command remains available as the fallback path, while the Prefect flow now exposes initialization, validation, experiment, and finalization as separate task states. Validation uses a small retry policy. The experiment task does not retry because retrying candidate runs can create duplicate MLflow runs. Candidate models still create MLflow runs, the champion selection logic still writes `reports/champion_run.json`, and the pipeline writes a separate run record under `pipeline_runs/`.

Pipeline metadata is not model metadata and it is not MLflow metadata. It records workflow-level state: stage status, failed stage, dataset version, MLflow run IDs, and champion run ID.

When the Prefect-wrapped pipeline fails, the command-level error preserves the failed `pipeline_run_id` and `failed_stage` from the pipeline metadata so the matching `pipeline_runs/<pipeline_run_id>.json` file can be inspected directly.

## Current Boundary

Prefect is active as a local wrapper.

The Prefect deployment scaffold exists, but its schedule is inactive by default.

The current V5 pipeline can still run without Prefect through `python -m app.run_training_pipeline`. The Prefect command adds local stage-level flow/task orchestration around the same validation and experiment helpers.

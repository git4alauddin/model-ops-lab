# V4 Experiment Tracking Flow

This diagram shows the completed V4 experiment tracking and champion selection workflow.

It is intentionally limited to V4 scope: MLflow run tracking, single-model training, multi-model candidate experiments, artifact logging, champion selection, and the champion report.

```mermaid
flowchart TD
    subgraph experiment_inputs["Experiment inputs"]
        config["configs/training.yaml"]
        validation["Validation gate"]
        dataset_version["Dataset version + checksum"]
    end

    subgraph baseline_path["Single-model baseline path"]
        train_cmd["python -m app.train"]
        single_run["Single baseline MLflow run"]
        single_artifacts["artifacts/model.pkl<br/>metrics.json<br/>confusion_matrix.json<br/>training_metadata.json"]
    end

    subgraph candidate_path["Multi-model candidate path"]
        experiment_cmd["python -m app.run_experiments"]
        candidates["Configured candidates"]
        logreg["logistic_regression_baseline"]
        tree["decision_tree_baseline"]
        forest["random_forest_baseline"]
        run_a["MLflow candidate run"]
        run_b["MLflow candidate run"]
        run_c["MLflow candidate run"]
        candidate_artifacts["artifacts/experiments/<candidate>/..."]
    end

    subgraph mlflow_tracking["MLflow tracking store"]
        mlflow["mlflow.db + mlruns/"]
        params["Params<br/>model, split, dataset, checksum"]
        metrics["Metrics<br/>accuracy, precision, recall, f1, durations"]
        tags["Tags<br/>candidate_name, champion"]
        artifacts["Artifacts<br/>model, metrics, confusion matrix, metadata"]
        ui["MLflow UI"]
    end

    subgraph champion_selection["Champion selection"]
        selection["Champion selection rule"]
        champion["Current champion run<br/>champion=true"]
        report["reports/champion_run.json"]
    end

    config --> validation
    validation --> train_cmd
    validation --> experiment_cmd
    dataset_version --> train_cmd
    dataset_version --> experiment_cmd

    train_cmd --> single_run
    single_run --> single_artifacts
    single_run --> mlflow

    experiment_cmd --> candidates
    candidates --> logreg
    candidates --> tree
    candidates --> forest

    logreg --> run_a
    tree --> run_b
    forest --> run_c

    run_a --> candidate_artifacts
    run_b --> candidate_artifacts
    run_c --> candidate_artifacts

    run_a --> mlflow
    run_b --> mlflow
    run_c --> mlflow

    mlflow --> params
    mlflow --> metrics
    mlflow --> tags
    mlflow --> artifacts

    run_a --> selection
    run_b --> selection
    run_c --> selection
    selection --> champion
    selection --> report
    champion --> tags

    mlflow --> ui
    report --> ui
```

## Operational Meaning

V4 makes experiment tracking useful, not just present.

The single-model path keeps a stable baseline command. The multi-model path trains configured candidates as separate MLflow runs, logs their params, metrics, tags, and artifacts, applies the documented champion selection rule, clears stale champion tags, marks exactly one current champion, and writes `reports/champion_run.json` as the local decision record.

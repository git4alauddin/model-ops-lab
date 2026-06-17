# V1 Pipeline Flow

This diagram shows the completed V1 baseline training workflow.

It is intentionally limited to V1 scope: config-driven training, baseline preprocessing/model flow, artifact persistence, and readable runtime logs.

```mermaid
flowchart TD
    subgraph inputs["Training inputs"]
        config["configs/training.yaml"]
        dataset["data/churn.csv"]
    end

    subgraph command_layer["Training command"]
        command["python -m app.train"]
        load_config["Load and validate config"]
        load_data["Load CSV dataset"]
    end

    subgraph data_preparation["Data preparation"]
        drop_cols["Drop configured non-feature columns"]
        split_target["Split features and target"]
        split_train["Create train/test split"]
        feature_types["Detect numeric and categorical features"]
    end

    subgraph model_training["Model training and evaluation"]
        preprocessing["Build preprocessing pipeline"]
        model["Build Logistic Regression model"]
        pipeline["Build sklearn training pipeline"]
        fit["Fit pipeline on training data"]
        evaluate["Evaluate held-out test set"]
    end

    subgraph runtime_outputs["Runtime outputs"]
        model_file["artifacts/model.pkl"]
        metrics_file["artifacts/metrics.json"]
        config_snapshot["artifacts/config_snapshot.json"]
        metadata_file["artifacts/training_metadata.json"]
        logs["logs/modelopslab.log"]
    end

    config --> command
    dataset --> command

    command --> load_config
    load_config --> load_data
    load_data --> drop_cols
    drop_cols --> split_target
    split_target --> split_train
    split_train --> feature_types
    feature_types --> preprocessing
    preprocessing --> pipeline
    model --> pipeline
    load_config --> model
    pipeline --> fit
    fit --> evaluate

    fit --> model_file
    evaluate --> metrics_file
    load_config --> config_snapshot
    fit --> metadata_file
    evaluate --> metadata_file

    command --> logs
    load_data --> logs
    split_train --> logs
    feature_types --> logs
    preprocessing --> logs
    fit --> logs
    evaluate --> logs
    model_file --> logs
```

## Runtime Outputs

```text
artifacts/model.pkl
artifacts/metrics.json
artifacts/config_snapshot.json
artifacts/training_metadata.json
logs/modelopslab.log
```

## Operational Meaning

V1 establishes the baseline training path.

The training command loads the configured dataset, prepares features, fits a Logistic Regression baseline, evaluates it on a held-out split, persists local runtime artifacts, and writes readable logs for inspection.

# V1 Pipeline Flow

This diagram shows the completed V1 baseline training workflow.

```mermaid
flowchart LR
  config["configs/training.yaml"]
  data["data/churn.csv"]
  load["Load Dataset"]
  drop_cols["Drop Configured Columns"]
  split_target["Split Features / Target"]
  split_train["Train / Test Split"]
  feature_types["Detect Feature Types"]
  preprocess["Build Preprocessing Pipeline"]
  model["Build Logistic Regression"]
  pipeline["Build Training Pipeline"]
  train["Train Fitted Pipeline"]
  evaluate["Evaluate Held-Out Test Set"]
  artifacts["Persist Artifacts"]
  logs["Write Runtime Logs"]

  config --> load
  config --> drop_cols
  config --> split_train
  config --> model
  config --> artifacts
  config --> logs
  data --> load
  load --> drop_cols
  drop_cols --> split_target
  split_target --> split_train
  split_train --> feature_types
  feature_types --> preprocess
  preprocess --> pipeline
  model --> pipeline
  pipeline --> train
  train --> evaluate
  evaluate --> artifacts
  train --> artifacts
  load --> logs
  train --> logs
  evaluate --> logs
  artifacts --> logs
```

## Outputs

```text
artifacts/model.pkl
artifacts/metrics.json
artifacts/config_snapshot.json
artifacts/training_metadata.json
logs/modelopslab.log
```

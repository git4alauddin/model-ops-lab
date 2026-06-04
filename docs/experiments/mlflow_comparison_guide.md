# MLflow Experiment Comparison Guide

This guide explains how to compare training runs in MLflow for ModelOpsLab.

## Purpose

Experiment comparison helps answer:

```text
Which run performed better?
Which config produced that result?
Which dataset version was used?
Which artifacts explain the result?
Was a slower run actually worth it?
```

MLflow does not decide the best model automatically for us yet. For now, this guide describes manual comparison.

## Start The MLflow UI

From the project root:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Open:

```text
http://127.0.0.1:5000
```

## Open The Experiment

In the UI:

```text
1. Open the experiment list.
2. Select customer_churn_baseline.
3. Review the run table.
```

Each row is one training run created by:

```powershell
python -m app.train
```

## Compare Multiple Runs

In the experiment run table:

```text
1. Select two or more runs using the checkboxes.
2. Click Compare.
3. Review params, metrics, and artifacts side by side.
```

Use comparison when you have multiple runs from different configs, model choices, dataset versions, or pipeline versions.

## Params To Compare

Params explain why runs differ.

Important params:

```text
pipeline_version
model_type
test_size
random_state
dataset_name
dataset_version
dataset_checksum_algorithm
dataset_checksum
```

Read params as the run setup.

Example interpretation:

```text
same metrics + same dataset_checksum = likely same data and setup
same model_type + different random_state = split randomness may explain metric changes
different dataset_version = compare carefully because data changed
```

## Metrics To Compare

Metrics explain numeric performance and runtime behavior.

Important quality metrics:

```text
accuracy
precision
recall
f1
```

Important runtime metrics:

```text
training_duration_seconds
evaluation_duration_seconds
```

Read metrics as the run result.

For classification, do not look at accuracy alone. Use F1, precision, recall, and the confusion matrix together.

## Artifact Inspection

Artifacts explain the run in detail.

Important artifacts:

```text
model.pkl
metrics.json
confusion_matrix.json
config_snapshot.json
training_metadata.json
```

Use artifacts this way:

```text
metrics.json
  full metric output saved by the project

confusion_matrix.json
  direct view of prediction errors by class

config_snapshot.json
  exact training config used for the run

training_metadata.json
  dataset version, row counts, feature counts, run ID, and timings

model.pkl
  trained model artifact for that run
```

## Duration vs Quality

Runtime metrics are useful, but they are not the main model-quality signal.

Use this rule of thumb:

```text
If quality is the same, prefer the simpler/faster run.
If quality improves meaningfully, a slower run may be acceptable.
If duration changes a lot, inspect config and artifacts before trusting the comparison.
```

For the current small sample dataset, duration numbers are mostly learning signals. They become more meaningful on larger data.

## Manual Comparison Checklist

Use this checklist before calling one run better than another:

```text
1. Same dataset version?
2. Same dataset checksum?
3. Same target column?
4. Same test_size?
5. Same random_state?
6. Same model_type?
7. Better F1?
8. Precision and recall acceptable?
9. Confusion matrix acceptable?
10. Training duration acceptable?
11. Evaluation duration acceptable?
12. Artifacts present?
```

If the dataset version or checksum differs, treat the comparison as a data comparison, not only a model comparison.

## UI vs SQL

Use the MLflow UI for normal experiment comparison.

Use SQL when:

```text
learning MLflow internals
checking raw database tables
debugging why a run does not appear
building custom reports later
```

SQL query references are kept in:

```text
project_details/proj_ref_notes/mlflow_sql_queries.md
```

## Current Project Context

Currently the project tracks one baseline model family:

```text
Logistic Regression
```

So most current comparisons are repeated baseline runs.

This guide becomes more useful when we add:

```text
different model types
different hyperparameters
different dataset versions
different preprocessing choices
```

## Mental Model

Use this mental model when comparing runs:

```text
Params explain what changed.
Metrics show what happened numerically.
Artifacts explain the result in detail.
Tags explain run labels or failures.
Dataset version/checksum tells whether the data was the same.
```

A good comparison always checks setup, result, and artifacts together.

# Best Run Selection Rule

This rule defines how to choose the best MLflow run for ModelOpsLab.

## Purpose

A best-run rule prevents subjective model selection.

The goal is to choose a run using a consistent order:

```text
valid run first
same data comparison second
model quality third
runtime and simplicity last
```

This rule is implemented by the multi-model experiment runner:

```powershell
python -m app.run_experiments
```

The runner applies this rule to the configured candidates and writes:

```text
reports/champion_run.json
```

## Eligible Runs

A run is eligible only if all conditions are true:

```text
status = FINISHED
required metrics exist
required params exist
required artifacts exist
validation passed before training
```

Required metrics:

```text
accuracy
precision
recall
f1
training_duration_seconds
evaluation_duration_seconds
```

Required params:

```text
pipeline_version
model_type
dataset_name
dataset_version
dataset_checksum
```

Required artifacts:

```text
model.pkl
metrics.json
confusion_matrix.json
config_snapshot.json
training_metadata.json
```

Reject runs that are failed, incomplete, missing required artifacts, or tied to unclear dataset metadata.

## Same-Data Requirement

Only compare model quality directly when runs use the same dataset identity.

The strongest same-data check is:

```text
dataset_name matches
dataset_version matches
dataset_checksum matches
```

If dataset checksum differs, treat the result as a data comparison, not a pure model comparison.

## Primary Metric

Primary ranking metric:

```text
f1
```

Reason:

```text
F1 balances precision and recall.
For churn classification, accuracy alone can hide weak minority-class behavior.
```

## Secondary Metrics

Use these to validate the F1 result:

```text
precision
recall
accuracy
confusion_matrix.json
```

Interpretation:

```text
higher F1 is preferred
precision and recall must both be acceptable
accuracy should not contradict the confusion matrix
confusion matrix should not show unacceptable class-specific errors
```

## Tie-Breakers

If two eligible same-data runs have the same F1, apply tie-breakers in this order:

```text
1. Higher recall
2. Higher precision
3. Higher accuracy
4. Lower training_duration_seconds
5. Lower evaluation_duration_seconds
6. Simpler model_type
7. Newer pipeline_version
```

For churn prediction, recall is placed before precision because missing churners is usually more costly than flagging extra customers for review.

## Rejection Rules

Reject a run from best-run selection if:

```text
run status is not FINISHED
required metrics are missing
required artifacts are missing
dataset checksum is missing
training metadata is missing
confusion matrix is missing
validation did not pass before training
metrics look inconsistent with confusion matrix
```

## Manual Selection Checklist

Use this checklist when reviewing the automated result in MLflow UI:

```text
1. Open customer_churn_baseline experiment.
2. Filter to FINISHED runs.
3. Confirm dataset_name, dataset_version, and dataset_checksum match.
4. Confirm required artifacts exist.
5. Sort by f1 descending.
6. Inspect precision and recall.
7. Open confusion_matrix.json.
8. Apply tie-breakers if needed.
9. Record selected run_id and reason.
```

## Decision Record Format

When selecting a best run manually, record:

```text
selected_run_id:
selection_date:
dataset_name:
dataset_version:
dataset_checksum:
primary_metric: f1
f1:
precision:
recall:
accuracy:
reason:
rejected_alternatives:
```

The current automated report is written to `reports/champion_run.json`. Later V6 can use the selected champion as the input to model registry registration or promotion.

## Current Project Context

Current baseline:

```text
model_type = logistic_regression
dataset_name = customer_churn
dataset_version = v1
```

Since the project currently has one baseline model family, this rule mainly prepares the project for future comparisons.

It becomes more important when we add:

```text
more model types
hyperparameter changes
new dataset versions
new preprocessing choices
```

## One-Line Rule

Choose the highest-F1 eligible run on the same dataset checksum, then break ties by recall, precision, accuracy, runtime, simplicity, and pipeline version.

# MLflow Learning Notes

This is a reference note for understanding MLflow while building ModelOpsLab. It is not a project status document.

## What MLflow Is

MLflow is an experiment tracking tool.

It does not train the model by itself. Our Python training code still does the real work:

```text
load data
validate data
split data
train model
evaluate model
save outputs
```

MLflow records what happened during that training run so we can inspect it later.

MLflow helps answer:

```text
Which runs happened?
What parameters were used?
What metrics were produced?
Which files were created?
Which dataset version was used?
Which run performed better?
Why did a run fail?
```

## What Does The Training

Training happens in our local Python code, not inside MLflow.

In this project, the training command is:

```powershell
python -m app.train
```

That code controls the actual ML workflow:

```text
load config
validate dataset
load dataset
split train/test
build preprocessing
build model
train model
evaluate model
save artifacts
```

MLflow only records what our code tells it to log:

```text
params
metrics
tags
artifacts
run status
start and end time
```

Clean mental model:

```text
app.train = does the ML work
MLflow    = records and displays what happened
```

## Core MLflow Concepts

### Experiment

An experiment is a group of related runs.

Example:

```text
customer_churn_baseline
```

Use one experiment when the runs belong to the same modeling problem.

### Run

A run is one execution of training.

Every time training runs, MLflow can create a new run.

A run usually has:

```text
run_id
status
start time
end time
params
metrics
tags
artifacts
```

### Params

Params describe the setup of the run.

Examples:

```text
model_type = logistic_regression
test_size = 0.2
random_state = 42
dataset_version = v1
dataset_checksum = sha256 value
pipeline_version = v4-c2
```

Params are normally fixed before or during training. They explain how the run was configured.

### Metrics

Metrics describe numeric results.

Examples:

```text
accuracy
precision
recall
f1
training_duration_seconds
evaluation_duration_seconds
```

Metrics are used for comparison across runs.

### Tags

Tags describe metadata about the run.

Examples:

```text
run_outcome = failed
failure_type = RuntimeError
failure_message = something went wrong
```

Use tags for labels and descriptions. Use metrics for numeric values you want to compare.

### Artifacts

Artifacts are files produced by a run.

Examples:

```text
model.pkl
metrics.json
config_snapshot.json
training_metadata.json
```

Artifacts are useful when we need the actual output files, not just numbers in a table.

## Why MLflow Has Multiple Storage Locations

This was the confusing part.

MLflow separates metadata from files.

```text
mlflow.db
  stores the tracking index/catalog

mlruns/ or mlartifacts/
  stores the actual artifact files
```

Think of it like this:

```text
mlflow.db = library catalog
mlruns/   = shelves containing the books/files
```

The database knows what exists and where it is. The artifact folders hold the actual files.

## What `mlflow.db` Stores

`mlflow.db` is the SQLite tracking database.

It stores structured tracking data:

```text
experiments
runs
run status
start and end times
params
metrics
latest metric values
tags
artifact locations
```

The MLflow UI reads this database to know:

```text
which experiments exist
which runs belong to each experiment
which run is latest
which params and metrics belong to each run
where that run's artifacts are stored
```

If `mlflow.db` is deleted, MLflow loses the catalog of runs, even if artifact files still exist on disk.

## What `mlruns/1/` Means

`mlruns/1/` is MLflow's artifact area for experiment ID `1`.

Example structure:

```text
mlruns/
  1/
    <run_id>/
      artifacts/
        model.pkl
        metrics.json
        config_snapshot.json
        training_metadata.json
```

The `1` is the internal MLflow experiment ID.

The experiment name may be something readable like:

```text
customer_churn_baseline
```

MLflow stores the mapping between experiment name and experiment ID in `mlflow.db`.

## Project Artifacts vs MLflow Artifacts

There are two artifact worlds.

### Project Artifacts

Stored here:

```text
modelOpsLab/artifacts/
```

These are written by our training code first.

Example:

```text
artifacts/model.pkl
artifacts/metrics.json
artifacts/config_snapshot.json
artifacts/training_metadata.json
```

Meaning:

```text
latest local output of the project pipeline
```

These files may be overwritten by the next training run.

### MLflow Artifacts

Stored under MLflow's run-specific artifact location.

Example:

```text
mlruns/1/<run_id>/artifacts/
```

Meaning:

```text
MLflow-tracked copy for one specific run
```

These files are historical per-run copies.

## Are The Files Same?

Content-wise, usually yes.

Physically, no.

Flow:

```text
training code
  -> writes files to artifacts/
  -> logs those files to MLflow
  -> MLflow stores run-specific artifact copies
  -> MLflow UI shows the MLflow-managed copies
```

So `artifacts/model.pkl` and the MLflow UI's `model.pkl` may contain the same model, but they are not the same physical file.

## How The MLflow UI Uses These Pieces

The UI does not simply scan folders blindly.

The UI flow is:

```text
MLflow UI
  -> reads mlflow.db
  -> gets experiments and runs
  -> gets params, metrics, tags, status
  -> reads artifact location from DB
  -> loads files from mlruns/ or mlartifacts/
```

So:

```text
mlflow.db tells the UI what exists
mlruns/ stores files the UI can display/download
```

If `mlruns/` is deleted:

```text
runs, params, and metrics may still show
artifacts will be missing
```

If `mlflow.db` is deleted:

```text
UI loses the run catalog
artifact files may still be on disk, but MLflow no longer knows how to organize them
```

## Why We Use SQLite

MLflow needs a tracking backend.

For local learning, SQLite is simple and inspectable:

```text
sqlite:///mlflow.db
```

This creates a local database file:

```text
mlflow.db
```

Benefits:

```text
works locally
can be inspected with a database GUI
keeps tracking metadata structured
supports MLflow UI
```

## What The Database GUI Is For

The database GUI lets us inspect `mlflow.db` directly.

It is useful for learning what MLflow stores behind the UI.

Good tables to inspect:

```text
experiments
runs
params
metrics
latest_metrics
tags
```

Use the MLflow UI for normal experiment work.

Use the DB GUI when learning, debugging, or understanding MLflow internals.

Helpful SQL queries are saved here:

```text
docs/experiments/mlflow_sql_queries.md
```

## How To Use The MLflow UI

From the project folder:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Then open:

```text
http://127.0.0.1:5000
```

In the UI:

```text
open the experiment
click a run
inspect Overview
inspect Params
inspect Metrics
inspect Tags
inspect Artifacts
compare multiple runs
```

## What To Look For In A Run

For learning, inspect these sections:

```text
Status
Run ID
Start time
Duration
Params
Metrics
Tags
Artifacts
```

Important params:

```text
pipeline_version
model_type
test_size
random_state
dataset_name
dataset_version
dataset_checksum
```

Important metrics:

```text
accuracy
precision
recall
f1
training_duration_seconds
evaluation_duration_seconds
```

Important artifacts:

```text
model.pkl
metrics.json
config_snapshot.json
training_metadata.json
```

## Mental Model

Use this simple mental model:

```text
Our code trains the model.
MLflow records the experiment.
mlflow.db stores the run catalog.
mlruns/ stores run artifact files.
MLflow UI reads both and shows them nicely.
```

More detailed flow:

```text
python -m app.train
  -> training code writes latest files to artifacts/
  -> MLflow creates a run
  -> params are logged
  -> metrics are logged
  -> tags are logged when needed
  -> artifacts are copied into MLflow artifact storage
  -> mlflow.db stores the index for all of it
  -> MLflow UI shows the run using mlflow.db + artifact files
```

## What To Commit And What Not To Commit

Do not commit local runtime tracking files:

```text
mlflow.db
mlflow.db-shm
mlflow.db-wal
mlruns/
mlartifacts/
artifacts/*.pkl
artifacts/*.json
logs/
```

Commit code, configs, tests, and docs.

Runtime outputs are generated again when training runs.

## One-Line Summary

MLflow is our experiment notebook: the DB stores the table of contents, the artifact folders store the files, and the UI combines both so we can inspect and compare training runs.

# Model Registry Learning Notes

This is a reference note for understanding model registry concepts while building ModelOpsLab. It is not a project status document.

## What A Model Registry Is

A model registry is a controlled place to track model versions and their lifecycle.

It helps answer:

```text
Which model version exists?
Which run produced it?
Which dataset produced it?
Which model is the current champion?
Which older models are archived?
Can we roll back to a previous model?
```

In this project, the model registry starts as a local file-based registry.

## Why We Added It After MLflow

MLflow tracks experiment runs.

The model registry tracks selected model versions.

Clean mental model:

```text
MLflow run        = one training or experiment attempt
champion_run.json = selected best experiment run
model registry    = lifecycle record for selected model versions
```

MLflow helps compare many runs.

The registry helps manage the model version we choose from those runs.

## MLflow Tracking vs Model Registry

These are related but not the same thing.

```text
MLflow experiment tracking:
  stores params, metrics, runs, artifacts, tags

Model registry:
  stores model version, lifecycle status, lineage, promotion state
```

In this project:

```text
MLflow chooses and records experiment evidence.
champion_run.json records the selected best run.
Local registry turns that selected run into a managed model version.
```

## Lifecycle States

The local registry uses three states:

```text
candidate
champion
archived
```

Meaning:

```text
candidate = model version is registered and available for review
champion  = current selected winner for this project
archived  = older model version that is not current anymore
```

Only one model version should be champion for the same model name.

## What The Registry Stores

Each model version record stores metadata such as:

```text
model_name
model_version
status
mlflow_run_id
candidate_name
model_type
dataset_name
dataset_version
dataset_checksum
metrics
artifact_uri
promotion_reason
created_at
updated_at
```

This gives lineage:

```text
model version
  -> came from this MLflow run
  -> used this dataset version
  -> used this dataset checksum
  -> produced these metrics
  -> points to this model artifact
```

## Where Registry Records Are Stored

Local registry records are stored here:

```text
modelOpsLab/model_registry/
```

Example file:

```text
customer_churn_model__v1-9c8c7bb8.json
```

The file name pattern is:

```text
<model_name>__<model_version>.json
```

These files are local runtime outputs and are not meant to be committed unless we intentionally decide to version sample registry records later.

## How To See The Registry In Action

Run commands from:

```text
modelOpsLab/
```

Activate the virtual environment first:

```powershell
.\vir_env\Scripts\Activate.ps1
```

### 1. Create Or Refresh Champion Run

```powershell
python -m app.run_experiments
```

This creates or refreshes:

```text
reports/champion_run.json
```

Meaning:

```text
the experiment layer selected the best run
```

### 2. Register Champion As Candidate

```powershell
python -m app.register_model
```

This reads:

```text
reports/champion_run.json
```

Then writes a local registry record:

```text
model_registry/<model_name>__<model_version>.json
```

The model status becomes:

```text
candidate
```

### 3. Promote Candidate To Champion

```powershell
python -m app.promote_model
```

This changes the registered candidate to:

```text
champion
```

If another champion already exists for the same model name, the old champion becomes:

```text
archived
```

### 4. Query Registry

```powershell
python -m app.query_model_registry
```

This prints the current registry state:

```text
current champion
all known model versions
status of each version
run id
candidate name
f1 score
```

This is the main command for quickly checking the registry.

## Rollback

Rollback means restoring an older archived model version as champion.

First inspect registry versions:

```powershell
python -m app.query_model_registry
```

Then choose a version with:

```text
status = archived
```

Run rollback:

```powershell
python -m app.rollback_model --model-version <archived-version> --reason "Rollback test"
```

Then query again:

```powershell
python -m app.query_model_registry
```

Expected behavior:

```text
old archived model -> champion
previous champion  -> archived
```

## Rollback Guardrails

Rollback is intentionally strict.

Rules:

```text
only archived versions can be rolled back
rollback reason is required
current champion is archived before rollback version becomes champion
only one active champion should remain
```

This prevents accidental promotion of random or unreviewed model versions.

## Important Files

Core registry logic:

```text
app/model_registry.py
```

Register selected champion run:

```text
app/register_model.py
```

Promote a candidate:

```text
app/promote_model.py
```

Query registry state:

```text
app/query_model_registry.py
```

Rollback to archived version:

```text
app/rollback_model.py
```

Visual flow:

```text
docs/diagrams/v6_model_registry_flow.md
```

Decision records:

```text
docs/decisions/adr_local_model_registry_for_v6.md
docs/decisions/adr_model_registry_rollback_for_v6.md
```

## How This Connects To The Whole Project

The project flow is:

```text
data validation
  -> experiment candidates
  -> MLflow runs
  -> champion selection
  -> champion_run.json
  -> register model candidate
  -> promote champion
  -> query or rollback registry
```

The registry does not train models.

The registry does not compare experiments.

The registry manages the lifecycle of the selected model version.

## What To Commit And What Not To Commit

Commit:

```text
registry code
tests
docs
decision records
learning notes
```

Do not commit local runtime registry outputs:

```text
model_registry/*.json
reports/champion_run.json
mlflow.db
mlruns/
artifacts/
logs/
```

## One-Line Summary

The model registry is our local model lifecycle control layer: MLflow records experiments, `champion_run.json` identifies the selected run, and the registry manages that selected model as candidate, champion, or archived.

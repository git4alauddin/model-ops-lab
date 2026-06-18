# Local Registry And Serving Update

## Purpose
This guide explains the first V10 step that changes actual local serving state.

Before C9, the project created and validated records:

```text
trigger decision
candidate model
comparison report
approval record
promotion record
serving handoff report
```

Those records did not change which model the FastAPI service loaded.

V10-C9 changes that locally.

## What Local Serving Uses
The FastAPI prediction route does not read directly from:

```text
retraining_runs/<run_id>/candidate/model.pkl
```

It uses this flow:

```text
POST /predict
-> model_registry/
-> exactly one champion record
-> champion artifact_uri
-> load model artifact
-> produce prediction
```

Therefore, making a retraining candidate live locally requires a model registry update.

## What C9 Does
C9 performs this controlled local update:

```text
validated serving handoff
-> load and validate candidate model artifact
-> snapshot current champion metadata
-> archive current champion
-> write retraining candidate as new champion
-> run local readiness validation
-> load new champion through the real serving loader
-> run a real prediction smoke test
-> write local serving update report
```

Command:

```powershell
python -m app.update_local_serving_model --run-id <run_id>
```

Output:

```text
retraining_runs/<run_id>/local_serving_update_report.json
```

## Registry Record
The new champion record contains:

```text
model name
new retraining model version
champion status
retraining run ID
candidate model type
dataset lineage
numeric candidate metrics
candidate model artifact path
promotion reason
```

The retraining run ID is stored in the registry metadata as lineage.

## Rollback Protection
C9 snapshots the current champion metadata before mutation.

If readiness or prediction validation fails after the registry change:

```text
remove the failed new champion record
restore the previous champion metadata
leave the retraining run incomplete
raise an error
```

This protects local serving from ending with a broken or missing champion.

## Validation Performed
After the registry update, C9 verifies:

```text
exactly one champion exists
/ready logic reports ready
the expected retraining model version is active
the serving loader can load the candidate artifact
a real prediction succeeds
the prediction response reports the new model version
```

This is stronger than checking that a JSON file was written.

## What Changes
C9 changes:

```text
local model_registry/
local champion selection
the model loaded by the local FastAPI serving process
retraining run metadata
```

## What Does Not Change
C9 does not change:

```text
GitHub Actions deployment
Docker image in Artifact Registry
Cloud Run revision
Cloud Run traffic
remote model artifacts
live cloud prediction behavior
```

Cloud Run remains unchanged because its container image and bundled files are not rebuilt or redeployed by this command.

## How To Verify Manually
After running C9, start the local API:

```powershell
uvicorn app.serve_api:app --reload
```

Check readiness:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ready'
```

The response should show the new retraining model version.

Then call `/predict` with a valid V1 request and confirm:

```text
status = success
model_version = new retraining champion version
```

## Mental Model
Use this distinction:

```text
promotion record = decision
serving handoff = readiness evidence
local registry update = local model becomes active
Cloud Run deployment = cloud model becomes active
```

These are separate stages because they have different risks and rollback procedures.

# Serving Update Handoff

## Purpose
This guide explains the boundary between a V10 promotion decision and an actual serving update.

The short version:

```text
promotion record
!= model registry update
!= serving model update
!= Cloud Run redeploy
```

V10-C8 validates that a promoted retraining run has enough evidence to be handed off to a future serving update step.

## Current Project Serving Behavior
The FastAPI serving layer loads the active model through the local model registry.

The serving flow is:

```text
GET /ready or POST /predict
-> read model_registry/
-> find exactly one champion model
-> resolve champion artifact_uri
-> load model artifact
-> serve prediction
```

A V10 candidate model is different. It is created inside:

```text
retraining_runs/<run_id>/candidate/
```

That candidate is not automatically visible to serving.

## What V10-C8 Validates
The handoff validation checks that the retraining run has:

```text
candidate_promoted status
approved human decision
promotion decision record
candidate model artifact
candidate metrics artifact
comparison report
approval record
promotion record
rollback target
registry_update = not_performed
serving_update = not_performed
```

If these are all present, the run is ready for a future serving update operation.

## What V10-C8 Does Not Do
V10-C8 does not:

```text
copy model artifacts
register a new champion
archive the current champion
change model_registry/
change artifacts/
redeploy Cloud Run
shift traffic
call /ready or /predict
```

This is intentional. It keeps evidence validation separate from production mutation.

## Why This Boundary Matters
Serving updates are higher-risk than metadata updates.

A real serving update may require:

```text
model registry write
artifact availability check
API readiness validation
prediction smoke test
container rebuild
Cloud Run redeploy
traffic migration
rollback plan
```

The handoff report makes sure we do not start that work from an incomplete promotion record.

## Command
Validate a promoted run:

```powershell
python -m app.validate_serving_handoff --run-id <run_id>
```

Output:

```text
retraining_runs/<run_id>/serving_handoff_report.json
```

## How To Read The Result
If the report says:

```text
status = ready
```

then the run has enough local evidence for the next operational step.

If the report says:

```text
status = blocked
```

then at least one required artifact or record is missing.

The report also records:

```text
live_serving_changed = false
model_registry_updated = false
cloud_run_redeployed = false
traffic_changed = false
```

Those fields are there to make the boundary clear for future review.

## Future Serving Update Options
The next implementation can choose one of these paths:

```text
local registry update only
local artifact copy plus registry update
Cloud Run image rebuild and deploy
external model artifact store integration
```

For this project, the safest next learning step is usually:

```text
promoted candidate
-> validate serving handoff
-> register or map candidate as new local champion
-> validate /ready locally
-> validate /predict locally
-> only then discuss Cloud Run deployment
```

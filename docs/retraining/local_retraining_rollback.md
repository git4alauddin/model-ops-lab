# Local Retraining Rollback

## Purpose
This guide explains how ModelOpsLab restores the previous local champion after a V10 retraining model has become active.

Rollback is not:

```text
change one status field
```

Rollback is:

```text
restore the known-good champion
archive the retraining champion
load the restored model
validate readiness
run a prediction
record evidence
```

## Rollback Source
The rollback target is captured before candidate promotion:

```text
promotion.rollback_target.model_name
promotion.rollback_target.model_version
promotion.rollback_target.artifact_uri
```

For the first V10 walkthrough, the target is:

```text
v1-7ab8f00a
```

The rollback command does not ask the operator to invent a target. It uses the target already recorded in the governed retraining run.

## Command

```powershell
python -m app.rollback_local_retraining_model --run-id <run_id> --reason "<reason>" --rolled-back-by <name>
```

Output:

```text
retraining_runs/<run_id>/local_serving_rollback_report.json
```

## Preconditions
Rollback requires:

```text
candidate_local_serving_updated status
recorded rollback target
rollback target exists in model_registry/
rollback target is archived
rollback target artifact URI matches registry metadata
exactly one current champion
current champion matches the retraining champion recorded by C9
```

These checks prevent an old retraining run from rolling back an unrelated current champion.

## Rollback Flow

```text
load retraining metadata
-> validate rollback target
-> snapshot all registry metadata
-> archive retraining champion
-> restore target as champion
-> validate /ready logic
-> load restored champion
-> run prediction smoke test
-> write rollback report
-> update retraining metadata
```

## Rollback Failure Protection
Rollback can fail after the registry has changed.

For example:

```text
restored artifact is missing
restored model cannot load
readiness reports the wrong version
prediction fails
```

If that happens, C10 restores the entire registry metadata snapshot from before the rollback attempt.

The result is:

```text
retraining champion becomes champion again
rollback target returns to archived
failed rollback raises an error
```

This prevents a failed rollback from leaving local serving in an unknown state.

## Validation Evidence
The rollback report records:

```text
restored champion
archived retraining champion
rollback reason
operator
timestamp
readiness response
prediction response
Cloud Run boundary
```

The prediction response must report the restored model version.

## What Changes

```text
local model registry champion
local FastAPI model selection
retraining run status
local rollback evidence
```

## What Does Not Change

```text
Artifact Registry image
Cloud Run revision
Cloud Run traffic
cloud prediction behavior
GitHub Actions deployment
```

Cloud Run remains unchanged because C10 is a local registry rollback only.

## Mental Model

```text
rollback target recorded before promotion
-> retraining model becomes local champion
-> incident or validation concern occurs
-> rollback restores previous champion
-> readiness and prediction prove restoration
```

A rollback is complete only after the restored model has been validated.

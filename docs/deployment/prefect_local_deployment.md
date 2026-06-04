# Prefect Local Deployment Scaffold

This guide explains the local Prefect deployment scaffold added in V5-C10.

The normal local command still remains:

```powershell
python -m app.run_prefect_pipeline
```

The deployment scaffold is for learning and future scheduling. It should not replace the direct local command while V5 is still being stabilized.

## What The Scaffold Adds

The project now has:

```text
prefect.yaml
```

This file defines one deployment:

```text
local-training-pipeline
```

It points to the current Prefect flow:

```text
app/orchestration/prefect_pipeline.py:training_pipeline_flow
```

The deployment uses:

```text
work pool : modelopslab-local-process-pool
queue     : default
schedule  : daily-local-training
timezone  : Asia/Kolkata
active    : false
```

The schedule is intentionally inactive by default. This prevents accidental scheduled training runs while we are still learning and building locally.

## Concepts

`prefect.yaml` is the version-controlled deployment definition.

A deployment is a registered way to run a Prefect flow later, manually or on a schedule.

A work pool tells Prefect where the flow run should execute. For local learning, a process work pool is the simplest option.

A worker is the local process that polls the work pool and actually runs scheduled or triggered flow runs.

A schedule belongs to a deployment. If the schedule is inactive, it is visible but does not create automatic runs.

## One-Time Local Setup

Run these from `modelOpsLab/` after activating the virtual environment.

```powershell
.\vir_env\Scripts\Activate.ps1
prefect server start
```

Open the UI shown by Prefect, usually:

```text
http://127.0.0.1:4200
```

In another terminal:

```powershell
.\vir_env\Scripts\Activate.ps1
prefect work-pool create modelopslab-local-process-pool --type process
prefect deploy --name local-training-pipeline --no-prompt
```

Start a worker when you want deployment-triggered runs to execute:

```powershell
prefect worker start --pool modelopslab-local-process-pool
```

## GUI Flow

Use the UI when possible for learning:

1. Open the Prefect UI.
2. Go to Work Pools.
3. Confirm `modelopslab-local-process-pool` exists.
4. Go to Deployments.
5. Open `modelopslab-training-pipeline/local-training-pipeline`.
6. Confirm the schedule exists and is inactive.
7. Use Run to trigger a manual deployment run.
8. Watch the flow run logs and task state transitions.

## CLI Checks

List deployments:

```powershell
prefect deployment ls
```

Inspect this deployment:

```powershell
prefect deployment inspect modelopslab-training-pipeline/local-training-pipeline
```

Trigger one deployment run manually:

```powershell
prefect deployment run modelopslab-training-pipeline/local-training-pipeline
```

List schedules:

```powershell
prefect deployment schedule ls modelopslab-training-pipeline/local-training-pipeline
```

## Guardrails

Do not turn on the schedule until the local worker setup is understood.

Do not remove the direct command path:

```powershell
python -m app.run_prefect_pipeline
```

Do not make tests depend on a running Prefect server or worker.

Do not commit generated runtime state from `pipeline_runs/`, `logs/`, `mlruns/`, or `mlflow.db`.

# Prefect Learning Notes

This is a reference note for understanding Prefect while building ModelOpsLab. It is not a project status document.

## What Prefect Is

Prefect is a workflow orchestration tool.

It does not train the model by itself. Our Python pipeline still does the real work:

```text
validate data
run experiment candidates
create MLflow runs
select champion
write pipeline metadata
```

Prefect coordinates that work and tracks the workflow execution.

Prefect helps answer:

```text
Which workflow ran?
Which task ran?
Did the workflow pass or fail?
Where did it fail?
How long did it take?
What parameters were used?
Can this later be scheduled or deployed?
```

## What Does The Work

The real project work happens in our Python code.

In this project, the plain pipeline command is:

```powershell
python -m app.run_training_pipeline
```

That command controls the actual workflow:

```text
create pipeline metadata
run validation once
run experiment workflow
create MLflow candidate runs
select champion
write pipeline_runs/<pipeline_run_id>.json
```

Prefect orchestrates the same pipeline stages through:

```powershell
python -m app.run_prefect_pipeline
```

Clean mental model:

```text
app.run_training_pipeline = does the workflow work
Prefect                   = orchestrates and observes the workflow stages
MLflow                    = tracks model experiment runs
pipeline_runs/            = stores workflow-level metadata
```

## Core Prefect Concepts

## Prefect Component Glossary

This is the short mental model for the main Prefect pieces.

### Flow

A flow is the full workflow definition.

In our project:

```text
modelopslab-training-pipeline
```

It defines the order of the pipeline stages.

### Flow Run

A flow run is one execution of a flow.

If the flow runs five times, Prefect records five flow runs.

Each flow run has a state:

```text
Scheduled
Running
Completed
Failed
Cancelled
```

### Task

A task is one tracked step inside a flow.

In our project:

```text
initialize-pipeline-run
validation-stage
experiment-stage
finalize-pipeline-run
```

Tasks make the flow easier to inspect because the UI can show which stage ran, failed, or retried.

### Task Run

A task run is one execution of a task inside one flow run.

Example:

```text
Flow run: pipeline attempt 1
  Task run: initialize-pipeline-run
  Task run: validation-stage
  Task run: experiment-stage
  Task run: finalize-pipeline-run
```

### Deployment

A deployment is a registered version of a flow.

It tells Prefect:

```text
which flow to run
where the flow code lives
what default parameters to use
which work pool should execute it
whether a schedule exists
```

In our project:

```text
modelopslab-training-pipeline/local-training-pipeline
```

Deployment is what lets us trigger a flow from the UI or CLI without manually running the Python module.

### Work Pool

A work pool is a queue/target for work.

It answers:

```text
Where should Prefect send deployment-created flow runs?
```

In our project:

```text
modelopslab-local-process-pool
```

For local learning, this is a process work pool, meaning runs execute as local processes.

### Work Queue

A work queue is a subdivision inside a work pool.

In our project:

```text
default
```

We keep one queue because this is a local learning setup.

### Worker

A worker is the running process that polls the work pool and executes flow runs.

Mental model:

```text
Prefect server says: there is a run waiting
worker sees it
worker starts the flow run locally
```

Command:

```powershell
prefect worker start --pool modelopslab-local-process-pool
```

If no worker is running, deployment-triggered runs can be created but will not execute.

### Schedule

A schedule tells Prefect to create flow runs automatically.

In our project, the schedule exists but is inactive:

```text
daily-local-training
active: false
```

This prevents accidental automatic training runs.

### Parameters

Parameters are inputs passed to the flow.

In our project:

```text
config_path: configs/training.yaml
```

This tells the flow which training config to use.

### Work Pool vs Worker

These are easy to confuse.

```text
work pool = where work is queued
worker    = process that picks up work and runs it
```

Analogy:

```text
work pool = job board
worker    = person watching the board and doing the job
```

### Deployment vs Flow

These are also easy to confuse.

```text
flow       = Python workflow definition
deployment = registered runnable version of that flow
```

Analogy:

```text
flow       = recipe
deployment = saved menu item that can be ordered
flow run   = one prepared meal
```

### Flow

A flow is the main workflow.

In code, a flow is a Python function decorated with:

```python
@flow
```

In this project, the main flow is:

```text
training_pipeline_flow
```

Location:

```text
modelOpsLab/app/orchestration/prefect_pipeline.py
```

Our flow name is:

```text
modelopslab-training-pipeline
```

A flow can:

```text
accept parameters
call tasks
track workflow state
return results
be deployed later
be scheduled later
```

### Flow Run

A flow run is one execution of a flow.

Every time this command runs:

```powershell
python -m app.run_prefect_pipeline
```

Prefect creates a flow run.

A flow run has state such as:

```text
Scheduled
Running
Completed
Failed
Cancelled
```

For now, we run flows locally, not as scheduled deployments.

### Task

A task is a smaller unit of work inside a flow.

In code, a task is a Python function decorated with:

```python
@task
```

In this project, the current Prefect tasks are:

```text
initialize_pipeline_run_task
validation_stage_task
experiment_stage_task
finalize_pipeline_run_task
```

Location:

```text
modelOpsLab/app/orchestration/prefect_pipeline.py
```

These tasks reuse the same stage helpers and metadata helpers used by the plain pipeline path.

### Task Run

A task run is one execution of a task.

In our current setup:

```text
flow run
  -> initialize task run
  -> validation task run
  -> experiment task run
  -> finalization task run
```

Important retry decision:

```text
validation task  = has small retry policy
experiment task  = no retry
```

The experiment task does not retry because retrying model candidates can create duplicate MLflow runs.

## Why We Added Prefect After The Plain Pipeline

We intentionally did not start with Prefect first.

Order matters:

```text
1. Build a working plain Python pipeline.
2. Prove validation, experiments, champion selection, and metadata work.
3. Wrap that proven behavior with Prefect.
4. Split into smaller Prefect tasks after the stage helpers were stable.
```

This avoids this bad pattern:

```text
new tool + new pipeline logic + new failures all at once
```

Current good pattern:

```text
stable pipeline logic + stage-level Prefect wrapper
```

## Current Project Flow

Command:

```powershell
python -m app.run_prefect_pipeline
```

Flow:

```text
app.run_prefect_pipeline
  -> training_pipeline_flow
  -> initialize_pipeline_run_task
  -> validation_stage_task
  -> experiment_stage_task
  -> finalize_pipeline_run_task
  -> MLflow candidate runs
  -> champion selection
  -> pipeline metadata persistence
```

Important files:

```text
app/run_prefect_pipeline.py
app/orchestration/prefect_pipeline.py
app/run_training_pipeline.py
app/run_experiments.py
app/pipeline_run_metadata.py
```

## What Prefect Adds In Our Project

Prefect currently adds:

```text
flow wrapper
stage-level task wrapper
flow run state
task run state
local orchestration logs
validation retry policy
future path to active scheduling
deployment scaffold
```

Prefect does not currently add:

```text
scheduled jobs
remote worker
cloud deployment
production server
```

The deployment scaffold exists, but its schedule is inactive by default.

## What Happened During The First Prefect Run

When we ran:

```powershell
python -m app.run_prefect_pipeline
```

Prefect printed lines like:

```text
Starting temporary server
Beginning flow run
Finished task run
Finished flow run
Stopping temporary server
```

Meaning:

```text
Prefect started local orchestration services temporarily.
It ran the flow locally.
It ran each stage task locally.
It completed successfully.
Then it stopped the temporary server.
```

This is normal for local Prefect runs.

It does not mean we created a permanent production server.

## Temporary Server vs Deployment

This distinction is important.

### Temporary Local Server

This happens during local execution.

```text
python -m app.run_prefect_pipeline
```

Prefect may start a temporary server so it can track the local flow run.

Meaning:

```text
local process
short lived
for development/testing
not a scheduled service
```

### Deployment

A deployment is a configured, runnable version of a flow that can be scheduled or triggered.

We added a local deployment scaffold in:

```text
prefect.yaml
```

The schedule exists but is inactive by default.

Deployment would involve concepts like:

```text
work pool
worker
schedule
deployment config
flow serving or remote execution
```

So current state is:

```text
Prefect local flow: yes
Prefect deployment scaffold: yes
Prefect active schedule: no
```

## Direct Flow Run vs Deployment Run

There are two ways to trigger the same flow.

### Direct Local Flow Run

This is the command we use for normal development:

```powershell
python -m app.run_prefect_pipeline
```

Mental model:

```text
you run command
  -> Python starts the Prefect flow now
  -> Prefect may start a temporary local server
  -> tasks run in the same local execution path
  -> temporary server stops
```

This does not require:

```text
registered deployment
running worker
active schedule
manual UI trigger
```

Use this when we simply want to test the pipeline locally.

### Deployment Run

A deployment run means Prefect already knows about a registered version of the flow.

Mental model:

```text
prefect.yaml
  -> registers flow as a deployment
  -> Prefect server stores that deployment
  -> worker listens to a work pool
  -> UI, CLI, API, or schedule creates a flow run
  -> worker executes the run
```

This is useful for learning real orchestration behavior:

```text
trigger from UI
trigger from CLI
inspect deployments
inspect work pools
watch workers pick up runs
later enable schedules
```

In this project, the deployment is:

```text
modelopslab-training-pipeline/local-training-pipeline
```

It is defined in:

```text
prefect.yaml
```

## What Deployment Behavior Means

Deployment behavior does not mean Prefect trains the model differently.

The same flow runs:

```text
modelopslab-training-pipeline
```

The same tasks run:

```text
initialize-pipeline-run
validation-stage
experiment-stage
finalize-pipeline-run
```

The difference is how the run is triggered and managed.

```text
Direct run:
you start it directly from Python

Deployment run:
Prefect stores the flow definition, then a worker runs it when triggered
```

Deployment adds operational concepts:

```text
server
UI
deployment
work pool
worker
manual run trigger
optional schedule
```

This is closer to real workflow orchestration.

## Running From The Prefect UI

To run from the UI, use three terminals.

Run all commands from:

```text
modelOpsLab/
```

### Terminal 1: Start Prefect Server

```powershell
.\vir_env\Scripts\Activate.ps1
prefect server start
```

Open:

```text
http://127.0.0.1:4200
```

Keep this terminal running.

### Terminal 2: Register Deployment

```powershell
.\vir_env\Scripts\Activate.ps1
prefect work-pool create modelopslab-local-process-pool --type process
prefect deploy --name local-training-pipeline --no-prompt
```

If the work pool already exists, that is not a problem. Continue.

### Terminal 3: Start Worker

```powershell
.\vir_env\Scripts\Activate.ps1
prefect worker start --pool modelopslab-local-process-pool
```

Keep this terminal running.

### UI Steps

In the Prefect UI:

```text
Deployments
  -> modelopslab-training-pipeline/local-training-pipeline
  -> Run
```

Then inspect:

```text
Flow Runs
  -> latest run
  -> task states
  -> logs
```

You should see:

```text
initialize-pipeline-run
validation-stage
experiment-stage
finalize-pipeline-run
```

## Why The Schedule Is Inactive

The schedule exists in `prefect.yaml`, but it is inactive.

This is intentional.

If the schedule is active, Prefect can create automatic runs whenever the schedule says so.

That can create real local outputs:

```text
pipeline_runs/*.json
MLflow runs
mlruns/
mlflow.db changes
logs/modelopslab.log
reports/champion_run.json
artifacts/
```

We keep the schedule inactive so we can learn deployment behavior manually first.

Safe order:

```text
1. direct local run
2. manual UI deployment run
3. manual CLI deployment run
4. active schedule later, only when intended
```

## Common Commands For Deployment Learning

List deployments:

```powershell
prefect deployment ls
```

Inspect deployment:

```powershell
prefect deployment inspect modelopslab-training-pipeline/local-training-pipeline
```

Trigger a deployment run from CLI:

```powershell
prefect deployment run modelopslab-training-pipeline/local-training-pipeline
```

Start a worker:

```powershell
prefect worker start --pool modelopslab-local-process-pool
```

List deployment schedules:

```powershell
prefect deployment schedule ls modelopslab-training-pipeline/local-training-pipeline
```

## Inspecting Local Outputs After A UI Run

Even when a run is triggered from the Prefect UI, the project still writes local runtime outputs.

The most important one is:

```text
pipeline_runs/<pipeline_run_id>.json
```

To get the latest pipeline metadata file from PowerShell:

```powershell
Get-ChildItem pipeline_runs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

To open the latest pipeline metadata JSON:

```powershell
Get-Content (Get-ChildItem pipeline_runs | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

Useful fields to check:

```text
pipeline_run_id
pipeline_version
status
stage_statuses
failed_stage
dataset_version
mlflow_run_ids
champion_run_id
```

A successful UI-triggered run should still show:

```text
status = passed
stage_statuses.validation = passed
stage_statuses.experiments = passed
champion_run_id = <some MLflow run id>
```

## Prefect vs MLflow

Prefect and MLflow solve different problems.

```text
Prefect = workflow orchestration
MLflow  = experiment tracking
```

Prefect answers:

```text
Did the pipeline run?
Which stage ran?
Did the workflow fail?
Can this be retried or scheduled later?
```

MLflow answers:

```text
Which model run happened?
What params were used?
What metrics were produced?
Which model is champion?
What artifacts belong to a run?
```

Clean mental model:

```text
Prefect watches the workflow.
MLflow watches the model experiments.
```

## Prefect vs pipeline_runs

Prefect tracks orchestration state.

Our `pipeline_runs/` folder stores our own project-level workflow metadata.

Example:

```text
pipeline_runs/<pipeline_run_id>.json
```

This includes:

```text
pipeline_run_id
pipeline_version
status
stage_statuses
failed_stage
dataset_version
mlflow_run_ids
champion_run_id
```

Why keep this if Prefect tracks state?

Because `pipeline_runs/` is our project contract.

It is:

```text
simple JSON
repo-specific
independent of Prefect internals
easy to inspect
easy to test
stable even if orchestration tool changes later
```

Clean mental model:

```text
Prefect state = orchestration tool state
pipeline_runs = our project workflow record
```

## Where Things Are Stored

### Project Code

```text
app/orchestration/prefect_pipeline.py
app/run_prefect_pipeline.py
prefect.yaml
```

### Project Pipeline Metadata

```text
pipeline_runs/<pipeline_run_id>.json
```

### MLflow Tracking Data

```text
mlflow.db
mlruns/
```

### Logs

```text
logs/modelopslab.log
```

### Prefect Local State

Prefect may use local profile/server state outside the repo or a temporary local server during execution.

We do not commit Prefect runtime state.

## Commands

Install or update dependencies:

```powershell
python -m pip install -r requirements.txt
```

Check Prefect version:

```powershell
prefect version
```

Run plain Python pipeline:

```powershell
python -m app.run_training_pipeline
```

Run Prefect pipeline:

```powershell
python -m app.run_prefect_pipeline
```

Run focused Prefect tests:

```powershell
python -m pytest -q tests/test_v5_c6_prefect_orchestration.py tests/test_v5_c11_prefect_stage_tasks.py
```

## Which File To Read First

For understanding, read in this order:

```text
1. docs/diagrams/v5_training_pipeline_flow.md
2. app/run_prefect_pipeline.py
3. app/orchestration/prefect_pipeline.py
4. app/run_training_pipeline.py
5. app/run_experiments.py
6. app/pipeline_run_metadata.py
```

## What To Commit And What Not To Commit

Commit:

```text
requirements.txt
app/orchestration/prefect_pipeline.py
app/run_prefect_pipeline.py
prefect.yaml
tests/test_v5_c6_prefect_orchestration.py
tests/test_v5_c11_prefect_stage_tasks.py
docs updates
```

Do not commit runtime outputs:

```text
pipeline_runs/*.json
logs/
mlflow.db
mlruns/
artifacts/*.json
artifacts/*.pkl
```

## One-Line Summary

Prefect is our workflow coordinator: it runs and observes the pipeline, while our Python code performs the work, MLflow tracks model experiments, and `pipeline_runs/` stores our project-level workflow record.

## References

Official Prefect references used for these notes:

```text
https://docs.prefect.io/v3/concepts/flows
https://docs.prefect.io/v3/concepts/tasks
https://docs.prefect.io/latest/getting-started/installation/
```

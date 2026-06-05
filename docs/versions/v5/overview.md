# V5 Overview

## Version Goal
Add training pipeline automation and workflow orchestration foundations.

V5 moves the project from manually executed training scripts toward reproducible, dependency-aware ML workflows.

## Completion Status
V5 is in progress.

Implemented chunks:
- V5-C1: orchestration foundation and documentation scaffold.
- V5-C2: pipeline run metadata contract and persistence helper.
- V5-C3: plain Python training pipeline entrypoint.
- V5-C4: single validation ownership for the training pipeline.
- V5-C5: training pipeline flow diagram.
- V5-C6: local Prefect orchestration wrapper.
- V5-C7: Prefect task retry policy.
- V5-C8: Prefect failure context visibility.
- V5-C9: pipeline stage task helpers.
- V5-C10: Prefect local deployment scaffold.
- V5-C11: stage-level Prefect tasks.

## Components Introduced
- V5 documentation scaffold
- pipeline run output folder
- orchestration decision record
- V5 status in README
- pipeline run metadata helper
- focused pipeline metadata tests
- plain Python pipeline command
- pipeline-level metadata persistence during real runtime execution
- reusable experiment workflow with optional validation
- V5 training pipeline flow diagram
- Prefect dependency
- local Prefect flow and stage-level task wrapper
- Prefect pipeline command
- Prefect retry policy for the validation task
- failure context propagation from pipeline metadata into Prefect command errors
- validation and experiment stage helper modules
- version-controlled Prefect deployment scaffold with inactive schedule

## Workflow To Introduce
V5 will move toward this workflow:

```text
pipeline command
  -> validation stage
  -> multi-model experiment stage
  -> champion report read
  -> pipeline metadata persistence
```

## Engineering Objectives
- isolate pipeline stages
- make pipeline dependencies explicit
- preserve existing `app.train` and `app.run_experiments` behavior while adding orchestration
- persist pipeline-level metadata
- support failure propagation across stages
- make failed Prefect-wrapped runs easy to inspect from their pipeline run ID
- prepare for retry behavior and future scheduling

## Operational Objectives
- run the full training workflow from one controlled pipeline command
- make stage order clear
- make failed stages traceable
- make pipeline runs reproducible
- create a foundation for future retraining automation

## Current V5 Outcome
V5 has the architecture direction, output structure, metadata contract, plain Python pipeline command, local Prefect stage-level wrapper, validation retry policy, Prefect failure context visibility, extracted validation/experiment stage helpers, and a local Prefect deployment scaffold. The pipeline owns validation once and then runs experiments without duplicate validation. The deployment schedule is intentionally inactive by default.

For the V5 training pipeline diagram, see `docs/diagrams/v5_training_pipeline_flow.md`.

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

## Components Introduced
- V5 documentation scaffold
- pipeline run output folder
- orchestration decision record
- V5 status in README
- pipeline run metadata helper
- focused pipeline metadata tests
- plain Python pipeline command
- pipeline-level metadata persistence during real runtime execution

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
- prepare for retry behavior and future scheduling

## Operational Objectives
- run the full training workflow from one controlled pipeline command
- make stage order clear
- make failed stages traceable
- make pipeline runs reproducible
- create a foundation for future retraining automation

## Current V5 Outcome
V5 has the architecture direction, output structure, metadata contract, and first plain Python pipeline command. Prefect orchestration is intentionally not added yet.

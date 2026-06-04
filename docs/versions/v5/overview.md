# V5 Overview

## Version Goal
Add training pipeline automation and workflow orchestration foundations.

V5 moves the project from manually executed training scripts toward reproducible, dependency-aware ML workflows.

## Completion Status
V5 is in progress.

Implemented chunks:
- V5-C1: orchestration foundation and documentation scaffold.
- V5-C2: pipeline run metadata contract and persistence helper.

## Components Introduced
- V5 documentation scaffold
- pipeline run output folder
- orchestration decision record
- V5 status in README
- pipeline run metadata helper
- focused pipeline metadata tests

## Workflow To Introduce
V5 will move toward this workflow:

```text
pipeline command
  -> validation stage
  -> dataset/version context stage
  -> training stage
  -> evaluation stage
  -> artifact persistence stage
  -> experiment logging stage
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
V5 has the architecture direction, output structure, and metadata contract for pipeline orchestration. Runtime orchestration code is intentionally not added yet.

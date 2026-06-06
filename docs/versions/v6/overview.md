# V6 Overview

## Version Goal
Add model registry and promotion lifecycle foundations.

V6 moves the project from selecting a champion run to managing model versions with explicit lifecycle states.

## Completion Status
V6 is complete.

Implemented chunks:
- V6-C1: model registry foundation and decision record.
- V6-C2: model registry metadata contract.
- V6-C3: model registry metadata persistence.
- V6-C4: model registration command.
- V6-C5: champion promotion command.
- V6-C6: single champion enforcement.
- V6-C7: model registry query command.
- V6-C8: model registry flow diagram.
- V6-C9: rollback guardrails decision record.
- V6-C10: model rollback command.
- V6-C11: model registry version closure.

## Components To Introduce
- V6 documentation scaffold
- model registry decision record
- model version metadata contract
- local registry folder placeholder
- local registry JSON persistence
- model registration command
- champion promotion command
- single champion enforcement
- model registry query command
- model registry flow diagram
- rollback guardrails
- rollback command
- V6 closure checks
- promotion lifecycle states
- registry output location
- archived model handling

## Registry Lifecycle
Initial lifecycle states:

```text
candidate
champion
archived
```

Meaning:

```text
candidate = model version was produced by an experiment and can be reviewed
champion  = currently selected production-style winner for this local project
archived  = previously useful model version that is no longer current
```

## Engineering Objectives
- separate model version records from experiment tracking records
- preserve MLflow run IDs as lineage references
- preserve dataset version and checksum lineage
- make champion promotion explicit
- avoid replacing MLflow tracking too early
- keep the registry inspectable as local project metadata

## Operational Objectives
- know which model version is current champion
- know which MLflow run produced a registered model
- know which dataset version produced a model
- support manual promotion before automated promotion
- create a foundation for future serving and deployment

## Current V6 Direction
V6 starts with a local project registry first.

MLflow remains the experiment tracking system. The local registry will store project-level model version and promotion records that are easy to inspect, test, and evolve. Direct MLflow Model Registry integration can be revisited after the local registry contract is stable.

## Closure Summary
V6 closes with a local, file-based model registry lifecycle:

```text
champion report
-> registered candidate
-> promoted champion
-> previous champion archived
-> registry query inspection
-> archived model rollback to champion
```

The registry remains local project metadata. It does not replace MLflow experiment tracking.

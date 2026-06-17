# V10 Overview

## Version Goal
Add governed retraining automation, production evolution safeguards, and portfolio-grade project packaging.

V10 moves ModelOpsLab from an observable ML service to a continuously managed ML lifecycle system.

## Completion Status
V10 is in progress.

Implemented chunks:
- V10-C1: retraining governance foundation.
- V10-C2: local retraining trigger decision.
- V10-C3: candidate retraining run metadata.
- V10-C4: candidate retraining command.
- V10-C5: candidate-vs-production comparison report.

## Final Definition
V10 is a production-style continuous ML lifecycle management layer with governed retraining workflows, drift-triggered automation, regression protection, deployment safeguards, architecture documentation, and portfolio-grade operational ML system presentation.

## Why V10 Exists
V9 made the system observable through prediction telemetry, monitoring summaries, drift checks, alert-ready outputs, and dashboard-ready data.

The next production question is:

```text
How does the system evolve safely after drift or model staleness is detected?
```

Without V10, monitoring can detect problems but the response still stays mostly manual:

```text
model staleness
drift without remediation
manual retraining
blind candidate promotion
missing retraining lineage
weak rollback story
incomplete portfolio presentation
```

## Components To Introduce
- scheduled retraining workflow
- drift-triggered retraining decision
- candidate model evaluation
- production model comparison
- regression protection gates
- human approval workflow
- retraining metadata and lineage
- promotion decision records
- rollback support
- architecture and portfolio packaging

## Retraining Governance Boundary
V10 should not start with blind automatic promotion.

The first safe retraining lifecycle is:

```text
monitoring signal
-> retraining trigger decision
-> candidate model training
-> evaluation and regression checks
-> human approval
-> production promotion or rejection
-> metadata and rollback record
```

This keeps retraining useful without allowing a worse model to overwrite the production model automatically.

## Recommended V10 Direction
V10 starts with retraining governance before automation.

The first practical implementation layers should be:

```text
retraining governance documentation
local retraining trigger decision from V9 reports
candidate retraining run metadata
candidate retraining command
candidate-vs-production comparison report
promotion gate
approval record
portfolio packaging docs
```

This order keeps the project teachable and prevents retraining automation from becoming unsafe.

## Out Of Scope For V10-C1
V10-C1 does not schedule jobs, run retraining, promote models, change production artifacts, install Airflow, or add new cloud infrastructure.

Those belong in later V10 chunks after the retraining governance contract is documented.

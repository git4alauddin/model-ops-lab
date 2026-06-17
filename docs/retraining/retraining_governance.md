# Retraining Governance

## Purpose
Retraining governance defines how ModelOpsLab should decide when to retrain, how to judge a candidate model, and when a model is safe to promote.

The goal is controlled continuous learning, not blind automatic retraining.

## Why Governance Is Needed
V9 can detect monitoring and drift signals, but detection alone does not safely update production.

Unsafe retraining can introduce:

```text
candidate model regressions
latency increases
schema incompatibility
temporary drift overreaction
feedback loop corruption
accidental production overwrite
missing rollback context
```

## Governed Retraining Lifecycle
The expected V10 retraining flow is:

```text
monitoring signal
-> retraining trigger decision
-> candidate model training
-> validation checks
-> candidate-vs-production comparison
-> regression protection gates
-> human approval
-> production promotion or rejection
-> retraining metadata persistence
-> rollback-ready production record
```

## Retraining Triggers
Retraining can be considered when one or more signals appear:

```text
scheduled retraining window
data drift detected
prediction distribution anomaly
high failure rate caused by model behavior
new labeled dataset available
manual operator request
```

The first implementation should treat these as decision inputs, not automatic promotion commands.

## Candidate Model Evaluation
Every candidate model should be compared against the current production model.

Candidate evaluation should include:

```text
accuracy
precision
recall
F1
latency
calibration
schema compatibility
prediction distribution stability
```

The production model remains the baseline until a candidate passes the promotion gate.

## Regression Protection
Promotion should be blocked when a candidate creates unacceptable regression.

Example gate categories:

```text
recall drop beyond allowed tolerance
F1 drop beyond allowed tolerance
latency increase beyond allowed tolerance
schema validation failure
missing evaluation metrics
missing retraining metadata
unstable prediction distribution
```

Higher accuracy alone is not enough to promote a model.

## Approval Workflow
The first safe approval workflow is human-in-the-loop:

```text
candidate trained
-> comparison report generated
-> promotion recommendation recorded
-> human approves or rejects
-> production artifact changes only after approval
```

Automatic promotion can be considered later only after the local approval and rollback process is reliable.

## Retraining Metadata
Each retraining run should persist enough context to reproduce the decision later.

Required metadata:

```text
run ID
trigger reason
trigger source report
dataset version
schema version
previous production model
candidate model path
comparison metrics
regression gate results
promotion recommendation
approval decision
rollback target
created timestamp
```

Recommended local destination:

```text
retraining_runs/
```

## Rollback Boundary
Promotion should always preserve the previous production model reference.

Rollback support should answer:

```text
Which model was active before promotion?
Why was the candidate promoted?
Which artifacts are needed to restore the previous model?
Which monitoring signal led to retraining?
```

## Portfolio Packaging Boundary
V10 also prepares the project for professional presentation.

Portfolio packaging should include:

```text
architecture overview
training workflow
serving workflow
deployment workflow
monitoring and drift workflow
retraining workflow
trade-off documentation
screenshots and validation evidence
resume-ready project summary
```

The README should read like a production engineering case study, not a tutorial checklist.

## V10-C1 Boundary
This document defines the governance contract only.

It does not schedule retraining, run retraining, promote models, install Airflow, or change production model artifacts.

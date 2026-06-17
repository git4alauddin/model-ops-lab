# V10 Issues Faced

## V10-C1: Retraining Governance Foundation

No implementation issue yet.

The main design risk is unsafe automation. A retraining system can damage production behavior if it automatically promotes a candidate model based only on one metric or one drift signal.

V10 starts with governance so later automation has clear triggers, checks, approval boundaries, metadata, and rollback expectations.

## V10-C2: Local Retraining Trigger Decision

No retraining job was added.

The main design choice was separating retraining recommendation from retraining execution. A drift alert can justify a candidate retraining run, but it should not automatically train or promote a model.

The decision report also treats insufficient telemetry as a blocker because retraining from unreliable monitoring data would create a false sense of automation maturity.

## V10-C3: Candidate Retraining Run Metadata

No training job was added yet.

The main design choice was making the candidate run initializer strict. It only starts when the trigger decision is `retraining_recommended`, because initializing retraining from a clean or insufficient signal would weaken the governance story.

The metadata also stores the current champion model as rollback context. That keeps the next steps safer because candidate evaluation and promotion can always answer what production model existed before the candidate run started.

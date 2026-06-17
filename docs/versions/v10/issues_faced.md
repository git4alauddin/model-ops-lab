# V10 Issues Faced

## V10-C1: Retraining Governance Foundation

No implementation issue yet.

The main design risk is unsafe automation. A retraining system can damage production behavior if it automatically promotes a candidate model based only on one metric or one drift signal.

V10 starts with governance so later automation has clear triggers, checks, approval boundaries, metadata, and rollback expectations.

## V10-C2: Local Retraining Trigger Decision

No retraining job was added.

The main design choice was separating retraining recommendation from retraining execution. A drift alert can justify a candidate retraining run, but it should not automatically train or promote a model.

The decision report also treats insufficient telemetry as a blocker because retraining from unreliable monitoring data would create a false sense of automation maturity.

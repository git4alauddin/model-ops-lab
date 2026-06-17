# V10 Issues Faced

## V10-C1: Retraining Governance Foundation

No implementation issue yet.

The main design risk is unsafe automation. A retraining system can damage production behavior if it automatically promotes a candidate model based only on one metric or one drift signal.

V10 starts with governance so later automation has clear triggers, checks, approval boundaries, metadata, and rollback expectations.

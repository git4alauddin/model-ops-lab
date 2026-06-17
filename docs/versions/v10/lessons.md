# V10 Lessons

## V10-C1: Retraining Governance Foundation

- Retraining should be governed because a fresh model is not automatically a better production model.
- Drift detection becomes more valuable when it can trigger a controlled retraining decision.
- Candidate models must be compared against the current production model before promotion.
- Regression protection should include ML metrics, latency, schema compatibility, and operational stability.
- Human approval is the safest first production maturity step before automatic promotion.
- Retraining metadata makes future debugging, audits, rollback, and portfolio storytelling possible.
- Portfolio packaging should explain engineering decisions, not only list tools.

## V10-C2: Local Retraining Trigger Decision

- Trigger decisions connect monitoring to retraining without starting unsafe automation.
- A retraining signal and a retraining command are different things.
- Drift and prediction failures can recommend retraining, but missing telemetry should block the decision until data is trustworthy.
- A decision report should explain why retraining is recommended, not only output a boolean.
- Source freshness matters because stale monitoring reports can lead to bad retraining decisions.

## V10-C3: Candidate Retraining Run Metadata

- Candidate run metadata is the handoff between a retraining recommendation and actual training.
- Starting a retraining run should create an audit record before changing any model artifacts.
- The trigger reason, source reports, dataset version, schema version, and current production model belong in the same retraining record.
- Capturing the previous production model early creates rollback context before promotion decisions are made.
- Pending candidate paths are useful because they show the lifecycle stage clearly: initialized, trained, compared, approved, then promoted or rejected.
- A governed retraining run can exist without automatic promotion; this is safer and easier to explain in a production review.

## V10-C4: Candidate Retraining Command

- Candidate training is still not promotion.
- The safest first retraining automation trains into an isolated run folder instead of overwriting production artifacts.
- The retraining metadata file becomes the lifecycle control record: initialized first, then trained, then later compared, approved, and promoted or rejected.
- Running validation again before candidate training prevents drift response from bypassing the same data quality gate used by normal training.
- Candidate metrics are useful evidence, but they are not enough for promotion until compared against the current production model.
- Keeping approval and promotion as pending after training protects the human-in-the-loop boundary.

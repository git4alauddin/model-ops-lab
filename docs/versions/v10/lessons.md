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

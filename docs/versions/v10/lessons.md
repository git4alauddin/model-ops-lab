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

## V10-C5: Candidate vs Production Comparison Report

- Comparison is evidence, not approval.
- A candidate model should be judged against the current production model, not only against an abstract metric target.
- Regression gates make the comparison explicit: which metric passed, which metric failed, and by how much.
- Missing candidate or production metrics should lead to manual review instead of a fake pass.
- A passing comparison can recommend `ready_for_approval`, but the actual promotion decision should still happen in a separate approval gate.
- Keeping the comparison report inside the retraining run folder makes the lifecycle auditable.

## V10-C6: Human Approval Record

- Approval is permission, not promotion.
- A model can pass metric comparison and still require human review before production changes.
- Separating approval from promotion creates a clean audit trail: comparison evidence, human decision, then production action.
- Approval should record who decided, when they decided, what they decided, and why.
- Rejected and needs-review decisions are useful records, not failures of the system.
- Keeping `promotion.decision` pending after approval protects the final production change as a separate operational step.

## V10-C7: Approved Candidate Promotion Record

- Promotion record is not the same as serving update.
- Approval says a human permits production change; promotion record says the approved candidate has been selected as the promoted candidate.
- Registry updates and serving updates are operational actions and should stay explicit.
- Recording `registry_update = not_performed` and `serving_update = not_performed` prevents us from pretending production changed when it did not.
- A good promotion record should preserve the rollback target before any production artifact changes.
- The retraining run now has a full decision trail: trigger, candidate training, comparison, approval, and promotion decision.

## V10-C8: Serving Update Handoff

- Serving handoff validates readiness, not deployment.
- The serving API currently loads the champion from `model_registry/`, while the V10 candidate lives under `retraining_runs/<run_id>/candidate/`.
- A promoted candidate is not live until the serving system can actually resolve and load it.
- A handoff report should prove the candidate model, metrics, comparison report, approval record, promotion record, and rollback target exist before any serving mutation.
- Keeping `registry_update = not_performed` and `serving_update = not_performed` in the handoff report makes the production boundary honest.
- `/health` only proves the API process is alive; `/ready` and `/predict` are the meaningful checks after a serving update.

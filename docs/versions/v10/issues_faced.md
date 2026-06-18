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

## V10-C4: Candidate Retraining Command

The main implementation risk was accidentally reusing the normal training command and overwriting global `artifacts/`.

The fix was to reuse lower-level training, preprocessing, evaluation, and validation helpers, but write all candidate outputs under:

```text
retraining_runs/<run_id>/candidate/
```

This keeps candidate training useful without changing production state.

Another boundary was avoiding repeated retraining of the same run. The command requires `candidate_run_initialized`, then moves the run to `candidate_trained`.

## V10-C5: Candidate vs Production Comparison Report

The main design choice was separating comparison from approval.

A candidate can pass metric comparison and still need human review before production changes. For that reason C5 only updates:

```text
regression_gates
promotion.recommendation
candidate.comparison_report_path
```

It keeps:

```text
approval.state = pending
promotion.decision = pending
```

Missing metrics are treated as manual review instead of passing by default.

## V10-C6: Human Approval Record

The main boundary was avoiding approval and promotion becoming the same thing.

C6 records a human decision and writes:

```text
retraining_runs/<run_id>/approval_record.json
```

But it keeps:

```text
promotion.decision = pending
```

This lets approval become a required permission step while production changes remain a separate, explicit operation.

## V10-C7: Approved Candidate Promotion Record

The confusing part is that "promotion" can mean two different things:

```text
promotion decision recorded
production serving model changed
```

C7 implements only the first meaning.

The promotion record explicitly stores:

```text
registry_update = not_performed
serving_update = not_performed
```

This avoids a false production story. The system has now recorded that the approved candidate is selected for promotion, but the registry and serving update remain separate controlled steps.

## V10-C8: Serving Update Handoff

The main confusion point was where the promoted candidate actually lives.

Current serving reads:

```text
model_registry/ -> champion -> artifact_uri -> loaded model
```

The retraining candidate lives at:

```text
retraining_runs/<run_id>/candidate/model.pkl
```

Those are not the same path or contract.

C8 validates that the promoted candidate is ready for a future serving update, but it does not update serving. This keeps the learning path honest and prevents metadata-only promotion from being confused with live model serving.

## V10-C9: Local Registry and Serving Update

The main risk was changing the local champion and discovering afterward that the candidate could not be loaded or used for prediction.

The implementation protects against that in two ways:

```text
validate candidate artifact before mutation
restore previous champion metadata if post-update validation fails
```

Another important distinction is environment scope:

```text
local registry changed
local FastAPI model selection changed
Cloud Run did not change
```

The local update report records this boundary explicitly.

## V10-C10: Local Retraining Rollback Validation

The main risk was a rollback that changes registry statuses but fails to restore a usable model.

C10 handles this by validating:

```text
exactly one restored champion
expected rollback model version
loadable restored artifact
successful prediction
```

The second risk was a failed rollback leaving the registry partially changed. The implementation snapshots every registry metadata record before mutation and restores that snapshot if post-rollback validation fails.

The focused failure-path test initially exposed a missing import for the registry metadata path helper. That defect only affected snapshot restoration and was fixed before the real rollback command was run. This is a useful example of why failure-path tests matter as much as success-path tests for production mutation code.

## V10-C11: Architecture And Portfolio Packaging

The primary risk was overstating project maturity during portfolio packaging.

The project has validated:

```text
Cloud Run container deployment and /health
local registry-based /ready and prediction
local retraining promotion and rollback
```

It has not validated:

```text
scheduled V10 execution
automatic cloud retraining
Cloud Run model rollout from retraining artifacts
real label-based concept drift
```

The README, case study, interview guide, and diagram keep those boundaries explicit.

## V10-C12: Final Closure

The closure risk was treating unchecked portfolio screenshots or deferred cloud retraining features as blockers for the implemented local-first V10 scope.

The final classification is:

```text
engineering lifecycle: complete
automated verification: complete
documentation packaging: complete
manual screenshots: optional follow-up evidence
cloud retraining rollout: deferred production extension
```

This keeps closure evidence-based without hiding future work.

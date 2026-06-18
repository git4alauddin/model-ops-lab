# V10 Portfolio Completion Checklist

## Functional Lifecycle

- [x] Monitoring and drift reports feed a retraining decision.
- [x] Retraining recommendation is persisted with reasons and source freshness.
- [x] Candidate run metadata captures trigger, dataset, schema, and previous champion lineage.
- [x] Candidate training writes isolated run artifacts.
- [x] Candidate metrics are compared with current production metrics.
- [x] Regression failures block approval readiness.
- [x] Human approval is persisted separately from promotion.
- [x] Promotion decision is persisted separately from serving mutation.
- [x] Serving handoff validates required records and artifacts.
- [x] Local registry champion update validates readiness and prediction.
- [x] Failed local update restores the previous registry state.
- [x] Local rollback restores the recorded previous champion.
- [x] Failed rollback restores the pre-rollback registry state.

## Documentation

- [x] V10 overview, implementation, issues, verification, and lessons exist.
- [x] Retraining governance guide exists.
- [x] Serving handoff guide exists.
- [x] Local serving update guide exists.
- [x] Local rollback guide exists.
- [x] V10 Mermaid lifecycle diagram exists.
- [x] Continuous ML lifecycle architecture narrative exists.
- [x] Portfolio case study exists.
- [x] Interview and resume guide exists.
- [x] Demo checklist exists.
- [x] README includes architecture, safety, trade-offs, and limitations.

## Operational Evidence

- [x] Focused tests cover V10 C1-C10.
- [x] Full test suite passes.
- [x] Local candidate training was executed.
- [x] Candidate comparison was executed.
- [x] Approval and promotion records were generated.
- [x] Serving handoff reported ready.
- [x] Local retraining champion was activated.
- [x] Local readiness and prediction succeeded with the retraining champion.
- [x] Local rollback restored the previous champion.
- [x] Local readiness and prediction succeeded after rollback.

## Portfolio Evidence To Capture Manually

- [ ] MLflow experiment comparison screenshot.
- [ ] FastAPI Swagger prediction screenshot.
- [ ] Local `/ready` response screenshot.
- [ ] Grafana dashboard screenshot.
- [ ] GitHub Actions successful workflow screenshot.
- [ ] Artifact Registry image screenshot.
- [ ] Cloud Run revision and `/health` screenshot.
- [ ] Rendered V10 Mermaid diagram screenshot.

Screenshots are intentionally manual because they must reflect real tool state and must not be fabricated.

## Explicitly Deferred

- [ ] Scheduled V10 retraining execution.
- [ ] Automatic promotion.
- [ ] Production label feedback and concept drift.
- [ ] Managed model registry.
- [ ] External model artifact storage.
- [ ] Cloud Run rollout from retraining artifacts.
- [ ] Cloud Run prediction validation with external model artifacts.
- [ ] Canary deployment and traffic migration for retrained models.
- [ ] Fairness, calibration, and latency promotion gates.

Deferred items are future production extensions, not hidden completion claims.


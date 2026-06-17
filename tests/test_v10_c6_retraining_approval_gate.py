import json
from pathlib import Path

from app.retraining.approval_gate import (
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    ApprovalGateError,
    build_approval_record,
    record_retraining_approval,
)
from app.retraining.candidate_comparison import GATE_FAILED, GATE_PASSED
from app.retraining.candidate_run_metadata import (
    APPROVAL_PENDING,
    CANDIDATE_APPROVAL_RECORDED,
    CANDIDATE_COMPARED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_record_retraining_approval_persists_record_and_updates_metadata(tmp_path) -> None:
    metadata = _compared_metadata(run_id="retrain-approval")
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path)

    record, updated_metadata, record_path = record_retraining_approval(
        run_id="retrain-approval",
        decision=APPROVAL_APPROVED,
        approved_by="alauddin",
        notes="Candidate passed metric comparison.",
        runs_dir=tmp_path,
        decided_at="2026-06-18T00:00:00+00:00",
    )
    persisted_record = json.loads(record_path.read_text(encoding="utf-8"))
    persisted_metadata = json.loads(
        (tmp_path / "retrain-approval" / "retraining_metadata.json").read_text(
            encoding="utf-8"
        )
    )

    assert record_path == tmp_path / "retrain-approval" / "approval_record.json"
    assert persisted_record == record
    assert persisted_metadata == updated_metadata
    assert record["decision"] == APPROVAL_APPROVED
    assert record["production_change_allowed"] is True
    assert updated_metadata["status"] == CANDIDATE_APPROVAL_RECORDED
    assert updated_metadata["approval"]["state"] == APPROVAL_APPROVED
    assert updated_metadata["approval"]["approved_by"] == "alauddin"
    assert updated_metadata["approval"]["approved_at"] == "2026-06-18T00:00:00+00:00"
    assert updated_metadata["promotion"]["decision"] == APPROVAL_PENDING
    assert updated_metadata["promotion"]["production_change_allowed"] is True


def test_record_retraining_rejection_keeps_production_change_blocked(tmp_path) -> None:
    metadata = _compared_metadata(run_id="retrain-reject")
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path)

    record, updated_metadata, _ = record_retraining_approval(
        run_id="retrain-reject",
        decision=APPROVAL_REJECTED,
        approved_by="alauddin",
        notes="Human review rejected the candidate.",
        runs_dir=tmp_path,
        decided_at="2026-06-18T00:00:00+00:00",
    )

    assert record["production_change_allowed"] is False
    assert updated_metadata["approval"]["state"] == APPROVAL_REJECTED
    assert updated_metadata["approval"]["approved_by"] is None
    assert updated_metadata["approval"]["approved_at"] is None
    assert updated_metadata["approval"]["decided_by"] == "alauddin"
    assert updated_metadata["promotion"]["decision"] == APPROVAL_PENDING
    assert updated_metadata["promotion"]["production_change_allowed"] is False


def test_approval_record_requires_compared_status_and_passed_gate() -> None:
    metadata = _compared_metadata()
    metadata["status"] = "candidate_trained"

    try:
        build_approval_record(
            metadata=metadata,
            decision=APPROVAL_APPROVED,
            approved_by="alauddin",
        )
    except ApprovalGateError as exc:
        assert CANDIDATE_COMPARED in str(exc)
    else:
        raise AssertionError("Expected ApprovalGateError for non-compared run.")

    metadata = _compared_metadata(gate_status=GATE_FAILED)
    try:
        build_approval_record(
            metadata=metadata,
            decision=APPROVAL_APPROVED,
            approved_by="alauddin",
        )
    except ApprovalGateError as exc:
        assert "regression_gates.status=passed" in str(exc)
    else:
        raise AssertionError("Expected ApprovalGateError for failed regression gate.")


def test_approval_record_rejects_invalid_decision_or_missing_approver() -> None:
    metadata = _compared_metadata()

    try:
        build_approval_record(
            metadata=metadata,
            decision="bad_decision",
            approved_by="alauddin",
        )
    except ApprovalGateError as exc:
        assert "Invalid approval decision" in str(exc)
    else:
        raise AssertionError("Expected ApprovalGateError for invalid decision.")

    try:
        build_approval_record(
            metadata=metadata,
            decision=APPROVAL_APPROVED,
            approved_by="",
        )
    except ApprovalGateError as exc:
        assert "approved_by is required" in str(exc)
    else:
        raise AssertionError("Expected ApprovalGateError for missing approver.")


def test_v10_c6_docs_mention_approval_command_and_record() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.record_retraining_approval --run-id <run_id>" in readme
    assert "retraining_runs/<run_id>/approval_record.json" in readme
    assert "V10-C6: Human Approval Record" in implementation
    assert "Approval is permission, not promotion" in lessons


def _compared_metadata(
    *,
    run_id: str = "retrain-test",
    gate_status: str = GATE_PASSED,
) -> dict:
    metadata = build_candidate_retraining_run_metadata(
        trigger_decision={
            "decision": "retraining_recommended",
            "recommendation": "Start a governed candidate retraining run.",
            "reason_count": 1,
            "reasons": [
                {
                    "name": "data_drift_detected",
                    "category": "retraining_signal",
                    "severity": "warning",
                    "source": "data_drift_summary",
                    "message": "Data drift summary detected drifted features.",
                    "recommended_action": "Start governed retraining.",
                }
            ],
            "source_reports": {},
            "source_freshness": {},
        },
        training_config={"dataset": {"path": "data/churn.csv", "target_column": "churn"}},
        dataset_version={
            "dataset_name": "customer_churn",
            "version": "v1",
            "path": "data/churn.csv",
            "checksum": {"algorithm": "sha256", "value": "abc123"},
        },
        schema={
            "name": "customer_churn",
            "version": "v1",
            "target_column": "churn",
        },
        previous_production_model={
            "model_name": "customer_churn_model",
            "model_version": "v1-prod",
            "artifact_uri": "mlflow-run://prod/artifacts/model",
            "status": "champion",
            "mlflow_run_id": "prod",
            "candidate_name": "decision_tree_baseline",
            "model_type": "decision_tree",
            "dataset_name": "customer_churn",
            "dataset_version": "v1",
            "dataset_checksum": "abc123",
            "metrics": {"f1": 1.0},
            "updated_at": "2026-06-18T00:00:00+00:00",
        },
        run_id=run_id,
        created_at="2026-06-18T00:00:00+00:00",
    )
    metadata["status"] = CANDIDATE_COMPARED
    metadata["candidate"]["comparison_report_path"] = (
        f"retraining_runs/{run_id}/comparison_report.json"
    )
    metadata["regression_gates"] = {
        "status": gate_status,
        "results": [{"metric": "f1", "status": gate_status}],
    }
    metadata["promotion"]["recommendation"] = "ready_for_approval"
    return metadata

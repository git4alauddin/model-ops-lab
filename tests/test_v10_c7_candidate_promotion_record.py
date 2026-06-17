import json
from pathlib import Path

from app.retraining.candidate_comparison import GATE_PASSED
from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    APPROVAL_PENDING,
    APPROVAL_REJECTED,
    CANDIDATE_APPROVAL_RECORDED,
    CANDIDATE_PROMOTED,
    PROMOTION_DECISION_PENDING,
    PROMOTION_DECISION_PROMOTED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.promotion_record import (
    PromotionRecordError,
    build_promotion_record,
    record_approved_candidate_promotion,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_record_approved_candidate_promotion_persists_record_and_updates_metadata(
    tmp_path,
) -> None:
    metadata = _approved_metadata(run_id="retrain-promote")
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path)

    record, updated_metadata, record_path = record_approved_candidate_promotion(
        run_id="retrain-promote",
        promoted_by="alauddin",
        reason="Approved candidate passed all local V10 gates.",
        runs_dir=tmp_path,
        promoted_at="2026-06-18T00:00:00+00:00",
    )
    persisted_record = json.loads(record_path.read_text(encoding="utf-8"))
    persisted_metadata = json.loads(
        (tmp_path / "retrain-promote" / "retraining_metadata.json").read_text(
            encoding="utf-8"
        )
    )

    assert record_path == tmp_path / "retrain-promote" / "promotion_record.json"
    assert persisted_record == record
    assert persisted_metadata == updated_metadata
    assert record["decision"] == PROMOTION_DECISION_PROMOTED
    assert record["registry_update"] == "not_performed"
    assert record["serving_update"] == "not_performed"
    assert record["rollback_target"]["model_version"] == "v1-prod"
    assert updated_metadata["status"] == CANDIDATE_PROMOTED
    assert updated_metadata["promotion"]["decision"] == PROMOTION_DECISION_PROMOTED
    assert updated_metadata["promotion"]["record_path"] == str(record_path)
    assert updated_metadata["promotion"]["registry_update"] == "not_performed"
    assert updated_metadata["promotion"]["serving_update"] == "not_performed"
    assert updated_metadata["approval"]["state"] == APPROVAL_APPROVED


def test_promotion_record_requires_approved_candidate() -> None:
    metadata = _approved_metadata()
    metadata["approval"]["state"] = APPROVAL_REJECTED

    try:
        build_promotion_record(
            metadata=metadata,
            promoted_by="alauddin",
            reason="Should not promote.",
        )
    except PromotionRecordError as exc:
        assert "approval.state=approved" in str(exc)
    else:
        raise AssertionError("Expected PromotionRecordError for rejected approval.")


def test_promotion_record_requires_pending_promotion_decision() -> None:
    metadata = _approved_metadata()
    metadata["promotion"]["decision"] = PROMOTION_DECISION_PROMOTED

    try:
        build_promotion_record(
            metadata=metadata,
            promoted_by="alauddin",
            reason="Duplicate promotion.",
        )
    except PromotionRecordError as exc:
        assert "promotion.decision=pending" in str(exc)
    else:
        raise AssertionError("Expected PromotionRecordError for duplicate promotion.")


def test_promotion_record_requires_permission_and_candidate_artifacts() -> None:
    metadata = _approved_metadata()
    metadata["promotion"]["production_change_allowed"] = False

    try:
        build_promotion_record(
            metadata=metadata,
            promoted_by="alauddin",
            reason="Permission missing.",
        )
    except PromotionRecordError as exc:
        assert "production_change_allowed=true" in str(exc)
    else:
        raise AssertionError("Expected PromotionRecordError for blocked production change.")

    metadata = _approved_metadata()
    metadata["candidate"]["model_path"] = None
    try:
        build_promotion_record(
            metadata=metadata,
            promoted_by="alauddin",
            reason="Artifact missing.",
        )
    except PromotionRecordError as exc:
        assert "Candidate model and metrics paths are required" in str(exc)
    else:
        raise AssertionError("Expected PromotionRecordError for missing artifact path.")


def test_promotion_record_requires_promoter_and_reason() -> None:
    metadata = _approved_metadata()

    try:
        build_promotion_record(
            metadata=metadata,
            promoted_by="",
            reason="Approved.",
        )
    except PromotionRecordError as exc:
        assert "promoted_by is required" in str(exc)
    else:
        raise AssertionError("Expected PromotionRecordError for missing promoter.")

    try:
        build_promotion_record(
            metadata=metadata,
            promoted_by="alauddin",
            reason="",
        )
    except PromotionRecordError as exc:
        assert "promotion reason is required" in str(exc)
    else:
        raise AssertionError("Expected PromotionRecordError for missing reason.")


def test_v10_c7_docs_mention_promotion_command_and_record() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.record_candidate_promotion --run-id <run_id>" in readme
    assert "retraining_runs/<run_id>/promotion_record.json" in readme
    assert "V10-C7: Approved Candidate Promotion Record" in implementation
    assert "Promotion record is not the same as serving update" in lessons


def _approved_metadata(run_id: str = "retrain-test") -> dict:
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
    metadata["status"] = CANDIDATE_APPROVAL_RECORDED
    metadata["candidate"].update(
        {
            "model_type": "logistic_regression",
            "model_path": f"retraining_runs/{run_id}/candidate/model.pkl",
            "metrics_path": f"retraining_runs/{run_id}/candidate/metrics.json",
            "comparison_report_path": f"retraining_runs/{run_id}/comparison_report.json",
            "metrics": {"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0},
        }
    )
    metadata["regression_gates"] = {
        "status": GATE_PASSED,
        "results": [{"metric": "f1", "status": GATE_PASSED}],
    }
    metadata["promotion"].update(
        {
            "decision": PROMOTION_DECISION_PENDING,
            "recommendation": "ready_for_approval",
            "production_change_allowed": True,
            "approval_record_path": f"retraining_runs/{run_id}/approval_record.json",
        }
    )
    metadata["approval"] = {
        "state": APPROVAL_APPROVED,
        "decision": APPROVAL_APPROVED,
        "approved_by": "alauddin",
        "approved_at": "2026-06-18T00:00:00+00:00",
        "decided_by": "alauddin",
        "decided_at": "2026-06-18T00:00:00+00:00",
        "notes": "Approved for promotion record.",
        "record_path": f"retraining_runs/{run_id}/approval_record.json",
    }
    assert metadata["promotion"]["decision"] == APPROVAL_PENDING
    return metadata

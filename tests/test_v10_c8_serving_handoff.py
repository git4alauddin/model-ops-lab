import json
from pathlib import Path

from app.retraining.candidate_comparison import GATE_PASSED
from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    CANDIDATE_PROMOTED,
    CANDIDATE_SERVING_HANDOFF_VALIDATED,
    PROMOTION_DECISION_PROMOTED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.serving_handoff import (
    HANDOFF_BLOCKED,
    HANDOFF_READY,
    build_serving_handoff_report,
    validate_serving_handoff,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"
HANDOFF_DOC_PATH = PROJECT_ROOT / "docs" / "retraining" / "serving_update_handoff.md"


def test_serving_handoff_report_is_ready_when_required_records_exist(tmp_path) -> None:
    metadata = _promoted_metadata(tmp_path, run_id="retrain-handoff")
    _write_required_files(metadata)

    report = build_serving_handoff_report(
        metadata=metadata,
        project_root=tmp_path,
        generated_at="2026-06-18T00:00:00+00:00",
    )

    assert report["status"] == HANDOFF_READY
    assert all(check["status"] == "passed" for check in report["checks"])
    assert report["serving_boundary"] == {
        "live_serving_changed": False,
        "model_registry_updated": False,
        "cloud_run_redeployed": False,
        "traffic_changed": False,
    }


def test_serving_handoff_report_blocks_missing_candidate_model(tmp_path) -> None:
    metadata = _promoted_metadata(tmp_path, run_id="retrain-blocked")
    _write_required_files(metadata, skip={"model_path"})

    report = build_serving_handoff_report(metadata=metadata, project_root=tmp_path)
    failed_checks = {check["name"] for check in report["checks"] if check["status"] == "failed"}

    assert report["status"] == HANDOFF_BLOCKED
    assert "candidate_model_available" in failed_checks


def test_validate_serving_handoff_persists_report_and_updates_metadata(tmp_path) -> None:
    metadata = _promoted_metadata(tmp_path, run_id="retrain-handoff")
    _write_required_files(metadata)
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path / "runs")

    report, updated_metadata, report_path = validate_serving_handoff(
        run_id="retrain-handoff",
        runs_dir=tmp_path / "runs",
        project_root=tmp_path,
        generated_at="2026-06-18T00:00:00+00:00",
    )
    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    persisted_metadata = json.loads(
        (tmp_path / "runs" / "retrain-handoff" / "retraining_metadata.json").read_text(
            encoding="utf-8"
        )
    )

    assert report_path == tmp_path / "runs" / "retrain-handoff" / "serving_handoff_report.json"
    assert persisted_report == report
    assert persisted_metadata == updated_metadata
    assert updated_metadata["status"] == CANDIDATE_SERVING_HANDOFF_VALIDATED
    assert updated_metadata["promotion"]["serving_handoff_status"] == HANDOFF_READY
    assert updated_metadata["promotion"]["serving_update_ready"] is True
    assert updated_metadata["promotion"]["serving_handoff_report_path"] == str(report_path)
    assert updated_metadata["promotion"]["serving_update"] == "not_performed"
    assert updated_metadata["promotion"]["registry_update"] == "not_performed"


def test_serving_handoff_blocks_non_promoted_status(tmp_path) -> None:
    metadata = _promoted_metadata(tmp_path)
    metadata["status"] = "candidate_approval_recorded"
    _write_required_files(metadata)

    report = build_serving_handoff_report(metadata=metadata, project_root=tmp_path)
    status_check = next(
        check for check in report["checks"] if check["name"] == "candidate_promoted_status"
    )

    assert report["status"] == HANDOFF_BLOCKED
    assert status_check["status"] == "failed"


def test_v10_c8_docs_mention_serving_handoff_command_and_boundary() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()
    handoff_doc = HANDOFF_DOC_PATH.read_text()

    assert "python -m app.validate_serving_handoff --run-id <run_id>" in readme
    assert "retraining_runs/<run_id>/serving_handoff_report.json" in readme
    assert "V10-C8: Serving Update Handoff" in implementation
    assert "Serving handoff validates readiness, not deployment" in lessons
    assert "promotion record" in handoff_doc
    assert "!= serving model update" in handoff_doc


def _promoted_metadata(tmp_path: Path, run_id: str = "retrain-test") -> dict:
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
    run_dir = tmp_path / "retraining_runs" / run_id
    metadata["status"] = CANDIDATE_PROMOTED
    metadata["candidate"].update(
        {
            "model_type": "logistic_regression",
            "model_path": str(run_dir / "candidate" / "model.pkl"),
            "metrics_path": str(run_dir / "candidate" / "metrics.json"),
            "comparison_report_path": str(run_dir / "comparison_report.json"),
            "metrics": {"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0},
        }
    )
    metadata["regression_gates"] = {
        "status": GATE_PASSED,
        "results": [{"metric": "f1", "status": GATE_PASSED}],
    }
    metadata["promotion"].update(
        {
            "decision": PROMOTION_DECISION_PROMOTED,
            "recommendation": "ready_for_approval",
            "production_change_allowed": True,
            "approval_record_path": str(run_dir / "approval_record.json"),
            "record_path": str(run_dir / "promotion_record.json"),
            "registry_update": "not_performed",
            "serving_update": "not_performed",
            "promoted_by": "alauddin",
            "promoted_at": "2026-06-18T00:00:00+00:00",
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
        "record_path": str(run_dir / "approval_record.json"),
    }
    return metadata


def _write_required_files(metadata: dict, skip: set[str] | None = None) -> None:
    skip = skip or set()
    candidate = metadata["candidate"]
    promotion = metadata["promotion"]
    approval = metadata["approval"]
    paths = {
        "model_path": candidate["model_path"],
        "metrics_path": candidate["metrics_path"],
        "comparison_report_path": candidate["comparison_report_path"],
        "approval_record_path": approval["record_path"],
        "promotion_record_path": promotion["record_path"],
    }
    for name, path_value in paths.items():
        if name in skip:
            continue
        path = Path(path_value)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

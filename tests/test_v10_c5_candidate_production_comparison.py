import json
from pathlib import Path

from app.retraining.candidate_comparison import (
    GATE_FAILED,
    GATE_MANUAL_REVIEW,
    GATE_PASSED,
    PROMOTION_READY_FOR_APPROVAL,
    PROMOTION_REJECT_CANDIDATE,
    CandidateComparisonError,
    build_and_save_candidate_comparison_report,
    build_candidate_comparison_report,
)
from app.retraining.candidate_run_metadata import (
    APPROVAL_PENDING,
    CANDIDATE_COMPARED,
    CANDIDATE_TRAINED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_candidate_comparison_passes_when_metrics_do_not_regress() -> None:
    metadata = _trained_metadata(
        candidate_metrics={"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0},
        production_metrics={"accuracy": 0.9, "precision": 0.9, "recall": 0.9, "f1": 0.9},
    )

    report = build_candidate_comparison_report(
        metadata=metadata,
        generated_at="2026-06-18T00:00:00+00:00",
    )

    assert report["status"] == GATE_PASSED
    assert report["promotion_recommendation"] == PROMOTION_READY_FOR_APPROVAL
    assert report["summary"] == {"passed": 4, "failed": 0, "manual_review": 0}
    assert all(result["delta"] >= 0 for result in report["metric_results"])


def test_candidate_comparison_fails_when_primary_metrics_regress() -> None:
    metadata = _trained_metadata(
        candidate_metrics={"accuracy": 0.8, "precision": 0.8, "recall": 0.8, "f1": 0.8},
        production_metrics={"accuracy": 0.9, "precision": 0.9, "recall": 0.9, "f1": 0.9},
    )

    report = build_candidate_comparison_report(metadata=metadata)

    assert report["status"] == GATE_FAILED
    assert report["promotion_recommendation"] == PROMOTION_REJECT_CANDIDATE
    assert report["summary"]["failed"] == 4


def test_candidate_comparison_marks_missing_metric_for_manual_review() -> None:
    metadata = _trained_metadata(
        candidate_metrics={"accuracy": 1.0, "precision": 1.0, "recall": 1.0},
        production_metrics={"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0},
    )

    report = build_candidate_comparison_report(metadata=metadata)
    f1_result = next(result for result in report["metric_results"] if result["metric"] == "f1")

    assert report["status"] == GATE_MANUAL_REVIEW
    assert f1_result["status"] == GATE_MANUAL_REVIEW
    assert f1_result["delta"] is None


def test_build_and_save_candidate_comparison_updates_metadata(tmp_path) -> None:
    metadata = _trained_metadata(
        run_id="retrain-compare",
        candidate_metrics={"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0},
        production_metrics={"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0},
    )
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path)

    report, updated_metadata, report_path = build_and_save_candidate_comparison_report(
        run_id="retrain-compare",
        runs_dir=tmp_path,
        generated_at="2026-06-18T00:00:00+00:00",
    )
    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    persisted_metadata = json.loads(
        (tmp_path / "retrain-compare" / "retraining_metadata.json").read_text(
            encoding="utf-8"
        )
    )

    assert report_path == tmp_path / "retrain-compare" / "comparison_report.json"
    assert persisted_report == report
    assert persisted_metadata == updated_metadata
    assert updated_metadata["status"] == CANDIDATE_COMPARED
    assert updated_metadata["candidate"]["comparison_report_path"] == str(report_path)
    assert updated_metadata["regression_gates"]["status"] == GATE_PASSED
    assert updated_metadata["promotion"]["recommendation"] == PROMOTION_READY_FOR_APPROVAL
    assert updated_metadata["promotion"]["decision"] == APPROVAL_PENDING
    assert updated_metadata["approval"]["state"] == APPROVAL_PENDING


def test_candidate_comparison_rejects_non_trained_run() -> None:
    metadata = _trained_metadata()
    metadata["status"] = "candidate_run_initialized"

    try:
        build_candidate_comparison_report(metadata=metadata)
    except CandidateComparisonError as exc:
        assert CANDIDATE_TRAINED in str(exc)
    else:
        raise AssertionError("Expected CandidateComparisonError for untrained run.")


def test_v10_c5_docs_mention_comparison_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.compare_candidate_to_production --run-id <run_id>" in readme
    assert "retraining_runs/<run_id>/comparison_report.json" in readme
    assert "V10-C5: Candidate vs Production Comparison Report" in implementation
    assert "Comparison is evidence, not approval" in lessons


def _trained_metadata(
    *,
    run_id: str = "retrain-test",
    candidate_metrics: dict | None = None,
    production_metrics: dict | None = None,
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
            "metrics": production_metrics or {"f1": 1.0},
            "updated_at": "2026-06-18T00:00:00+00:00",
        },
        run_id=run_id,
        created_at="2026-06-18T00:00:00+00:00",
    )
    metadata["status"] = CANDIDATE_TRAINED
    metadata["candidate"].update(
        {
            "model_type": "logistic_regression",
            "model_path": f"retraining_runs/{run_id}/candidate/model.pkl",
            "metrics_path": f"retraining_runs/{run_id}/candidate/metrics.json",
            "metrics": candidate_metrics or {"f1": 1.0},
        }
    )
    return metadata

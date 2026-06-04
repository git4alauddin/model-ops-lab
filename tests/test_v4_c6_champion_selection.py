"""Tests for V4 champion run selection."""

from app.champion_selection import ChampionSelectionError, select_champion_run


def test_select_champion_run_prefers_highest_f1():
    report = select_champion_run(
        [
            _candidate("run-logreg", "logistic_regression", f1=0.7, recall=0.8),
            _candidate("run-forest", "random_forest", f1=0.9, recall=0.7),
        ]
    )

    assert report["champion"]["run_id"] == "run-forest"
    assert report["champion"]["model_type"] == "random_forest"


def test_select_champion_run_uses_recall_as_first_tie_breaker():
    report = select_champion_run(
        [
            _candidate("run-low-recall", "logistic_regression", f1=0.8, recall=0.6),
            _candidate("run-high-recall", "decision_tree", f1=0.8, recall=0.9),
        ]
    )

    assert report["champion"]["run_id"] == "run-high-recall"


def test_select_champion_run_rejects_different_dataset_checksum():
    report = select_champion_run(
        [
            _candidate("run-valid", "logistic_regression", f1=0.8),
            _candidate("run-other-data", "random_forest", f1=0.9, checksum="other"),
        ]
    )

    assert report["champion"]["run_id"] == "run-valid"
    assert report["rejected_runs"] == [
        {
            "run_id": "run-other-data",
            "candidate_name": "random_forest_candidate",
            "reason": "dataset identity does not match the comparison group",
        }
    ]


def test_select_champion_run_fails_when_no_runs_are_eligible():
    try:
        select_champion_run([_candidate("run-failed", "logistic_regression", status="FAILED")])
    except ChampionSelectionError as exc:
        assert "No eligible candidate runs" in str(exc)
    else:
        raise AssertionError("Expected ChampionSelectionError for no eligible runs.")


def _candidate(
    run_id: str,
    model_type: str,
    f1: float = 0.8,
    recall: float = 0.7,
    checksum: str = "abc123",
    status: str = "FINISHED",
) -> dict:
    return {
        "run_id": run_id,
        "candidate_name": f"{model_type}_candidate",
        "model_type": model_type,
        "status": status,
        "dataset_name": "customer_churn",
        "dataset_version": "v1",
        "dataset_checksum": checksum,
        "pipeline_version": "v4-c6",
        "metrics": {
            "accuracy": 0.75,
            "precision": 0.7,
            "recall": recall,
            "f1": f1,
            "training_duration_seconds": 0.2,
            "evaluation_duration_seconds": 0.1,
        },
        "artifacts": {
            "model": "model.pkl",
            "metrics": "metrics.json",
            "confusion_matrix": "confusion_matrix.json",
            "config_snapshot": "config_snapshot.json",
            "metadata": "training_metadata.json",
        },
    }

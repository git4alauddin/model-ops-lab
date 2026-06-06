"""Tests for V6 model rollback command."""

from app.model_registry import (
    build_model_version_metadata,
    find_champion_model_versions,
    load_model_version_metadata,
    save_model_version_metadata,
)
from app.rollback_model import ModelRollbackError, rollback_model_version


def _model_metadata(
    *,
    model_name: str = "customer_churn_model",
    model_version: str,
    status: str,
) -> dict:
    return build_model_version_metadata(
        model_name=model_name,
        model_version=model_version,
        status=status,
        created_at="2026-06-06T10:00:00+00:00",
        updated_at="2026-06-06T10:00:00+00:00",
        mlflow_run_id=f"run-{model_version}",
        candidate_name="decision_tree_baseline",
        model_type="decision_tree",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"accuracy": 0.91, "f1": 0.87},
        artifact_uri=f"mlflow-run://run-{model_version}/artifacts/model",
    )


def test_archived_model_can_be_rolled_back_to_champion(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-previous", status="archived"),
        output_dir=tmp_path,
    )

    metadata = rollback_model_version(
        model_version="v1-previous",
        rollback_reason="Restore previous stable model.",
        output_dir=tmp_path,
    )

    assert metadata["status"] == "champion"
    assert metadata["promoted_from"] == "archived"


def test_current_champion_becomes_archived_on_rollback(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-previous", status="archived"),
        output_dir=tmp_path,
    )

    rollback_model_version(
        model_version="v1-previous",
        rollback_reason="Restore previous stable model.",
        output_dir=tmp_path,
    )

    previous_champion = load_model_version_metadata(
        "customer_churn_model",
        "v1-current",
        output_dir=tmp_path,
    )
    assert previous_champion["status"] == "archived"
    assert previous_champion["promoted_from"] == "champion"


def test_rollback_reason_is_persisted(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-previous", status="archived"),
        output_dir=tmp_path,
    )

    metadata = rollback_model_version(
        model_version="v1-previous",
        rollback_reason="Production regression detected.",
        output_dir=tmp_path,
    )

    assert metadata["promotion_reason"] == "Production regression detected."


def test_candidate_cannot_be_rolled_back(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-candidate", status="candidate"),
        output_dir=tmp_path,
    )

    try:
        rollback_model_version(
            model_version="v1-candidate",
            rollback_reason="Restore candidate.",
            output_dir=tmp_path,
        )
    except ModelRollbackError as exc:
        assert "Only archived model versions" in str(exc)
    else:
        raise AssertionError("Expected ModelRollbackError for candidate rollback.")


def test_champion_cannot_be_rolled_back(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )

    try:
        rollback_model_version(
            model_version="v1-current",
            rollback_reason="Rollback current champion.",
            output_dir=tmp_path,
        )
    except ModelRollbackError as exc:
        assert "Only archived model versions" in str(exc)
    else:
        raise AssertionError("Expected ModelRollbackError for champion rollback.")


def test_missing_rollback_reason_fails(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-previous", status="archived"),
        output_dir=tmp_path,
    )

    try:
        rollback_model_version(
            model_version="v1-previous",
            rollback_reason="",
            output_dir=tmp_path,
        )
    except ModelRollbackError as exc:
        assert "rollback_reason is required" in str(exc)
    else:
        raise AssertionError("Expected ModelRollbackError for missing reason.")


def test_unrelated_model_champion_is_not_changed(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-previous", status="archived"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(
            model_name="fraud_model",
            model_version="v1-current",
            status="champion",
        ),
        output_dir=tmp_path,
    )

    rollback_model_version(
        model_version="v1-previous",
        rollback_reason="Restore previous stable model.",
        output_dir=tmp_path,
    )

    unrelated_champion = load_model_version_metadata(
        "fraud_model",
        "v1-current",
        output_dir=tmp_path,
    )
    champions = find_champion_model_versions(
        "customer_churn_model",
        output_dir=tmp_path,
    )
    assert unrelated_champion["status"] == "champion"
    assert [champion["model_version"] for champion in champions] == ["v1-previous"]

"""Tests for V6 champion promotion command."""

from app.model_registry import (
    ModelRegistryError,
    build_model_version_metadata,
    load_model_version_metadata,
    save_model_version_metadata,
)
from app.promote_model import ModelPromotionError, promote_candidate_model


def _model_metadata(status: str = "candidate") -> dict:
    return build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1-run12345",
        status=status,
        created_at="2026-06-06T10:00:00+00:00",
        updated_at="2026-06-06T10:00:00+00:00",
        mlflow_run_id="run123456789",
        candidate_name="decision_tree_baseline",
        model_type="decision_tree",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"accuracy": 0.91, "f1": 0.87},
        artifact_uri="mlflow-run://run123456789/artifacts/model",
    )


def test_promote_candidate_model_updates_status_to_champion(tmp_path):
    save_model_version_metadata(_model_metadata(), output_dir=tmp_path)

    metadata = promote_candidate_model(
        model_version="v1-run12345",
        output_dir=tmp_path,
    )

    assert metadata["status"] == "champion"
    assert metadata["promoted_from"] == "candidate"


def test_promote_candidate_model_persists_promotion_reason(tmp_path):
    save_model_version_metadata(_model_metadata(), output_dir=tmp_path)

    metadata = promote_candidate_model(
        model_version="v1-run12345",
        promotion_reason="Approved after manual review.",
        output_dir=tmp_path,
    )

    assert metadata["promotion_reason"] == "Approved after manual review."
    loaded_metadata = load_model_version_metadata(
        "customer_churn_model",
        "v1-run12345",
        output_dir=tmp_path,
    )
    assert loaded_metadata == metadata


def test_promote_candidate_model_fails_when_record_is_missing(tmp_path):
    try:
        promote_candidate_model(model_version="missing-v1", output_dir=tmp_path)
    except ModelRegistryError as exc:
        assert "metadata file not found" in str(exc)
    else:
        raise AssertionError("Expected failure for missing model record.")


def test_promote_candidate_model_rejects_non_candidate_model(tmp_path):
    save_model_version_metadata(_model_metadata(status="champion"), output_dir=tmp_path)

    try:
        promote_candidate_model(model_version="v1-run12345", output_dir=tmp_path)
    except ModelPromotionError as exc:
        assert "Only candidate model versions" in str(exc)
    else:
        raise AssertionError("Expected ModelPromotionError for non-candidate model.")


def test_promote_candidate_model_can_resolve_version_from_champion_report(tmp_path):
    save_model_version_metadata(_model_metadata(), output_dir=tmp_path)
    champion_report_path = tmp_path / "champion_run.json"
    champion_report_path.write_text(
        """
        {
          "champion": {
            "run_id": "run123456789",
            "dataset_version": "v1"
          }
        }
        """,
        encoding="utf-8",
    )

    metadata = promote_candidate_model(
        champion_report_path=champion_report_path,
        output_dir=tmp_path,
    )

    assert metadata["model_version"] == "v1-run12345"
    assert metadata["status"] == "champion"

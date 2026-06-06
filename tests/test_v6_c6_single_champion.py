"""Tests for V6 single champion enforcement."""

from app.model_registry import (
    build_model_version_metadata,
    find_champion_model_versions,
    list_model_version_metadata,
    load_model_version_metadata,
    save_model_version_metadata,
)
from app.promote_model import ModelPromotionError, promote_candidate_model


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


def test_promoting_candidate_archives_existing_champion(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-old", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-new", status="candidate"),
        output_dir=tmp_path,
    )

    promoted_metadata = promote_candidate_model(
        model_version="v1-new",
        output_dir=tmp_path,
    )

    previous_champion = load_model_version_metadata(
        "customer_churn_model",
        "v1-old",
        output_dir=tmp_path,
    )
    assert previous_champion["status"] == "archived"
    assert previous_champion["promoted_from"] == "champion"
    assert promoted_metadata["status"] == "champion"


def test_promoted_candidate_is_only_champion_for_model_name(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-old", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-new", status="candidate"),
        output_dir=tmp_path,
    )

    promote_candidate_model(model_version="v1-new", output_dir=tmp_path)

    champions = find_champion_model_versions(
        "customer_churn_model",
        output_dir=tmp_path,
    )
    assert [champion["model_version"] for champion in champions] == ["v1-new"]


def test_unrelated_model_champion_is_not_archived(tmp_path):
    save_model_version_metadata(
        _model_metadata(
            model_name="customer_churn_model",
            model_version="v1-old",
            status="champion",
        ),
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
    save_model_version_metadata(
        _model_metadata(
            model_name="customer_churn_model",
            model_version="v1-new",
            status="candidate",
        ),
        output_dir=tmp_path,
    )

    promote_candidate_model(model_version="v1-new", output_dir=tmp_path)

    unrelated_champion = load_model_version_metadata(
        "fraud_model",
        "v1-current",
        output_dir=tmp_path,
    )
    assert unrelated_champion["status"] == "champion"


def test_non_candidate_promotion_still_fails_without_archiving(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-old", status="champion"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-archived", status="archived"),
        output_dir=tmp_path,
    )

    try:
        promote_candidate_model(model_version="v1-archived", output_dir=tmp_path)
    except ModelPromotionError as exc:
        assert "Only candidate model versions" in str(exc)
    else:
        raise AssertionError("Expected ModelPromotionError for non-candidate model.")

    previous_champion = load_model_version_metadata(
        "customer_churn_model",
        "v1-old",
        output_dir=tmp_path,
    )
    assert previous_champion["status"] == "champion"


def test_registry_listing_ignores_non_registry_json_files(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )
    (tmp_path / "champion_run.json").write_text(
        '{"champion": {"run_id": "run-1"}}',
        encoding="utf-8",
    )

    records = list_model_version_metadata(output_dir=tmp_path)

    assert len(records) == 1
    assert records[0]["model_version"] == "v1-current"

"""Tests for V6 model registry query command."""

from app.model_registry import build_model_version_metadata, save_model_version_metadata
from app.query_model_registry import (
    ModelRegistryQueryError,
    build_registry_summary,
    format_registry_summary,
)


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


def test_build_registry_summary_lists_model_records(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-old", status="archived"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )

    summary = build_registry_summary(output_dir=tmp_path)

    assert summary["model_name"] == "customer_churn_model"
    assert [record["model_version"] for record in summary["records"]] == [
        "v1-old",
        "v1-current",
    ]


def test_build_registry_summary_finds_current_champion(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-candidate", status="candidate"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )

    summary = build_registry_summary(output_dir=tmp_path)

    assert summary["champion"]["model_version"] == "v1-current"


def test_build_registry_summary_fails_when_registry_is_empty(tmp_path):
    try:
        build_registry_summary(output_dir=tmp_path)
    except ModelRegistryQueryError as exc:
        assert "No model registry records found" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryQueryError for empty registry.")


def test_build_registry_summary_ignores_unrelated_non_registry_json(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )
    (tmp_path / "champion_run.json").write_text(
        '{"champion": {"run_id": "run-1"}}',
        encoding="utf-8",
    )

    summary = build_registry_summary(output_dir=tmp_path)

    assert len(summary["records"]) == 1
    assert summary["records"][0]["model_version"] == "v1-current"


def test_format_registry_summary_prints_compact_summary(tmp_path):
    save_model_version_metadata(
        _model_metadata(model_version="v1-current", status="champion"),
        output_dir=tmp_path,
    )

    output = format_registry_summary(build_registry_summary(output_dir=tmp_path))

    assert "Model Registry: customer_churn_model" in output
    assert "Champion: v1-current" in output
    assert "model_version | status | run_id | candidate | f1" in output

"""Tests for V5 pipeline run metadata."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from app.pipeline_run_metadata import (
    PIPELINE_VERSION,
    PipelineRunMetadataError,
    build_pipeline_run_id,
    build_pipeline_run_metadata,
    build_pipeline_run_metadata_path,
    complete_pipeline_run,
    save_pipeline_run_metadata,
    update_stage_status,
)


def test_build_pipeline_run_id_is_filesystem_safe():
    run_id = build_pipeline_run_id(datetime(2026, 6, 4, 10, 30, tzinfo=UTC))

    assert re.fullmatch(r"pipeline_20260604T103000000000Z_[a-f0-9]{8}", run_id)


def test_build_pipeline_run_metadata_uses_expected_contract():
    metadata = build_pipeline_run_metadata(
        pipeline_run_id="pipeline_test_001",
        started_at="2026-06-04T10:30:00+00:00",
        dataset_version={"dataset_name": "customer_churn", "version": "v1"},
        config_path=Path("configs/training.yaml"),
    )

    assert metadata == {
        "pipeline_run_id": "pipeline_test_001",
        "pipeline_version": PIPELINE_VERSION,
        "started_at": "2026-06-04T10:30:00+00:00",
        "completed_at": None,
        "status": "running",
        "stage_statuses": {},
        "failed_stage": None,
        "dataset_version": {"dataset_name": "customer_churn", "version": "v1"},
        "config_path": "configs\\training.yaml",
        "mlflow_run_ids": [],
        "champion_run_id": None,
    }


def test_update_stage_status_returns_updated_copy():
    metadata = build_pipeline_run_metadata(pipeline_run_id="pipeline_test_001")

    updated_metadata = update_stage_status(metadata, "validation", "passed")

    assert metadata["stage_statuses"] == {}
    assert updated_metadata["stage_statuses"] == {"validation": "passed"}


def test_build_pipeline_run_metadata_rejects_failed_status_without_failed_stage():
    try:
        build_pipeline_run_metadata(
            pipeline_run_id="pipeline_test_001",
            status="failed",
            completed_at="2026-06-04T10:35:00+00:00",
        )
    except PipelineRunMetadataError as exc:
        assert "failed_stage" in str(exc)
    else:
        raise AssertionError("Expected PipelineRunMetadataError for invalid failure.")


def test_complete_pipeline_run_records_success_outputs():
    metadata = build_pipeline_run_metadata(pipeline_run_id="pipeline_test_001")

    completed_metadata = complete_pipeline_run(
        metadata,
        status="passed",
        completed_at="2026-06-04T10:35:00+00:00",
        mlflow_run_ids=["mlflow-run-1", "mlflow-run-2"],
        champion_run_id="mlflow-run-2",
    )

    assert completed_metadata["status"] == "passed"
    assert completed_metadata["completed_at"] == "2026-06-04T10:35:00+00:00"
    assert completed_metadata["failed_stage"] is None
    assert completed_metadata["mlflow_run_ids"] == ["mlflow-run-1", "mlflow-run-2"]
    assert completed_metadata["champion_run_id"] == "mlflow-run-2"


def test_complete_pipeline_run_requires_failed_stage_for_failure():
    metadata = build_pipeline_run_metadata(pipeline_run_id="pipeline_test_001")

    try:
        complete_pipeline_run(metadata, status="failed")
    except PipelineRunMetadataError as exc:
        assert "failed_stage" in str(exc)
    else:
        raise AssertionError("Expected PipelineRunMetadataError for missing failed_stage.")


def test_build_pipeline_run_metadata_path_rejects_path_traversal():
    try:
        build_pipeline_run_metadata_path("../bad")
    except PipelineRunMetadataError as exc:
        assert "filesystem-safe" in str(exc)
    else:
        raise AssertionError("Expected PipelineRunMetadataError for unsafe run ID.")


def test_save_pipeline_run_metadata_persists_json(tmp_path):
    metadata = complete_pipeline_run(
        build_pipeline_run_metadata(pipeline_run_id="pipeline_test_001"),
        status="passed",
        completed_at="2026-06-04T10:35:00+00:00",
    )

    output_path = save_pipeline_run_metadata(metadata, output_dir=tmp_path)

    assert output_path == tmp_path / "pipeline_test_001.json"
    assert json.loads(output_path.read_text(encoding="utf-8")) == metadata

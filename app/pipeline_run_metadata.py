"""Pipeline run metadata helpers for V5 orchestration."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from app.utils.artifacts import ArtifactError, save_json

DEFAULT_PIPELINE_RUNS_DIR = Path("pipeline_runs")
PIPELINE_VERSION = "v5-c8"
VALID_PIPELINE_STATUSES = {"running", "passed", "failed"}
VALID_STAGE_STATUSES = {"pending", "running", "passed", "failed", "skipped"}
_SAFE_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class PipelineRunMetadataError(ValueError):
    """Raised when pipeline run metadata is invalid or cannot be persisted."""


def build_pipeline_run_id(started_at: datetime | None = None) -> str:
    """Build a filesystem-safe pipeline run ID."""
    timestamp_source = started_at or datetime.now(UTC)
    if timestamp_source.tzinfo is None:
        timestamp_source = timestamp_source.replace(tzinfo=UTC)
    timestamp = timestamp_source.astimezone(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"pipeline_{timestamp}_{uuid4().hex[:8]}"


def build_pipeline_run_metadata(
    *,
    pipeline_run_id: str | None = None,
    pipeline_version: str = PIPELINE_VERSION,
    started_at: str | None = None,
    completed_at: str | None = None,
    status: str = "running",
    stage_statuses: dict[str, str] | None = None,
    failed_stage: str | None = None,
    dataset_version: Any = None,
    config_path: str | Path = "configs/training.yaml",
    mlflow_run_ids: list[str] | None = None,
    champion_run_id: str | None = None,
) -> dict[str, Any]:
    """Build the canonical pipeline run metadata payload."""
    _validate_pipeline_status(status)
    stage_statuses = stage_statuses or {}
    _validate_stage_statuses(stage_statuses)
    if status == "running" and completed_at is not None:
        raise PipelineRunMetadataError("running runs cannot define completed_at.")
    if status in {"passed", "failed"} and completed_at is None:
        raise PipelineRunMetadataError("completed runs require completed_at.")
    if status == "failed" and not failed_stage:
        raise PipelineRunMetadataError("failed runs require failed_stage.")
    if status != "failed" and failed_stage is not None:
        raise PipelineRunMetadataError("failed_stage is only valid for failed runs.")

    run_id = pipeline_run_id or build_pipeline_run_id()
    _validate_pipeline_run_id(run_id)
    return {
        "pipeline_run_id": run_id,
        "pipeline_version": pipeline_version,
        "started_at": started_at or datetime.now(UTC).isoformat(),
        "completed_at": completed_at,
        "status": status,
        "stage_statuses": dict(stage_statuses),
        "failed_stage": failed_stage,
        "dataset_version": dataset_version,
        "config_path": str(config_path),
        "mlflow_run_ids": list(mlflow_run_ids or []),
        "champion_run_id": champion_run_id,
    }


def update_stage_status(
    metadata: dict[str, Any],
    stage_name: str,
    stage_status: str,
) -> dict[str, Any]:
    """Return metadata with one stage status updated."""
    if not stage_name:
        raise PipelineRunMetadataError("stage_name is required.")
    _validate_stage_status(stage_status)

    updated_metadata = deepcopy(metadata)
    stage_statuses = updated_metadata.setdefault("stage_statuses", {})
    if not isinstance(stage_statuses, dict):
        raise PipelineRunMetadataError("stage_statuses must be a mapping.")
    stage_statuses[stage_name] = stage_status
    return updated_metadata


def complete_pipeline_run(
    metadata: dict[str, Any],
    *,
    status: str,
    completed_at: str | None = None,
    failed_stage: str | None = None,
    mlflow_run_ids: list[str] | None = None,
    champion_run_id: str | None = None,
) -> dict[str, Any]:
    """Return metadata marked as passed or failed."""
    if status not in {"passed", "failed"}:
        raise PipelineRunMetadataError(
            "completed pipeline status must be passed or failed."
        )
    if status == "failed" and not failed_stage:
        raise PipelineRunMetadataError("failed runs require failed_stage.")
    if status == "passed" and failed_stage is not None:
        raise PipelineRunMetadataError("passed runs cannot define failed_stage.")

    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = status
    updated_metadata["completed_at"] = completed_at or datetime.now(UTC).isoformat()
    updated_metadata["failed_stage"] = failed_stage
    if mlflow_run_ids is not None:
        updated_metadata["mlflow_run_ids"] = list(mlflow_run_ids)
    if champion_run_id is not None:
        updated_metadata["champion_run_id"] = champion_run_id
    return updated_metadata


def build_pipeline_run_metadata_path(
    pipeline_run_id: str,
    output_dir: Path = DEFAULT_PIPELINE_RUNS_DIR,
) -> Path:
    """Build a safe metadata JSON path for one pipeline run."""
    _validate_pipeline_run_id(pipeline_run_id)
    return output_dir / f"{pipeline_run_id}.json"


def save_pipeline_run_metadata(
    metadata: dict[str, Any],
    output_dir: Path = DEFAULT_PIPELINE_RUNS_DIR,
) -> Path:
    """Persist pipeline run metadata and return the output path."""
    pipeline_run_id = metadata.get("pipeline_run_id")
    if not isinstance(pipeline_run_id, str):
        raise PipelineRunMetadataError("metadata requires pipeline_run_id.")

    path = build_pipeline_run_metadata_path(pipeline_run_id, output_dir)
    try:
        save_json(metadata, path)
    except ArtifactError as exc:
        raise PipelineRunMetadataError("Failed to save pipeline run metadata.") from exc
    return path


def _validate_pipeline_status(status: str) -> None:
    if status not in VALID_PIPELINE_STATUSES:
        raise PipelineRunMetadataError(
            "Invalid pipeline status: "
            f"{status}. Expected one of {sorted(VALID_PIPELINE_STATUSES)}."
        )


def _validate_stage_statuses(stage_statuses: dict[str, str]) -> None:
    for stage_name, stage_status in stage_statuses.items():
        if not stage_name:
            raise PipelineRunMetadataError("stage names cannot be empty.")
        _validate_stage_status(stage_status)


def _validate_stage_status(stage_status: str) -> None:
    if stage_status not in VALID_STAGE_STATUSES:
        raise PipelineRunMetadataError(
            "Invalid stage status: "
            f"{stage_status}. Expected one of {sorted(VALID_STAGE_STATUSES)}."
        )


def _validate_pipeline_run_id(pipeline_run_id: str) -> None:
    if not pipeline_run_id:
        raise PipelineRunMetadataError("pipeline_run_id is required.")
    if not _SAFE_RUN_ID_PATTERN.fullmatch(pipeline_run_id):
        raise PipelineRunMetadataError("pipeline_run_id must be filesystem-safe.")

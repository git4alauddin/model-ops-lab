"""Rollback a V10 local serving update to its recorded champion target."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    build_model_version_metadata_path,
    find_champion_model_versions,
    list_model_version_metadata,
    load_model_version_metadata,
    save_model_version_metadata,
)
from app.register_model import DEFAULT_MODEL_NAME
from app.retraining.candidate_run_metadata import (
    CANDIDATE_LOCAL_SERVING_ROLLED_BACK,
    CANDIDATE_LOCAL_SERVING_UPDATED,
    DEFAULT_RETRAINING_RUNS_DIR,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.local_serving_update import (
    CLOUD_RUN_UPDATE_NOT_PERFORMED,
    LocalServingUpdateError,
    _validate_updated_serving,
)
from app.rollback_model import ModelRollbackError, rollback_model_version
from app.utils.artifacts import ArtifactError, save_json

ROLLBACK_COMPLETED = "completed"
SERVING_UPDATE_ROLLED_BACK = "local_registry_rolled_back"


class LocalServingRollbackError(ValueError):
    """Raised when retraining-aware local serving rollback cannot complete."""


def rollback_local_retraining_serving(
    *,
    run_id: str,
    reason: str,
    rolled_back_by: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    rolled_back_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Restore the recorded rollback target and validate local serving."""
    timestamp = rolled_back_at or _utc_now()
    original_registry: list[dict[str, Any]] = []
    mutation_started = False

    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        rollback_target, retraining_champion = _validate_rollback_inputs(
            metadata=metadata,
            reason=reason,
            rolled_back_by=rolled_back_by,
            registry_dir=registry_dir,
            model_name=model_name,
        )
        original_registry = deepcopy(list_model_version_metadata(registry_dir))
        mutation_started = True
        restored_model = rollback_model_version(
            model_name=model_name,
            model_version=rollback_target["model_version"],
            rollback_reason=reason.strip(),
            output_dir=registry_dir,
        )
        readiness, prediction = _validate_updated_serving(
            registry_dir=registry_dir,
            model_name=model_name,
            expected_model_version=rollback_target["model_version"],
        )
        report = _build_rollback_report(
            metadata=metadata,
            restored_model=restored_model,
            retraining_champion=retraining_champion,
            readiness=readiness,
            prediction=prediction,
            reason=reason.strip(),
            rolled_back_by=rolled_back_by.strip(),
            rolled_back_at=timestamp,
        )
        report_path = _save_rollback_report(
            report,
            run_id=run_id,
            runs_dir=runs_dir,
        )
        updated_metadata = _update_retraining_metadata(
            metadata,
            report=report,
            report_path=report_path,
        )
        save_candidate_retraining_run_metadata(updated_metadata, runs_dir=runs_dir)
    except (
        ArtifactError,
        CandidateRetrainingRunError,
        LocalServingRollbackError,
        LocalServingUpdateError,
        ModelRegistryError,
        ModelRollbackError,
    ) as exc:
        if mutation_started:
            _restore_registry_snapshot(original_registry, registry_dir=registry_dir)
        if isinstance(exc, LocalServingRollbackError):
            raise
        raise LocalServingRollbackError(
            f"Local serving rollback failed for run_id={run_id}: {exc}"
        ) from exc

    return report, updated_metadata, report_path


def _validate_rollback_inputs(
    *,
    metadata: dict[str, Any],
    reason: str,
    rolled_back_by: str,
    registry_dir: Path,
    model_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if metadata.get("status") != CANDIDATE_LOCAL_SERVING_UPDATED:
        raise LocalServingRollbackError(
            "Local serving rollback requires status="
            f"{CANDIDATE_LOCAL_SERVING_UPDATED}; got {metadata.get('status')}."
        )
    if not isinstance(reason, str) or not reason.strip():
        raise LocalServingRollbackError("rollback reason is required.")
    if not isinstance(rolled_back_by, str) or not rolled_back_by.strip():
        raise LocalServingRollbackError("rolled_back_by is required.")

    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict):
        raise LocalServingRollbackError("Promotion metadata is required.")
    rollback_target = promotion.get("rollback_target")
    if not isinstance(rollback_target, dict):
        raise LocalServingRollbackError("Rollback target metadata is required.")
    target_version = rollback_target.get("model_version")
    if not isinstance(target_version, str) or not target_version:
        raise LocalServingRollbackError(
            "Rollback target model_version is required."
        )

    target_metadata = load_model_version_metadata(
        model_name,
        target_version,
        output_dir=registry_dir,
    )
    if target_metadata["status"] != "archived":
        raise LocalServingRollbackError(
            "Rollback target must currently be archived; "
            f"got {target_metadata['status']}."
        )
    if rollback_target.get("artifact_uri") != target_metadata["artifact_uri"]:
        raise LocalServingRollbackError(
            "Rollback target artifact URI does not match registry metadata."
        )

    champions = find_champion_model_versions(model_name, registry_dir)
    if len(champions) != 1:
        raise LocalServingRollbackError(
            "Local serving rollback requires exactly one current champion; "
            f"found {len(champions)}."
        )
    expected_retraining_version = promotion.get("local_champion_model_version")
    if champions[0]["model_version"] != expected_retraining_version:
        raise LocalServingRollbackError(
            "Current champion does not match the retraining champion recorded "
            "for this run."
        )
    return deepcopy(rollback_target), deepcopy(champions[0])


def _build_rollback_report(
    *,
    metadata: dict[str, Any],
    restored_model: dict[str, Any],
    retraining_champion: dict[str, Any],
    readiness: dict[str, Any],
    prediction: dict[str, Any],
    reason: str,
    rolled_back_by: str,
    rolled_back_at: str,
) -> dict[str, Any]:
    return {
        "run_id": metadata["run_id"],
        "rolled_back_at": rolled_back_at,
        "rolled_back_by": rolled_back_by,
        "reason": reason,
        "status": ROLLBACK_COMPLETED,
        "serving_update": SERVING_UPDATE_ROLLED_BACK,
        "cloud_run_update": CLOUD_RUN_UPDATE_NOT_PERFORMED,
        "restored_champion": deepcopy(restored_model),
        "archived_retraining_champion": deepcopy(retraining_champion),
        "readiness_validation": deepcopy(readiness),
        "prediction_validation": deepcopy(prediction),
        "boundary": {
            "local_registry_changed": True,
            "local_serving_rolled_back": True,
            "cloud_run_redeployed": False,
            "cloud_traffic_changed": False,
        },
    }


def _update_retraining_metadata(
    metadata: dict[str, Any],
    *,
    report: dict[str, Any],
    report_path: Path,
) -> dict[str, Any]:
    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = CANDIDATE_LOCAL_SERVING_ROLLED_BACK
    updated_metadata["promotion"].update(
        {
            "serving_update": SERVING_UPDATE_ROLLED_BACK,
            "local_rollback_status": ROLLBACK_COMPLETED,
            "local_rollback_report_path": str(report_path),
            "local_rolled_back_at": report["rolled_back_at"],
            "local_rolled_back_by": report["rolled_back_by"],
            "local_rollback_reason": report["reason"],
            "local_active_model_version": report["restored_champion"][
                "model_version"
            ],
            "cloud_run_update": CLOUD_RUN_UPDATE_NOT_PERFORMED,
        }
    )
    return updated_metadata


def _save_rollback_report(
    report: dict[str, Any],
    *,
    run_id: str,
    runs_dir: Path,
) -> Path:
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    report_path = metadata_path.parent / "local_serving_rollback_report.json"
    save_json(report, report_path)
    return report_path


def _restore_registry_snapshot(
    records: list[dict[str, Any]],
    *,
    registry_dir: Path,
) -> None:
    expected_paths = {
        build_model_version_metadata_path(
            record["model_name"],
            record["model_version"],
            registry_dir,
        )
        for record in records
    }
    if registry_dir.exists():
        for metadata_path in registry_dir.glob("*__*.json"):
            if metadata_path not in expected_paths:
                metadata_path.unlink()
    for record in records:
        save_model_version_metadata(record, output_dir=registry_dir)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()

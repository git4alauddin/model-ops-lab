"""Update the local serving champion from a governed retraining run."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib

from app.api.schemas import PredictionRequest
from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    archive_existing_champions,
    build_model_version_metadata,
    build_model_version_metadata_path,
    find_champion_model_versions,
    save_model_version_metadata,
)
from app.register_model import DEFAULT_MODEL_NAME
from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    CANDIDATE_LOCAL_SERVING_UPDATED,
    CANDIDATE_SERVING_HANDOFF_VALIDATED,
    DEFAULT_RETRAINING_RUNS_DIR,
    PROMOTION_DECISION_PROMOTED,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.serving_handoff import HANDOFF_READY
from app.serving.model_loader import ModelLoaderError, load_champion_model
from app.serving.predictor import PredictionError, predict_customer_churn
from app.serving.readiness import build_readiness_status
from app.utils.artifacts import ArtifactError, save_json

REGISTRY_UPDATE_COMPLETED = "completed"
SERVING_UPDATE_LOCAL_REGISTRY = "local_registry_completed"
CLOUD_RUN_UPDATE_NOT_PERFORMED = "not_performed"


class LocalServingUpdateError(ValueError):
    """Raised when the local registry and serving update cannot complete."""


def build_retraining_champion_metadata(
    *,
    metadata: dict[str, Any],
    model_name: str = DEFAULT_MODEL_NAME,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Build registry metadata for the promoted retraining candidate."""
    _validate_update_inputs(metadata)
    candidate = metadata["candidate"]
    lineage = metadata["lineage"]
    run_id = metadata["run_id"]
    timestamp = updated_at or _utc_now()
    registry_metadata = build_model_version_metadata(
        model_name=model_name,
        model_version=f"{lineage['dataset_version']}-{run_id}",
        status="champion",
        mlflow_run_id=run_id,
        candidate_name="v10_retraining_candidate",
        model_type=candidate["model_type"],
        dataset_name=lineage["dataset_name"],
        dataset_version=lineage["dataset_version"],
        dataset_checksum=lineage["dataset_checksum"],
        metrics=_numeric_metrics(candidate["metrics"]),
        artifact_uri=candidate["model_path"],
        created_at=timestamp,
        updated_at=timestamp,
        promoted_from="candidate",
        promotion_reason=(
            metadata["promotion"].get("reason")
            or "Approved V10 retraining candidate."
        ),
    )
    registry_metadata["lineage_source"] = "v10_retraining_run"
    registry_metadata["retraining_run_id"] = run_id
    return registry_metadata


def update_local_registry_and_serving(
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    updated_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Install the promoted candidate as local champion and validate serving."""
    timestamp = updated_at or _utc_now()
    previous_champions: list[dict[str, Any]] = []
    new_record_path: Path | None = None
    mutation_started = False

    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        champion_metadata = build_retraining_champion_metadata(
            metadata=metadata,
            model_name=model_name,
            updated_at=timestamp,
        )
        _validate_candidate_model_artifact(champion_metadata["artifact_uri"])

        new_record_path = build_model_version_metadata_path(
            model_name,
            champion_metadata["model_version"],
            registry_dir,
        )
        if new_record_path.exists():
            raise LocalServingUpdateError(
                f"Target registry version already exists: {new_record_path}"
            )

        previous_champions = deepcopy(
            find_champion_model_versions(model_name, registry_dir)
        )
        if len(previous_champions) != 1:
            raise LocalServingUpdateError(
                "Local serving update requires exactly one current champion; "
                f"found {len(previous_champions)}."
            )

        mutation_started = True
        archive_existing_champions(
            model_name,
            archive_reason=f"Archived by V10 retraining run {run_id}.",
            output_dir=registry_dir,
        )
        save_model_version_metadata(champion_metadata, output_dir=registry_dir)

        readiness, prediction = _validate_updated_serving(
            registry_dir=registry_dir,
            model_name=model_name,
            expected_model_version=champion_metadata["model_version"],
        )
        report = _build_update_report(
            metadata=metadata,
            champion_metadata=champion_metadata,
            previous_champions=previous_champions,
            readiness=readiness,
            prediction=prediction,
            updated_at=timestamp,
        )
        report_path = _save_update_report(
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
        LocalServingUpdateError,
        ModelLoaderError,
        ModelRegistryError,
        PredictionError,
    ) as exc:
        if mutation_started:
            _restore_previous_champions(
                previous_champions,
                registry_dir=registry_dir,
                new_record_path=new_record_path,
            )
        if isinstance(exc, LocalServingUpdateError):
            raise
        raise LocalServingUpdateError(
            f"Local serving update failed for run_id={run_id}: {exc}"
        ) from exc

    return report, updated_metadata, report_path


def _validate_update_inputs(metadata: dict[str, Any]) -> None:
    if metadata.get("status") != CANDIDATE_SERVING_HANDOFF_VALIDATED:
        raise LocalServingUpdateError(
            "Local serving update requires status="
            f"{CANDIDATE_SERVING_HANDOFF_VALIDATED}; got {metadata.get('status')}."
        )
    if metadata.get("approval", {}).get("state") != APPROVAL_APPROVED:
        raise LocalServingUpdateError(
            "Local serving update requires approval.state=approved."
        )

    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict):
        raise LocalServingUpdateError("Promotion metadata is required.")
    if promotion.get("decision") != PROMOTION_DECISION_PROMOTED:
        raise LocalServingUpdateError(
            "Local serving update requires promotion.decision=promoted."
        )
    if promotion.get("serving_handoff_status") != HANDOFF_READY:
        raise LocalServingUpdateError(
            "Local serving update requires serving_handoff_status=ready."
        )
    if promotion.get("serving_update_ready") is not True:
        raise LocalServingUpdateError(
            "Local serving update requires serving_update_ready=true."
        )

    candidate = metadata.get("candidate")
    if not isinstance(candidate, dict):
        raise LocalServingUpdateError("Candidate metadata is required.")
    required_candidate_fields = ("model_path", "model_type", "metrics")
    missing = [
        field for field in required_candidate_fields if not candidate.get(field)
    ]
    if missing:
        raise LocalServingUpdateError(
            f"Candidate serving fields are missing: {missing}"
        )


def _validate_candidate_model_artifact(artifact_uri: str) -> None:
    path = Path(artifact_uri)
    if not path.is_file():
        raise LocalServingUpdateError(
            f"Candidate model artifact not found: {path}"
        )
    try:
        model = joblib.load(path)
    except Exception as exc:
        raise LocalServingUpdateError(
            f"Candidate model artifact could not be loaded: {path}"
        ) from exc
    if not hasattr(model, "predict"):
        raise LocalServingUpdateError(
            "Candidate model artifact must expose predict()."
        )


def _validate_updated_serving(
    *,
    registry_dir: Path,
    model_name: str,
    expected_model_version: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    readiness = build_readiness_status(
        model_name=model_name,
        registry_dir=registry_dir,
    )
    if readiness.get("status") != "ready":
        raise LocalServingUpdateError(
            f"Local readiness validation failed: {readiness}"
        )
    if readiness.get("model_version") != expected_model_version:
        raise LocalServingUpdateError(
            "Readiness returned an unexpected champion model version."
        )

    loaded_model = load_champion_model(
        model_name=model_name,
        registry_dir=registry_dir,
    )
    prediction = predict_customer_churn(
        _smoke_prediction_request(),
        loaded_model,
        request_id="v10-local-serving-smoke-test",
    ).model_dump()
    if prediction["model_version"] != expected_model_version:
        raise LocalServingUpdateError(
            "Prediction returned an unexpected champion model version."
        )
    return readiness, prediction


def _build_update_report(
    *,
    metadata: dict[str, Any],
    champion_metadata: dict[str, Any],
    previous_champions: list[dict[str, Any]],
    readiness: dict[str, Any],
    prediction: dict[str, Any],
    updated_at: str,
) -> dict[str, Any]:
    return {
        "run_id": metadata["run_id"],
        "updated_at": updated_at,
        "status": "completed",
        "registry_update": REGISTRY_UPDATE_COMPLETED,
        "serving_update": SERVING_UPDATE_LOCAL_REGISTRY,
        "cloud_run_update": CLOUD_RUN_UPDATE_NOT_PERFORMED,
        "new_champion": deepcopy(champion_metadata),
        "previous_champions": deepcopy(previous_champions),
        "rollback_target": deepcopy(metadata["promotion"]["rollback_target"]),
        "readiness_validation": deepcopy(readiness),
        "prediction_validation": deepcopy(prediction),
        "boundary": {
            "local_registry_changed": True,
            "local_serving_changed": True,
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
    updated_metadata["status"] = CANDIDATE_LOCAL_SERVING_UPDATED
    updated_metadata["promotion"].update(
        {
            "registry_update": REGISTRY_UPDATE_COMPLETED,
            "serving_update": SERVING_UPDATE_LOCAL_REGISTRY,
            "local_serving_update_report_path": str(report_path),
            "local_serving_updated_at": report["updated_at"],
            "local_champion_model_version": report["new_champion"][
                "model_version"
            ],
            "cloud_run_update": CLOUD_RUN_UPDATE_NOT_PERFORMED,
        }
    )
    return updated_metadata


def _save_update_report(
    report: dict[str, Any],
    *,
    run_id: str,
    runs_dir: Path,
) -> Path:
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    report_path = metadata_path.parent / "local_serving_update_report.json"
    save_json(report, report_path)
    return report_path


def _restore_previous_champions(
    previous_champions: list[dict[str, Any]],
    *,
    registry_dir: Path,
    new_record_path: Path | None,
) -> None:
    if new_record_path is not None and new_record_path.exists():
        new_record_path.unlink()
    for champion in previous_champions:
        save_model_version_metadata(champion, output_dir=registry_dir)


def _numeric_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    numeric_metrics = {
        name: float(value)
        for name, value in metrics.items()
        if isinstance(value, int | float) and not isinstance(value, bool)
    }
    if not numeric_metrics:
        raise LocalServingUpdateError(
            "Candidate registry metrics must contain numeric values."
        )
    return numeric_metrics


def _smoke_prediction_request() -> PredictionRequest:
    return PredictionRequest(
        schema_version="v1",
        tenure_months=12,
        monthly_charges=79.5,
        total_charges=950.0,
        contract_type="month_to_month",
        internet_service="fiber_optic",
        payment_method="credit_card",
        is_senior=False,
    )


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()

"""Candidate retraining run metadata for V10."""

from copy import deepcopy
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any

import yaml

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    find_champion_model_versions,
)
from app.observability.retraining_trigger import (
    DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
    RETRAINING_RECOMMENDED,
)
from app.register_model import DEFAULT_MODEL_NAME
from app.utils.artifacts import ArtifactError, save_json

DEFAULT_RETRAINING_RUNS_DIR = Path("retraining_runs")
DEFAULT_TRAINING_CONFIG_PATH = Path("configs/training.yaml")
DEFAULT_DATASET_VERSION_PATH = Path("data_versions/customer_churn/v1.yaml")
DEFAULT_SCHEMA_PATH = Path("schema_versions/customer_churn_v1.yaml")

CANDIDATE_RUN_INITIALIZED = "candidate_run_initialized"
CANDIDATE_TRAINED = "candidate_trained"
CANDIDATE_COMPARED = "candidate_compared"
CANDIDATE_APPROVAL_RECORDED = "candidate_approval_recorded"
CANDIDATE_PROMOTED = "candidate_promoted"
CANDIDATE_SERVING_HANDOFF_VALIDATED = "candidate_serving_handoff_validated"
APPROVAL_PENDING = "pending"
APPROVAL_APPROVED = "approved"
APPROVAL_REJECTED = "rejected"
APPROVAL_NEEDS_REVIEW = "needs_review"
PROMOTION_PENDING_EVALUATION = "pending_evaluation"
PROMOTION_DECISION_PENDING = "pending"
PROMOTION_DECISION_PROMOTED = "promoted"
VALID_APPROVAL_STATES = {
    APPROVAL_APPROVED,
    APPROVAL_NEEDS_REVIEW,
    APPROVAL_PENDING,
    APPROVAL_REJECTED,
}
VALID_PROMOTION_DECISIONS = {
    PROMOTION_DECISION_PENDING,
    PROMOTION_DECISION_PROMOTED,
}
VALID_CANDIDATE_RUN_STATUSES = {
    CANDIDATE_APPROVAL_RECORDED,
    CANDIDATE_COMPARED,
    CANDIDATE_PROMOTED,
    CANDIDATE_RUN_INITIALIZED,
    CANDIDATE_SERVING_HANDOFF_VALIDATED,
    CANDIDATE_TRAINED,
}
_SAFE_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class CandidateRetrainingRunError(ValueError):
    """Raised when candidate retraining metadata cannot be created."""


def load_json_object(path: Path) -> dict[str, Any]:
    """Load a JSON object used by candidate retraining metadata."""
    if not path.is_file():
        raise CandidateRetrainingRunError(f"JSON metadata source not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CandidateRetrainingRunError(f"Invalid JSON metadata source: {path}") from exc
    if not isinstance(data, dict):
        raise CandidateRetrainingRunError("JSON metadata source must be an object.")
    return data


def load_yaml_object(path: Path) -> dict[str, Any]:
    """Load a YAML object used by candidate retraining metadata."""
    if not path.is_file():
        raise CandidateRetrainingRunError(f"YAML metadata source not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CandidateRetrainingRunError(f"Invalid YAML metadata source: {path}") from exc
    if not isinstance(data, dict):
        raise CandidateRetrainingRunError("YAML metadata source must be an object.")
    return data


def build_candidate_retraining_run_metadata_path(
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> Path:
    """Build a safe metadata path for one candidate retraining run."""
    _validate_run_id(run_id)
    return runs_dir / run_id / "retraining_metadata.json"


def load_candidate_retraining_run_metadata(
    run_id: str,
    *,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> dict[str, Any]:
    """Load one candidate retraining run metadata record."""
    metadata = load_json_object(
        build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    )
    _validate_candidate_retraining_run_metadata(metadata)
    return metadata


def find_previous_production_model(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any] | None:
    """Return the single current champion model as rollback context."""
    try:
        champions = find_champion_model_versions(model_name, registry_dir)
    except ModelRegistryError as exc:
        raise CandidateRetrainingRunError(
            f"Unable to read production model registry: {exc}"
        ) from exc

    if not champions:
        return None
    if len(champions) > 1:
        raise CandidateRetrainingRunError(
            f"Expected one production champion for {model_name}, found {len(champions)}."
        )

    champion = champions[0]
    return {
        "model_name": champion["model_name"],
        "model_version": champion["model_version"],
        "status": champion["status"],
        "mlflow_run_id": champion["mlflow_run_id"],
        "candidate_name": champion["candidate_name"],
        "model_type": champion["model_type"],
        "dataset_name": champion["dataset_name"],
        "dataset_version": champion["dataset_version"],
        "dataset_checksum": champion["dataset_checksum"],
        "metrics": deepcopy(champion["metrics"]),
        "artifact_uri": champion["artifact_uri"],
        "updated_at": champion["updated_at"],
    }


def build_candidate_retraining_run_metadata(
    *,
    trigger_decision: dict[str, Any],
    training_config: dict[str, Any],
    dataset_version: dict[str, Any],
    schema: dict[str, Any],
    previous_production_model: dict[str, Any] | None,
    run_id: str | None = None,
    created_at: str | None = None,
    trigger_source_path: Path = DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
    training_config_path: Path = DEFAULT_TRAINING_CONFIG_PATH,
    dataset_version_path: Path = DEFAULT_DATASET_VERSION_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Build candidate retraining run metadata without training a model."""
    _validate_retraining_trigger(trigger_decision)
    resolved_created_at = created_at or _utc_now()
    resolved_run_id = run_id or _build_run_id(resolved_created_at)
    dataset_config = _section(training_config, "dataset")

    metadata = {
        "run_id": resolved_run_id,
        "created_at": resolved_created_at,
        "status": CANDIDATE_RUN_INITIALIZED,
        "trigger": {
            "decision": trigger_decision["decision"],
            "recommendation": trigger_decision.get("recommendation"),
            "reason_count": trigger_decision.get("reason_count", 0),
            "reasons": deepcopy(trigger_decision.get("reasons", [])),
            "source_reports": deepcopy(trigger_decision.get("source_reports", {})),
            "source_freshness": deepcopy(trigger_decision.get("source_freshness", {})),
            "trigger_source_path": str(trigger_source_path),
        },
        "lineage": {
            "training_config_path": str(training_config_path),
            "dataset_version_path": str(dataset_version_path),
            "schema_path": str(schema_path),
            "dataset_name": dataset_version.get("dataset_name") or schema.get("name"),
            "dataset_version": dataset_version.get("version") or schema.get("version"),
            "dataset_path": dataset_config.get("path") or dataset_version.get("path"),
            "target_column": (
                dataset_config.get("target_column")
                or dataset_version.get("target_column")
                or schema.get("target_column")
            ),
            "schema_name": schema.get("name"),
            "schema_version": schema.get("version"),
            "dataset_checksum": _dataset_checksum(dataset_version),
        },
        "previous_production_model": deepcopy(previous_production_model),
        "candidate": {
            "model_path": None,
            "metrics_path": None,
            "comparison_report_path": None,
        },
        "regression_gates": {
            "status": "not_evaluated",
            "results": [],
        },
        "promotion": {
            "recommendation": PROMOTION_PENDING_EVALUATION,
            "decision": PROMOTION_DECISION_PENDING,
            "promoted_at": None,
            "rollback_target": _rollback_target(previous_production_model),
        },
        "approval": {
            "state": APPROVAL_PENDING,
            "approved_by": None,
            "approved_at": None,
            "notes": None,
        },
    }
    _validate_candidate_retraining_run_metadata(metadata)
    return metadata


def save_candidate_retraining_run_metadata(
    metadata: dict[str, Any],
    *,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> Path:
    """Persist candidate retraining metadata under retraining_runs/<run_id>/."""
    _validate_candidate_retraining_run_metadata(metadata)
    run_id = metadata["run_id"]
    path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    try:
        save_json(metadata, path)
    except ArtifactError as exc:
        raise CandidateRetrainingRunError(
            f"Failed to save candidate retraining metadata: {path}"
        ) from exc
    return path


def build_and_save_candidate_retraining_run_metadata(
    *,
    trigger_decision_path: Path = DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
    training_config_path: Path = DEFAULT_TRAINING_CONFIG_PATH,
    dataset_version_path: Path = DEFAULT_DATASET_VERSION_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
    run_id: str | None = None,
    created_at: str | None = None,
) -> tuple[dict[str, Any], Path]:
    """Load governance inputs and persist initialized candidate run metadata."""
    trigger_decision = load_json_object(trigger_decision_path)
    training_config = load_yaml_object(training_config_path)
    dataset_version = load_yaml_object(dataset_version_path)
    schema = load_yaml_object(schema_path)
    previous_production_model = find_previous_production_model(
        model_name=model_name,
        registry_dir=registry_dir,
    )
    metadata = build_candidate_retraining_run_metadata(
        trigger_decision=trigger_decision,
        training_config=training_config,
        dataset_version=dataset_version,
        schema=schema,
        previous_production_model=previous_production_model,
        run_id=run_id,
        created_at=created_at,
        trigger_source_path=trigger_decision_path,
        training_config_path=training_config_path,
        dataset_version_path=dataset_version_path,
        schema_path=schema_path,
    )
    output_path = save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)
    return metadata, output_path


def _validate_retraining_trigger(trigger_decision: dict[str, Any]) -> None:
    if not isinstance(trigger_decision, dict):
        raise CandidateRetrainingRunError("Retraining trigger decision must be an object.")
    decision = trigger_decision.get("decision")
    if decision != RETRAINING_RECOMMENDED:
        raise CandidateRetrainingRunError(
            "Candidate retraining run requires decision="
            f"{RETRAINING_RECOMMENDED}; got {decision}."
        )


def _validate_candidate_retraining_run_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise CandidateRetrainingRunError("Candidate retraining metadata must be an object.")
    required_fields = (
        "run_id",
        "created_at",
        "status",
        "trigger",
        "lineage",
        "candidate",
        "regression_gates",
        "promotion",
        "approval",
    )
    missing = [field for field in required_fields if field not in metadata]
    if missing:
        raise CandidateRetrainingRunError(
            f"Missing candidate retraining metadata fields: {missing}"
        )
    if metadata["status"] not in VALID_CANDIDATE_RUN_STATUSES:
        raise CandidateRetrainingRunError(
            "Invalid candidate retraining status: "
            f"{metadata['status']}. Expected one of {sorted(VALID_CANDIDATE_RUN_STATUSES)}."
        )
    approval_state = metadata["approval"].get("state")
    if approval_state not in VALID_APPROVAL_STATES:
        raise CandidateRetrainingRunError(
            "Invalid approval state: "
            f"{approval_state}. Expected one of {sorted(VALID_APPROVAL_STATES)}."
        )
    promotion_decision = metadata["promotion"].get("decision")
    if promotion_decision not in VALID_PROMOTION_DECISIONS:
        raise CandidateRetrainingRunError(
            "Invalid promotion decision: "
            f"{promotion_decision}. Expected one of {sorted(VALID_PROMOTION_DECISIONS)}."
        )


def _section(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name)
    return value if isinstance(value, dict) else {}


def _dataset_checksum(dataset_version: dict[str, Any]) -> str | None:
    checksum = dataset_version.get("checksum")
    if isinstance(checksum, dict):
        value = checksum.get("value")
        return str(value) if value else None
    return None


def _rollback_target(
    previous_production_model: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if previous_production_model is None:
        return None
    return {
        "model_name": previous_production_model["model_name"],
        "model_version": previous_production_model["model_version"],
        "artifact_uri": previous_production_model["artifact_uri"],
    }


def _build_run_id(created_at: str) -> str:
    safe_timestamp = (
        created_at.replace("+00:00", "Z")
        .replace(":", "")
        .replace("-", "")
        .replace(".", "")
    )
    return f"retrain-{safe_timestamp}"


def _validate_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or not run_id:
        raise CandidateRetrainingRunError("run_id is required.")
    if not _SAFE_RUN_ID_PATTERN.fullmatch(run_id):
        raise CandidateRetrainingRunError("run_id must be filesystem-safe.")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()

"""Readiness checks for the serving API."""

from pathlib import Path
from typing import Any

from app.api.constants import SERVICE_NAME
from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    find_champion_model_versions,
)
from app.register_model import DEFAULT_MODEL_NAME


def build_readiness_status(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Return whether the API has one champion model available to serve."""
    try:
        champions = find_champion_model_versions(model_name, registry_dir)
    except ModelRegistryError as exc:
        return _not_ready(f"Model registry unavailable: {exc}")

    if not champions:
        return _not_ready("No champion model found.")
    if len(champions) > 1:
        return _not_ready("Multiple champion models found.")

    champion = champions[0]
    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "model_loaded": True,
        "model_name": champion["model_name"],
        "model_version": champion["model_version"],
        "mlflow_run_id": champion["mlflow_run_id"],
    }


def _not_ready(reason: str) -> dict[str, Any]:
    return {
        "status": "not_ready",
        "service": SERVICE_NAME,
        "model_loaded": False,
        "reason": reason,
    }

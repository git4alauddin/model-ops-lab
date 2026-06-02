"""Artifact persistence helpers for V1."""

import json
from pathlib import Path
from typing import Any

import joblib


class ArtifactError(ValueError):
    """Raised when artifact path building or persistence fails."""


def ensure_artifact_dir(path: Path) -> Path:
    """Create and return artifact directory path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_artifact_paths(config: dict[str, Any]) -> dict[str, Path]:
    """Build artifact file paths from config."""
    artifact_config = config.get("artifacts")
    if not isinstance(artifact_config, dict):
        raise ArtifactError("Missing artifacts config section.")

    required_keys = (
        "dir",
        "model_file",
        "metrics_file",
        "config_snapshot_file",
        "metadata_file",
    )
    missing_keys = [
        key for key in required_keys if not artifact_config.get(key)
    ]
    if missing_keys:
        raise ArtifactError(f"Missing artifact config keys: {missing_keys}")

    artifact_dir = Path(artifact_config["dir"])
    return {
        "model": artifact_dir / artifact_config["model_file"],
        "metrics": artifact_dir / artifact_config["metrics_file"],
        "config_snapshot": artifact_dir / artifact_config["config_snapshot_file"],
        "metadata": artifact_dir / artifact_config["metadata_file"],
    }


def save_json(data: dict[str, Any], path: Path) -> None:
    """Persist JSON data to disk."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except (OSError, TypeError) as exc:
        raise ArtifactError(f"Failed to save JSON artifact: {path}") from exc


def save_model(model: Any, path: Path) -> None:
    """Persist a model artifact to disk."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
    except (OSError, TypeError, ValueError) as exc:
        raise ArtifactError(f"Failed to save model artifact: {path}") from exc

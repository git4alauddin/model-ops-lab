"""Registry-based model loading for the serving layer."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    find_champion_model_versions,
)
from app.register_model import DEFAULT_MODEL_NAME

MLFLOW_RUN_URI_PREFIX = "mlflow-run://"


class ModelLoaderError(ValueError):
    """Raised when a serving model cannot be resolved or loaded."""


@dataclass(frozen=True)
class LoadedModel:
    """Loaded model object with registry lineage metadata."""

    model: Any
    metadata: dict[str, Any]
    artifact_path: Path


def load_champion_model(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
    mlruns_dir: Path = Path("mlruns"),
) -> LoadedModel:
    """Load the active champion model from local registry metadata."""
    metadata = resolve_champion_model_metadata(
        model_name=model_name,
        registry_dir=registry_dir,
    )
    artifact_path = resolve_model_artifact_path(
        metadata["artifact_uri"],
        mlruns_dir=mlruns_dir,
    )
    try:
        model = joblib.load(artifact_path)
    except Exception as exc:
        raise ModelLoaderError(
            f"Failed to load model artifact: {artifact_path}"
        ) from exc

    return LoadedModel(
        model=model,
        metadata=metadata,
        artifact_path=artifact_path,
    )


def resolve_champion_model_metadata(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Return exactly one champion metadata record for serving."""
    try:
        champions = find_champion_model_versions(model_name, registry_dir)
    except ModelRegistryError as exc:
        raise ModelLoaderError(f"Model registry unavailable: {exc}") from exc

    if not champions:
        raise ModelLoaderError("No champion model found.")
    if len(champions) > 1:
        raise ModelLoaderError("Multiple champion models found.")
    return champions[0]


def resolve_model_artifact_path(
    artifact_uri: str,
    *,
    mlruns_dir: Path = Path("mlruns"),
) -> Path:
    """Resolve a registry artifact URI to a local model artifact path."""
    if not isinstance(artifact_uri, str) or not artifact_uri:
        raise ModelLoaderError("artifact_uri is required.")

    if artifact_uri.startswith(MLFLOW_RUN_URI_PREFIX):
        return _resolve_mlflow_run_artifact_path(artifact_uri, mlruns_dir)

    path = Path(artifact_uri)
    if not path.exists():
        raise ModelLoaderError(f"Model artifact not found: {path}")
    if path.is_dir():
        path = path / "model.pkl"
    if not path.exists():
        raise ModelLoaderError(f"Model artifact not found: {path}")
    return path


def _resolve_mlflow_run_artifact_path(artifact_uri: str, mlruns_dir: Path) -> Path:
    suffix = artifact_uri.removeprefix(MLFLOW_RUN_URI_PREFIX)
    run_id, separator, artifact_reference = suffix.partition("/artifacts/")
    if not run_id or not separator:
        raise ModelLoaderError(f"Invalid MLflow run artifact URI: {artifact_uri}")

    artifact_root = _find_mlflow_run_artifact_root(run_id, mlruns_dir)
    artifact_path = artifact_root / artifact_reference
    candidates = _build_artifact_path_candidates(artifact_path)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    raise ModelLoaderError(f"Model artifact not found for URI: {artifact_uri}")


def _find_mlflow_run_artifact_root(run_id: str, mlruns_dir: Path) -> Path:
    if not mlruns_dir.exists():
        raise ModelLoaderError(f"MLflow runs directory not found: {mlruns_dir}")

    matches = [
        run_dir / "artifacts"
        for run_dir in mlruns_dir.glob(f"*/{run_id}")
        if (run_dir / "artifacts").exists()
    ]
    if not matches:
        raise ModelLoaderError(f"MLflow artifact directory not found for run: {run_id}")
    if len(matches) > 1:
        raise ModelLoaderError(f"Multiple MLflow artifact directories found for run: {run_id}")
    return matches[0]


def _build_artifact_path_candidates(artifact_path: Path) -> list[Path]:
    candidates = [artifact_path]
    if artifact_path.suffix == "":
        candidates.append(artifact_path.with_suffix(".pkl"))
        candidates.append(artifact_path / "model.pkl")
    if artifact_path.is_dir():
        candidates.append(artifact_path / "model.pkl")
    return candidates

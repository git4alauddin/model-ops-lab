"""Register the selected champion run as a V6 candidate model version."""

import json
from pathlib import Path
from typing import Any

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    build_model_version_metadata,
    save_model_version_metadata,
)
from app.utils.logger import get_logger

DEFAULT_CHAMPION_REPORT_PATH = Path("reports/champion_run.json")
DEFAULT_MODEL_NAME = "customer_churn_model"
LOGGER_NAME = "modelopslab.model_registry"


class ModelRegistrationError(ValueError):
    """Raised when a champion run cannot be registered."""


def register_champion_model(
    champion_report_path: str | Path = DEFAULT_CHAMPION_REPORT_PATH,
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    model_version: str | None = None,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Register the champion run from a champion report as a candidate model."""
    champion_report = load_champion_report(champion_report_path)
    champion = _extract_champion(champion_report)
    resolved_model_version = model_version or _build_model_version(champion)
    metadata = build_model_version_metadata(
        model_name=model_name,
        model_version=resolved_model_version,
        status="candidate",
        mlflow_run_id=champion["run_id"],
        candidate_name=champion["candidate_name"],
        model_type=champion["model_type"],
        dataset_name=champion["dataset_name"],
        dataset_version=champion["dataset_version"],
        dataset_checksum=champion["dataset_checksum"],
        metrics=champion["metrics"],
        artifact_uri=_resolve_artifact_uri(champion),
        promotion_reason=champion.get("selection_reason"),
    )
    save_model_version_metadata(metadata, output_dir=output_dir)
    return metadata


def load_champion_report(champion_report_path: str | Path) -> dict[str, Any]:
    """Load a champion selection report from disk."""
    path = Path(champion_report_path)
    try:
        with path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except FileNotFoundError as exc:
        raise ModelRegistrationError(f"Champion report not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ModelRegistrationError(f"Invalid champion report JSON: {path}") from exc
    except OSError as exc:
        raise ModelRegistrationError(f"Unable to read champion report: {path}") from exc

    if not isinstance(report, dict):
        raise ModelRegistrationError("Champion report root must be a dictionary.")
    return report


def main() -> None:
    """Register the current champion report as a candidate model version."""
    logger = get_logger(LOGGER_NAME)
    try:
        metadata = register_champion_model()
    except (ModelRegistrationError, ModelRegistryError) as exc:
        logger.error("Model registration failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Registered candidate model. model_name=%s model_version=%s run_id=%s",
        metadata["model_name"],
        metadata["model_version"],
        metadata["mlflow_run_id"],
    )


def _extract_champion(champion_report: dict[str, Any]) -> dict[str, Any]:
    champion = champion_report.get("champion")
    if not isinstance(champion, dict):
        raise ModelRegistrationError("Champion report requires a champion object.")

    required_fields = (
        "run_id",
        "candidate_name",
        "model_type",
        "dataset_name",
        "dataset_version",
        "dataset_checksum",
        "metrics",
    )
    missing_fields = [
        field for field in required_fields if champion.get(field) in (None, "")
    ]
    if missing_fields:
        raise ModelRegistrationError(
            f"Champion report is missing champion fields: {missing_fields}"
        )
    if not isinstance(champion["metrics"], dict):
        raise ModelRegistrationError("Champion metrics must be a dictionary.")
    return champion


def _build_model_version(champion: dict[str, Any]) -> str:
    run_id_prefix = str(champion["run_id"])[:8]
    return f"{champion['dataset_version']}-{run_id_prefix}"


def _resolve_artifact_uri(champion: dict[str, Any]) -> str:
    artifact_uri = champion.get("artifact_uri")
    if isinstance(artifact_uri, str) and artifact_uri:
        return artifact_uri

    artifacts = champion.get("artifacts")
    if isinstance(artifacts, dict):
        model_artifact = artifacts.get("model")
        if isinstance(model_artifact, str) and model_artifact:
            return model_artifact

    return f"mlflow-run://{champion['run_id']}/artifacts/model"


if __name__ == "__main__":
    main()

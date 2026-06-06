"""Rollback an archived V6 model version to champion."""

import argparse
from pathlib import Path
from typing import Any

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    archive_existing_champions,
    load_model_version_metadata,
    save_model_version_metadata,
    update_model_lifecycle_status,
)
from app.register_model import DEFAULT_MODEL_NAME
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.model_registry"


class ModelRollbackError(ValueError):
    """Raised when a model rollback cannot be completed."""


def rollback_model_version(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    model_version: str,
    rollback_reason: str,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Rollback an archived model version to champion."""
    if not isinstance(rollback_reason, str) or not rollback_reason.strip():
        raise ModelRollbackError("rollback_reason is required.")

    metadata = load_model_version_metadata(
        model_name,
        model_version,
        output_dir=output_dir,
    )
    if metadata["status"] != "archived":
        raise ModelRollbackError(
            "Only archived model versions can be rolled back to champion. "
            f"Current status is {metadata['status']}."
        )

    archive_existing_champions(
        model_name,
        exclude_model_version=model_version,
        archive_reason=f"Archived by rollback to {model_version}.",
        output_dir=output_dir,
    )
    rollback_metadata = update_model_lifecycle_status(
        metadata,
        status="champion",
        promotion_reason=rollback_reason.strip(),
    )
    save_model_version_metadata(rollback_metadata, output_dir=output_dir)
    return rollback_metadata


def main() -> None:
    """Rollback an archived model version to champion."""
    args = _parse_args()
    logger = get_logger(LOGGER_NAME)
    try:
        metadata = rollback_model_version(
            model_name=args.model_name,
            model_version=args.model_version,
            rollback_reason=args.reason,
            output_dir=Path(args.output_dir),
        )
    except (ModelRollbackError, ModelRegistryError) as exc:
        logger.error("Model rollback failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Rolled back model to champion. model_name=%s model_version=%s run_id=%s",
        metadata["model_name"],
        metadata["model_version"],
        metadata["mlflow_run_id"],
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rollback an archived model registry version to champion."
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help="Registered model name to rollback.",
    )
    parser.add_argument(
        "--model-version",
        required=True,
        help="Archived model version to restore as champion.",
    )
    parser.add_argument(
        "--reason",
        required=True,
        help="Rollback reason recorded in registry metadata.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_MODEL_REGISTRY_DIR),
        help="Local model registry directory.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()

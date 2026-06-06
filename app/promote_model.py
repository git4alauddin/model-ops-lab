"""Promote a registered V6 candidate model version to champion."""

from pathlib import Path
from typing import Any

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    load_model_version_metadata,
    save_model_version_metadata,
    update_model_lifecycle_status,
)
from app.register_model import (
    DEFAULT_CHAMPION_REPORT_PATH,
    DEFAULT_MODEL_NAME,
    ModelRegistrationError,
    load_champion_report,
)
from app.utils.logger import get_logger

DEFAULT_PROMOTION_REASON = "Manual promotion to champion."
LOGGER_NAME = "modelopslab.model_registry"


class ModelPromotionError(ValueError):
    """Raised when a model version cannot be promoted."""


def promote_candidate_model(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    model_version: str | None = None,
    promotion_reason: str = DEFAULT_PROMOTION_REASON,
    champion_report_path: str | Path = DEFAULT_CHAMPION_REPORT_PATH,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Promote one registered candidate model version to champion."""
    resolved_model_version = model_version or _resolve_model_version_from_report(
        champion_report_path
    )
    metadata = load_model_version_metadata(
        model_name,
        resolved_model_version,
        output_dir=output_dir,
    )
    if metadata["status"] != "candidate":
        raise ModelPromotionError(
            "Only candidate model versions can be promoted to champion. "
            f"Current status is {metadata['status']}."
        )

    promoted_metadata = update_model_lifecycle_status(
        metadata,
        status="champion",
        promotion_reason=promotion_reason,
    )
    save_model_version_metadata(promoted_metadata, output_dir=output_dir)
    return promoted_metadata


def main() -> None:
    """Promote the current registered candidate model to champion."""
    logger = get_logger(LOGGER_NAME)
    try:
        metadata = promote_candidate_model()
    except (ModelPromotionError, ModelRegistrationError, ModelRegistryError) as exc:
        logger.error("Model promotion failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Promoted model to champion. model_name=%s model_version=%s run_id=%s",
        metadata["model_name"],
        metadata["model_version"],
        metadata["mlflow_run_id"],
    )


def _resolve_model_version_from_report(champion_report_path: str | Path) -> str:
    champion_report = load_champion_report(champion_report_path)
    champion = champion_report.get("champion")
    if not isinstance(champion, dict):
        raise ModelPromotionError("Champion report requires a champion object.")

    run_id = champion.get("run_id")
    dataset_version = champion.get("dataset_version")
    if not isinstance(run_id, str) or not run_id:
        raise ModelPromotionError("Champion report requires champion.run_id.")
    if not isinstance(dataset_version, str) or not dataset_version:
        raise ModelPromotionError("Champion report requires champion.dataset_version.")

    return f"{dataset_version}-{run_id[:8]}"


if __name__ == "__main__":
    main()

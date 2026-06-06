"""Query local V6 model registry records."""

from pathlib import Path
from typing import Any

from app.model_registry import (
    DEFAULT_MODEL_REGISTRY_DIR,
    ModelRegistryError,
    find_champion_model_versions,
    list_model_version_metadata,
)
from app.register_model import DEFAULT_MODEL_NAME
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.model_registry"


class ModelRegistryQueryError(ValueError):
    """Raised when the model registry cannot be queried."""


def build_registry_summary(
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Build a compact summary of local registry state."""
    records = list_model_version_metadata(output_dir)
    if not records:
        raise ModelRegistryQueryError("No model registry records found.")

    model_records = [
        record for record in records if record["model_name"] == model_name
    ]
    if not model_records:
        raise ModelRegistryQueryError(
            f"No model registry records found for model_name={model_name}."
        )

    champions = find_champion_model_versions(model_name, output_dir)
    champion = champions[0] if champions else None
    return {
        "model_name": model_name,
        "champion": champion,
        "records": sorted(
            model_records,
            key=lambda record: (record["status"], record["model_version"]),
        ),
    }


def format_registry_summary(summary: dict[str, Any]) -> str:
    """Return a readable model registry summary."""
    lines = [f"Model Registry: {summary['model_name']}"]
    champion = summary["champion"]
    if champion is None:
        lines.append("Champion: none")
    else:
        champion_metrics = champion["metrics"]
        lines.append(
            "Champion: "
            f"{champion['model_version']} | "
            f"run={champion['mlflow_run_id']} | "
            f"candidate={champion['candidate_name']} | "
            f"f1={champion_metrics.get('f1')}"
        )

    lines.append("")
    lines.append("Versions:")
    lines.append("model_version | status | run_id | candidate | f1")
    for record in summary["records"]:
        metrics = record["metrics"]
        lines.append(
            f"{record['model_version']} | "
            f"{record['status']} | "
            f"{record['mlflow_run_id']} | "
            f"{record['candidate_name']} | "
            f"{metrics.get('f1')}"
        )
    return "\n".join(lines)


def main() -> None:
    """Print local model registry summary."""
    logger = get_logger(LOGGER_NAME)
    try:
        summary = build_registry_summary()
    except (ModelRegistryError, ModelRegistryQueryError) as exc:
        logger.error("Model registry query failed: %s", exc)
        raise SystemExit(1) from exc

    print(format_registry_summary(summary))


if __name__ == "__main__":
    main()

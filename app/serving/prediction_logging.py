"""Prediction logging helpers for serving observability."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.api.schemas import PredictionRequest, PredictionResponse

DEFAULT_PREDICTION_LOG_PATH = Path("logs/predictions.jsonl")


class PredictionLoggingError(ValueError):
    """Raised when prediction log persistence fails."""


def build_prediction_success_log(
    request: PredictionRequest,
    response: PredictionResponse,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a structured log record for a successful prediction."""
    return {
        "timestamp": timestamp or _utc_now(),
        "request_id": response.request_id,
        "status": response.status,
        "model_name": response.model_name,
        "model_version": response.model_version,
        "schema_version": request.schema_version,
        "prediction": response.prediction,
        "probability": response.probability,
        "latency_ms": response.latency_ms,
    }


def build_prediction_failure_log(
    request: PredictionRequest,
    *,
    request_id: str,
    error: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a structured log record for a failed prediction."""
    return {
        "timestamp": timestamp or _utc_now(),
        "request_id": request_id,
        "status": "failed",
        "schema_version": request.schema_version,
        "error": error,
    }


def write_prediction_log(
    record: dict[str, Any],
    *,
    log_path: Path = DEFAULT_PREDICTION_LOG_PATH,
) -> None:
    """Append one prediction log record as JSONL."""
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, sort_keys=True))
            file.write("\n")
    except (OSError, TypeError) as exc:
        raise PredictionLoggingError(
            f"Failed to write prediction log: {log_path}"
        ) from exc


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()

"""Prediction logging helpers for serving observability."""

import json
from pathlib import Path
from typing import Any

from app.api.schemas import PredictionRequest, PredictionResponse
from app.observability.prediction_telemetry import (
    build_prediction_failure_event,
    build_prediction_success_event,
    build_prediction_validation_failure_event,
)

DEFAULT_PREDICTION_LOG_PATH = Path("logs/predictions.jsonl")
DEFAULT_SERVING_ENVIRONMENT = "local"
DEFAULT_DEPLOYMENT_VERSION = "local"


class PredictionLoggingError(ValueError):
    """Raised when prediction log persistence fails."""


def build_prediction_success_log(
    request: PredictionRequest,
    response: PredictionResponse,
    *,
    endpoint: str = "/predict",
    serving_environment: str = DEFAULT_SERVING_ENVIRONMENT,
    deployment_version: str = DEFAULT_DEPLOYMENT_VERSION,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a structured log record for a successful prediction."""
    return build_prediction_success_event(
        request,
        response,
        endpoint=endpoint,
        serving_environment=serving_environment,
        deployment_version=deployment_version,
        timestamp=timestamp,
    )


def build_prediction_failure_log(
    request: PredictionRequest,
    *,
    request_id: str,
    error: str,
    endpoint: str = "/predict",
    error_category: str = "prediction",
    failure_stage: str = "prediction",
    serving_environment: str = DEFAULT_SERVING_ENVIRONMENT,
    deployment_version: str = DEFAULT_DEPLOYMENT_VERSION,
    model_name: str | None = None,
    model_version: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a structured log record for a failed prediction."""
    return build_prediction_failure_event(
        request,
        request_id=request_id,
        endpoint=endpoint,
        error_category=error_category,
        error_message=error,
        failure_stage=failure_stage,
        serving_environment=serving_environment,
        deployment_version=deployment_version,
        model_name=model_name,
        model_version=model_version,
        timestamp=timestamp,
    )


def build_prediction_validation_failure_log(
    *,
    request_id: str,
    endpoint: str,
    error: str,
    serving_environment: str = DEFAULT_SERVING_ENVIRONMENT,
    deployment_version: str = DEFAULT_DEPLOYMENT_VERSION,
    input_schema_version: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a structured log record for a validation failure."""
    return build_prediction_validation_failure_event(
        request_id=request_id,
        endpoint=endpoint,
        error_message=error,
        serving_environment=serving_environment,
        deployment_version=deployment_version,
        input_schema_version=input_schema_version,
        timestamp=timestamp,
    )


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

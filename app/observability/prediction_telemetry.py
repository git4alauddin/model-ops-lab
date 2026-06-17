"""Versioned prediction telemetry event contract."""

from datetime import UTC, datetime
from typing import Any, Literal

from app.api.schemas import PredictionRequest, PredictionResponse

PREDICTION_TELEMETRY_VERSION = "v1"
PREDICTION_SUCCESS_EVENT = "prediction_success"
PREDICTION_FAILURE_EVENT = "prediction_failure"
PREDICTION_VALIDATION_FAILURE_EVENT = "prediction_validation_failure"

PredictionTelemetryStatus = Literal["success", "failed"]


def build_prediction_success_event(
    request: PredictionRequest,
    response: PredictionResponse,
    *,
    endpoint: str,
    serving_environment: str,
    deployment_version: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a telemetry event for a successful prediction."""
    return _base_event(
        event_type=PREDICTION_SUCCESS_EVENT,
        timestamp=timestamp,
        request_id=response.request_id,
        endpoint=endpoint,
        status="success",
        input_schema_version=request.schema_version,
        input_features=_input_features(request),
        model_name=response.model_name,
        model_version=response.model_version,
        serving_environment=serving_environment,
        deployment_version=deployment_version,
        prediction=response.prediction,
        probability=response.probability,
        latency_ms=response.latency_ms,
        error_category=None,
        error_message=None,
        failure_stage=None,
    )


def build_prediction_failure_event(
    request: PredictionRequest,
    *,
    request_id: str,
    endpoint: str,
    error_category: str,
    error_message: str,
    failure_stage: str,
    serving_environment: str,
    deployment_version: str,
    model_name: str | None = None,
    model_version: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a telemetry event for a controlled prediction failure."""
    return _base_event(
        event_type=PREDICTION_FAILURE_EVENT,
        timestamp=timestamp,
        request_id=request_id,
        endpoint=endpoint,
        status="failed",
        input_schema_version=request.schema_version,
        input_features=_input_features(request),
        model_name=model_name,
        model_version=model_version,
        serving_environment=serving_environment,
        deployment_version=deployment_version,
        prediction=None,
        probability=None,
        latency_ms=None,
        error_category=error_category,
        error_message=error_message,
        failure_stage=failure_stage,
    )


def build_prediction_validation_failure_event(
    *,
    request_id: str,
    endpoint: str,
    error_message: str,
    serving_environment: str,
    deployment_version: str,
    input_schema_version: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a telemetry event for schema validation failure."""
    return _base_event(
        event_type=PREDICTION_VALIDATION_FAILURE_EVENT,
        timestamp=timestamp,
        request_id=request_id,
        endpoint=endpoint,
        status="failed",
        input_schema_version=input_schema_version,
        input_features=None,
        model_name=None,
        model_version=None,
        serving_environment=serving_environment,
        deployment_version=deployment_version,
        prediction=None,
        probability=None,
        latency_ms=None,
        error_category="schema_validation",
        error_message=error_message,
        failure_stage="validation",
    )


def prediction_telemetry_fields() -> tuple[str, ...]:
    """Return the stable field order for the prediction telemetry contract."""
    return (
        "event_version",
        "event_type",
        "timestamp",
        "request_id",
        "endpoint",
        "status",
        "input_schema_version",
        "input_features",
        "model_name",
        "model_version",
        "serving_environment",
        "deployment_version",
        "prediction",
        "probability",
        "latency_ms",
        "error_category",
        "error_message",
        "failure_stage",
    )


def _base_event(
    *,
    event_type: str,
    timestamp: str | None,
    request_id: str,
    endpoint: str,
    status: PredictionTelemetryStatus,
    input_schema_version: str | None,
    input_features: dict[str, Any] | None,
    model_name: str | None,
    model_version: str | None,
    serving_environment: str,
    deployment_version: str,
    prediction: int | None,
    probability: float | None,
    latency_ms: float | None,
    error_category: str | None,
    error_message: str | None,
    failure_stage: str | None,
) -> dict[str, Any]:
    event = {
        "event_version": PREDICTION_TELEMETRY_VERSION,
        "event_type": event_type,
        "timestamp": timestamp or _utc_now(),
        "request_id": request_id,
        "endpoint": endpoint,
        "status": status,
        "input_schema_version": input_schema_version,
        "input_features": input_features,
        "model_name": model_name,
        "model_version": model_version,
        "serving_environment": serving_environment,
        "deployment_version": deployment_version,
        "prediction": prediction,
        "probability": probability,
        "latency_ms": latency_ms,
        "error_category": error_category,
        "error_message": error_message,
        "failure_stage": failure_stage,
    }
    return {field: event[field] for field in prediction_telemetry_fields()}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _input_features(request: PredictionRequest) -> dict[str, Any]:
    return {
        key: value
        for key, value in request.model_dump().items()
        if key != "schema_version"
    }

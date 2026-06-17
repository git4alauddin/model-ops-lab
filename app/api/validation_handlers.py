"""API validation error handlers with observability hooks."""

from uuid import uuid4

from fastapi import Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from app.serving.prediction_logging import (
    PredictionLoggingError,
    build_prediction_validation_failure_log,
    write_prediction_log,
)
from app.serving.settings import get_serving_settings

PREDICTION_ENDPOINTS = {"/predict", "/predict/batch"}


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Log prediction validation failures without changing FastAPI's 422 shape."""
    if request.url.path in PREDICTION_ENDPOINTS:
        settings = get_serving_settings()
        try:
            write_prediction_log(
                build_prediction_validation_failure_log(
                    request_id=str(uuid4()),
                    endpoint=request.url.path,
                    error=_summarize_validation_error(exc),
                    serving_environment=settings.modelopslab_env,
                    deployment_version=settings.deployment_version,
                ),
                log_path=settings.prediction_log_path,
            )
        except PredictionLoggingError:
            pass

    return await request_validation_exception_handler(request, exc)


def _summarize_validation_error(exc: RequestValidationError) -> str:
    error_count = len(exc.errors())
    if error_count == 1:
        return "Request validation failed: 1 error."
    return f"Request validation failed: {error_count} errors."

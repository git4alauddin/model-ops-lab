"""Human-readable runtime logging for the serving API."""

from pathlib import Path
from typing import Any

from app.utils.logger import get_logger

DEFAULT_SERVING_LOG_PATH = Path("logs/modelopslab.log")
SERVING_LOGGER_NAME = "modelopslab.serving"


def get_serving_logger(log_path: Path = DEFAULT_SERVING_LOG_PATH):
    """Return the serving logger configured for the master runtime log."""
    return get_logger(SERVING_LOGGER_NAME, log_path)


def log_prediction_received(
    *,
    request_id: str,
    endpoint: str,
    instances: int = 1,
    log_path: Path = DEFAULT_SERVING_LOG_PATH,
) -> None:
    """Log that a prediction request reached route logic."""
    logger = get_serving_logger(log_path)
    logger.info(
        "Prediction request received. endpoint=%s request_id=%s instances=%s",
        endpoint,
        request_id,
        instances,
    )


def log_prediction_completed(
    *,
    request_id: str,
    endpoint: str,
    model_name: str,
    model_version: str,
    prediction_count: int,
    log_path: Path = DEFAULT_SERVING_LOG_PATH,
) -> None:
    """Log that a prediction request completed successfully."""
    logger = get_serving_logger(log_path)
    logger.info(
        "Prediction request completed. endpoint=%s request_id=%s "
        "model_name=%s model_version=%s predictions=%s",
        endpoint,
        request_id,
        model_name,
        model_version,
        prediction_count,
    )


def log_prediction_failed(
    *,
    request_id: str,
    endpoint: str,
    stage: str,
    error: Any,
    log_path: Path = DEFAULT_SERVING_LOG_PATH,
) -> None:
    """Log that a prediction request failed in a controlled stage."""
    logger = get_serving_logger(log_path)
    logger.error(
        "Prediction request failed. endpoint=%s request_id=%s stage=%s error=%s",
        endpoint,
        request_id,
        stage,
        error,
    )

"""Build a local monitoring summary from prediction telemetry."""

from pathlib import Path

from app.observability.monitoring_summary import (
    DEFAULT_MONITORING_SUMMARY_PATH,
    DEFAULT_PREDICTION_TELEMETRY_PATH,
    MonitoringSummaryError,
    build_and_save_prediction_monitoring_summary,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.monitoring"


def main() -> None:
    """Build the local prediction monitoring summary report."""
    logger = get_logger(LOGGER_NAME)
    try:
        summary = build_and_save_prediction_monitoring_summary(
            log_path=DEFAULT_PREDICTION_TELEMETRY_PATH,
            output_path=DEFAULT_MONITORING_SUMMARY_PATH,
        )
    except MonitoringSummaryError as exc:
        logger.error("Prediction monitoring summary failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Prediction monitoring summary written to %s | events=%s failures=%s",
        DEFAULT_MONITORING_SUMMARY_PATH,
        summary["total_events"],
        summary["failure_count"],
    )
    print(Path(DEFAULT_MONITORING_SUMMARY_PATH))


if __name__ == "__main__":
    main()

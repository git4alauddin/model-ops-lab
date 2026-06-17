"""Build local alert report from prediction monitoring summary."""

from pathlib import Path

from app.observability.monitoring_alerts import (
    DEFAULT_MONITORING_ALERTS_PATH,
    DEFAULT_MONITORING_SUMMARY_PATH,
    MonitoringAlertsError,
    build_and_save_monitoring_alerts,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.monitoring"


def main() -> None:
    """Build the local monitoring alert report."""
    logger = get_logger(LOGGER_NAME)
    try:
        alert_report = build_and_save_monitoring_alerts(
            summary_path=DEFAULT_MONITORING_SUMMARY_PATH,
            output_path=DEFAULT_MONITORING_ALERTS_PATH,
        )
    except MonitoringAlertsError as exc:
        logger.error("Monitoring alert evaluation failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Monitoring alerts written to %s | status=%s active_alerts=%s",
        DEFAULT_MONITORING_ALERTS_PATH,
        alert_report["overall_status"],
        alert_report["active_alert_count"],
    )
    print(Path(DEFAULT_MONITORING_ALERTS_PATH))


if __name__ == "__main__":
    main()

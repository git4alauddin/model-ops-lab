"""Build a local static HTML monitoring dashboard."""

from pathlib import Path

from app.observability.monitoring_dashboard import (
    DEFAULT_MONITORING_DASHBOARD_PATH,
    MonitoringDashboardError,
    build_and_save_monitoring_dashboard,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.monitoring"


def main() -> None:
    """Build and persist the local monitoring dashboard HTML."""
    logger = get_logger(LOGGER_NAME)
    try:
        html = build_and_save_monitoring_dashboard(
            output_path=DEFAULT_MONITORING_DASHBOARD_PATH,
        )
    except MonitoringDashboardError as exc:
        logger.error("Monitoring dashboard failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Monitoring dashboard written to %s | bytes=%s",
        DEFAULT_MONITORING_DASHBOARD_PATH,
        len(html.encode("utf-8")),
    )
    print(Path(DEFAULT_MONITORING_DASHBOARD_PATH))


if __name__ == "__main__":
    main()

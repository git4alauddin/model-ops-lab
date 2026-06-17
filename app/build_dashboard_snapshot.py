"""Build a dashboard-ready local monitoring snapshot."""

from pathlib import Path

from app.observability.dashboard_snapshot import (
    DEFAULT_DASHBOARD_SNAPSHOT_PATH,
    DashboardSnapshotError,
    build_and_save_dashboard_snapshot,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.monitoring"


def main() -> None:
    """Build and persist the local dashboard snapshot."""
    logger = get_logger(LOGGER_NAME)
    try:
        snapshot = build_and_save_dashboard_snapshot(
            output_path=DEFAULT_DASHBOARD_SNAPSHOT_PATH,
        )
    except DashboardSnapshotError as exc:
        logger.error("Dashboard snapshot failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Dashboard snapshot written to %s | status=%s active_alerts=%s",
        DEFAULT_DASHBOARD_SNAPSHOT_PATH,
        snapshot["overall_status"],
        snapshot["cards"]["alerts"]["active_alert_count"],
    )
    print(Path(DEFAULT_DASHBOARD_SNAPSHOT_PATH))


if __name__ == "__main__":
    main()

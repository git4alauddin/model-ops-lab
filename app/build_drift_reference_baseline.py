"""Build the local reference baseline for future drift detection."""

from pathlib import Path

from app.observability.drift_baseline import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_DRIFT_BASELINE_PATH,
    DriftBaselineError,
    build_and_save_reference_baseline,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.drift"


def main() -> None:
    """Build and persist the local drift reference baseline."""
    logger = get_logger(LOGGER_NAME)
    try:
        baseline = build_and_save_reference_baseline(
            config_path=DEFAULT_CONFIG_PATH,
            output_path=DEFAULT_DRIFT_BASELINE_PATH,
        )
    except DriftBaselineError as exc:
        logger.error("Drift reference baseline failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Drift reference baseline written to %s | rows=%s features=%s",
        DEFAULT_DRIFT_BASELINE_PATH,
        baseline["row_count"],
        baseline["feature_count"],
    )
    print(Path(DEFAULT_DRIFT_BASELINE_PATH))


if __name__ == "__main__":
    main()

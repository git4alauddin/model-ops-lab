"""Build local data drift summary from reference and inference snapshots."""

from pathlib import Path

from app.observability.drift_comparison import (
    DEFAULT_DATA_DRIFT_SUMMARY_PATH,
    DEFAULT_DRIFT_BASELINE_PATH,
    DEFAULT_INFERENCE_SNAPSHOT_PATH,
    DriftComparisonError,
    build_and_save_data_drift_summary,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.drift"


def main() -> None:
    """Build and persist the local data drift summary."""
    logger = get_logger(LOGGER_NAME)
    try:
        summary = build_and_save_data_drift_summary(
            reference_path=DEFAULT_DRIFT_BASELINE_PATH,
            inference_path=DEFAULT_INFERENCE_SNAPSHOT_PATH,
            output_path=DEFAULT_DATA_DRIFT_SUMMARY_PATH,
        )
    except DriftComparisonError as exc:
        logger.error("Data drift summary failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Data drift summary written to %s | status=%s drifted_features=%s",
        DEFAULT_DATA_DRIFT_SUMMARY_PATH,
        summary["overall_status"],
        summary["drifted_feature_count"],
    )
    print(Path(DEFAULT_DATA_DRIFT_SUMMARY_PATH))


if __name__ == "__main__":
    main()

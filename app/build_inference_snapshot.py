"""Build an inference feature snapshot from prediction telemetry."""

from pathlib import Path

from app.observability.inference_snapshot import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_INFERENCE_SNAPSHOT_PATH,
    DEFAULT_PREDICTION_TELEMETRY_PATH,
    InferenceSnapshotError,
    build_and_save_inference_snapshot,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.drift"


def main() -> None:
    """Build and persist the local inference feature snapshot."""
    logger = get_logger(LOGGER_NAME)
    try:
        snapshot = build_and_save_inference_snapshot(
            config_path=DEFAULT_CONFIG_PATH,
            telemetry_path=DEFAULT_PREDICTION_TELEMETRY_PATH,
            output_path=DEFAULT_INFERENCE_SNAPSHOT_PATH,
        )
    except InferenceSnapshotError as exc:
        logger.error("Inference feature snapshot failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Inference feature snapshot written to %s | rows=%s skipped=%s",
        DEFAULT_INFERENCE_SNAPSHOT_PATH,
        snapshot["row_count"],
        snapshot["skipped_event_count"],
    )
    print(Path(DEFAULT_INFERENCE_SNAPSHOT_PATH))


if __name__ == "__main__":
    main()

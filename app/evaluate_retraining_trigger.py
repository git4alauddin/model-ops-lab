"""Build local retraining trigger decision from monitoring reports."""

from pathlib import Path

from app.observability.retraining_trigger import (
    DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
    RetrainingTriggerError,
    build_and_save_retraining_trigger_decision,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Build the local retraining trigger decision report."""
    logger = get_logger(LOGGER_NAME)
    try:
        decision_report = build_and_save_retraining_trigger_decision(
            output_path=DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
        )
    except RetrainingTriggerError as exc:
        logger.error("Retraining trigger evaluation failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Retraining trigger decision written to %s | decision=%s reasons=%s",
        DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
        decision_report["decision"],
        decision_report["reason_count"],
    )
    print(Path(DEFAULT_RETRAINING_TRIGGER_DECISION_PATH))


if __name__ == "__main__":
    main()

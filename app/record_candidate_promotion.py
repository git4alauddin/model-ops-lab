"""Record an approved V10 candidate promotion decision."""

import argparse
from pathlib import Path

from app.retraining.promotion_record import (
    PromotionRecordError,
    record_approved_candidate_promotion,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Record an approved promotion decision from the command line."""
    parser = argparse.ArgumentParser(
        description="Record an approved candidate promotion decision."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID.")
    parser.add_argument(
        "--promoted-by",
        required=True,
        help="Person recording the promotion decision.",
    )
    parser.add_argument(
        "--reason",
        required=True,
        help="Reason for recording the promotion decision.",
    )
    parser.add_argument(
        "--runs-dir",
        default="retraining_runs",
        help="Directory containing retraining run metadata.",
    )
    args = parser.parse_args()

    logger = get_logger(LOGGER_NAME)
    try:
        record, _, record_path = record_approved_candidate_promotion(
            run_id=args.run_id,
            promoted_by=args.promoted_by,
            reason=args.reason,
            runs_dir=Path(args.runs_dir),
        )
    except PromotionRecordError as exc:
        logger.error("Candidate promotion record command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Candidate promotion recorded. run_id=%s decision=%s record=%s",
        record["run_id"],
        record["decision"],
        record_path,
    )
    print(Path(record_path))


if __name__ == "__main__":
    main()

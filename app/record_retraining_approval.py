"""Record a human approval decision for a V10 retraining run."""

import argparse
from pathlib import Path

from app.retraining.approval_gate import (
    ApprovalGateError,
    VALID_APPROVAL_DECISIONS,
    record_retraining_approval,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Record a human approval decision from the command line."""
    parser = argparse.ArgumentParser(
        description="Record a human approval decision for a retraining run."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID.")
    parser.add_argument(
        "--decision",
        required=True,
        choices=sorted(VALID_APPROVAL_DECISIONS),
        help="Human approval decision.",
    )
    parser.add_argument(
        "--approved-by",
        "--decided-by",
        dest="approved_by",
        required=True,
        help="Person recording the decision.",
    )
    parser.add_argument("--notes", default=None, help="Decision notes.")
    parser.add_argument(
        "--runs-dir",
        default="retraining_runs",
        help="Directory containing retraining run metadata.",
    )
    args = parser.parse_args()

    logger = get_logger(LOGGER_NAME)
    try:
        record, _, record_path = record_retraining_approval(
            run_id=args.run_id,
            decision=args.decision,
            approved_by=args.approved_by,
            notes=args.notes,
            runs_dir=Path(args.runs_dir),
        )
    except ApprovalGateError as exc:
        logger.error("Retraining approval command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Retraining approval recorded. run_id=%s decision=%s record=%s",
        record["run_id"],
        record["decision"],
        record_path,
    )
    print(Path(record_path))


if __name__ == "__main__":
    main()

"""Rollback a V10 local serving update to its recorded champion target."""

import argparse
from pathlib import Path

from app.retraining.local_serving_rollback import (
    LocalServingRollbackError,
    rollback_local_retraining_serving,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Rollback and validate the local serving champion."""
    parser = argparse.ArgumentParser(
        description="Rollback a V10 local serving update."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID.")
    parser.add_argument(
        "--reason",
        required=True,
        help="Reason for rolling back the retraining champion.",
    )
    parser.add_argument(
        "--rolled-back-by",
        required=True,
        help="Person recording the rollback.",
    )
    parser.add_argument(
        "--runs-dir",
        default="retraining_runs",
        help="Directory containing retraining run metadata.",
    )
    parser.add_argument(
        "--registry-dir",
        default="model_registry",
        help="Local model registry directory used by serving.",
    )
    args = parser.parse_args()

    logger = get_logger(LOGGER_NAME)
    try:
        report, _, report_path = rollback_local_retraining_serving(
            run_id=args.run_id,
            reason=args.reason,
            rolled_back_by=args.rolled_back_by,
            runs_dir=Path(args.runs_dir),
            registry_dir=Path(args.registry_dir),
        )
    except LocalServingRollbackError as exc:
        logger.error("Local retraining rollback command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Local retraining rollback completed. run_id=%s restored=%s report=%s",
        report["run_id"],
        report["restored_champion"]["model_version"],
        report_path,
    )
    print(Path(report_path))


if __name__ == "__main__":
    main()

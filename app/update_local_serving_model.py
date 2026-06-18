"""Update the local serving champion from a V10 retraining run."""

import argparse
from pathlib import Path

from app.retraining.local_serving_update import (
    LocalServingUpdateError,
    update_local_registry_and_serving,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Update and validate the local serving champion."""
    parser = argparse.ArgumentParser(
        description="Update local serving from a validated retraining handoff."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID.")
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
        report, _, report_path = update_local_registry_and_serving(
            run_id=args.run_id,
            runs_dir=Path(args.runs_dir),
            registry_dir=Path(args.registry_dir),
        )
    except LocalServingUpdateError as exc:
        logger.error("Local serving update command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Local serving update completed. run_id=%s champion=%s report=%s",
        report["run_id"],
        report["new_champion"]["model_version"],
        report_path,
    )
    print(Path(report_path))


if __name__ == "__main__":
    main()

"""Run candidate retraining for an initialized V10 retraining run."""

import argparse
from pathlib import Path

from app.retraining.candidate_training import (
    CandidateTrainingError,
    run_candidate_retraining,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Run candidate retraining from the command line."""
    parser = argparse.ArgumentParser(
        description="Train a candidate model for a governed retraining run."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID to train.")
    parser.add_argument(
        "--runs-dir",
        default="retraining_runs",
        help="Directory containing retraining run metadata.",
    )
    args = parser.parse_args()

    logger = get_logger(LOGGER_NAME)
    try:
        metadata, output_path = run_candidate_retraining(
            run_id=args.run_id,
            runs_dir=Path(args.runs_dir),
        )
    except CandidateTrainingError as exc:
        logger.error("Candidate retraining command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Candidate retraining completed. run_id=%s output=%s model=%s",
        metadata["run_id"],
        output_path,
        metadata["candidate"]["model_path"],
    )
    print(Path(output_path))


if __name__ == "__main__":
    main()

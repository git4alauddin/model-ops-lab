"""Initialize governed candidate retraining run metadata."""

from pathlib import Path

from app.retraining.candidate_run_metadata import (
    CandidateRetrainingRunError,
    build_and_save_candidate_retraining_run_metadata,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Create a candidate retraining run metadata record."""
    logger = get_logger(LOGGER_NAME)
    try:
        metadata, output_path = build_and_save_candidate_retraining_run_metadata()
    except CandidateRetrainingRunError as exc:
        logger.error("Candidate retraining run initialization failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Candidate retraining run initialized. run_id=%s output=%s",
        metadata["run_id"],
        output_path,
    )
    print(Path(output_path))


if __name__ == "__main__":
    main()

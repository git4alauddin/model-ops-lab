"""Build candidate-vs-production comparison report for V10."""

import argparse
from pathlib import Path

from app.retraining.candidate_comparison import (
    CandidateComparisonError,
    build_and_save_candidate_comparison_report,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Run candidate-vs-production comparison from the command line."""
    parser = argparse.ArgumentParser(
        description="Compare a trained retraining candidate against production."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID to compare.")
    parser.add_argument(
        "--runs-dir",
        default="retraining_runs",
        help="Directory containing retraining run metadata.",
    )
    args = parser.parse_args()

    logger = get_logger(LOGGER_NAME)
    try:
        report, _, report_path = build_and_save_candidate_comparison_report(
            run_id=args.run_id,
            runs_dir=Path(args.runs_dir),
        )
    except CandidateComparisonError as exc:
        logger.error("Candidate comparison command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Candidate comparison completed. run_id=%s status=%s recommendation=%s report=%s",
        report["run_id"],
        report["status"],
        report["promotion_recommendation"],
        report_path,
    )
    print(Path(report_path))


if __name__ == "__main__":
    main()

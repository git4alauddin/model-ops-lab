"""Validate serving update handoff readiness for a promoted V10 candidate."""

import argparse
from pathlib import Path

from app.retraining.serving_handoff import (
    ServingHandoffError,
    validate_serving_handoff,
)
from app.utils.logger import get_logger

LOGGER_NAME = "modelopslab.retraining"


def main() -> None:
    """Validate serving handoff readiness from the command line."""
    parser = argparse.ArgumentParser(
        description="Validate serving handoff readiness for a promoted candidate."
    )
    parser.add_argument("--run-id", required=True, help="Retraining run ID.")
    parser.add_argument(
        "--runs-dir",
        default="retraining_runs",
        help="Directory containing retraining run metadata.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root used to resolve relative artifact paths.",
    )
    args = parser.parse_args()

    logger = get_logger(LOGGER_NAME)
    try:
        report, _, report_path = validate_serving_handoff(
            run_id=args.run_id,
            runs_dir=Path(args.runs_dir),
            project_root=Path(args.project_root),
        )
    except ServingHandoffError as exc:
        logger.error("Serving handoff validation command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Serving handoff validation completed. run_id=%s status=%s report=%s",
        report["run_id"],
        report["status"],
        report_path,
    )
    print(Path(report_path))


if __name__ == "__main__":
    main()

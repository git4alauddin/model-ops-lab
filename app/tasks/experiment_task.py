"""Experiment stage helper for the V5 training pipeline."""

from pathlib import Path
from typing import Any, Callable

from app.run_experiments import run_experiment_workflow


class ExperimentStageError(ValueError):
    """Raised when the experiment stage cannot produce a champion report."""


def run_experiment_stage(
    *,
    config_path: str | Path,
    experiment_runner: Callable[..., dict[str, Any]] = run_experiment_workflow,
) -> dict[str, Any]:
    """Run the experiment workflow as a pipeline-owned stage."""
    try:
        champion_report = experiment_runner(
            Path(config_path),
            validate_before_run=False,
        )
    except SystemExit as exc:
        if exc.code in (None, 0):
            raise ExperimentStageError(
                "Experiment runner exited without a champion report."
            ) from exc
        raise ExperimentStageError(
            f"Experiment runner exited with code {exc.code}."
        ) from exc
    return validate_champion_report(champion_report)


def validate_champion_report(champion_report: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a champion report dictionary."""
    if not isinstance(champion_report, dict):
        raise ExperimentStageError("Experiment runner must return a champion report.")

    champion = champion_report.get("champion")
    if not isinstance(champion, dict) or not isinstance(champion.get("run_id"), str):
        raise ExperimentStageError("Champion report requires champion.run_id.")

    eligible_runs = champion_report.get("eligible_runs")
    if not isinstance(eligible_runs, list):
        raise ExperimentStageError("Champion report requires eligible_runs.")

    return champion_report


def extract_champion_run_id(champion_report: dict[str, Any]) -> str:
    """Return the champion MLflow run ID from a champion report."""
    champion = champion_report["champion"]
    return str(champion["run_id"])


def extract_mlflow_run_ids(champion_report: dict[str, Any]) -> list[str]:
    """Return unique MLflow run IDs from eligible runs and the champion."""
    run_ids = []
    for run in champion_report.get("eligible_runs", []):
        if isinstance(run, dict) and isinstance(run.get("run_id"), str):
            run_ids.append(run["run_id"])
    run_ids.append(extract_champion_run_id(champion_report))
    return list(dict.fromkeys(run_ids))

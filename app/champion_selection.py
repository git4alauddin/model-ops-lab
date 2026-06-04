"""Champion run selection helpers for V4 experiment comparison."""

from datetime import UTC, datetime
from typing import Any


class ChampionSelectionError(ValueError):
    """Raised when a champion run cannot be selected."""


REQUIRED_METRICS = (
    "accuracy",
    "precision",
    "recall",
    "f1",
    "training_duration_seconds",
    "evaluation_duration_seconds",
)
REQUIRED_ARTIFACTS = (
    "model",
    "metrics",
    "confusion_matrix",
    "config_snapshot",
    "metadata",
)
MODEL_COMPLEXITY_RANK = {
    "logistic_regression": 0,
    "decision_tree": 1,
    "random_forest": 2,
}


def select_champion_run(candidate_runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Select a champion run from finished same-dataset candidate runs."""
    if not candidate_runs:
        raise ChampionSelectionError("No candidate runs provided.")

    reference_dataset = _dataset_identity(candidate_runs[0])
    eligible_runs = []
    rejected_runs = []

    for candidate_run in candidate_runs:
        rejection_reason = _get_rejection_reason(candidate_run, reference_dataset)
        if rejection_reason:
            rejected_runs.append(
                {
                    "run_id": candidate_run.get("run_id"),
                    "candidate_name": candidate_run.get("candidate_name"),
                    "reason": rejection_reason,
                }
            )
            continue
        eligible_runs.append(candidate_run)

    if not eligible_runs:
        raise ChampionSelectionError("No eligible candidate runs found.")

    champion = max(eligible_runs, key=_ranking_key)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "selection_rule": (
            "highest_f1_same_dataset_checksum_then_recall_precision_accuracy_"
            "runtime_simplicity_pipeline_version"
        ),
        "primary_metric": "f1",
        "champion": _build_champion_summary(champion),
        "eligible_runs": [_build_candidate_summary(run) for run in eligible_runs],
        "rejected_runs": rejected_runs,
    }


def _get_rejection_reason(
    candidate_run: dict[str, Any],
    reference_dataset: dict[str, str],
) -> str | None:
    if candidate_run.get("status") != "FINISHED":
        return "run status is not FINISHED"

    if _dataset_identity(candidate_run) != reference_dataset:
        return "dataset identity does not match the comparison group"

    metrics = candidate_run.get("metrics")
    if not isinstance(metrics, dict):
        return "metrics are missing"
    missing_metrics = [key for key in REQUIRED_METRICS if key not in metrics]
    if missing_metrics:
        return f"required metrics are missing: {missing_metrics}"

    artifacts = candidate_run.get("artifacts")
    if not isinstance(artifacts, dict):
        return "artifacts are missing"
    missing_artifacts = [key for key in REQUIRED_ARTIFACTS if key not in artifacts]
    if missing_artifacts:
        return f"required artifacts are missing: {missing_artifacts}"

    return None


def _dataset_identity(candidate_run: dict[str, Any]) -> dict[str, str]:
    return {
        "dataset_name": str(candidate_run.get("dataset_name")),
        "dataset_version": str(candidate_run.get("dataset_version")),
        "dataset_checksum": str(candidate_run.get("dataset_checksum")),
    }


def _ranking_key(candidate_run: dict[str, Any]) -> tuple:
    metrics = candidate_run["metrics"]
    model_type = candidate_run["model_type"]
    return (
        float(metrics["f1"]),
        float(metrics["recall"]),
        float(metrics["precision"]),
        float(metrics["accuracy"]),
        -float(metrics["training_duration_seconds"]),
        -float(metrics["evaluation_duration_seconds"]),
        -MODEL_COMPLEXITY_RANK.get(str(model_type), 99),
        str(candidate_run.get("pipeline_version", "")),
    )


def _build_champion_summary(candidate_run: dict[str, Any]) -> dict[str, Any]:
    summary = _build_candidate_summary(candidate_run)
    summary["selection_reason"] = (
        "Selected by highest F1 among eligible runs on the same dataset checksum, "
        "with documented tie-breakers applied."
    )
    return summary


def _build_candidate_summary(candidate_run: dict[str, Any]) -> dict[str, Any]:
    metrics = candidate_run["metrics"]
    return {
        "run_id": candidate_run["run_id"],
        "candidate_name": candidate_run["candidate_name"],
        "model_type": candidate_run["model_type"],
        "dataset_name": candidate_run["dataset_name"],
        "dataset_version": candidate_run["dataset_version"],
        "dataset_checksum": candidate_run["dataset_checksum"],
        "pipeline_version": candidate_run["pipeline_version"],
        "metrics": {
            "accuracy": float(metrics["accuracy"]),
            "precision": float(metrics["precision"]),
            "recall": float(metrics["recall"]),
            "f1": float(metrics["f1"]),
            "training_duration_seconds": float(metrics["training_duration_seconds"]),
            "evaluation_duration_seconds": float(
                metrics["evaluation_duration_seconds"]
            ),
        },
    }

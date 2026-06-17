"""Compare a trained retraining candidate against production."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.retraining.candidate_run_metadata import (
    APPROVAL_PENDING,
    CANDIDATE_COMPARED,
    CANDIDATE_TRAINED,
    DEFAULT_RETRAINING_RUNS_DIR,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.utils.artifacts import ArtifactError, save_json

DEFAULT_COMPARISON_METRICS = ("accuracy", "precision", "recall", "f1")
DEFAULT_METRIC_TOLERANCES = {
    "accuracy": 0.0,
    "precision": 0.0,
    "recall": 0.0,
    "f1": 0.0,
}
GATE_PASSED = "passed"
GATE_FAILED = "failed"
GATE_MANUAL_REVIEW = "manual_review"
PROMOTION_READY_FOR_APPROVAL = "ready_for_approval"
PROMOTION_REJECT_CANDIDATE = "reject_candidate"
PROMOTION_MANUAL_REVIEW = "manual_review"


class CandidateComparisonError(ValueError):
    """Raised when candidate-vs-production comparison cannot complete."""


def build_candidate_comparison_report(
    *,
    metadata: dict[str, Any],
    metrics: tuple[str, ...] = DEFAULT_COMPARISON_METRICS,
    tolerances: dict[str, float] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a candidate-vs-production comparison report."""
    _validate_candidate_can_compare(metadata)
    candidate = _section(metadata, "candidate")
    production = _section(metadata, "previous_production_model")
    candidate_metrics = _section(candidate, "metrics")
    production_metrics = _section(production, "metrics")
    resolved_tolerances = {
        **DEFAULT_METRIC_TOLERANCES,
        **(tolerances or {}),
    }

    metric_results = [
        _compare_metric(
            metric_name,
            candidate_metrics,
            production_metrics,
            resolved_tolerances.get(metric_name, 0.0),
        )
        for metric_name in metrics
    ]
    gate_status = _overall_gate_status(metric_results)
    promotion_recommendation = _promotion_recommendation(gate_status)
    return {
        "generated_at": generated_at or _utc_now(),
        "run_id": metadata["run_id"],
        "status": gate_status,
        "promotion_recommendation": promotion_recommendation,
        "candidate": {
            "model_type": candidate.get("model_type"),
            "model_path": candidate.get("model_path"),
            "metrics_path": candidate.get("metrics_path"),
        },
        "production": {
            "model_name": production.get("model_name"),
            "model_version": production.get("model_version"),
            "artifact_uri": production.get("artifact_uri"),
        },
        "metric_results": metric_results,
        "summary": _summary(metric_results),
    }


def save_candidate_comparison_report(
    report: dict[str, Any],
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> Path:
    """Persist a candidate comparison report inside the retraining run."""
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    output_path = metadata_path.parent / "comparison_report.json"
    try:
        save_json(report, output_path)
    except ArtifactError as exc:
        raise CandidateComparisonError(
            f"Failed to save candidate comparison report: {output_path}"
        ) from exc
    return output_path


def update_metadata_after_candidate_comparison(
    metadata: dict[str, Any],
    *,
    report: dict[str, Any],
    report_path: Path,
) -> dict[str, Any]:
    """Return retraining metadata updated with comparison evidence."""
    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = CANDIDATE_COMPARED
    updated_metadata["candidate"]["comparison_report_path"] = str(report_path)
    updated_metadata["regression_gates"] = {
        "status": report["status"],
        "results": deepcopy(report["metric_results"]),
    }
    updated_metadata["promotion"]["recommendation"] = report[
        "promotion_recommendation"
    ]
    updated_metadata["promotion"]["decision"] = APPROVAL_PENDING
    updated_metadata["comparison"] = {
        "generated_at": report["generated_at"],
        "report_path": str(report_path),
        "summary": deepcopy(report["summary"]),
    }
    return updated_metadata


def build_and_save_candidate_comparison_report(
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    generated_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Build comparison report, persist it, and update run metadata."""
    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        report = build_candidate_comparison_report(
            metadata=metadata,
            generated_at=generated_at,
        )
        report_path = save_candidate_comparison_report(
            report,
            run_id=run_id,
            runs_dir=runs_dir,
        )
        updated_metadata = update_metadata_after_candidate_comparison(
            metadata,
            report=report,
            report_path=report_path,
        )
        save_candidate_retraining_run_metadata(updated_metadata, runs_dir=runs_dir)
    except (ArtifactError, CandidateRetrainingRunError) as exc:
        raise CandidateComparisonError(
            f"Candidate comparison failed for run_id={run_id}: {exc}"
        ) from exc

    return report, updated_metadata, report_path


def _validate_candidate_can_compare(metadata: dict[str, Any]) -> None:
    status = metadata.get("status")
    if status != CANDIDATE_TRAINED:
        raise CandidateComparisonError(
            "Candidate comparison requires status="
            f"{CANDIDATE_TRAINED}; got {status}."
        )
    candidate = _section(metadata, "candidate")
    production = _section(metadata, "previous_production_model")
    if not _section(candidate, "metrics"):
        raise CandidateComparisonError("Candidate metrics are required.")
    if not _section(production, "metrics"):
        raise CandidateComparisonError("Previous production metrics are required.")


def _compare_metric(
    metric_name: str,
    candidate_metrics: dict[str, Any],
    production_metrics: dict[str, Any],
    tolerance: float,
) -> dict[str, Any]:
    candidate_value = _metric_value(candidate_metrics, metric_name)
    production_value = _metric_value(production_metrics, metric_name)
    if candidate_value is None or production_value is None:
        return {
            "metric": metric_name,
            "candidate_value": candidate_value,
            "production_value": production_value,
            "delta": None,
            "tolerance": tolerance,
            "status": GATE_MANUAL_REVIEW,
            "message": "Metric missing from candidate or production record.",
        }

    delta = candidate_value - production_value
    status = GATE_PASSED if delta >= -abs(tolerance) else GATE_FAILED
    return {
        "metric": metric_name,
        "candidate_value": candidate_value,
        "production_value": production_value,
        "delta": delta,
        "tolerance": tolerance,
        "status": status,
        "message": _metric_message(metric_name, delta, tolerance, status),
    }


def _metric_value(metrics: dict[str, Any], metric_name: str) -> float | None:
    value = metrics.get(metric_name)
    if isinstance(value, int | float):
        return float(value)
    return None


def _overall_gate_status(metric_results: list[dict[str, Any]]) -> str:
    statuses = {result["status"] for result in metric_results}
    if GATE_FAILED in statuses:
        return GATE_FAILED
    if GATE_MANUAL_REVIEW in statuses:
        return GATE_MANUAL_REVIEW
    return GATE_PASSED


def _promotion_recommendation(gate_status: str) -> str:
    if gate_status == GATE_PASSED:
        return PROMOTION_READY_FOR_APPROVAL
    if gate_status == GATE_FAILED:
        return PROMOTION_REJECT_CANDIDATE
    return PROMOTION_MANUAL_REVIEW


def _summary(metric_results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "passed": sum(1 for result in metric_results if result["status"] == GATE_PASSED),
        "failed": sum(1 for result in metric_results if result["status"] == GATE_FAILED),
        "manual_review": sum(
            1 for result in metric_results if result["status"] == GATE_MANUAL_REVIEW
        ),
    }


def _metric_message(
    metric_name: str,
    delta: float,
    tolerance: float,
    status: str,
) -> str:
    if status == GATE_PASSED:
        return f"{metric_name} is within allowed regression tolerance."
    return (
        f"{metric_name} regressed by {abs(delta):.6f}, "
        f"which exceeds tolerance {abs(tolerance):.6f}."
    )


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


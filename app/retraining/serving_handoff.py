"""Validate the serving update handoff for a promoted candidate."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    CANDIDATE_PROMOTED,
    CANDIDATE_SERVING_HANDOFF_VALIDATED,
    DEFAULT_RETRAINING_RUNS_DIR,
    PROMOTION_DECISION_PROMOTED,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.utils.artifacts import ArtifactError, save_json

HANDOFF_READY = "ready"
HANDOFF_BLOCKED = "blocked"
CHECK_PASSED = "passed"
CHECK_FAILED = "failed"


class ServingHandoffError(ValueError):
    """Raised when serving handoff validation cannot complete."""


def build_serving_handoff_report(
    *,
    metadata: dict[str, Any],
    project_root: Path = Path("."),
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a report that validates readiness for serving update handoff."""
    checks = _serving_handoff_checks(metadata, project_root=project_root)
    status = HANDOFF_READY if all(check["status"] == CHECK_PASSED for check in checks) else HANDOFF_BLOCKED
    candidate = _section(metadata, "candidate")
    promotion = _section(metadata, "promotion")
    return {
        "generated_at": generated_at or _utc_now(),
        "run_id": metadata.get("run_id"),
        "status": status,
        "checks": checks,
        "candidate": {
            "model_path": candidate.get("model_path"),
            "metrics_path": candidate.get("metrics_path"),
            "comparison_report_path": candidate.get("comparison_report_path"),
        },
        "promotion": {
            "decision": promotion.get("decision"),
            "record_path": promotion.get("record_path"),
            "registry_update": promotion.get("registry_update"),
            "serving_update": promotion.get("serving_update"),
            "rollback_target": deepcopy(promotion.get("rollback_target")),
        },
        "serving_boundary": {
            "live_serving_changed": False,
            "model_registry_updated": False,
            "cloud_run_redeployed": False,
            "traffic_changed": False,
        },
        "next_steps": [
            "Decide whether the next operational action updates the local model registry, serving artifact path, or Cloud Run image.",
            "Validate rollback target before any production-serving mutation.",
            "After a serving update, validate /ready and /predict, not only /health.",
            "Record the serving update evidence separately from this handoff report.",
        ],
    }


def save_serving_handoff_report(
    report: dict[str, Any],
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> Path:
    """Persist serving handoff validation inside the retraining run."""
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    output_path = metadata_path.parent / "serving_handoff_report.json"
    try:
        save_json(report, output_path)
    except ArtifactError as exc:
        raise ServingHandoffError(
            f"Failed to save serving handoff report: {output_path}"
        ) from exc
    return output_path


def update_metadata_after_serving_handoff(
    metadata: dict[str, Any],
    *,
    report: dict[str, Any],
    report_path: Path,
) -> dict[str, Any]:
    """Return retraining metadata updated with serving handoff validation."""
    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = CANDIDATE_SERVING_HANDOFF_VALIDATED
    updated_metadata["promotion"]["serving_handoff_status"] = report["status"]
    updated_metadata["promotion"]["serving_handoff_report_path"] = str(report_path)
    updated_metadata["promotion"]["serving_update_ready"] = (
        report["status"] == HANDOFF_READY
    )
    updated_metadata["promotion"]["serving_update"] = report["promotion"].get(
        "serving_update"
    )
    updated_metadata["promotion"]["registry_update"] = report["promotion"].get(
        "registry_update"
    )
    return updated_metadata


def validate_serving_handoff(
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    project_root: Path = Path("."),
    generated_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Validate serving handoff readiness and update retraining metadata."""
    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        report = build_serving_handoff_report(
            metadata=metadata,
            project_root=project_root,
            generated_at=generated_at,
        )
        report_path = save_serving_handoff_report(
            report,
            run_id=run_id,
            runs_dir=runs_dir,
        )
        updated_metadata = update_metadata_after_serving_handoff(
            metadata,
            report=report,
            report_path=report_path,
        )
        save_candidate_retraining_run_metadata(updated_metadata, runs_dir=runs_dir)
    except CandidateRetrainingRunError as exc:
        raise ServingHandoffError(
            f"Serving handoff validation failed for run_id={run_id}: {exc}"
        ) from exc

    return report, updated_metadata, report_path


def _serving_handoff_checks(
    metadata: dict[str, Any],
    *,
    project_root: Path,
) -> list[dict[str, Any]]:
    candidate = _section(metadata, "candidate")
    approval = _section(metadata, "approval")
    promotion = _section(metadata, "promotion")
    checks = [
        _check(
            "candidate_promoted_status",
            metadata.get("status") == CANDIDATE_PROMOTED,
            f"run status must be {CANDIDATE_PROMOTED}.",
            {"actual": metadata.get("status")},
        ),
        _check(
            "approval_recorded",
            approval.get("state") == APPROVAL_APPROVED,
            "approval.state must be approved.",
            {"actual": approval.get("state")},
        ),
        _check(
            "promotion_decision_recorded",
            promotion.get("decision") == PROMOTION_DECISION_PROMOTED,
            "promotion.decision must be promoted.",
            {"actual": promotion.get("decision")},
        ),
        _check_path(
            "candidate_model_available",
            candidate.get("model_path"),
            project_root=project_root,
        ),
        _check_path(
            "candidate_metrics_available",
            candidate.get("metrics_path"),
            project_root=project_root,
        ),
        _check_path(
            "comparison_report_available",
            candidate.get("comparison_report_path"),
            project_root=project_root,
        ),
        _check_path(
            "approval_record_available",
            approval.get("record_path") or promotion.get("approval_record_path"),
            project_root=project_root,
        ),
        _check_path(
            "promotion_record_available",
            promotion.get("record_path"),
            project_root=project_root,
        ),
        _check(
            "rollback_target_recorded",
            isinstance(promotion.get("rollback_target"), dict)
            and bool(promotion["rollback_target"].get("model_version"))
            and bool(promotion["rollback_target"].get("artifact_uri")),
            "rollback target must include model_version and artifact_uri.",
            {"rollback_target": promotion.get("rollback_target")},
        ),
        _check(
            "registry_update_not_performed",
            promotion.get("registry_update") == "not_performed",
            "registry update should still be explicitly not_performed before handoff.",
            {"actual": promotion.get("registry_update")},
        ),
        _check(
            "serving_update_not_performed",
            promotion.get("serving_update") == "not_performed",
            "serving update should still be explicitly not_performed before handoff.",
            {"actual": promotion.get("serving_update")},
        ),
    ]
    return checks


def _check(
    name: str,
    passed: bool,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": CHECK_PASSED if passed else CHECK_FAILED,
        "message": message,
        "details": details or {},
    }


def _check_path(
    name: str,
    path_value: Any,
    *,
    project_root: Path,
) -> dict[str, Any]:
    if not isinstance(path_value, str) or not path_value:
        return _check(
            name,
            False,
            "required path is missing.",
            {"path": path_value},
        )

    path = Path(path_value)
    resolved_path = path if path.is_absolute() else project_root / path
    return _check(
        name,
        resolved_path.is_file(),
        "required file must exist before serving update handoff.",
        {"path": path_value, "resolved_path": str(resolved_path)},
    )


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


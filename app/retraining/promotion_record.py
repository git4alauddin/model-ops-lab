"""Approved candidate promotion record for V10."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    CANDIDATE_APPROVAL_RECORDED,
    CANDIDATE_PROMOTED,
    DEFAULT_RETRAINING_RUNS_DIR,
    PROMOTION_DECISION_PENDING,
    PROMOTION_DECISION_PROMOTED,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.utils.artifacts import ArtifactError, save_json


class PromotionRecordError(ValueError):
    """Raised when an approved candidate promotion cannot be recorded."""


def build_promotion_record(
    *,
    metadata: dict[str, Any],
    promoted_by: str,
    reason: str,
    promoted_at: str | None = None,
) -> dict[str, Any]:
    """Build an audited promotion decision record without updating serving."""
    _validate_promotion_inputs(
        metadata=metadata,
        promoted_by=promoted_by,
        reason=reason,
    )
    candidate = metadata["candidate"]
    approval = metadata["approval"]
    promotion = metadata["promotion"]
    return {
        "run_id": metadata["run_id"],
        "promoted_at": promoted_at or _utc_now(),
        "decision": PROMOTION_DECISION_PROMOTED,
        "promoted_by": promoted_by.strip(),
        "reason": reason.strip(),
        "approval_record_path": approval.get("record_path"),
        "comparison_report_path": candidate.get("comparison_report_path"),
        "candidate": {
            "model_type": candidate.get("model_type"),
            "model_path": candidate.get("model_path"),
            "metrics_path": candidate.get("metrics_path"),
            "metrics": deepcopy(candidate.get("metrics", {})),
        },
        "previous_production_model": deepcopy(
            metadata.get("previous_production_model")
        ),
        "rollback_target": deepcopy(promotion.get("rollback_target")),
        "registry_update": "not_performed",
        "serving_update": "not_performed",
        "notes": (
            "This record captures the approved promotion decision only. "
            "Model registry and serving updates are intentionally separate."
        ),
    }


def save_promotion_record(
    record: dict[str, Any],
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> Path:
    """Persist an approved candidate promotion record inside the retraining run."""
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    output_path = metadata_path.parent / "promotion_record.json"
    try:
        save_json(record, output_path)
    except ArtifactError as exc:
        raise PromotionRecordError(
            f"Failed to save promotion record: {output_path}"
        ) from exc
    return output_path


def update_metadata_after_promotion_record(
    metadata: dict[str, Any],
    *,
    record: dict[str, Any],
    record_path: Path,
) -> dict[str, Any]:
    """Return retraining metadata updated with the promotion decision record."""
    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = CANDIDATE_PROMOTED
    updated_metadata["promotion"].update(
        {
            "decision": PROMOTION_DECISION_PROMOTED,
            "promoted_at": record["promoted_at"],
            "promoted_by": record["promoted_by"],
            "reason": record["reason"],
            "record_path": str(record_path),
            "registry_update": record["registry_update"],
            "serving_update": record["serving_update"],
            "rollback_target": deepcopy(record["rollback_target"]),
        }
    )
    return updated_metadata


def record_approved_candidate_promotion(
    *,
    run_id: str,
    promoted_by: str,
    reason: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    promoted_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Record an approved candidate promotion decision."""
    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        record = build_promotion_record(
            metadata=metadata,
            promoted_by=promoted_by,
            reason=reason,
            promoted_at=promoted_at,
        )
        record_path = save_promotion_record(record, run_id=run_id, runs_dir=runs_dir)
        updated_metadata = update_metadata_after_promotion_record(
            metadata,
            record=record,
            record_path=record_path,
        )
        save_candidate_retraining_run_metadata(updated_metadata, runs_dir=runs_dir)
    except CandidateRetrainingRunError as exc:
        raise PromotionRecordError(
            f"Promotion record failed for run_id={run_id}: {exc}"
        ) from exc

    return record, updated_metadata, record_path


def _validate_promotion_inputs(
    *,
    metadata: dict[str, Any],
    promoted_by: str,
    reason: str,
) -> None:
    if metadata.get("status") != CANDIDATE_APPROVAL_RECORDED:
        raise PromotionRecordError(
            "Promotion record requires status="
            f"{CANDIDATE_APPROVAL_RECORDED}; got {metadata.get('status')}."
        )
    approval = metadata.get("approval")
    if not isinstance(approval, dict) or approval.get("state") != APPROVAL_APPROVED:
        raise PromotionRecordError("Promotion record requires approval.state=approved.")
    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict):
        raise PromotionRecordError("Promotion metadata is required.")
    if promotion.get("decision") != PROMOTION_DECISION_PENDING:
        raise PromotionRecordError(
            "Promotion record requires promotion.decision="
            f"{PROMOTION_DECISION_PENDING}; got {promotion.get('decision')}."
        )
    if promotion.get("production_change_allowed") is not True:
        raise PromotionRecordError(
            "Promotion record requires production_change_allowed=true."
        )
    candidate = metadata.get("candidate")
    if not isinstance(candidate, dict):
        raise PromotionRecordError("Candidate metadata is required.")
    if not candidate.get("model_path") or not candidate.get("metrics_path"):
        raise PromotionRecordError("Candidate model and metrics paths are required.")
    if not isinstance(promoted_by, str) or not promoted_by.strip():
        raise PromotionRecordError("promoted_by is required.")
    if not isinstance(reason, str) or not reason.strip():
        raise PromotionRecordError("promotion reason is required.")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


"""Human approval gate for governed retraining runs."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.retraining.candidate_comparison import GATE_PASSED
from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    APPROVAL_NEEDS_REVIEW,
    APPROVAL_REJECTED,
    CANDIDATE_APPROVAL_RECORDED,
    CANDIDATE_COMPARED,
    DEFAULT_RETRAINING_RUNS_DIR,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.utils.artifacts import ArtifactError, save_json

VALID_APPROVAL_DECISIONS = {
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    APPROVAL_NEEDS_REVIEW,
}


class ApprovalGateError(ValueError):
    """Raised when a retraining approval decision cannot be recorded."""


def build_approval_record(
    *,
    metadata: dict[str, Any],
    decision: str,
    approved_by: str,
    notes: str | None = None,
    decided_at: str | None = None,
) -> dict[str, Any]:
    """Build a human approval decision record."""
    _validate_approval_inputs(
        metadata=metadata,
        decision=decision,
        approved_by=approved_by,
    )
    return {
        "run_id": metadata["run_id"],
        "decided_at": decided_at or _utc_now(),
        "decision": decision,
        "approved_by": approved_by,
        "notes": notes,
        "comparison_report_path": metadata["candidate"].get(
            "comparison_report_path"
        ),
        "regression_gate_status": metadata["regression_gates"]["status"],
        "promotion_recommendation": metadata["promotion"]["recommendation"],
        "production_change_allowed": decision == APPROVAL_APPROVED,
    }


def save_approval_record(
    record: dict[str, Any],
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> Path:
    """Persist a human approval record inside the retraining run."""
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    output_path = metadata_path.parent / "approval_record.json"
    try:
        save_json(record, output_path)
    except ArtifactError as exc:
        raise ApprovalGateError(
            f"Failed to save approval record: {output_path}"
        ) from exc
    return output_path


def update_metadata_after_approval_record(
    metadata: dict[str, Any],
    *,
    record: dict[str, Any],
    record_path: Path,
) -> dict[str, Any]:
    """Return retraining metadata updated with the human approval decision."""
    updated_metadata = deepcopy(metadata)
    decision = record["decision"]
    updated_metadata["status"] = CANDIDATE_APPROVAL_RECORDED
    updated_metadata["approval"] = {
        "state": decision,
        "decision": decision,
        "approved_by": record["approved_by"] if decision == APPROVAL_APPROVED else None,
        "approved_at": record["decided_at"] if decision == APPROVAL_APPROVED else None,
        "decided_by": record["approved_by"],
        "decided_at": record["decided_at"],
        "notes": record.get("notes"),
        "record_path": str(record_path),
    }
    updated_metadata["promotion"]["decision"] = "pending"
    updated_metadata["promotion"]["approval_record_path"] = str(record_path)
    updated_metadata["promotion"]["production_change_allowed"] = (
        decision == APPROVAL_APPROVED
    )
    return updated_metadata


def record_retraining_approval(
    *,
    run_id: str,
    decision: str,
    approved_by: str,
    notes: str | None = None,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    decided_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Record a human approval decision and update retraining metadata."""
    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        record = build_approval_record(
            metadata=metadata,
            decision=decision,
            approved_by=approved_by,
            notes=notes,
            decided_at=decided_at,
        )
        record_path = save_approval_record(record, run_id=run_id, runs_dir=runs_dir)
        updated_metadata = update_metadata_after_approval_record(
            metadata,
            record=record,
            record_path=record_path,
        )
        save_candidate_retraining_run_metadata(updated_metadata, runs_dir=runs_dir)
    except CandidateRetrainingRunError as exc:
        raise ApprovalGateError(
            f"Approval decision failed for run_id={run_id}: {exc}"
        ) from exc

    return record, updated_metadata, record_path


def _validate_approval_inputs(
    *,
    metadata: dict[str, Any],
    decision: str,
    approved_by: str,
) -> None:
    if metadata.get("status") != CANDIDATE_COMPARED:
        raise ApprovalGateError(
            "Approval decision requires status="
            f"{CANDIDATE_COMPARED}; got {metadata.get('status')}."
        )
    if decision not in VALID_APPROVAL_DECISIONS:
        raise ApprovalGateError(
            "Invalid approval decision: "
            f"{decision}. Expected one of {sorted(VALID_APPROVAL_DECISIONS)}."
        )
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise ApprovalGateError("approved_by is required.")
    regression_gates = metadata.get("regression_gates")
    if not isinstance(regression_gates, dict):
        raise ApprovalGateError("Regression gate results are required.")
    if regression_gates.get("status") != GATE_PASSED:
        raise ApprovalGateError(
            "Approval decision requires regression_gates.status="
            f"{GATE_PASSED}; got {regression_gates.get('status')}."
        )


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


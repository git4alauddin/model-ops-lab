"""Validation stage helper for the V5 training pipeline."""

from pathlib import Path
from typing import Callable

from app.train import enforce_validation_gate
from app.validate_data import validate_dataset_readiness
from app.validation.reports import ValidationReport


def run_validation_stage(
    *,
    config_path: str | Path,
    schema_path: str | Path,
    validation_runner: Callable[[str | Path, str | Path], ValidationReport] = (
        validate_dataset_readiness
    ),
) -> ValidationReport:
    """Run dataset validation and enforce the training gate."""
    validation_report = validation_runner(config_path, schema_path)
    enforce_validation_gate(validation_report)
    return validation_report

"""Validation schema loading and structural checks."""

from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from yaml import YAMLError

from app.validation.reports import ValidationIssue


class ValidationError(ValueError):
    """Raised when validation setup or checks fail."""


def load_validation_schema(schema_path: str | Path) -> dict[str, Any]:
    """Load and validate a versioned dataset schema file."""
    path = Path(schema_path)
    if not path.exists():
        raise ValidationError(f"Validation schema file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            schema = yaml.safe_load(file) or {}
    except OSError as exc:
        raise ValidationError(f"Unable to read validation schema: {path}") from exc
    except YAMLError as exc:
        raise ValidationError(f"Invalid YAML in validation schema: {path}") from exc

    if not isinstance(schema, dict):
        raise ValidationError("Validation schema root must be a dictionary.")

    _validate_schema_contract(schema)
    return schema


def validate_required_columns(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for schema columns missing from the dataframe."""
    expected_columns = _schema_column_names(schema)
    actual_columns = set(dataframe.columns)

    return [
        ValidationIssue(
            severity="ERROR",
            check="required_columns",
            message=f"missing required column: {column}",
        )
        for column in expected_columns
        if column not in actual_columns
    ]


def validate_unexpected_columns(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for dataframe columns not defined in the schema."""
    expected_columns = set(_schema_column_names(schema))

    return [
        ValidationIssue(
            severity="ERROR",
            check="unexpected_columns",
            message=f"unexpected column: {column}",
        )
        for column in dataframe.columns
        if column not in expected_columns
    ]


def validate_schema_columns(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Run structural dataframe-vs-schema column checks."""
    issues: list[ValidationIssue] = []
    issues.extend(validate_required_columns(dataframe, schema))
    issues.extend(validate_unexpected_columns(dataframe, schema))
    return issues


def _validate_schema_contract(schema: dict[str, Any]) -> None:
    required_keys = ["name", "version", "columns"]
    for key in required_keys:
        if schema.get(key) in (None, ""):
            raise ValidationError(f"Missing validation schema key: {key}")

    columns = schema["columns"]
    if not isinstance(columns, dict) or not columns:
        raise ValidationError("Validation schema columns must be a non-empty map.")

    for column_name, column_rules in columns.items():
        if not isinstance(column_rules, dict):
            raise ValidationError(
                f"Validation rules for column '{column_name}' must be a map."
            )
        if column_rules.get("dtype") in (None, ""):
            raise ValidationError(f"Missing dtype for column: {column_name}")
        if "nullable" not in column_rules:
            raise ValidationError(f"Missing nullable rule for column: {column_name}")


def _schema_column_names(schema: dict[str, Any]) -> list[str]:
    columns = schema.get("columns")
    if not isinstance(columns, dict):
        raise ValidationError("Validation schema columns must be a map.")
    return list(columns.keys())

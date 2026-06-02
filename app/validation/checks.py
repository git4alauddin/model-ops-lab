"""Validation schema loading helpers."""

from pathlib import Path
from typing import Any

import yaml
from yaml import YAMLError


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

"""Validation schema loading and structural checks."""

from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
)
import yaml
from yaml import YAMLError

from app.validation.reports import ValidationIssue

SUPPORTED_SCHEMA_DTYPES = {"boolean", "category", "float", "integer", "string"}


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


def validate_column_dtypes(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for present columns whose pandas dtype does not match schema."""
    issues: list[ValidationIssue] = []
    for column_name, column_rules in _schema_columns(schema).items():
        if column_name not in dataframe.columns:
            continue

        expected_dtype = str(column_rules["dtype"]).lower()
        series = dataframe[column_name]
        if not _series_matches_schema_dtype(series, expected_dtype):
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    check="column_dtypes",
                    message=(
                        f"column '{column_name}' expected {expected_dtype} "
                        f"but found {series.dtype}"
                    ),
                )
            )

    return issues


def validate_nullable_columns(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for non-nullable columns that contain null values."""
    issues: list[ValidationIssue] = []
    for column_name, column_rules in _schema_columns(schema).items():
        if column_name not in dataframe.columns:
            continue

        if bool(column_rules["nullable"]):
            continue

        null_count = int(dataframe[column_name].isna().sum())
        if null_count:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    check="nullable_columns",
                    message=(
                        f"column '{column_name}' is not nullable "
                        f"but contains {null_count} null value(s)"
                    ),
                )
            )

    return issues


def validate_numeric_ranges(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for numeric values outside schema min/max bounds."""
    issues: list[ValidationIssue] = []
    for column_name, column_rules in _schema_columns(schema).items():
        if column_name not in dataframe.columns:
            continue

        min_value = column_rules.get("min")
        max_value = column_rules.get("max")
        if min_value is None and max_value is None:
            continue

        series = dataframe[column_name].dropna()
        if series.empty or not _series_supports_numeric_ranges(series):
            continue

        if min_value is not None:
            below_min_count = int((series < min_value).sum())
            if below_min_count:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        check="numeric_ranges",
                        message=(
                            f"column '{column_name}' has {below_min_count} "
                            f"value(s) below min {min_value}"
                        ),
                    )
                )

        if max_value is not None:
            above_max_count = int((series > max_value).sum())
            if above_max_count:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        check="numeric_ranges",
                        message=(
                            f"column '{column_name}' has {above_max_count} "
                            f"value(s) above max {max_value}"
                        ),
                    )
                )

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
        dtype = str(column_rules["dtype"]).lower()
        if dtype not in SUPPORTED_SCHEMA_DTYPES:
            raise ValidationError(
                f"Unsupported dtype '{dtype}' for column: {column_name}"
            )
        if "nullable" not in column_rules:
            raise ValidationError(f"Missing nullable rule for column: {column_name}")
        _validate_numeric_bound(column_name, column_rules, "min")
        _validate_numeric_bound(column_name, column_rules, "max")


def _schema_column_names(schema: dict[str, Any]) -> list[str]:
    return list(_schema_columns(schema).keys())


def _schema_columns(schema: dict[str, Any]) -> dict[str, Any]:
    columns = schema.get("columns")
    if not isinstance(columns, dict):
        raise ValidationError("Validation schema columns must be a map.")
    return columns


def _series_matches_schema_dtype(series: pd.Series, expected_dtype: str) -> bool:
    dtype_name = str(series.dtype)
    if expected_dtype == "boolean":
        return bool(is_bool_dtype(series))

    if expected_dtype == "integer":
        return bool(is_integer_dtype(series) and not is_bool_dtype(series))

    if expected_dtype == "float":
        return bool(is_float_dtype(series))

    if expected_dtype == "string":
        return bool(
            dtype_name in {"str", "string"}
            or _non_null_values_match_type(series, str)
        )

    if expected_dtype == "category":
        return bool(
            isinstance(series.dtype, pd.CategoricalDtype)
            or dtype_name in {"str", "string"}
            or _non_null_values_match_type(series, str)
        )

    raise ValidationError(f"Unsupported dtype: {expected_dtype}")


def _series_supports_numeric_ranges(series: pd.Series) -> bool:
    return bool(is_numeric_dtype(series) and not is_bool_dtype(series))


def _non_null_values_match_type(series: pd.Series, expected_type: type) -> bool:
    non_null_values = series.dropna()
    return bool(non_null_values.map(lambda value: isinstance(value, expected_type)).all())


def _validate_numeric_bound(
    column_name: str,
    column_rules: dict[str, Any],
    bound_name: str,
) -> None:
    if bound_name not in column_rules:
        return

    bound_value = column_rules[bound_name]
    if isinstance(bound_value, bool) or not isinstance(bound_value, (int, float)):
        raise ValidationError(
            f"{bound_name} for column '{column_name}' must be numeric."
        )

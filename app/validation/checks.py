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


def validate_allowed_values(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for values outside schema allowed_values lists."""
    issues: list[ValidationIssue] = []
    for column_name, column_rules in _schema_columns(schema).items():
        if column_name not in dataframe.columns:
            continue

        allowed_values = column_rules.get("allowed_values")
        if allowed_values is None:
            continue

        allowed_set = set(allowed_values)
        observed_values = set(dataframe[column_name].dropna().unique())
        invalid_values = sorted(
            observed_values - allowed_set,
            key=lambda value: str(value),
        )
        if invalid_values:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    check="allowed_values",
                    message=(
                        f"column '{column_name}' contains invalid value(s): "
                        f"{invalid_values}"
                    ),
                )
            )

    return issues


def validate_duplicate_rows(dataframe: pd.DataFrame) -> list[ValidationIssue]:
    """Return a warning when exact duplicate rows exist."""
    duplicate_count = int(dataframe.duplicated().sum())
    if not duplicate_count:
        return []

    return [
        ValidationIssue(
            severity="WARNING",
            check="duplicate_rows",
            message=f"dataset contains {duplicate_count} duplicate row(s)",
        )
    ]


def validate_duplicate_ids(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return an error when the schema id_column has duplicate values."""
    id_column = schema.get("id_column")
    if not id_column:
        return []

    if not isinstance(id_column, str):
        raise ValidationError("Validation schema id_column must be a string.")

    if id_column not in dataframe.columns:
        return []

    duplicate_id_count = int(dataframe[id_column].dropna().duplicated().sum())
    if not duplicate_id_count:
        return []

    return [
        ValidationIssue(
            severity="ERROR",
            check="duplicate_ids",
            message=(
                f"id column '{id_column}' contains "
                f"{duplicate_id_count} duplicate value(s)"
            ),
        )
    ]


def validate_target_distribution(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> list[ValidationIssue]:
    """Return issues for unusable or suspicious target class distributions."""
    target_rules = _target_distribution_rules(schema)
    if not target_rules:
        return []

    target_column = schema.get("target_column")
    if not isinstance(target_column, str) or not target_column:
        return []

    if target_column not in dataframe.columns:
        return []

    target_values = dataframe[target_column].dropna()
    if target_values.empty:
        return [
            ValidationIssue(
                severity="ERROR",
                check="target_distribution",
                message=f"target column '{target_column}' contains no non-null values",
            )
        ]

    class_counts = target_values.value_counts()
    if len(class_counts) == 1:
        only_class = class_counts.index[0]
        return [
            ValidationIssue(
                severity="ERROR",
                check="target_distribution",
                message=(
                    f"target column '{target_column}' contains only one class: "
                    f"{only_class}"
                ),
            )
        ]

    total_count = int(class_counts.sum())
    minority_ratio = float(class_counts.min() / total_count)
    dominant_ratio = float(class_counts.max() / total_count)
    min_class_ratio = float(target_rules.get("min_class_ratio", 0.0))
    max_class_ratio = float(target_rules.get("max_class_ratio", 1.0))

    if minority_ratio < min_class_ratio or dominant_ratio > max_class_ratio:
        return [
            ValidationIssue(
                severity="WARNING",
                check="target_distribution",
                message=(
                    f"target column '{target_column}' has suspicious class "
                    f"distribution: {_format_distribution_counts(class_counts)} "
                    f"(minority_ratio={minority_ratio:.4f}, "
                    f"dominant_ratio={dominant_ratio:.4f})"
                ),
            )
        ]

    return []


def _validate_schema_contract(schema: dict[str, Any]) -> None:
    required_keys = ["name", "version", "columns"]
    for key in required_keys:
        if schema.get(key) in (None, ""):
            raise ValidationError(f"Missing validation schema key: {key}")

    columns = schema["columns"]
    if not isinstance(columns, dict) or not columns:
        raise ValidationError("Validation schema columns must be a non-empty map.")

    id_column = schema.get("id_column")
    if id_column is not None and not isinstance(id_column, str):
        raise ValidationError("Validation schema id_column must be a string.")

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
        _validate_allowed_values(column_name, column_rules)
    _validate_quality_checks(schema)


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


def _validate_allowed_values(
    column_name: str,
    column_rules: dict[str, Any],
) -> None:
    if "allowed_values" not in column_rules:
        return

    allowed_values = column_rules["allowed_values"]
    if not isinstance(allowed_values, list) or not allowed_values:
        raise ValidationError(
            f"allowed_values for column '{column_name}' must be a non-empty list."
        )


def _validate_quality_checks(schema: dict[str, Any]) -> None:
    quality_checks = schema.get("quality_checks")
    if quality_checks is None:
        return

    if not isinstance(quality_checks, dict):
        raise ValidationError("Validation schema quality_checks must be a map.")

    target_rules = quality_checks.get("target_distribution")
    if target_rules is None:
        return

    if not isinstance(target_rules, dict):
        raise ValidationError(
            "Validation schema quality_checks.target_distribution must be a map."
        )

    enabled = target_rules.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValidationError("target_distribution.enabled must be a boolean.")

    if not enabled:
        return

    target_column = schema.get("target_column")
    if not isinstance(target_column, str) or not target_column:
        raise ValidationError(
            "target_distribution requires a non-empty schema target_column."
        )

    min_ratio = _validate_ratio_bound(target_rules, "min_class_ratio", 0.0)
    max_ratio = _validate_ratio_bound(target_rules, "max_class_ratio", 1.0)
    if min_ratio >= max_ratio:
        raise ValidationError(
            "target_distribution min_class_ratio must be less than max_class_ratio."
        )


def _validate_ratio_bound(
    target_rules: dict[str, Any],
    key: str,
    default: float,
) -> float:
    value = target_rules.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"target_distribution.{key} must be numeric.")

    ratio = float(value)
    if ratio < 0 or ratio > 1:
        raise ValidationError(f"target_distribution.{key} must be between 0 and 1.")

    return ratio


def _target_distribution_rules(schema: dict[str, Any]) -> dict[str, Any]:
    quality_checks = schema.get("quality_checks")
    if not isinstance(quality_checks, dict):
        return {}

    target_rules = quality_checks.get("target_distribution")
    if not isinstance(target_rules, dict):
        return {}

    if target_rules.get("enabled", True) is False:
        return {}

    return target_rules


def _format_distribution_counts(class_counts: pd.Series) -> str:
    parts = [
        f"{value}={int(count)}"
        for value, count in sorted(class_counts.items(), key=lambda item: str(item[0]))
    ]
    return ", ".join(parts)

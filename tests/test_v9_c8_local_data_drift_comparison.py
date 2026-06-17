import json
from pathlib import Path

import pytest

from app.observability.drift_comparison import (
    DriftComparisonError,
    build_and_save_data_drift_summary,
    compare_data_drift,
    load_drift_json,
    save_data_drift_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"


def test_data_drift_summary_is_ok_for_similar_distributions() -> None:
    summary = compare_data_drift(
        _reference_baseline(),
        _inference_snapshot(
            tenure_mean=24.0,
            tenure_min=2.0,
            tenure_max=58.0,
            contract_ratios={"month_to_month": 0.45, "one_year": 0.25, "two_year": 0.30},
        ),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert summary["overall_status"] == "ok"
    assert summary["drifted_feature_count"] == 0
    assert summary["insufficient_feature_count"] == 0
    assert summary["features"]["tenure_months"]["status"] == "ok"
    assert summary["features"]["contract_type"]["status"] == "ok"


def test_data_drift_summary_flags_numeric_and_categorical_drift() -> None:
    summary = compare_data_drift(
        _reference_baseline(),
        _inference_snapshot(
            tenure_mean=40.0,
            tenure_min=-10.0,
            tenure_max=90.0,
            contract_ratios={"month_to_month": 0.90, "one_year": 0.05, "two_year": 0.05},
        ),
    )

    assert summary["overall_status"] == "drift_detected"
    assert summary["drifted_feature_count"] == 2
    assert summary["features"]["tenure_months"]["status"] == "drift_detected"
    assert summary["features"]["tenure_months"]["checks"]["mean_relative_change"] > 0.2
    assert summary["features"]["contract_type"]["status"] == "drift_detected"
    assert summary["features"]["contract_type"]["checks"]["max_ratio_change"] == 0.4


def test_data_drift_summary_reports_insufficient_data_for_empty_inference() -> None:
    summary = compare_data_drift(
        _reference_baseline(),
        {
            "snapshot_version": "v1",
            "generated_at": "2026-06-17T00:00:00+00:00",
            "row_count": 0,
            "features": {},
        },
    )

    assert summary["overall_status"] == "insufficient_data"
    assert summary["drifted_feature_count"] == 0
    assert summary["insufficient_feature_count"] == 2
    assert summary["features"]["tenure_months"]["status"] == "insufficient_data"
    assert summary["features"]["tenure_months"]["feature_name"] == "tenure_months"
    assert summary["features"]["tenure_months"]["checks"]["reason"] == "no_inference_rows"
    assert summary["features"]["contract_type"]["status"] == "insufficient_data"
    assert summary["features"]["contract_type"]["feature_name"] == "contract_type"
    assert summary["features"]["contract_type"]["checks"]["reason"] == "no_inference_rows"


def test_save_and_build_data_drift_summary_persist_json(tmp_path) -> None:
    reference_path = tmp_path / "reference_baseline.json"
    inference_path = tmp_path / "inference_snapshot.json"
    output_path = tmp_path / "data_drift_summary.json"
    reference_path.write_text(json.dumps(_reference_baseline()), encoding="utf-8")
    inference_path.write_text(json.dumps(_inference_snapshot()), encoding="utf-8")

    summary = build_and_save_data_drift_summary(
        reference_path=reference_path,
        inference_path=inference_path,
        output_path=output_path,
    )

    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8")) == summary

    second_output_path = tmp_path / "copy.json"
    save_data_drift_summary(summary, second_output_path)

    assert json.loads(second_output_path.read_text(encoding="utf-8")) == summary


def test_load_drift_json_rejects_missing_or_invalid_file(tmp_path) -> None:
    with pytest.raises(DriftComparisonError, match="not found"):
        load_drift_json(tmp_path / "missing.json")

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(DriftComparisonError, match="Invalid drift JSON"):
        load_drift_json(invalid_path)


def test_v9_c8_docs_mention_drift_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()

    assert "python -m app.build_data_drift_summary" in readme
    assert "reports/drift/data_drift_summary.json" in readme
    assert "V9-C8: Local Data Drift Comparison" in implementation


def _reference_baseline() -> dict:
    return {
        "baseline_version": "v1",
        "generated_at": "2026-06-17T00:00:00+00:00",
        "schema_name": "customer_churn",
        "schema_version": "v1",
        "row_count": 20,
        "features": {
            "tenure_months": {
                "kind": "numeric",
                "count": 20,
                "stats": {
                    "min": 1.0,
                    "max": 60.0,
                    "mean": 22.85,
                },
            },
            "contract_type": {
                "kind": "categorical",
                "count": 20,
                "value_ratios": {
                    "month_to_month": 0.5,
                    "one_year": 0.2,
                    "two_year": 0.3,
                },
            },
        },
    }


def _inference_snapshot(
    *,
    tenure_mean: float = 24.0,
    tenure_min: float = 2.0,
    tenure_max: float = 58.0,
    contract_ratios: dict[str, float] | None = None,
) -> dict:
    return {
        "snapshot_version": "v1",
        "generated_at": "2026-06-17T00:00:00+00:00",
        "row_count": 10,
        "features": {
            "tenure_months": {
                "kind": "numeric",
                "count": 10,
                "stats": {
                    "min": tenure_min,
                    "max": tenure_max,
                    "mean": tenure_mean,
                },
            },
            "contract_type": {
                "kind": "categorical",
                "count": 10,
                "value_ratios": contract_ratios
                or {
                    "month_to_month": 0.45,
                    "one_year": 0.25,
                    "two_year": 0.30,
                },
            },
        },
    }

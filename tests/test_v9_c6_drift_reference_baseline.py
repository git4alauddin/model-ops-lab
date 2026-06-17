import json
from pathlib import Path

import pandas as pd
import pytest

from app.observability.drift_baseline import (
    DriftBaselineError,
    build_and_save_reference_baseline,
    build_reference_baseline,
    build_reference_baseline_from_config,
    save_reference_baseline,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"


def test_reference_baseline_contains_feature_and_target_distributions() -> None:
    baseline = build_reference_baseline(
        _dataframe(),
        _schema(),
        dataset_path=Path("data/churn.csv"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert baseline["baseline_version"] == "v1"
    assert baseline["row_count"] == 4
    assert baseline["feature_count"] == 3
    assert set(baseline["features"]) == {
        "tenure_months",
        "contract_type",
        "is_senior",
    }
    assert set(baseline["targets"]) == {"churn"}


def test_reference_baseline_summarizes_numeric_feature_stats() -> None:
    baseline = build_reference_baseline(
        _dataframe(),
        _schema(),
        dataset_path=Path("data/churn.csv"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
    )

    tenure = baseline["features"]["tenure_months"]

    assert tenure["kind"] == "numeric"
    assert tenure["dtype"] == "integer"
    assert tenure["count"] == 4
    assert tenure["null_count"] == 0
    assert tenure["stats"]["min"] == 1.0
    assert tenure["stats"]["max"] == 40.0
    assert tenure["stats"]["mean"] == 16.75
    assert tenure["stats"]["p50"] == 13.0


def test_reference_baseline_summarizes_categorical_and_boolean_ratios() -> None:
    baseline = build_reference_baseline(
        _dataframe(),
        _schema(),
        dataset_path=Path("data/churn.csv"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
    )

    contract = baseline["features"]["contract_type"]
    senior = baseline["features"]["is_senior"]
    churn = baseline["targets"]["churn"]

    assert contract["kind"] == "categorical"
    assert contract["value_counts"] == {"month_to_month": 2, "one_year": 1, "two_year": 1}
    assert contract["value_ratios"] == {
        "month_to_month": 0.5,
        "one_year": 0.25,
        "two_year": 0.25,
    }
    assert senior["value_counts"] == {"False": 3, "True": 1}
    assert churn["value_counts"] == {"0": 2, "1": 2}


def test_reference_baseline_from_config_uses_project_training_contract() -> None:
    baseline = build_reference_baseline_from_config(
        PROJECT_ROOT / "configs" / "training.yaml",
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert baseline["schema_name"] == "customer_churn"
    assert baseline["schema_version"] == "v1"
    assert baseline["row_count"] == 20
    assert baseline["feature_count"] == 7
    assert "monthly_charges" in baseline["features"]
    assert "churn" in baseline["targets"]


def test_save_and_build_reference_baseline_persist_json(tmp_path) -> None:
    output_path = tmp_path / "reports" / "drift" / "reference_baseline.json"
    baseline = build_reference_baseline(
        _dataframe(),
        _schema(),
        dataset_path=Path("data/churn.csv"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    save_reference_baseline(baseline, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == baseline

    built = build_and_save_reference_baseline(
        config_path=PROJECT_ROOT / "configs" / "training.yaml",
        output_path=output_path,
    )

    assert output_path.is_file()
    assert built["feature_count"] == 7


def test_reference_baseline_rejects_empty_dataset() -> None:
    with pytest.raises(DriftBaselineError, match="empty dataset"):
        build_reference_baseline(
            pd.DataFrame(),
            _schema(),
            dataset_path=Path("data/churn.csv"),
            schema_path=Path("schema_versions/customer_churn_v1.yaml"),
        )


def test_v9_c6_docs_mention_baseline_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()

    assert "python -m app.build_drift_reference_baseline" in readme
    assert "reports/drift/reference_baseline.json" in readme
    assert "V9-C6: Data Drift Reference Baseline Foundation" in implementation


def _dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "tenure_months": [1, 10, 16, 40],
            "contract_type": [
                "month_to_month",
                "one_year",
                "two_year",
                "month_to_month",
            ],
            "is_senior": [False, False, True, False],
            "churn": [1, 0, 1, 0],
        }
    )


def _schema() -> dict:
    return {
        "name": "customer_churn",
        "version": "v1",
        "columns": {
            "tenure_months": {
                "dtype": "integer",
                "nullable": False,
                "role": "feature",
            },
            "contract_type": {
                "dtype": "category",
                "nullable": False,
                "role": "feature",
                "allowed_values": ["month_to_month", "one_year", "two_year"],
            },
            "is_senior": {
                "dtype": "boolean",
                "nullable": False,
                "role": "feature",
                "allowed_values": [True, False],
            },
            "churn": {
                "dtype": "integer",
                "nullable": False,
                "role": "target",
                "allowed_values": [0, 1],
            },
        },
    }

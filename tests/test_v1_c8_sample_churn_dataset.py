"""Tests for V1 sample churn dataset smoke support."""

from pathlib import Path

import pandas as pd

from app.train import DataError, drop_configured_columns, load_dataset


def test_sample_churn_dataset_exists_and_loads():
    dataframe = load_dataset(Path("data/churn.csv"))

    assert not dataframe.empty
    assert "churn" in dataframe.columns
    assert set(dataframe["churn"].unique()) == {0, 1}


def test_drop_configured_columns_success():
    dataframe = pd.DataFrame(
        {
            "customer_id": ["C001", "C002"],
            "tenure_months": [2, 24],
            "churn": [1, 0],
        }
    )

    transformed = drop_configured_columns(dataframe, ["customer_id"])

    assert "customer_id" not in transformed.columns
    assert list(transformed.columns) == ["tenure_months", "churn"]


def test_drop_configured_columns_missing_column():
    dataframe = pd.DataFrame({"tenure_months": [2, 24], "churn": [1, 0]})

    try:
        drop_configured_columns(dataframe, ["customer_id"])
    except DataError as exc:
        assert "drop columns" in str(exc)
    else:
        raise AssertionError("Expected DataError for missing drop column.")

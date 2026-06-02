"""Tests for V1 train-test split behavior."""

import pandas as pd

from app.pipeline.preprocessing import PreprocessingError, split_train_test


def test_split_train_test_success():
    features = pd.DataFrame({"age": range(10), "tenure": range(10, 20)})
    target = pd.Series([0, 1] * 5, name="churn")

    x_train, x_test, y_train, y_test = split_train_test(
        features,
        target,
        test_size=0.3,
        random_state=42,
    )

    assert len(x_train) == 7
    assert len(x_test) == 3
    assert len(y_train) == 7
    assert len(y_test) == 3


def test_split_train_test_reproducible():
    features = pd.DataFrame({"age": range(20), "tenure": range(20, 40)})
    target = pd.Series([0, 1] * 10, name="churn")

    first_split = split_train_test(features, target, test_size=0.25, random_state=42)
    second_split = split_train_test(features, target, test_size=0.25, random_state=42)

    assert list(first_split[0].index) == list(second_split[0].index)
    assert list(first_split[1].index) == list(second_split[1].index)
    assert list(first_split[2].index) == list(second_split[2].index)
    assert list(first_split[3].index) == list(second_split[3].index)


def test_split_train_test_mismatched_lengths():
    features = pd.DataFrame({"age": [30, 45, 50]})
    target = pd.Series([0, 1], name="churn")

    try:
        split_train_test(features, target, test_size=0.2, random_state=42)
    except PreprocessingError as exc:
        assert "same row count" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError for mismatched lengths.")


def test_split_train_test_invalid_test_size():
    features = pd.DataFrame({"age": [30, 45, 50]})
    target = pd.Series([0, 1, 0], name="churn")

    try:
        split_train_test(features, target, test_size=1.0, random_state=42)
    except PreprocessingError as exc:
        assert "test_size" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError for invalid test_size.")

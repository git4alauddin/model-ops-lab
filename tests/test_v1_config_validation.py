"""Tests for V1 configuration loading and validation."""

from app.config import ConfigError, load_config


def test_load_config_success(tmp_path):
    config_file = tmp_path / "training.yaml"
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "  target_column: churn",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config["dataset"]["path"] == "data/churn.csv"
    assert config["training"]["random_state"] == 42


def test_load_config_missing_required_key(tmp_path):
    config_file = tmp_path / "training.yaml"
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_config(config_file)
    except ConfigError as exc:
        assert "dataset.target_column" in str(exc)
    else:
        raise AssertionError("Expected ConfigError for missing target column.")


def test_load_config_invalid_test_size(tmp_path):
    config_file = tmp_path / "training.yaml"
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "  target_column: churn",
                "training:",
                "  test_size: 1.5",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_config(config_file)
    except ConfigError as exc:
        assert "training.test_size" in str(exc)
    else:
        raise AssertionError("Expected ConfigError for invalid test_size.")

"""Configuration loading and validation for V1."""

from pathlib import Path
from typing import Any

import yaml
from yaml import YAMLError

from app.schemas import REQUIRED_CONFIG_KEYS


class ConfigError(ValueError):
    """Raised when training configuration is missing or invalid."""


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate a YAML config file."""
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
    except OSError as exc:
        raise ConfigError(f"Unable to read config file: {config_path}") from exc
    except YAMLError as exc:
        raise ConfigError(f"Invalid YAML in config file: {config_path}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Config root must be a dictionary.")

    validate_config(data)
    return data


def validate_config(config: dict[str, Any]) -> None:
    """Validate required config sections and value constraints."""
    for key_path in REQUIRED_CONFIG_KEYS:
        if _get_nested(config, key_path) in (None, ""):
            raise ConfigError(f"Missing required config key: {key_path}")

    test_size = _get_nested(config, "training.test_size")
    if not isinstance(test_size, (int, float)) or not 0 < float(test_size) < 1:
        raise ConfigError("training.test_size must be a number between 0 and 1.")

    random_state = _get_nested(config, "training.random_state")
    if not isinstance(random_state, int):
        raise ConfigError("training.random_state must be an integer.")


def _get_nested(config: dict[str, Any], key_path: str) -> Any:
    """Return nested config value for dot-separated key path."""
    current: Any = config
    for key in key_path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current

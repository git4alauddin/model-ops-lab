"""Lightweight contracts used by V1 configuration validation."""

REQUIRED_CONFIG_KEYS: tuple[str, ...] = (
    "dataset.path",
    "dataset.target_column",
    "training.test_size",
    "training.random_state",
)

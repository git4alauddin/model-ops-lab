"""Artifact persistence scaffold for V1."""

from pathlib import Path


def ensure_artifact_dir(path: Path) -> Path:
    """Create and return artifact directory path."""
    path.mkdir(parents=True, exist_ok=True)
    return path

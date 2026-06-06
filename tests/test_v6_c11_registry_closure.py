"""Closure checks for V6 model registry lifecycle."""

from pathlib import Path

from app.model_registry import MODEL_LIFECYCLE_STATES

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v6_lifecycle_states_are_defined():
    assert MODEL_LIFECYCLE_STATES == ("candidate", "champion", "archived")


def test_v6_registry_commands_exist():
    expected_commands = (
        "register_model.py",
        "promote_model.py",
        "query_model_registry.py",
        "rollback_model.py",
    )

    for command in expected_commands:
        assert (PROJECT_ROOT / "app" / command).exists()


def test_v6_registry_support_docs_exist():
    expected_docs = (
        "docs/diagrams/v6_model_registry_flow.md",
        "docs/decisions/adr_local_model_registry_for_v6.md",
        "docs/decisions/adr_model_registry_rollback_for_v6.md",
    )

    for doc_path in expected_docs:
        assert (PROJECT_ROOT / doc_path).exists()


def test_v6_version_docs_mark_completion():
    overview = (PROJECT_ROOT / "docs/versions/v6/overview.md").read_text(
        encoding="utf-8"
    )

    assert "V6 is complete." in overview

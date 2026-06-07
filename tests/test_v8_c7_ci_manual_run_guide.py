from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "ci_manual_run_guide.md"


def test_v8_ci_manual_run_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_ci_manual_run_guide_documents_workflow_dispatch() -> None:
    guide = GUIDE_PATH.read_text()

    assert "workflow_dispatch" in guide


def test_v8_ci_manual_run_guide_documents_github_ui_path() -> None:
    guide = GUIDE_PATH.read_text()

    assert "GitHub repository" in guide
    assert "Actions" in guide
    assert "Run workflow" in guide
    assert "Branch: main" in guide


def test_v8_ci_manual_run_guide_explains_workflow_jobs() -> None:
    guide = GUIDE_PATH.read_text()

    assert "tests" in guide
    assert "docker-image" in guide
    assert "python -m pytest -q" in guide
    assert "docker build" in guide


def test_v8_ci_manual_run_guide_states_no_registry_push_yet() -> None:
    guide = GUIDE_PATH.read_text().lower()

    assert "does not" in guide
    assert "docker hub" in guide
    assert "push images" in guide

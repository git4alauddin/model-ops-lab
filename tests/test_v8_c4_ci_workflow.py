from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_ci_workflow_exists() -> None:
    assert WORKFLOW_PATH.is_file()


def test_v8_ci_workflow_runs_on_push_and_pull_request() -> None:
    workflow_text = WORKFLOW_PATH.read_text()

    assert "on:" in workflow_text
    assert "push:" in workflow_text
    assert "pull_request:" in workflow_text
    assert "branches:" in workflow_text
    assert "- main" in workflow_text


def test_v8_ci_workflow_has_pytest_job() -> None:
    workflow = _load_workflow()

    assert "jobs" in workflow
    assert "tests" in workflow["jobs"]
    assert workflow["jobs"]["tests"]["runs-on"] == "ubuntu-latest"


def test_v8_ci_workflow_checks_out_repository() -> None:
    steps = _load_workflow()["jobs"]["tests"]["steps"]

    assert any(step.get("uses") == "actions/checkout@v4" for step in steps)


def test_v8_ci_workflow_sets_up_python() -> None:
    steps = _load_workflow()["jobs"]["tests"]["steps"]
    setup_step = next(
        step for step in steps if step.get("uses") == "actions/setup-python@v5"
    )

    assert setup_step["with"]["python-version"] == "3.11"
    assert setup_step["with"]["cache"] == "pip"
    assert setup_step["with"]["cache-dependency-path"] == "requirements.txt"


def test_v8_ci_workflow_installs_project_requirements() -> None:
    workflow_text = WORKFLOW_PATH.read_text()

    assert "python -m pip install --upgrade pip" in workflow_text
    assert "python -m pip install -r requirements.txt" in workflow_text


def test_v8_ci_workflow_runs_pytest() -> None:
    workflow_text = WORKFLOW_PATH.read_text()

    assert "python -m pytest -q" in workflow_text

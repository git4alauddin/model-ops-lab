from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_ci_docker_build_job_exists() -> None:
    jobs = _load_workflow()["jobs"]

    assert "docker-image" in jobs


def test_v8_ci_docker_build_runs_after_tests() -> None:
    job = _load_workflow()["jobs"]["docker-image"]

    assert job["needs"] == "tests"
    assert job["runs-on"] == "ubuntu-latest"


def test_v8_ci_docker_build_checks_out_repository() -> None:
    steps = _load_workflow()["jobs"]["docker-image"]["steps"]

    assert any(step.get("uses") == "actions/checkout@v4" for step in steps)


def test_v8_ci_docker_build_uses_serving_dockerfile() -> None:
    workflow_text = WORKFLOW_PATH.read_text()

    assert "docker build -f deployment/Dockerfile" in workflow_text
    assert "-t modelopslab-serving:ci" in workflow_text


def test_v8_ci_docker_build_does_not_push_image() -> None:
    workflow_text = WORKFLOW_PATH.read_text().lower()

    assert "docker login" not in workflow_text
    assert "docker push" not in workflow_text
    assert "docker/login-action" not in workflow_text

from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "dockerhub_publish_run_guide.md"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_dockerhub_publish_gate_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_ci_workflow_keeps_manual_trigger_only() -> None:
    workflow_text = WORKFLOW_PATH.read_text()

    assert "workflow_dispatch:" in workflow_text
    assert "push:" not in workflow_text
    assert "pull_request:" not in workflow_text


def test_v8_ci_workflow_publish_input_defaults_to_false() -> None:
    workflow = _load_workflow()
    publish_input = workflow[True]["workflow_dispatch"]["inputs"]["publish_image"]

    assert publish_input["default"] == "false"
    assert publish_input["required"] is False
    assert publish_input["type"] == "choice"
    assert publish_input["options"] == ["false", "true"]


def test_v8_ci_workflow_logs_in_with_dockerhub_secrets_only_when_enabled() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "docker/login-action@v3" in workflow
    assert "username: ${{ secrets.DOCKERHUB_USERNAME }}" in workflow
    assert "password: ${{ secrets.DOCKERHUB_TOKEN }}" in workflow
    assert "if: ${{ inputs.publish_image == 'true' }}" in workflow


def test_v8_ci_workflow_pushes_ci_and_git_sha_tags() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "docker push ${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}" in workflow
    assert "docker push ${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:ci" in workflow


def test_v8_ci_workflow_tests_gate_image_build_and_publish() -> None:
    workflow = _load_workflow()
    docker_job = workflow["jobs"]["docker-image"]

    assert docker_job["needs"] == "tests"


def test_v8_dockerhub_publish_run_guide_documents_gui_flow() -> None:
    guide = GUIDE_PATH.read_text()

    assert "GitHub repository" in guide
    assert "Actions" in guide
    assert "Run workflow" in guide
    assert "publish_image" in guide
    assert "Docker Hub" in guide

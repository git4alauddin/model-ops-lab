from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = PROJECT_ROOT / "docs" / "deployment" / "dockerhub_publishing_plan.md"
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"


def test_v8_dockerhub_publishing_plan_exists() -> None:
    assert PLAN_PATH.is_file()


def test_v8_dockerhub_publishing_plan_documents_required_secrets() -> None:
    plan = PLAN_PATH.read_text()

    assert "DOCKERHUB_USERNAME" in plan
    assert "DOCKERHUB_TOKEN" in plan


def test_v8_dockerhub_publishing_plan_requires_token_not_password() -> None:
    plan = PLAN_PATH.read_text().lower()

    assert "token, not password" in plan
    assert "access token" in plan
    assert "password" in plan


def test_v8_dockerhub_publishing_plan_documents_image_name_format() -> None:
    plan = PLAN_PATH.read_text()

    assert "<dockerhub-username>/modelopslab-serving:<tag>" in plan
    assert "modelopslab-serving:${{ github.sha }}" in plan
    assert "modelopslab-serving:ci" in plan


def test_v8_dockerhub_publishing_plan_documents_github_secret_ui_path() -> None:
    plan = PLAN_PATH.read_text()

    assert "Settings" in plan
    assert "Secrets and variables" in plan
    assert "Actions" in plan
    assert "New repository secret" in plan


def test_v8_ci_workflow_still_does_not_publish_to_dockerhub() -> None:
    workflow = WORKFLOW_PATH.read_text().lower()

    assert "docker login" not in workflow
    assert "docker push" not in workflow
    assert "docker/login-action" not in workflow
    assert "dockerhub_token" not in workflow

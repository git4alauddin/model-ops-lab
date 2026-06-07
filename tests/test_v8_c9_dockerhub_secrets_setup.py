from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "dockerhub_secrets_setup.md"
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"


def test_v8_dockerhub_secrets_setup_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_dockerhub_secrets_setup_documents_required_secrets() -> None:
    guide = GUIDE_PATH.read_text()

    assert "DOCKERHUB_USERNAME" in guide
    assert "DOCKERHUB_TOKEN" in guide


def test_v8_dockerhub_secrets_setup_documents_dockerhub_token_flow() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Docker Hub" in guide
    assert "Account Settings" in guide
    assert "Security" in guide
    assert "Access Tokens" in guide
    assert "Generate new token" in guide


def test_v8_dockerhub_secrets_setup_documents_github_secrets_ui_path() -> None:
    guide = GUIDE_PATH.read_text()

    assert "GitHub repository" in guide
    assert "Settings" in guide
    assert "Secrets and variables" in guide
    assert "Actions" in guide
    assert "New repository secret" in guide


def test_v8_dockerhub_secrets_setup_discourages_passwords_and_exposure() -> None:
    guide = GUIDE_PATH.read_text().lower()

    assert "token, not password" in guide
    assert "do not print the token" in guide
    assert "do not paste the token into code" in guide
    assert ".env" in guide


def test_v8_ci_workflow_uses_secrets_only_when_publish_is_enabled() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "docker/login-action@v3" in workflow
    assert "secrets.DOCKERHUB_USERNAME" in workflow
    assert "secrets.DOCKERHUB_TOKEN" in workflow
    assert "if: ${{ inputs.publish_image == 'true' }}" in workflow

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"
IMAGE_TAGS_PATH = PROJECT_ROOT / "deployment" / "image_tags.md"


def test_v8_image_tagging_contract_exists() -> None:
    assert IMAGE_TAGS_PATH.is_file()


def test_v8_image_tagging_contract_documents_supported_tags() -> None:
    contract = IMAGE_TAGS_PATH.read_text()

    assert "modelopslab-serving:ci" in contract
    assert "modelopslab-serving:<git-sha>" in contract
    assert "modelopslab-serving:vX.Y.Z" in contract
    assert "modelopslab-serving:latest" in contract


def test_v8_image_tagging_contract_warns_against_latest_only() -> None:
    contract = IMAGE_TAGS_PATH.read_text().lower()

    assert "must never be the only" in contract
    assert "avoid rollback to" in contract


def test_v8_ci_build_tags_image_with_ci_and_git_sha() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "-t modelopslab-serving:ci" in workflow
    assert "-t modelopslab-serving:${{ github.sha }}" in workflow


def test_v8_ci_build_uses_single_docker_build_command() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "docker build \\" in workflow
    assert "-f deployment/Dockerfile" in workflow


def test_v8_ci_image_versioning_pushes_traceable_tags_only_when_enabled() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "docker push ${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}" in workflow
    assert "docker push ${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:ci" in workflow
    assert "if: ${{ inputs.publish_image == 'true' }}" in workflow

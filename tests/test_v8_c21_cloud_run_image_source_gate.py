from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_image_source_gate.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
README_PATH = PROJECT_ROOT / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_cloud_run_image_source_gate_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_cloud_run_image_source_input_defaults_to_dockerhub() -> None:
    workflow = _load_workflow()
    source_input = workflow[True]["workflow_dispatch"]["inputs"]["cloud_run_image_source"]

    assert source_input["default"] == "dockerhub"
    assert source_input["required"] is False
    assert source_input["type"] == "choice"
    assert source_input["options"] == ["dockerhub", "artifact_registry"]


def test_v8_cloud_run_deploy_validates_source_specific_publish_gate() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "CLOUD_RUN_IMAGE_SOURCE: ${{ inputs.cloud_run_image_source }}" in workflow
    assert "cloud_run_image_source must be dockerhub or artifact_registry" in workflow
    assert "deploy_cloud_run=true with cloud_run_image_source=dockerhub requires publish_image=true" in workflow
    assert "deploy_cloud_run=true with cloud_run_image_source=artifact_registry requires publish_artifact_registry=true" in workflow


def test_v8_cloud_run_deploy_validates_artifact_registry_inputs_for_artifact_source() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "ARTIFACT_REGISTRY_LOCATION: ${{ inputs.artifact_registry_location }}" in workflow
    assert "ARTIFACT_REGISTRY_REPOSITORY: ${{ inputs.artifact_registry_repository }}" in workflow
    assert "Missing workflow input: artifact_registry_location" in workflow
    assert "Missing workflow input: artifact_registry_repository" in workflow


def test_v8_cloud_run_deploy_resolves_dockerhub_or_artifact_registry_image() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Resolve Cloud Run image" in workflow
    assert 'if [ "$CLOUD_RUN_IMAGE_SOURCE" = "artifact_registry" ]; then' in workflow
    assert 'image="${ARTIFACT_REGISTRY_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPOSITORY}/modelopslab-serving:${{ github.sha }}"' in workflow
    assert 'image="docker.io/${DOCKERHUB_USERNAME}/modelopslab-serving:${{ github.sha }}"' in workflow
    assert 'echo "image=$image" >> "$GITHUB_OUTPUT"' in workflow


def test_v8_cloud_run_deploy_action_uses_resolved_image_output() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "id: cloud-run-image" in workflow
    assert "image: ${{ steps.cloud-run-image.outputs.image }}" in workflow
    assert "image: docker.io/${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}" not in workflow


def test_v8_cloud_run_image_source_docs_describe_both_paths() -> None:
    guide = GUIDE_PATH.read_text()

    assert "cloud_run_image_source: dockerhub | artifact_registry" in guide
    assert "cloud_run_image_source: dockerhub" in guide
    assert "cloud_run_image_source: artifact_registry" in guide
    assert "docker.io/${DOCKERHUB_USERNAME}/modelopslab-serving:${{ github.sha }}" in guide
    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}" in guide
    assert "validate /health from an Artifact Registry deployed revision" in guide


def test_v8_cloud_run_image_source_docs_are_linked() -> None:
    readme = README_PATH.read_text()
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "cloud_run_image_source_gate.md" in readme
    assert "cloud_run_image_source_gate.md" in deployment_readme
    assert "cloud_run_image_source_gate.md" in overview


def test_v8_commit_log_has_c20_hash_and_c21_pending_entry() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "da03220 - v8-c20: validate Artifact Registry publish gate" in commit_log
    assert "Pending - v8-c21: add Cloud Run image source gate" in commit_log

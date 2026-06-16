from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_publish_gate.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_artifact_registry_publish_gate_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_artifact_registry_publish_input_is_manual_and_disabled_by_default() -> None:
    workflow = _load_workflow()
    publish_input = workflow[True]["workflow_dispatch"]["inputs"]["publish_artifact_registry"]

    assert publish_input["default"] == "false"
    assert publish_input["required"] is False
    assert publish_input["type"] == "choice"
    assert publish_input["options"] == ["false", "true"]


def test_v8_artifact_registry_publish_inputs_have_project_defaults() -> None:
    workflow = _load_workflow()
    inputs = workflow[True]["workflow_dispatch"]["inputs"]

    assert inputs["artifact_registry_location"]["default"] == "us-central1"
    assert inputs["artifact_registry_repository"]["default"] == "modelopslab"
    assert inputs["artifact_registry_location"]["type"] == "string"
    assert inputs["artifact_registry_repository"]["type"] == "string"


def test_v8_artifact_registry_publish_uses_workload_identity_and_gcloud() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Authenticate to Google Cloud for Artifact Registry" in workflow
    assert "google-github-actions/auth@v3" in workflow
    assert "google-github-actions/setup-gcloud@v3" in workflow
    assert "workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}" in workflow
    assert "service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}" in workflow
    assert "credentials_json" not in workflow


def test_v8_artifact_registry_publish_configures_docker_host() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Configure Docker for Artifact Registry" in workflow
    assert 'gcloud auth configure-docker "${ARTIFACT_REGISTRY_LOCATION}-docker.pkg.dev" --quiet' in workflow
    assert "permissions:" in workflow
    assert "id-token: write" in workflow


def test_v8_artifact_registry_publish_pushes_exact_git_sha_image() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Tag Artifact Registry image" in workflow
    assert "Push Artifact Registry image" in workflow
    assert 'artifact_registry_image="${ARTIFACT_REGISTRY_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPOSITORY}/modelopslab-serving"' in workflow
    assert 'docker tag modelopslab-serving:${{ github.sha }} "${artifact_registry_image}:${{ github.sha }}"' in workflow
    assert 'docker push "${artifact_registry_image}:${{ github.sha }}"' in workflow
    assert 'docker push "${artifact_registry_image}:ci"' not in workflow


def test_v8_artifact_registry_publish_validates_required_inputs_and_secrets() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Validate Artifact Registry inputs" in workflow
    assert "Missing GitHub Actions secret: GCP_WORKLOAD_IDENTITY_PROVIDER" in workflow
    assert "Missing GitHub Actions secret: GCP_SERVICE_ACCOUNT" in workflow
    assert "Missing workflow input: gcp_project_id" in workflow
    assert "Missing workflow input: artifact_registry_location" in workflow
    assert "Missing workflow input: artifact_registry_repository" in workflow


def test_v8_artifact_registry_publish_keeps_cloud_run_deploy_source_explicit() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "cloud_run_image_source" in workflow
    assert "image: ${{ steps.cloud-run-image.outputs.image }}" in workflow
    assert "docker.io/${DOCKERHUB_USERNAME}/modelopslab-serving:${{ github.sha }}" in workflow
    assert "${ARTIFACT_REGISTRY_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPOSITORY}/modelopslab-serving:${{ github.sha }}" in workflow


def test_v8_artifact_registry_publish_docs_describe_boundary_and_links() -> None:
    guide = GUIDE_PATH.read_text()
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "publish_artifact_registry: true" in guide
    assert "Cloud Run still deploys from Docker Hub" in guide
    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}" in guide
    assert "artifact_registry_publish_gate.md" in deployment_readme
    assert "artifact_registry_publish_gate.md" in overview


def test_v8_commit_log_has_c18_and_c19_hashes() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "c376a07 - v8-c18: validate Artifact Registry setup" in commit_log
    assert "55464a7 - v8-c19: add Artifact Registry publish gate" in commit_log

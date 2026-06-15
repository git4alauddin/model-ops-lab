from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_github_actions_deploy.md"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"
DOCKERIGNORE_PATH = PROJECT_ROOT / ".dockerignore"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_cloud_run_github_actions_deploy_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_cloud_run_deploy_input_is_manual_and_disabled_by_default() -> None:
    workflow = _load_workflow()
    deploy_input = workflow[True]["workflow_dispatch"]["inputs"]["deploy_cloud_run"]

    assert deploy_input["default"] == "false"
    assert deploy_input["required"] is False
    assert deploy_input["type"] == "choice"
    assert deploy_input["options"] == ["false", "true"]


def test_v8_cloud_run_deploy_job_is_gated_after_docker_image_job() -> None:
    workflow = _load_workflow()
    deploy_job = workflow["jobs"]["cloud-run-deploy"]

    assert deploy_job["needs"] == "docker-image"
    assert deploy_job["if"] == "${{ inputs.deploy_cloud_run == 'true' }}"
    assert deploy_job["permissions"]["contents"] == "read"
    assert deploy_job["permissions"]["id-token"] == "write"


def test_v8_cloud_run_deploy_requires_published_image() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "deploy_cloud_run=true requires publish_image=true" in workflow
    assert "PUBLISH_IMAGE: ${{ inputs.publish_image }}" in workflow
    assert 'if [ "$PUBLISH_IMAGE" != "true" ]; then' in workflow


def test_v8_cloud_run_deploy_validates_required_gcp_inputs_and_secrets() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Missing GitHub Actions secret: GCP_WORKLOAD_IDENTITY_PROVIDER" in workflow
    assert "Missing GitHub Actions secret: GCP_SERVICE_ACCOUNT" in workflow
    assert "Missing workflow input: gcp_project_id" in workflow
    assert "Missing workflow input: cloud_run_service" in workflow
    assert "Missing workflow input: cloud_run_region" in workflow


def test_v8_cloud_run_deploy_uses_workload_identity_auth() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "google-github-actions/auth@v3" in workflow
    assert "workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}" in workflow
    assert "service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}" in workflow
    assert "credentials_json" not in workflow


def test_v8_cloud_run_deploy_uses_exact_git_sha_image() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "google-github-actions/deploy-cloudrun@v3" in workflow
    assert "image: docker.io/${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}" in workflow
    assert "image: docker.io/${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:ci" not in workflow


def test_v8_cloud_run_deploy_sets_runtime_environment_and_port() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "MODELOPSLAB_ENV=cloud-run" in workflow
    assert "SERVING_HOST=0.0.0.0" in workflow
    assert "SERVING_PORT=8000" in workflow
    assert 'flags: "--allow-unauthenticated --port=8000"' in workflow


def test_v8_cloud_run_deploy_checks_health_endpoint() -> None:
    workflow = WORKFLOW_PATH.read_text()

    assert "Validate deployed health endpoint" in workflow
    assert 'health_url="${CLOUD_RUN_URL%/}/health"' in workflow
    assert "curl --fail --silent --show-error" in workflow
    assert "payload.get('status') == 'ok'" in workflow
    assert "payload.get('service') == 'modelopslab-serving'" in workflow


def test_v8_cloud_run_deploy_docs_describe_contract_and_failures() -> None:
    guide = GUIDE_PATH.read_text()

    assert "publish_image: true" in guide
    assert "deploy_cloud_run: true" in guide
    assert "GCP_WORKLOAD_IDENTITY_PROVIDER" in guide
    assert "GCP_SERVICE_ACCOUNT" in guide
    assert "Workload Identity Federation" in guide
    assert "post-deploy /health validation" in guide
    assert "Automated Cloud Run revision rollback is not part of this chunk" in guide


def test_v8_cloud_run_auth_credentials_are_ignored() -> None:
    assert "gha-creds-*.json" in GITIGNORE_PATH.read_text()
    assert "gha-creds-*.json" in DOCKERIGNORE_PATH.read_text()

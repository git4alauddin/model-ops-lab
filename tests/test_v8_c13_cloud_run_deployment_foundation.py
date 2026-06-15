from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_deployment_foundation.md"
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"


def test_v8_cloud_run_deployment_foundation_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_cloud_run_deployment_foundation_documents_target_and_tradeoff() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Cloud Run" in guide
    assert "Docker Hub" in guide
    assert "Artifact Registry" in guide
    assert "recommended by Google" in guide


def test_v8_cloud_run_deployment_foundation_documents_gui_flow() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Google Cloud Console" in guide
    assert "Create service" in guide
    assert "Deploy one revision from an existing container image" in guide
    assert "modelopslab-serving:<git-sha>" in guide


def test_v8_cloud_run_deployment_foundation_documents_service_settings() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Service name: modelopslab-serving" in guide
    assert "Region: us-central1" in guide
    assert "Container port: 8000" in guide
    assert "MODELOPSLAB_ENV=cloud-run" in guide


def test_v8_cloud_run_deployment_foundation_documents_health_check() -> None:
    guide = GUIDE_PATH.read_text()

    assert "<cloud-run-service-url>/health" in guide
    assert "status is ok" in guide
    assert "service is modelopslab-serving" in guide


def test_v8_cloud_run_deployment_foundation_points_to_automation_boundary() -> None:
    guide = GUIDE_PATH.read_text()
    workflow = WORKFLOW_PATH.read_text()

    assert "Deployment Automation Boundary" in guide
    assert "cloud_run_github_actions_deploy.md" in guide
    assert "google-github-actions/deploy-cloudrun" in guide
    assert "Workload Identity Federation" in guide
    assert "Cloud Run revision rollback" in guide
    assert "Artifact Registry publishing" in guide
    assert "google-github-actions/deploy-cloudrun" in workflow
    assert "google-github-actions/auth" in workflow

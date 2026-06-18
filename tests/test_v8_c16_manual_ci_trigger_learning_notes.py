from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEARNING_PATH = PROJECT_ROOT / "docs" / "learning" / "manual_ci_cloud_run_trigger_notes.md"
LEARNING_INDEX_PATH = PROJECT_ROOT / "docs" / "learning" / "README.md"
DEPLOY_GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_github_actions_deploy.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"


def test_v8_manual_ci_trigger_learning_notes_exist() -> None:
    assert LEARNING_PATH.is_file()


def test_v8_manual_ci_trigger_notes_explain_workflow_dispatch_inputs() -> None:
    notes = LEARNING_PATH.read_text()

    assert "workflow_dispatch" in notes
    assert "publish_image: true" in notes
    assert "deploy_cloud_run: true" in notes
    assert "gcp_project_id: key-component-498805-h0" in notes
    assert "cloud_run_service: modelopslab-serving" in notes
    assert "cloud_run_region: us-central1" in notes
    assert "deploy_cloud_run=true requires publish_image=true" in notes


def test_v8_manual_ci_trigger_notes_explain_connected_jobs_and_systems() -> None:
    notes = LEARNING_PATH.read_text()

    assert "pytest job" in notes
    assert "Docker image job" in notes
    assert "Cloud Run deploy job" in notes
    assert "Docker Hub push" in notes
    assert "Workload Identity Federation auth" in notes
    assert "Cloud Run revision update" in notes
    assert "/health validation" in notes


def test_v8_manual_ci_trigger_notes_explain_secrets_and_gcp_components() -> None:
    notes = LEARNING_PATH.read_text()

    assert "DOCKERHUB_USERNAME" in notes
    assert "DOCKERHUB_TOKEN" in notes
    assert "GCP_WORKLOAD_IDENTITY_PROVIDER" in notes
    assert "GCP_SERVICE_ACCOUNT" in notes
    assert "github-actions-pool" in notes
    assert "github-actions-provider" in notes
    assert "modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com" in notes
    assert "roles/run.admin" in notes
    assert "roles/iam.serviceAccountUser" in notes


def test_v8_manual_ci_trigger_notes_include_gui_checkpoints_and_failure_points() -> None:
    notes = LEARNING_PATH.read_text()

    assert "In GitHub Actions" in notes
    assert "In Docker Hub" in notes
    assert "In Google Cloud Console" in notes
    assert "rerun failed jobs option" in notes
    assert "fresh Docker Hub image is not immediately pullable" in notes
    assert "check which job failed" in notes


def test_v8_manual_ci_trigger_notes_are_linked_from_public_docs() -> None:
    learning_index = LEARNING_INDEX_PATH.read_text()
    guide = DEPLOY_GUIDE_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "manual_ci_cloud_run_trigger_notes.md" in learning_index
    assert "manual_ci_cloud_run_trigger_notes.md" in guide
    assert "manual_ci_cloud_run_trigger_notes.md" in overview

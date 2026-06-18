from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_foundation.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def test_v8_artifact_registry_foundation_doc_exists() -> None:
    assert FOUNDATION_PATH.is_file()


def test_v8_artifact_registry_foundation_records_project_target() -> None:
    guide = FOUNDATION_PATH.read_text()

    assert "key-component-498805-h0" in guide
    assert "153930851596" in guide
    assert "modelopslab-serving" in guide
    assert "us-central1" in guide
    assert "modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com" in guide


def test_v8_artifact_registry_foundation_records_image_path_contract() -> None:
    guide = FOUNDATION_PATH.read_text()

    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>" in guide
    assert "LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG" in guide
    assert "gcloud auth configure-docker us-central1-docker.pkg.dev" in guide


def test_v8_artifact_registry_foundation_records_gui_setup_and_iam() -> None:
    guide = FOUNDATION_PATH.read_text()

    assert "Artifact Registry API" in guide
    assert "Create Repository" in guide
    assert "Format: Docker" in guide
    assert "Mode: Standard" in guide
    assert "roles/artifactregistry.writer" in guide
    assert "roles/artifactregistry.reader" in guide
    assert "no service account key JSON was created" in guide


def test_v8_artifact_registry_foundation_records_future_workflow_boundary() -> None:
    guide = FOUNDATION_PATH.read_text()

    assert "Future GitHub Actions Direction" in guide
    assert "authenticate to GCP with Workload Identity Federation" in guide
    assert "push Git SHA image to Artifact Registry" in guide
    assert "deploy that Artifact Registry image to Cloud Run" in guide
    assert "change GitHub Actions" in guide
    assert "deploy from Artifact Registry" in guide
    assert "validate a live Artifact Registry deployment" in guide


def test_v8_artifact_registry_foundation_links_are_visible() -> None:
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "artifact_registry_foundation.md" in deployment_readme
    assert "artifact_registry_foundation.md" in overview


def test_v8_commit_log_has_c16_and_c17_hashes() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "58cbcf9 - v8-c16: add manual CI trigger learning notes" in commit_log
    assert "9dcce01 - v8-c17: add Artifact Registry deployment foundation" in commit_log

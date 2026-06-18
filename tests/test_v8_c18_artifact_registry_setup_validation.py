from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_setup_validation.md"
FOUNDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_foundation.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def test_v8_artifact_registry_setup_validation_doc_exists() -> None:
    assert VALIDATION_PATH.is_file()


def test_v8_artifact_registry_setup_validation_records_api_state() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "artifactregistry.googleapis.com" in validation
    assert "state: ENABLED" in validation
    assert "projects/153930851596" in validation
    assert "gcloud services list --enabled" in validation


def test_v8_artifact_registry_setup_validation_records_repository() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "projects/key-component-498805-h0/locations/us-central1/repositories/modelopslab" in validation
    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab" in validation
    assert "format: DOCKER" in validation
    assert "mode: STANDARD_REPOSITORY" in validation
    assert "encryption: Google-managed key" in validation
    assert "repository size: 0.000MB" in validation


def test_v8_artifact_registry_setup_validation_records_iam_binding() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "roles/artifactregistry.writer" in validation
    assert "serviceAccount:modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com" in validation
    assert "repository-level access" in validation
    assert "no service account key JSON" in validation


def test_v8_artifact_registry_setup_validation_records_boundary() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "Artifact Registry API is enabled" in validation
    assert "Docker repository exists" in validation
    assert "GitHub deploy service account can write to the repository" in validation
    assert "push image to Artifact Registry" in validation
    assert "deploy Cloud Run from Artifact Registry" in validation
    assert "validate live /health after Artifact Registry deployment" in validation


def test_v8_artifact_registry_setup_validation_links_are_visible() -> None:
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    foundation = FOUNDATION_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "artifact_registry_setup_validation.md" in deployment_readme
    assert "artifact_registry_setup_validation.md" in foundation
    assert "artifact_registry_setup_validation.md" in overview


def test_v8_commit_log_has_c17_and_c18_hashes() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "9dcce01 - v8-c17: add Artifact Registry deployment foundation" in commit_log
    assert "c376a07 - v8-c18: validate Artifact Registry setup" in commit_log

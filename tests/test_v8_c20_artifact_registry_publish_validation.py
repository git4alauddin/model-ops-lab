from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_publish_validation.md"
PUBLISH_GATE_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_publish_gate.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
README_PATH = PROJECT_ROOT / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def test_v8_artifact_registry_publish_validation_doc_exists() -> None:
    assert VALIDATION_PATH.is_file()


def test_v8_artifact_registry_publish_validation_records_run_and_inputs() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "workflow run: 27641517665" in validation
    assert "https://github.com/git4alauddin/model-ops-lab/actions/runs/27641517665" in validation
    assert "publish_image: false" in validation
    assert "publish_artifact_registry: true" in validation
    assert "deploy_cloud_run: false" in validation
    assert "gcp_project_id: key-component-498805-h0" in validation
    assert "artifact_registry_location: us-central1" in validation
    assert "artifact_registry_repository: modelopslab" in validation


def test_v8_artifact_registry_publish_validation_records_source_commit() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "55464a7e17ba6833673ddf897b6284fc772333df" in validation
    assert "short commit: 55464a7" in validation
    assert "v8-c19: add Artifact Registry publish gate" in validation


def test_v8_artifact_registry_publish_validation_records_jobs_and_skipped_paths() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "pytest: success" in validation
    assert "docker image build: success" in validation
    assert "cloud run deploy: skipped" in validation
    assert "Validate Docker Hub secrets: skipped" in validation
    assert "Push Docker Hub image: skipped" in validation
    assert "Push Artifact Registry image: success" in validation


def test_v8_artifact_registry_publish_validation_records_image_and_digest() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving" in validation
    assert "sha256:b073b2bdd44249ee6a3de10abb8d96035c391170d338850dabc0393a5a5e84f2" in validation
    assert "imageSizeBytes: 332707074" in validation
    assert "application/vnd.docker.distribution.manifest.v2+json" in validation


def test_v8_artifact_registry_publish_validation_records_boundary() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "manual publish_artifact_registry input works" in validation
    assert "Workload Identity Federation auth works for Artifact Registry publishing" in validation
    assert "Git SHA image is pushed to Artifact Registry" in validation
    assert "deploy Cloud Run from Artifact Registry" in validation
    assert "validate /health from an Artifact Registry deployed revision" in validation


def test_v8_artifact_registry_publish_validation_links_are_visible() -> None:
    readme = README_PATH.read_text()
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    publish_gate = PUBLISH_GATE_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "artifact_registry_publish_validation.md" in readme
    assert "artifact_registry_publish_validation.md" in deployment_readme
    assert "artifact_registry_publish_validation.md" in publish_gate
    assert "artifact_registry_publish_validation.md" in overview


def test_v8_commit_log_has_c19_hash_and_c20_pending_entry() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "55464a7 - v8-c19: add Artifact Registry publish gate" in commit_log
    assert "Pending - v8-c20: validate Artifact Registry publish gate" in commit_log

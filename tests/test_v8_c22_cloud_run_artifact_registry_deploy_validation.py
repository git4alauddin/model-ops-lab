from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_artifact_registry_deploy_validation.md"
SOURCE_GATE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_image_source_gate.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def test_v8_cloud_run_artifact_registry_deploy_validation_doc_exists() -> None:
    assert VALIDATION_PATH.is_file()


def test_v8_cloud_run_artifact_registry_deploy_validation_records_run_and_inputs() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "workflow run: 27645315977" in validation
    assert "https://github.com/git4alauddin/model-ops-lab/actions/runs/27645315977" in validation
    assert "publish_image: false" in validation
    assert "publish_artifact_registry: true" in validation
    assert "deploy_cloud_run: true" in validation
    assert "cloud_run_image_source: artifact_registry" in validation
    assert "artifact_registry_repository: modelopslab" in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_records_source_commit() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "ee825dad109380d7f53e4a576de0fd2b042e704a" in validation
    assert "short commit: ee825da" in validation
    assert "v8-c21: add Cloud Run image source gate" in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_records_jobs() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "pytest: success" in validation
    assert "docker image build: success" in validation
    assert "cloud run deploy: success" in validation
    assert "Push Docker Hub image: skipped" in validation
    assert "Push Artifact Registry image: success" in validation
    assert "Resolve Cloud Run image: success" in validation
    assert "Validate deployed health endpoint: success" in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_records_image_and_digest() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving" in validation
    assert "sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b" in validation
    assert "imageSizeBytes: 332661375" in validation
    assert "application/vnd.docker.distribution.manifest.v2+json" in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_records_cloud_run_revision() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "modelopslab-serving-00003-zsc" in validation
    assert "percent: 100" in validation
    assert "commit-sha: ee825dad109380d7f53e4a576de0fd2b042e704a" in validation
    assert "managed-by: github-actions" in validation
    assert "MODELOPSLAB_ENV=cloud-run" in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_records_health() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "https://modelopslab-serving-pv3rkohw6q-uc.a.run.app/health" in validation
    assert '"status":"ok"' in validation
    assert '"service":"modelopslab-serving"' in validation
    assert '"api_version":"v7"' in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_records_boundary() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "Artifact Registry is now a validated end-to-end image source for Cloud Run" in validation
    assert "remove Docker Hub deployment support" in validation
    assert "externalize model registry and MLflow artifacts" in validation
    assert "add rollback automation for Cloud Run revisions" in validation


def test_v8_cloud_run_artifact_registry_deploy_validation_links_are_visible() -> None:
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    source_gate = SOURCE_GATE_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "cloud_run_artifact_registry_deploy_validation.md" in deployment_readme
    assert "cloud_run_artifact_registry_deploy_validation.md" in source_gate
    assert "cloud_run_artifact_registry_deploy_validation.md" in overview


def test_v8_commit_log_has_c21_and_c22_hashes() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "ee825da - v8-c21: add Cloud Run image source gate" in commit_log
    assert "e24f5b1 - v8-c22: validate Cloud Run deployment from Artifact Registry" in commit_log

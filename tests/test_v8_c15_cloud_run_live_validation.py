from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_live_validation.md"
LEARNING_PATH = PROJECT_ROOT / "docs" / "learning" / "workload_identity_federation_notes.md"
DEPLOY_GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_github_actions_deploy.md"


def test_v8_cloud_run_live_validation_doc_exists() -> None:
    assert VALIDATION_PATH.is_file()


def test_v8_cloud_run_live_validation_records_target_and_inputs() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "key-component-498805-h0" in validation
    assert "modelopslab-serving" in validation
    assert "us-central1" in validation
    assert "publish_image: true" in validation
    assert "deploy_cloud_run: true" in validation


def test_v8_cloud_run_live_validation_records_image_and_digest() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "4388088e4b5f605a552ecf4e46d4edaab2a8e7fb" in validation
    assert "sha256:62ff4b9ac2487e3457972958cc4f0531bd9700ae639b265dff903a7c0127f71b" in validation
    assert "alaudddin/modelopslab-serving" in validation


def test_v8_cloud_run_live_validation_records_service_url_and_health() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "https://modelopslab-serving-pv3rkohw6q-uc.a.run.app" in validation
    assert '"status":"ok"' in validation
    assert '"service":"modelopslab-serving"' in validation
    assert '"api_version":"v7"' in validation


def test_v8_cloud_run_live_validation_records_failure_and_resolution() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "Image 'mirror.gcr.io/alaudddin/modelopslab-serving" in validation
    assert "not found" in validation
    assert "reran the failed cloud run deploy job" in validation
    assert "The rerun succeeded" in validation


def test_v8_workload_identity_learning_notes_exist_and_explain_trust_chain() -> None:
    notes = LEARNING_PATH.read_text()

    assert "Workload Identity Federation" in notes
    assert "GitHub Actions OIDC token" in notes
    assert "github-actions-pool" in notes
    assert "github-actions-provider" in notes
    assert "principalSet://iam.googleapis.com" in notes
    assert "roles/iam.workloadIdentityUser" in notes
    assert "no long-lived service account key JSON" in notes


def test_v8_deploy_guide_links_live_validation_and_learning_notes() -> None:
    guide = DEPLOY_GUIDE_PATH.read_text()

    assert "cloud_run_live_validation.md" in guide
    assert "workload_identity_federation_notes.md" in guide

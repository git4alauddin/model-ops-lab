from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_rollback_cleanup_guide.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def test_v8_cloud_run_rollback_cleanup_guide_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_cloud_run_rollback_cleanup_guide_records_known_good_revisions() -> None:
    guide = GUIDE_PATH.read_text()

    assert "modelopslab-serving-00002-fbc" in guide
    assert "modelopslab-serving-00003-zsc" in guide
    assert "4388088e4b5f605a552ecf4e46d4edaab2a8e7fb" in guide
    assert "ee825dad109380d7f53e4a576de0fd2b042e704a" in guide
    assert "sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b" in guide


def test_v8_cloud_run_rollback_cleanup_guide_documents_revision_traffic_rollback() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Rollback Option 1: Move Traffic To A Previous Revision" in guide
    assert "gcloud run services update-traffic modelopslab-serving" in guide
    assert "--to-revisions modelopslab-serving-00003-zsc=100" in guide
    assert "traffic revisionName" in guide
    assert "traffic percent" in guide


def test_v8_cloud_run_rollback_cleanup_guide_documents_redeploy_by_git_sha() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Rollback Option 2: Redeploy A Known-Good Git SHA Image" in guide
    assert "gcloud run deploy modelopslab-serving" in guide
    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>" in guide
    assert "docker.io/<dockerhub-username>/modelopslab-serving:<git-sha>" in guide


def test_v8_cloud_run_rollback_cleanup_guide_documents_health_and_boundaries() -> None:
    guide = GUIDE_PATH.read_text()

    assert "https://modelopslab-serving-pv3rkohw6q-uc.a.run.app/health" in guide
    assert '"status":"ok"' in guide
    assert "/ready and prediction endpoints still need externalized model registry and MLflow artifacts" in guide
    assert "Do not treat a successful `/health` rollback as proof that `/predict` is production-ready" in guide


def test_v8_cloud_run_rollback_cleanup_guide_documents_cleanup_rules() -> None:
    guide = GUIDE_PATH.read_text()

    assert "Do not delete" in guide
    assert "Cloud Run revision currently receiving traffic" in guide
    assert "Artifact Registry image digest used by the current ready revision" in guide
    assert "gcloud run revisions delete <revision-name>" in guide
    assert "run cleanup in dry-run mode before enforcing deletion" in guide
    assert "Do not rely on the moving `ci` tag for rollback" in guide


def test_v8_cloud_run_rollback_cleanup_guide_links_are_visible() -> None:
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "cloud_run_rollback_cleanup_guide.md" in deployment_readme
    assert "cloud_run_rollback_cleanup_guide.md" in overview


def test_v8_commit_log_has_c23_and_c24_hashes() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "40bcb14 - v8-c23: make Artifact Registry the default Cloud Run image source" in commit_log
    assert "c78ee47 - v8-c24: add Cloud Run rollback and cleanup guide" in commit_log

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLOSURE_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "closure.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "implementation.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"
ROLLBACK_GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_rollback_cleanup_guide.md"


def test_v8_closure_doc_exists() -> None:
    assert CLOSURE_PATH.is_file()


def test_v8_closure_marks_version_complete() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "status: complete" in closure
    assert "final chunk: v8-c25" in closure
    assert "preferred registry: Artifact Registry" in closure
    assert "preferred Cloud Run image source: artifact_registry" in closure


def test_v8_closure_records_final_validated_path() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "GitHub Actions manual trigger" in closure
    assert "pytest" in closure
    assert "Docker image build" in closure
    assert "Artifact Registry push" in closure
    assert "Cloud Run deploy from Artifact Registry" in closure
    assert "/health check" in closure


def test_v8_closure_records_live_runtime_evidence() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "modelopslab-serving-00003-zsc" in closure
    assert '"status":"ok"' in closure
    assert '"service":"modelopslab-serving"' in closure
    assert '"api_version":"v7"' in closure
    assert "ee825dad109380d7f53e4a576de0fd2b042e704a" in closure
    assert "sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b" in closure


def test_v8_closure_records_completed_capabilities() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "Docker serving image" in closure
    assert "Docker Compose serving runtime" in closure
    assert "GitHub Actions manual CI" in closure
    assert "Workload Identity Federation setup and validation" in closure
    assert "Artifact Registry as default Cloud Run image source" in closure
    assert "Cloud Run rollback and cleanup guide" in closure


def test_v8_closure_records_v9_handoff() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "What Moves To V9" in closure
    assert "externalize model registry artifacts for Cloud Run" in closure
    assert "validate /ready against cloud-accessible model artifacts" in closure
    assert "validate /predict and /predict/batch live on Cloud Run" in closure
    assert "monitoring, logging, and alerting" in closure
    assert "infrastructure-as-code" in closure


def test_v8_closure_links_are_visible() -> None:
    overview = V8_OVERVIEW_PATH.read_text()
    implementation = V8_IMPLEMENTATION_PATH.read_text()

    assert "closure.md" in overview
    assert "closure.md" in implementation


def test_v8_rollback_guide_remains_linked_from_closure_context() -> None:
    closure = CLOSURE_PATH.read_text()
    rollback_guide = ROLLBACK_GUIDE_PATH.read_text()

    assert "Cloud Run rollback and cleanup guide" in closure
    assert "Cloud Run Rollback And Cleanup Guide" in rollback_guide


def test_v8_commit_log_has_c24_hash_and_c25_pending_entry() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "c78ee47 - v8-c24: add Cloud Run rollback and cleanup guide" in commit_log
    assert "Pending - v8-c25: close V8 deployment foundation" in commit_log

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROLLBACK_GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "docker_rollback_guide.md"


def test_v8_docker_rollback_guide_exists() -> None:
    assert ROLLBACK_GUIDE_PATH.is_file()


def test_v8_docker_rollback_guide_documents_git_sha_rollback() -> None:
    guide = ROLLBACK_GUIDE_PATH.read_text()

    assert "Git SHA image tags" in guide
    assert "modelopslab-serving:<git-sha>" in guide
    assert "one exact source commit" in guide


def test_v8_docker_rollback_guide_warns_against_ci_tag_rollback() -> None:
    guide = ROLLBACK_GUIDE_PATH.read_text()

    assert "Do not use `ci`" in guide
    assert "ci is a moving tag" in guide
    assert "does not guarantee the exact previous image" in guide


def test_v8_docker_rollback_guide_documents_local_commands() -> None:
    guide = ROLLBACK_GUIDE_PATH.read_text()

    assert "docker pull <dockerhub-username>/modelopslab-serving:<git-sha>" in guide
    assert "docker run --rm -p 8000:8000 <dockerhub-username>/modelopslab-serving:<git-sha>" in guide
    assert "Invoke-RestMethod http://127.0.0.1:8000/health" in guide


def test_v8_docker_rollback_guide_keeps_cloud_run_rollback_out_of_scope() -> None:
    guide = ROLLBACK_GUIDE_PATH.read_text()

    assert "does not yet mean rolling back a live Cloud Run service" in guide
    assert "Cloud Run service rollback" in guide
    assert "When Cloud Run deployment is added later" in guide

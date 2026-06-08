from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = PROJECT_ROOT / "docs" / "deployment" / "dockerhub_publish_validation.md"


def test_v8_dockerhub_publish_validation_doc_exists() -> None:
    assert VALIDATION_PATH.is_file()


def test_v8_dockerhub_publish_validation_records_completed_publish_path() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "publish_image: true" in validation
    assert "tests passed" in validation
    assert "Docker image built" in validation
    assert "Docker Hub login succeeded" in validation
    assert "Docker Hub image tags pushed" in validation


def test_v8_dockerhub_publish_validation_records_required_external_config() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "modelopslab-serving" in validation
    assert "DOCKERHUB_USERNAME" in validation
    assert "DOCKERHUB_TOKEN" in validation


def test_v8_dockerhub_publish_validation_documents_published_tags() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "modelopslab-serving:<git-sha>" in validation
    assert "modelopslab-serving:ci" in validation
    assert "Git SHA tag" in validation


def test_v8_dockerhub_publish_validation_keeps_cloud_deployment_out_of_scope() -> None:
    validation = VALIDATION_PATH.read_text()

    assert "not live cloud deployment" in validation
    assert "Cloud Run service" in validation
    assert "public hosted API URL" in validation

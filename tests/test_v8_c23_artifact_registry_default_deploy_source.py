from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yaml"
GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "artifact_registry_default_deploy_source.md"
IMAGE_SOURCE_GUIDE_PATH = PROJECT_ROOT / "docs" / "deployment" / "cloud_run_image_source_gate.md"
DEPLOYMENT_README_PATH = PROJECT_ROOT / "docs" / "deployment" / "README.md"
V8_OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "overview.md"
V8_COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v8" / "commit_log.md"


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_v8_artifact_registry_default_deploy_source_doc_exists() -> None:
    assert GUIDE_PATH.is_file()


def test_v8_cloud_run_image_source_defaults_to_artifact_registry() -> None:
    workflow = _load_workflow()
    source_input = workflow[True]["workflow_dispatch"]["inputs"]["cloud_run_image_source"]

    assert source_input["default"] == "artifact_registry"
    assert source_input["required"] is False
    assert source_input["type"] == "choice"
    assert source_input["options"] == ["dockerhub", "artifact_registry"]


def test_v8_artifact_registry_default_docs_describe_preferred_and_fallback_paths() -> None:
    guide = GUIDE_PATH.read_text()

    assert "cloud_run_image_source: artifact_registry" in guide
    assert "cloud_run_image_source: dockerhub" in guide
    assert "Artifact Registry has been validated" in guide
    assert "Docker Hub remains available as an explicit fallback" in guide
    assert "us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}" in guide


def test_v8_artifact_registry_default_docs_preserve_boundaries() -> None:
    guide = GUIDE_PATH.read_text()

    assert "make Artifact Registry the default Cloud Run image source" in guide
    assert "keep Docker Hub as an explicit fallback" in guide
    assert "remove Docker Hub publishing" in guide
    assert "trigger a live deployment after changing the default" in guide
    assert "add automatic deployment on push" in guide


def test_v8_artifact_registry_default_links_are_visible() -> None:
    deployment_readme = DEPLOYMENT_README_PATH.read_text()
    image_source_guide = IMAGE_SOURCE_GUIDE_PATH.read_text()
    overview = V8_OVERVIEW_PATH.read_text()

    assert "artifact_registry_default_deploy_source.md" in deployment_readme
    assert "artifact_registry_default_deploy_source.md" in image_source_guide
    assert "artifact_registry_default_deploy_source.md" in overview


def test_v8_commit_log_has_c22_and_c23_hashes() -> None:
    commit_log = V8_COMMIT_LOG_PATH.read_text()

    assert "e24f5b1 - v8-c22: validate Cloud Run deployment from Artifact Registry" in commit_log
    assert "40bcb14 - v8-c23: make Artifact Registry the default Cloud Run image source" in commit_log

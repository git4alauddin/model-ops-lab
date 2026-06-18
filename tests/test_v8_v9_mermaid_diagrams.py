from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = PROJECT_ROOT / "docs" / "diagrams"
V8_DIAGRAM_PATH = PROJECT_ROOT / "docs" / "diagrams" / "v8_deployment_flow.md"
V9_DIAGRAM_PATH = PROJECT_ROOT / "docs" / "diagrams" / "v9_observability_flow.md"
ARCHITECTURE_INDEX_PATH = PROJECT_ROOT / "docs" / "architecture" / "README.md"


@pytest.mark.parametrize(
    "diagram_name",
    [
        "v1_pipeline_flow.md",
        "v2_validation_flow.md",
        "v3_reproducibility_flow.md",
        "v4_experiment_tracking_flow.md",
        "v5_training_pipeline_flow.md",
        "v6_model_registry_flow.md",
        "v7_serving_flow.md",
        "v8_deployment_flow.md",
        "v9_observability_flow.md",
    ],
)
def test_version_diagrams_use_grouped_mermaid_boundaries(diagram_name: str) -> None:
    diagram = (DIAGRAM_DIR / diagram_name).read_text(encoding="utf-8")

    assert "```mermaid" in diagram
    assert "flowchart TD" in diagram
    assert "subgraph " in diagram


def test_v8_deployment_mermaid_diagram_exists() -> None:
    diagram = V8_DIAGRAM_PATH.read_text(encoding="utf-8")

    assert "```mermaid" in diagram
    assert "flowchart TD" in diagram
    assert "GitHub Actions manual trigger" in diagram
    assert "Artifact Registry" in diagram
    assert "Workload Identity Federation" in diagram
    assert "Cloud Run deploy from Artifact Registry" in diagram


def test_v9_observability_mermaid_diagram_exists() -> None:
    diagram = V9_DIAGRAM_PATH.read_text(encoding="utf-8")

    assert "```mermaid" in diagram
    assert "flowchart TD" in diagram
    assert "logs/predictions.jsonl" in diagram
    assert "reports/monitoring/prediction_summary.json" in diagram
    assert "GET /metrics" in diagram
    assert "Prometheus" in diagram
    assert "Grafana" in diagram
    assert "incident debugging workflow" in diagram


def test_architecture_index_links_v8_and_v9_diagrams() -> None:
    architecture_index = ARCHITECTURE_INDEX_PATH.read_text(encoding="utf-8")

    assert "docs/diagrams/v8_deployment_flow.md" in architecture_index
    assert "docs/diagrams/v9_observability_flow.md" in architecture_index

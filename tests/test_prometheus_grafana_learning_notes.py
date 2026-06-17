from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTES_PATH = PROJECT_ROOT / "docs" / "learning" / "prometheus_grafana_notes.md"
README_PATH = PROJECT_ROOT / "README.md"


def test_prometheus_grafana_learning_notes_exist() -> None:
    assert NOTES_PATH.is_file()


def test_prometheus_grafana_learning_notes_explain_core_concepts() -> None:
    notes = NOTES_PATH.read_text(encoding="utf-8")

    required_terms = [
        "What Is Prometheus?",
        "What Is Grafana?",
        "What Is Scraping?",
        "What Is The `/metrics` Endpoint?",
        "What Is A Datasource?",
        "What Is Provisioning?",
    ]

    for term in required_terms:
        assert term in notes


def test_prometheus_grafana_learning_notes_connect_to_modelopslab_files() -> None:
    notes = NOTES_PATH.read_text(encoding="utf-8")

    required_terms = [
        "app/observability/prometheus_metrics.py",
        "app/api/routes.py",
        "deployment/docker-compose.monitoring.yaml",
        "deployment/monitoring/prometheus/prometheus.yml",
        "deployment/monitoring/grafana/dashboards/modelopslab-monitoring.json",
        "host.docker.internal:8000/metrics",
    ]

    for term in required_terms:
        assert term in notes


def test_readme_links_prometheus_grafana_learning_notes() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    assert "docs/learning/prometheus_grafana_notes.md" in readme

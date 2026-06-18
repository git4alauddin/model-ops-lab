import json
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_PATH = PROJECT_ROOT / "deployment" / "docker-compose.monitoring.yaml"
PROMETHEUS_PATH = PROJECT_ROOT / "deployment" / "monitoring" / "prometheus" / "prometheus.yml"
DATASOURCE_PATH = (
    PROJECT_ROOT
    / "deployment"
    / "monitoring"
    / "grafana"
    / "provisioning"
    / "datasources"
    / "prometheus.yaml"
)
DASHBOARD_PROVIDER_PATH = (
    PROJECT_ROOT
    / "deployment"
    / "monitoring"
    / "grafana"
    / "provisioning"
    / "dashboards"
    / "modelopslab.yaml"
)
DASHBOARD_PATH = (
    PROJECT_ROOT
    / "deployment"
    / "monitoring"
    / "grafana"
    / "dashboards"
    / "modelopslab-monitoring.json"
)
README_PATH = PROJECT_ROOT / "README.md"
MONITORING_INDEX_PATH = PROJECT_ROOT / "docs" / "monitoring" / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
GUIDE_PATH = PROJECT_ROOT / "docs" / "monitoring" / "grafana_prometheus_local_stack.md"


def test_monitoring_compose_defines_prometheus_and_grafana_services() -> None:
    compose = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))

    assert set(compose["services"]) == {"prometheus", "grafana"}
    assert "9090:9090" in compose["services"]["prometheus"]["ports"]
    assert "3000:3000" in compose["services"]["grafana"]["ports"]
    assert "prom/prometheus:v2.55.1" == compose["services"]["prometheus"]["image"]
    assert "grafana/grafana:11.3.1" == compose["services"]["grafana"]["image"]


def test_prometheus_scrapes_modelopslab_metrics_endpoint() -> None:
    config = yaml.safe_load(PROMETHEUS_PATH.read_text(encoding="utf-8"))
    scrape_configs = config["scrape_configs"]

    target_config = scrape_configs[0]

    assert target_config["job_name"] == "modelopslab-serving"
    assert target_config["metrics_path"] == "/metrics"
    assert "host.docker.internal:8000" in target_config["static_configs"][0]["targets"]


def test_grafana_provisions_prometheus_datasource_and_dashboard_provider() -> None:
    datasource = yaml.safe_load(DATASOURCE_PATH.read_text(encoding="utf-8"))
    provider = yaml.safe_load(DASHBOARD_PROVIDER_PATH.read_text(encoding="utf-8"))

    assert datasource["datasources"][0]["name"] == "ModelOpsLab Prometheus"
    assert datasource["datasources"][0]["type"] == "prometheus"
    assert datasource["datasources"][0]["url"] == "http://prometheus:9090"
    assert provider["providers"][0]["name"] == "ModelOpsLab"
    assert provider["providers"][0]["options"]["path"] == "/var/lib/grafana/dashboards"


def test_grafana_dashboard_contains_modelopslab_metrics() -> None:
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    dashboard_text = json.dumps(dashboard)

    assert dashboard["title"] == "ModelOpsLab Monitoring"
    assert dashboard["uid"] == "modelopslab-monitoring"
    assert "modelopslab_prediction_requests" in dashboard_text
    assert "modelopslab_prediction_failure_rate" in dashboard_text
    assert "modelopslab_prediction_latency_ms" in dashboard_text
    assert "modelopslab_monitoring_active_alerts" in dashboard_text
    assert "modelopslab_data_drift_detected" in dashboard_text
    assert "modelopslab_monitoring_report_available" in dashboard_text


def test_v9_c14_docs_mention_local_grafana_stack() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    monitoring_index = MONITORING_INDEX_PATH.read_text(encoding="utf-8")
    implementation = IMPLEMENTATION_PATH.read_text(encoding="utf-8")
    guide = GUIDE_PATH.read_text(encoding="utf-8")

    assert "docker compose -f deployment/docker-compose.monitoring.yaml up" in readme
    assert "grafana_prometheus_local_stack.md" in monitoring_index
    assert "V9-C14: Prometheus And Grafana Local Stack" in implementation
    assert "host.docker.internal:8000/metrics" in guide

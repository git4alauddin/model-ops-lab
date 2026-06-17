from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = (
    PROJECT_ROOT / "docs" / "monitoring" / "monitoring_retention_incident_workflow.md"
)
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "lessons.md"


def test_monitoring_retention_incident_workflow_exists() -> None:
    assert WORKFLOW_PATH.is_file()


def test_workflow_lists_core_monitoring_artifacts() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    required_terms = [
        "logs/predictions.jsonl",
        "reports/monitoring/prediction_summary.json",
        "reports/monitoring/alerts.json",
        "reports/drift/data_drift_summary.json",
        "reports/monitoring/dashboard_snapshot.json",
        "reports/monitoring/dashboard.html",
        "GET /metrics",
        "http://localhost:9090",
        "http://localhost:3000",
    ]

    for term in required_terms:
        assert term in workflow


def test_workflow_defines_retention_privacy_and_git_boundaries() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    required_terms = [
        "Local monitoring artifacts are intentionally ignored by Git",
        "logs/",
        "reports/",
        "Privacy Boundary",
        "raw invalid request payloads",
        "do not commit runtime reports or logs",
    ]

    for term in required_terms:
        assert term in workflow


def test_workflow_defines_incident_debugging_steps() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    required_terms = [
        "Step 1: Start With The Symptom",
        "Step 2: Check Service Health",
        "Step 3: Check Prometheus Target Health",
        "Step 4: Check Grafana Datasource And Time Range",
        "Step 5: Inspect Alert Report",
        "Step 6: Inspect Prediction Summary",
        "Step 7: Inspect Raw Prediction Events",
        "Step 8: Inspect Drift Reports",
        "Step 9: Regenerate Monitoring Reports",
        "Step 10: Record The Incident Summary",
    ]

    for term in required_terms:
        assert term in workflow


def test_v9_c15_docs_mention_retention_and_incident_workflow() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    implementation = IMPLEMENTATION_PATH.read_text(encoding="utf-8")
    lessons = LESSONS_PATH.read_text(encoding="utf-8")

    assert "docs/monitoring/monitoring_retention_incident_workflow.md" in readme
    assert "V9-C15: Monitoring Retention And Incident Debugging Workflow" in implementation
    assert "Incident debugging starts from the symptom" in lessons

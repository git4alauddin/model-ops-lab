from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = (
    PROJECT_ROOT / "docs" / "monitoring" / "fresh_feature_telemetry_workflow.md"
)
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "lessons.md"


def test_fresh_feature_telemetry_workflow_documents_gui_and_cli_paths() -> None:
    workflow = WORKFLOW_PATH.read_text()

    required_terms = [
        "http://127.0.0.1:8000/docs",
        "POST /predict",
        "python -m app.build_prediction_monitoring_summary",
        "python -m app.build_inference_snapshot",
        "python -m app.build_data_drift_summary",
        "python -m app.build_monitoring_alerts",
    ]

    for term in required_terms:
        assert term in workflow


def test_fresh_feature_telemetry_workflow_records_expected_report_transition() -> None:
    workflow = WORKFLOW_PATH.read_text()

    required_terms = [
        "overall_status: insufficient_data",
        "row_count > 0",
        "feature_event_count > 0",
        "overall_status: drift_detected",
        "data_drift_summary.inference_row_count: 16",
    ]

    for term in required_terms:
        assert term in workflow


def test_v9_c9_docs_reference_fresh_telemetry_workflow() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "docs/monitoring/fresh_feature_telemetry_workflow.md" in readme
    assert "V9-C9: Fresh Feature-Bearing Telemetry Workflow" in implementation
    assert "Fresh feature-bearing telemetry turns drift comparison from missing-data reporting into real drift evaluation." in lessons

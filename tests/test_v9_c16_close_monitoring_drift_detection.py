from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLOSURE_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "closure.md"
OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "overview.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
COMMIT_LOG_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "commit_log.md"


def test_v9_closure_doc_exists() -> None:
    assert CLOSURE_PATH.is_file()


def test_v9_closure_marks_version_complete() -> None:
    closure = CLOSURE_PATH.read_text(encoding="utf-8")
    overview = OVERVIEW_PATH.read_text(encoding="utf-8")

    assert "status: complete" in closure
    assert "final chunk: v9-c16" in closure
    assert "metrics endpoint: /metrics" in closure
    assert "dashboard stack: static HTML and Grafana" in closure
    assert "V9 is complete." in overview


def test_v9_closure_records_final_observability_path() -> None:
    closure = CLOSURE_PATH.read_text(encoding="utf-8")

    required_terms = [
        "prediction telemetry event",
        "local monitoring summary",
        "local alert report",
        "local data drift summary",
        "dashboard snapshot",
        "static dashboard HTML",
        "Prometheus /metrics endpoint",
        "Grafana dashboard",
        "incident debugging workflow",
    ]

    for term in required_terms:
        assert term in closure


def test_v9_closure_records_completed_capabilities() -> None:
    closure = CLOSURE_PATH.read_text(encoding="utf-8")

    required_terms = [
        "prediction telemetry contract",
        "local monitoring alert rules",
        "local baseline-vs-inference drift comparison",
        "drift alert integration",
        "Prometheus-compatible /metrics endpoint",
        "starter Grafana monitoring dashboard",
        "monitoring retention workflow",
    ]

    for term in required_terms:
        assert term in closure


def test_v9_closure_records_deferred_scope_and_v10_handoff() -> None:
    closure = CLOSURE_PATH.read_text(encoding="utf-8")

    required_terms = [
        "real concept drift automation",
        "alert notification channels",
        "long-term Prometheus storage",
        "managed cloud monitoring",
        "Evidently AI HTML drift reports",
        "What Moves To V10",
        "governed retraining trigger decisions",
        "candidate-vs-production model comparison",
        "regression protection gates",
    ]

    for term in required_terms:
        assert term in closure


def test_v9_closure_links_are_visible() -> None:
    overview = OVERVIEW_PATH.read_text(encoding="utf-8")

    assert "docs/versions/v9/closure.md" in overview


def test_v9_implementation_and_commit_log_record_c16() -> None:
    implementation = IMPLEMENTATION_PATH.read_text(encoding="utf-8")
    commit_log = COMMIT_LOG_PATH.read_text(encoding="utf-8")

    assert "V9-C16: Close Monitoring And Drift Detection" in implementation
    assert "v9-c16: close monitoring and drift detection" in commit_log

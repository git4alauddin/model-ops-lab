from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
V9_DOCS_DIR = PROJECT_ROOT / "docs" / "versions" / "v9"
OBSERVABILITY_STRATEGY_PATH = (
    PROJECT_ROOT / "docs" / "monitoring" / "observability_strategy.md"
)
README_PATH = PROJECT_ROOT / "README.md"


def test_v9_documentation_scaffold_exists() -> None:
    expected_files = {
        "overview.md",
        "implementation.md",
        "lessons.md",
        "issues_faced.md",
        "commit_log.md",
        "verification.md",
    }

    assert V9_DOCS_DIR.is_dir()
    assert expected_files.issubset(
        {path.name for path in V9_DOCS_DIR.iterdir() if path.is_file()}
    )


def test_v9_overview_defines_observability_scope() -> None:
    overview = (V9_DOCS_DIR / "overview.md").read_text()

    required_terms = [
        "monitoring",
        "drift detection",
        "prediction telemetry",
        "alert-ready metrics",
        "incident debugging",
        "traceable production metrics",
    ]

    for term in required_terms:
        assert term in overview


def test_observability_strategy_defines_operational_and_ml_metrics() -> None:
    strategy = OBSERVABILITY_STRATEGY_PATH.read_text()

    required_terms = [
        "request volume",
        "p95 latency",
        "p99 latency",
        "failure rate",
        "prediction distribution",
        "prediction probability distribution",
        "drift score",
    ]

    for term in required_terms:
        assert term in strategy


def test_observability_strategy_defines_drift_and_alert_boundaries() -> None:
    strategy = OBSERVABILITY_STRATEGY_PATH.read_text()

    required_terms = [
        "Data drift compares",
        "Concept drift is harder",
        "reports/drift/",
        "high latency",
        "severe data drift",
        "prediction distribution collapse",
        "missing prediction telemetry",
    ]

    for term in required_terms:
        assert term in strategy


def test_readme_lists_v9_current_scope() -> None:
    readme = README_PATH.read_text()

    assert "| V9 | Monitoring, drift detection, and production observability |" in readme
    assert "docs/monitoring/observability_strategy.md" in readme

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
V10_DOCS_DIR = PROJECT_ROOT / "docs" / "versions" / "v10"
RETRAINING_GOVERNANCE_PATH = (
    PROJECT_ROOT / "docs" / "retraining" / "retraining_governance.md"
)
README_PATH = PROJECT_ROOT / "README.md"
RETRAINING_INDEX_PATH = PROJECT_ROOT / "docs" / "retraining" / "README.md"


def test_v10_documentation_scaffold_exists() -> None:
    expected_files = {
        "overview.md",
        "implementation.md",
        "lessons.md",
        "issues_faced.md",
        "commit_log.md",
        "verification.md",
    }

    assert V10_DOCS_DIR.is_dir()
    assert expected_files.issubset(
        {path.name for path in V10_DOCS_DIR.iterdir() if path.is_file()}
    )


def test_v10_overview_defines_retraining_scope() -> None:
    overview = (V10_DOCS_DIR / "overview.md").read_text()

    required_terms = [
        "continuous ML lifecycle management",
        "drift-triggered automation",
        "regression protection",
        "deployment safeguards",
        "portfolio-grade",
        "human approval",
    ]

    for term in required_terms:
        assert term in overview


def test_retraining_governance_defines_lifecycle_and_triggers() -> None:
    governance = RETRAINING_GOVERNANCE_PATH.read_text()

    required_terms = [
        "monitoring signal",
        "retraining trigger decision",
        "candidate model training",
        "candidate-vs-production comparison",
        "human approval",
        "data drift detected",
        "scheduled retraining window",
    ]

    for term in required_terms:
        assert term in governance


def test_retraining_governance_defines_regression_and_metadata() -> None:
    governance = RETRAINING_GOVERNANCE_PATH.read_text()

    required_terms = [
        "recall drop beyond allowed tolerance",
        "latency increase beyond allowed tolerance",
        "schema validation failure",
        "trigger reason",
        "previous production model",
        "promotion recommendation",
        "rollback target",
    ]

    for term in required_terms:
        assert term in governance


def test_readme_lists_v10_current_scope_and_docs() -> None:
    readme = README_PATH.read_text()
    retraining_index = RETRAINING_INDEX_PATH.read_text()

    assert "| V10 | Retraining automation, governance, and portfolio packaging |" in readme
    assert "retraining_governance.md" in retraining_index

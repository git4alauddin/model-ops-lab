from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLOSURE_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "closure.md"
OVERVIEW_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "overview.md"
README_PATH = PROJECT_ROOT / "README.md"
CHECKLIST_PATH = (
    PROJECT_ROOT / "docs" / "portfolio" / "v10_completion_checklist.md"
)
IMPLEMENTATION_PATH = (
    PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
)
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_v10_closure_records_complete_status_and_final_lifecycle() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "status: complete" in closure
    assert "final chunk: v10-c12" in closure
    assert "## Final Lifecycle" in closure
    assert "## Completed Chunks" in closure
    assert "V10-C12  final closure" in closure
    assert "candidate_local_serving_rolled_back" in closure


def test_v10_closure_records_real_final_registry_state() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "active local champion: v1-7ab8f00a" in closure
    assert "retraining model status: archived" in closure
    assert "retraining champion: v1-retrain-20260617T184250573186Z" in closure
    assert "Cloud Run update: not performed" in closure


def test_v10_closure_separates_manual_and_deferred_scope() -> None:
    closure = CLOSURE_PATH.read_text()

    assert "## Manual Portfolio Evidence" in closure
    assert "These tasks do not block V10 engineering closure." in closure
    assert "## Intentionally Deferred" in closure
    assert "scheduled retraining execution" in closure
    assert "retraining-driven Cloud Run rollout" in closure
    assert "fairness, calibration, or latency promotion gates" in closure


def test_v10_overview_readme_and_checklist_show_closure() -> None:
    overview = OVERVIEW_PATH.read_text()
    readme = README_PATH.read_text()
    checklist = CHECKLIST_PATH.read_text()

    assert "V10 is complete." in overview
    assert "V10-C12: final closure." in overview
    assert "docs/versions/v10/closure.md" in readme
    assert "- [x] V10 closure document exists." in checklist


def test_v10_c12_documentation_records_closure_chunk() -> None:
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "V10-C12: Final Closure" in implementation
    assert "Closure is a scope decision backed by evidence" in lessons


from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
PORTFOLIO_INDEX_PATH = PROJECT_ROOT / "docs" / "portfolio" / "README.md"
DIAGRAM_PATH = PROJECT_ROOT / "docs" / "diagrams" / "v10_retraining_flow.md"
ARCHITECTURE_PATH = (
    PROJECT_ROOT / "docs" / "architecture" / "continuous_ml_lifecycle.md"
)
CASE_STUDY_PATH = PROJECT_ROOT / "docs" / "portfolio" / "project_case_study.md"
INTERVIEW_PATH = (
    PROJECT_ROOT / "docs" / "portfolio" / "interview_resume_guide.md"
)
DEMO_PATH = PROJECT_ROOT / "docs" / "portfolio" / "demo_checklist.md"
CHECKLIST_PATH = (
    PROJECT_ROOT / "docs" / "portfolio" / "v10_completion_checklist.md"
)
IMPLEMENTATION_PATH = (
    PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
)
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_v10_retraining_diagram_uses_component_subgraphs() -> None:
    diagram = DIAGRAM_PATH.read_text()

    assert "```mermaid" in diagram
    for component in (
        'subgraph observability_signals["V9 observability signals"]',
        'subgraph trigger_governance["Retraining trigger governance"]',
        'subgraph retraining_run["Governed retraining run"]',
        'subgraph candidate_training["Candidate training"]',
        'subgraph comparison_gates["Candidate vs production evaluation"]',
        'subgraph approval_promotion["Human governance"]',
        'subgraph local_serving_update["Local serving update"]',
        'subgraph rollback_path["Rollback protection"]',
        'subgraph deployment_boundary["Cloud deployment boundary"]',
    ):
        assert component in diagram

    assert "python -m app.update_local_serving_model" in diagram
    assert "python -m app.rollback_local_retraining_model" in diagram
    assert "not changed by V10 local serving commands" in diagram


def test_architecture_doc_explains_control_runtime_and_boundaries() -> None:
    architecture = ARCHITECTURE_PATH.read_text()

    assert "## Control Plane And Runtime Plane" in architecture
    assert "## Safety Model" in architecture
    assert "## Key Architecture Decisions" in architecture
    assert "## Known Boundaries" in architecture
    assert "human approval" in architecture
    assert "registry snapshot restoration" in architecture


def test_portfolio_case_study_is_implementation_grounded() -> None:
    case_study = CASE_STUDY_PATH.read_text()

    assert "## Problem" in case_study
    assert "## Implemented Lifecycle" in case_study
    assert "## Production Engineering Highlights" in case_study
    assert "## Engineering Trade-Offs" in case_study
    assert "## Current Limitations" in case_study
    assert "no scheduled V10 retraining job" in case_study
    assert "no automated Cloud Run model rollout" in case_study


def test_interview_and_demo_assets_cover_honest_project_story() -> None:
    interview = INTERVIEW_PATH.read_text()
    demo = DEMO_PATH.read_text()

    assert "## Thirty-Second Pitch" in interview
    assert "## Resume Bullets" in interview
    assert "## Honest Scope Statements" in interview
    assert "Do not claim" in interview
    assert "## Recommended Demo Order" in demo
    assert "## Evidence To Capture" in demo
    assert "Cloud Run" in demo


def test_v10_completion_checklist_separates_done_manual_and_deferred() -> None:
    checklist = CHECKLIST_PATH.read_text()

    assert "## Functional Lifecycle" in checklist
    assert "## Operational Evidence" in checklist
    assert "## Portfolio Evidence To Capture Manually" in checklist
    assert "## Explicitly Deferred" in checklist
    assert "- [x] Local rollback restored the previous champion." in checklist
    assert "- [ ] Scheduled V10 retraining execution." in checklist
    assert "must not be fabricated" in checklist


def test_readme_and_v10_docs_link_portfolio_packaging() -> None:
    readme = README_PATH.read_text()
    portfolio_index = PORTFOLIO_INDEX_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "## Problem Statement" in readme
    assert "## Architecture At A Glance" in readme
    assert "## Engineering Highlights" in readme
    assert "## Trade-Offs And Limitations" in readme
    assert "docs/diagrams/v10_retraining_flow.md" in readme
    assert "project_case_study.md" in portfolio_index
    assert "V10-C11: Architecture And Portfolio Packaging" in implementation
    assert "Technical storytelling must preserve operational boundaries" in lessons

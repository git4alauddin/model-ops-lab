"""Tests for V3 validation dataset version metadata."""

import json
from pathlib import Path

from app.validate_data import validate_dataset_readiness
from app.validation.reports import (
    build_validation_report,
    build_validation_summary,
    save_validation_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _dataset_version_snapshot() -> dict[str, str]:
    return {
        "metadata_path": "data_versions/customer_churn/v1.yaml",
        "dataset_name": "customer_churn",
        "version": "v1",
        "path": "data/churn.csv",
        "schema_path": "schema_versions/customer_churn_v1.yaml",
        "target_column": "churn",
        "id_column": "customer_id",
        "source_type": "local_csv",
    }


def test_validation_report_includes_dataset_version_snapshot():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        dataset_version=_dataset_version_snapshot(),
    )

    assert report.dataset_version is not None
    assert report.dataset_version["dataset_name"] == "customer_churn"
    assert report.dataset_version["version"] == "v1"


def test_save_validation_report_persists_dataset_version(tmp_path):
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        dataset_version=_dataset_version_snapshot(),
    )
    report_path = tmp_path / "validation_report.json"

    save_validation_report(report, report_path)

    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["dataset_version"]["dataset_name"] == "customer_churn"
    assert data["dataset_version"]["version"] == "v1"
    assert data["dataset_version"]["schema_path"] == (
        "schema_versions/customer_churn_v1.yaml"
    )


def test_validation_summary_includes_dataset_version():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        dataset_version=_dataset_version_snapshot(),
    )

    summary = build_validation_summary(report)

    assert "dataset_version:" in summary
    assert "dataset_name: customer_churn" in summary
    assert "version: v1" in summary


def test_validate_dataset_readiness_populates_dataset_version():
    report = validate_dataset_readiness(
        PROJECT_ROOT / "configs" / "training.yaml",
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml",
    )

    assert report.status == "passed"
    assert report.dataset_version is not None
    assert report.dataset_version["dataset_name"] == "customer_churn"
    assert report.dataset_version["version"] == "v1"

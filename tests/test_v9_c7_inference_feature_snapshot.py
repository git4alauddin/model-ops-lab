import json
from pathlib import Path

import pytest

from app.observability.inference_snapshot import (
    InferenceSnapshotError,
    build_and_save_inference_snapshot,
    build_inference_snapshot,
    save_inference_snapshot,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
CONTRACT_PATH = PROJECT_ROOT / "docs" / "monitoring" / "prediction_telemetry_contract.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"


def test_inference_snapshot_summarizes_feature_bearing_telemetry() -> None:
    snapshot = build_inference_snapshot(
        [
            _event("request-1", tenure_months=1, contract_type="month_to_month"),
            _event("request-2", tenure_months=10, contract_type="one_year"),
            _event("request-3", tenure_months=40, contract_type="month_to_month"),
        ],
        _schema(),
        source_path=Path("logs/predictions.jsonl"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert snapshot["snapshot_version"] == "v1"
    assert snapshot["row_count"] == 3
    assert snapshot["feature_event_count"] == 3
    assert snapshot["feature_count"] == 2
    assert snapshot["skipped_event_count"] == 0
    assert snapshot["features"]["tenure_months"]["stats"]["mean"] == 17.0
    assert snapshot["features"]["contract_type"]["value_counts"] == {
        "month_to_month": 2,
        "one_year": 1,
    }


def test_inference_snapshot_skips_non_feature_telemetry() -> None:
    snapshot = build_inference_snapshot(
        [
            _event("request-1", tenure_months=1, contract_type="month_to_month"),
            {"event_version": "v1", "event_type": "prediction_validation_failure"},
            {"event_version": "v1", "event_type": "prediction_success"},
            {"event_version": "v0", "event_type": "prediction_success"},
        ],
        _schema(),
        source_path=Path("logs/predictions.jsonl"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
    )

    assert snapshot["row_count"] == 1
    assert snapshot["skipped_event_count"] == 3
    assert snapshot["skipped_events"] == {
        "missing_input_features": 1,
        "unsupported_event_type": 1,
        "unsupported_or_missing_event_version": 1,
    }


def test_inference_snapshot_allows_empty_feature_window() -> None:
    snapshot = build_inference_snapshot(
        [
            {"event_version": "v1", "event_type": "prediction_validation_failure"},
        ],
        _schema(),
        source_path=Path("logs/predictions.jsonl"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
    )

    assert snapshot["row_count"] == 0
    assert snapshot["feature_count"] == 0
    assert snapshot["features"] == {}
    assert snapshot["skipped_events"] == {"unsupported_event_type": 1}


def test_inference_snapshot_rejects_empty_telemetry() -> None:
    with pytest.raises(InferenceSnapshotError, match="No prediction telemetry"):
        build_inference_snapshot(
            [],
            _schema(),
            source_path=Path("logs/predictions.jsonl"),
            schema_path=Path("schema_versions/customer_churn_v1.yaml"),
        )


def test_save_and_build_inference_snapshot_persist_json(tmp_path) -> None:
    telemetry_path = tmp_path / "predictions.jsonl"
    output_path = tmp_path / "reports" / "drift" / "inference_snapshot.json"
    telemetry_path.write_text(json.dumps(_full_customer_event("request-1")), encoding="utf-8")

    snapshot = build_and_save_inference_snapshot(
        config_path=PROJECT_ROOT / "configs" / "training.yaml",
        telemetry_path=telemetry_path,
        output_path=output_path,
    )

    assert output_path.is_file()
    assert snapshot["row_count"] == 1
    assert "monthly_charges" in snapshot["features"]

    second_output = tmp_path / "copy.json"
    save_inference_snapshot(snapshot, second_output)

    assert json.loads(second_output.read_text(encoding="utf-8")) == snapshot


def test_v9_c7_docs_mention_inference_snapshot_command_and_report() -> None:
    readme = README_PATH.read_text()
    contract = CONTRACT_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()

    assert "python -m app.build_inference_snapshot" in readme
    assert "reports/drift/inference_snapshot.json" in readme
    assert "`input_features`" in contract
    assert "V9-C7: Production Inference Feature Snapshot" in implementation


def _event(
    request_id: str,
    *,
    tenure_months: int,
    contract_type: str,
) -> dict:
    return {
        "event_version": "v1",
        "event_type": "prediction_success",
        "request_id": request_id,
        "input_features": {
            "tenure_months": tenure_months,
            "contract_type": contract_type,
        },
    }


def _full_customer_event(request_id: str) -> dict:
    return {
        "event_version": "v1",
        "event_type": "prediction_success",
        "request_id": request_id,
        "input_features": {
            "tenure_months": 12,
            "monthly_charges": 79.5,
            "total_charges": 950.0,
            "contract_type": "month_to_month",
            "internet_service": "fiber_optic",
            "payment_method": "credit_card",
            "is_senior": False,
        },
    }


def _schema() -> dict:
    return {
        "name": "customer_churn",
        "version": "v1",
        "columns": {
            "tenure_months": {
                "dtype": "integer",
                "nullable": False,
                "role": "feature",
            },
            "contract_type": {
                "dtype": "category",
                "nullable": False,
                "role": "feature",
                "allowed_values": ["month_to_month", "one_year", "two_year"],
            },
            "churn": {
                "dtype": "integer",
                "nullable": False,
                "role": "target",
                "allowed_values": [0, 1],
            },
        },
    }

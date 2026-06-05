"""Tests for V5 Prefect deployment scaffold."""

from pathlib import Path

import yaml


def test_prefect_yaml_defines_local_training_pipeline_deployment():
    prefect_config = _load_prefect_yaml()

    deployments = prefect_config["deployments"]
    assert len(deployments) == 1

    deployment = deployments[0]
    assert deployment["name"] == "local-training-pipeline"
    assert deployment["version"] == "v5-c11"
    assert deployment["entrypoint"] == (
        "app/orchestration/prefect_pipeline.py:training_pipeline_flow"
    )
    assert deployment["parameters"] == {
        "config_path": "configs/training.yaml",
    }


def test_prefect_yaml_uses_local_process_work_pool():
    deployment = _load_prefect_yaml()["deployments"][0]

    assert deployment["work_pool"] == {
        "name": "modelopslab-local-process-pool",
        "work_queue_name": "default",
    }


def test_prefect_yaml_schedule_is_inactive_by_default():
    deployment = _load_prefect_yaml()["deployments"][0]

    assert deployment["schedules"] == [
        {
            "slug": "daily-local-training",
            "cron": "0 9 * * *",
            "timezone": "Asia/Kolkata",
            "active": False,
        }
    ]


def _load_prefect_yaml() -> dict:
    prefect_yaml_path = Path("prefect.yaml")
    assert prefect_yaml_path.exists()
    return yaml.safe_load(prefect_yaml_path.read_text(encoding="utf-8"))

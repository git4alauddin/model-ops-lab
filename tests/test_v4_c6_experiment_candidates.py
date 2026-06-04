"""Tests for V4 multi-model experiment candidate configuration."""

from pathlib import Path

from app.run_experiments import (
    ExperimentCandidateError,
    build_candidate_config,
    load_experiment_candidates,
    resolve_champion_report_path,
)


def test_load_experiment_candidates_returns_configured_candidates():
    config = {
        "experiment_candidates": [
            {
                "name": "logistic_regression_baseline",
                "model": {"type": "logistic_regression", "params": {"max_iter": 200}},
            }
        ]
    }

    candidates = load_experiment_candidates(config)

    assert candidates == config["experiment_candidates"]


def test_load_experiment_candidates_requires_non_empty_list():
    try:
        load_experiment_candidates({"experiment_candidates": []})
    except ExperimentCandidateError as exc:
        assert "non-empty list" in str(exc)
    else:
        raise AssertionError("Expected ExperimentCandidateError for empty candidates.")


def test_build_candidate_config_sets_model_and_candidate_artifact_dir():
    config = {
        "model": {"type": "logistic_regression", "params": {"max_iter": 200}},
        "artifacts": {"dir": "artifacts"},
    }
    candidate = {
        "name": "random_forest_baseline",
        "model": {"type": "random_forest", "params": {"n_estimators": 50}},
    }

    candidate_config = build_candidate_config(config, candidate)

    assert candidate_config["model"]["type"] == "random_forest"
    assert candidate_config["active_experiment_candidate"] == "random_forest_baseline"
    assert candidate_config["artifacts"]["dir"] == str(
        Path("artifacts") / "experiments" / "random_forest_baseline"
    )


def test_resolve_champion_report_path_uses_configured_path():
    config = {"champion_selection": {"report_path": "reports/champion_run.json"}}

    assert resolve_champion_report_path(config) == Path("reports/champion_run.json")

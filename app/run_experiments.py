"""Run V4 multi-model MLflow experiments and select a champion run."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
import re
from typing import Any, cast

from app.champion_selection import ChampionSelectionError, select_champion_run
from app.config import ConfigError, load_config
from app.data import DataError, load_dataset
from app.dataset_registry import (
    build_dataset_version_snapshot,
    DatasetRegistryError,
    load_dataset_version_metadata,
    resolve_dataset_version_metadata_path,
)
from app.evaluate import EvaluationError, evaluate_model_with_duration
from app.experiment_tracking import (
    ExperimentTrackingError,
    PIPELINE_VERSION,
    clear_champion_tags,
    get_run_id,
    log_training_outputs,
    set_run_tags,
    start_experiment_run,
)
from app.pipeline.preprocessing import (
    build_preprocessing_pipeline,
    identify_feature_types,
    PreprocessingError,
    split_features_target,
    split_train_test,
)
from app.pipeline.trainer import (
    TrainingError,
    build_model,
    build_training_pipeline,
    train_model,
)
from app.train import (
    ValidationGateError,
    count_validation_issues,
    drop_configured_columns,
    enforce_validation_gate,
    resolve_validation_schema_path,
)
from app.utils.artifacts import (
    ArtifactError,
    build_artifact_paths,
    save_json,
    save_model,
)
from app.utils.logger import build_log_path, get_logger
from app.validate_data import validate_dataset_readiness
from app.validation.reports import ValidationReport

LOGGER_NAME = "modelopslab.experiments"
DEFAULT_CONFIG_PATH = Path("configs/training.yaml")


class ExperimentCandidateError(ValueError):
    """Raised when experiment candidate configuration is invalid."""


def load_experiment_candidates(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Return configured experiment candidates."""
    candidates = config.get("experiment_candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ExperimentCandidateError("experiment_candidates must be a non-empty list.")

    validated_candidates = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ExperimentCandidateError("Each experiment candidate must be a mapping.")
        name = candidate.get("name")
        model_config = candidate.get("model")
        if not isinstance(name, str) or not name:
            raise ExperimentCandidateError("Each experiment candidate requires a name.")
        if not isinstance(model_config, dict):
            raise ExperimentCandidateError(
                f"Experiment candidate {name} requires a model config."
            )
        validated_candidates.append({"name": name, "model": model_config})

    return validated_candidates


def build_candidate_config(
    config: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """Build a training config for one experiment candidate."""
    candidate_config = deepcopy(config)
    candidate_name = str(candidate["name"])
    candidate_config["model"] = candidate["model"]
    candidate_config["active_experiment_candidate"] = candidate_name
    candidate_config["artifacts"]["dir"] = str(
        Path(config["artifacts"]["dir"]) / "experiments" / _safe_path_name(candidate_name)
    )
    return candidate_config


def resolve_champion_report_path(config: dict[str, Any]) -> Path:
    """Return champion report path from config or default."""
    selection_config = config.get("champion_selection")
    if not isinstance(selection_config, dict):
        return Path("reports/champion_run.json")
    return Path(cast(str, selection_config.get("report_path", "reports/champion_run.json")))


def run_experiment_workflow(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    *,
    validate_before_run: bool = True,
) -> dict[str, Any]:
    """Run configured experiment candidates and return the champion report."""
    resolved_config_path = Path(config_path)
    logger = get_logger(LOGGER_NAME)

    config = load_config(resolved_config_path)
    log_path = build_log_path(config)
    logger = get_logger(LOGGER_NAME, log_path)
    run_started_at = datetime.now(UTC).isoformat()
    logger.info(
        "===== RUN STARTED %s | workflow=experiments =====",
        run_started_at,
    )

    if validate_before_run:
        validation_schema_path = resolve_validation_schema_path(config)
        validation_report = validate_dataset_readiness(
            resolved_config_path,
            validation_schema_path,
        )
        _log_validation_summary(logger, validation_report)
        enforce_validation_gate(validation_report)

    candidates = load_experiment_candidates(config)
    dataset_context = _build_dataset_context(config)
    candidate_runs = [
        _run_candidate(config, dataset_context, candidate, logger)
        for candidate in candidates
    ]
    champion_report = select_champion_run(candidate_runs)
    champion = champion_report["champion"]
    cleared_champions = clear_champion_tags(config)
    for candidate_run in candidate_runs:
        set_run_tags(
            config,
            candidate_run["run_id"],
            {
                "champion": "false",
                "champion_selection_batch": run_started_at,
            },
        )
    set_run_tags(
        config,
        champion["run_id"],
        {
            "champion": "true",
            "champion_selection_rule": champion_report["selection_rule"],
            "champion_primary_metric": champion_report["primary_metric"],
            "champion_selection_batch": run_started_at,
        },
    )
    champion_report_path = resolve_champion_report_path(config)
    save_json(champion_report, champion_report_path)

    logger.info(_format_log_section("RUNTIME", {"log_file": log_path}))
    logger.info(
        _format_log_section(
            "CHAMPION",
            {
                "run_id": champion["run_id"],
                "candidate_name": champion["candidate_name"],
                "model_type": champion["model_type"],
                "f1": champion["metrics"]["f1"],
                "report": champion_report_path,
                "cleared_previous_champions": cleared_champions,
            },
        )
    )
    logger.info("Experiment candidate run completed.")
    return champion_report


def main() -> None:
    """Run all configured experiment candidates and select a champion."""
    logger = get_logger(LOGGER_NAME)

    try:
        run_experiment_workflow(DEFAULT_CONFIG_PATH, validate_before_run=True)
    except (
        ArtifactError,
        ChampionSelectionError,
        ConfigError,
        DataError,
        DatasetRegistryError,
        EvaluationError,
        ExperimentCandidateError,
        ExperimentTrackingError,
        PreprocessingError,
        TrainingError,
        ValidationGateError,
    ) as exc:
        logger.exception("Experiment candidate run failed: %s", exc)
        raise SystemExit(1) from exc


def _log_validation_summary(logger, validation_report: ValidationReport) -> None:
    validation_counts = count_validation_issues(validation_report)
    logger.info(
        _format_log_section(
            "VALIDATION",
            {
                "status": validation_report.status,
                "issues": len(validation_report.issues),
                "info": validation_counts["INFO"],
                "warnings": validation_counts["WARNING"],
                "errors": validation_counts["ERROR"],
                "critical": validation_counts["CRITICAL"],
            },
        )
    )


def _build_dataset_context(config: dict[str, Any]) -> dict[str, Any]:
    dataset_config = cast(dict[str, Any], config["dataset"])
    training_config = cast(dict[str, Any], config["training"])
    dataset_path = cast(str, dataset_config["path"])
    target_column = cast(str, dataset_config["target_column"])
    drop_columns = cast(list[str], dataset_config.get("drop_columns", []))
    test_size = cast(float, training_config["test_size"])
    random_state = cast(int, training_config["random_state"])
    dataset_version_metadata_path = resolve_dataset_version_metadata_path(config)
    dataset_version_metadata = load_dataset_version_metadata(
        dataset_version_metadata_path
    )
    dataset_version_snapshot = build_dataset_version_snapshot(
        dataset_version_metadata_path,
        dataset_version_metadata,
    )

    dataframe = load_dataset(dataset_path)
    dataframe = drop_configured_columns(dataframe, drop_columns)
    features, target = split_features_target(dataframe, target_column)
    x_train, x_test, y_train, y_test = split_train_test(
        features,
        target,
        test_size,
        random_state,
    )
    numeric_features, categorical_features = identify_feature_types(x_train)
    return {
        "dataset_path": dataset_path,
        "target_column": target_column,
        "drop_columns": drop_columns,
        "dataframe": dataframe,
        "features": features,
        "x_train": x_train,
        "x_test": x_test,
        "y_train": y_train,
        "y_test": y_test,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "dataset_version_snapshot": dataset_version_snapshot,
    }


def _run_candidate(
    config: dict[str, Any],
    dataset_context: dict[str, Any],
    candidate: dict[str, Any],
    logger,
) -> dict[str, Any]:
    candidate_config = build_candidate_config(config, candidate)
    candidate_name = str(candidate["name"])
    run_started_at = datetime.now(UTC).isoformat()

    with start_experiment_run(
        candidate_config,
        run_name=f"candidate-{candidate_name}-{run_started_at}",
    ) as run:
        mlflow_run_id = get_run_id(run)
        model_config = cast(dict[str, Any], candidate_config["model"])
        preprocessing_pipeline = build_preprocessing_pipeline(
            dataset_context["numeric_features"],
            dataset_context["categorical_features"],
        )
        model = build_model(model_config)
        training_pipeline = build_training_pipeline(
            preprocessing_pipeline,
            model,
        )
        fitted_pipeline, training_duration = train_model(
            training_pipeline,
            dataset_context["x_train"],
            dataset_context["y_train"],
        )
        metrics, evaluation_duration = evaluate_model_with_duration(
            fitted_pipeline,
            dataset_context["x_test"],
            dataset_context["y_test"],
        )
        artifact_paths = build_artifact_paths(candidate_config)
        metadata = _build_candidate_metadata(
            candidate_name,
            mlflow_run_id,
            run_started_at,
            model_config,
            training_duration,
            evaluation_duration,
            dataset_context,
        )

        save_model(fitted_pipeline, artifact_paths["model"])
        save_json(metrics, artifact_paths["metrics"])
        save_json(
            {"labels": [0, 1], "matrix": metrics["confusion_matrix"]},
            artifact_paths["confusion_matrix"],
        )
        save_json(candidate_config, artifact_paths["config_snapshot"])
        save_json(metadata, artifact_paths["metadata"])
        log_training_outputs(candidate_config, metrics, metadata, artifact_paths)

    set_run_tags(
        config,
        mlflow_run_id,
        {
            "candidate_name": candidate_name,
            "candidate_model_type": str(model_config["type"]),
        },
    )
    logger.info(
        _format_log_section(
            "CANDIDATE",
            {
                "name": candidate_name,
                "run_id": mlflow_run_id,
                "model_type": model_config["type"],
                "f1": f"{metrics['f1']:.6f}",
            },
        )
    )
    selection_metrics = {
        **metrics,
        "training_duration_seconds": training_duration,
        "evaluation_duration_seconds": evaluation_duration,
    }
    return {
        "run_id": mlflow_run_id,
        "candidate_name": candidate_name,
        "model_type": model_config["type"],
        "status": "FINISHED",
        "dataset_name": dataset_context["dataset_version_snapshot"]["dataset_name"],
        "dataset_version": dataset_context["dataset_version_snapshot"]["version"],
        "dataset_checksum": dataset_context["dataset_version_snapshot"]["checksum"][
            "value"
        ],
        "pipeline_version": PIPELINE_VERSION,
        "metrics": selection_metrics,
        "artifacts": {key: str(path) for key, path in artifact_paths.items()},
    }


def _build_candidate_metadata(
    candidate_name: str,
    mlflow_run_id: str,
    run_started_at: str,
    model_config: dict[str, Any],
    training_duration: float,
    evaluation_duration: float,
    dataset_context: dict[str, Any],
) -> dict[str, Any]:
    dataframe = dataset_context["dataframe"]
    features = dataset_context["features"]
    return {
        "generated_at": run_started_at,
        "mlflow_run_id": mlflow_run_id,
        "candidate_name": candidate_name,
        "dataset_path": dataset_context["dataset_path"],
        "dataset_version": dataset_context["dataset_version_snapshot"],
        "target_column": dataset_context["target_column"],
        "dropped_columns": dataset_context["drop_columns"],
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "feature_columns": len(features.columns),
        "train_rows": len(dataset_context["x_train"]),
        "test_rows": len(dataset_context["x_test"]),
        "numeric_features": dataset_context["numeric_features"],
        "categorical_features": dataset_context["categorical_features"],
        "model_type": model_config["type"],
        "training_duration_seconds": training_duration,
        "evaluation_duration_seconds": evaluation_duration,
    }


def _format_log_section(title: str, values: dict[str, Any]) -> str:
    key_width = max(len(key) for key in values)
    lines = [f"[{title}]"]
    lines.extend(f"{key:<{key_width}} : {value}" for key, value in values.items())
    return "\n".join(lines)


def _safe_path_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_")


if __name__ == "__main__":
    main()

"""Train a candidate model inside a governed retraining run."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from app.config import ConfigError, load_config
from app.data import DataError, load_dataset
from app.dataset_registry import (
    DatasetRegistryError,
    build_dataset_version_snapshot,
    load_dataset_version_metadata,
    resolve_dataset_version_metadata_path,
)
from app.evaluate import EvaluationError, evaluate_model_with_duration
from app.pipeline.preprocessing import (
    PreprocessingError,
    build_preprocessing_pipeline,
    identify_feature_types,
    split_features_target,
    split_train_test,
)
from app.pipeline.trainer import (
    TrainingError,
    build_model,
    build_training_pipeline,
    train_model,
)
from app.retraining.candidate_run_metadata import (
    CANDIDATE_RUN_INITIALIZED,
    CANDIDATE_TRAINED,
    DEFAULT_RETRAINING_RUNS_DIR,
    CandidateRetrainingRunError,
    build_candidate_retraining_run_metadata_path,
    load_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.train import (
    ValidationGateError,
    drop_configured_columns,
    enforce_validation_gate,
    resolve_validation_schema_path,
)
from app.utils.artifacts import ArtifactError, save_json, save_model
from app.validate_data import validate_dataset_readiness

CANDIDATE_ARTIFACT_DIR_NAME = "candidate"


class CandidateTrainingError(ValueError):
    """Raised when candidate retraining cannot complete."""


def run_candidate_retraining(
    *,
    run_id: str,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
    config_path: Path | None = None,
    trained_at: str | None = None,
) -> tuple[dict[str, Any], Path]:
    """Train a candidate model for an initialized retraining run."""
    try:
        metadata = load_candidate_retraining_run_metadata(run_id, runs_dir=runs_dir)
        _validate_candidate_can_train(metadata)
        resolved_config_path = config_path or Path(
            str(metadata["lineage"]["training_config_path"])
        )
        config = load_config(resolved_config_path)
        schema_path = _metadata_schema_path(metadata, config)
        validation_report = validate_dataset_readiness(
            resolved_config_path,
            schema_path,
        )
        enforce_validation_gate(validation_report)
        artifact_paths = build_candidate_artifact_paths(run_id, runs_dir=runs_dir)
        result = train_candidate_model(
            config=config,
            config_path=resolved_config_path,
            artifact_paths=artifact_paths,
            trained_at=trained_at,
        )
        updated_metadata = update_metadata_after_candidate_training(
            metadata,
            result=result,
            validation_report=validation_report.to_dict(),
        )
        output_path = save_candidate_retraining_run_metadata(
            updated_metadata,
            runs_dir=runs_dir,
        )
    except (
        ArtifactError,
        CandidateRetrainingRunError,
        ConfigError,
        DataError,
        DatasetRegistryError,
        EvaluationError,
        PreprocessingError,
        TrainingError,
        ValidationGateError,
    ) as exc:
        raise CandidateTrainingError(
            f"Candidate retraining failed for run_id={run_id}: {exc}"
        ) from exc

    return updated_metadata, output_path


def build_candidate_artifact_paths(
    run_id: str,
    *,
    runs_dir: Path = DEFAULT_RETRAINING_RUNS_DIR,
) -> dict[str, Path]:
    """Build local artifact paths for one candidate retraining run."""
    metadata_path = build_candidate_retraining_run_metadata_path(run_id, runs_dir)
    artifact_dir = metadata_path.parent / CANDIDATE_ARTIFACT_DIR_NAME
    return {
        "model": artifact_dir / "model.pkl",
        "metrics": artifact_dir / "metrics.json",
        "confusion_matrix": artifact_dir / "confusion_matrix.json",
        "config_snapshot": artifact_dir / "config_snapshot.json",
        "training_metadata": artifact_dir / "training_metadata.json",
    }


def train_candidate_model(
    *,
    config: dict[str, Any],
    config_path: Path,
    artifact_paths: dict[str, Path],
    trained_at: str | None = None,
) -> dict[str, Any]:
    """Train the configured model and persist candidate artifacts."""
    started_at = trained_at or _utc_now()
    dataset_context = _build_dataset_context(config, config_path)
    model_config = cast(dict[str, Any], config["model"])
    preprocessing_pipeline = build_preprocessing_pipeline(
        dataset_context["numeric_features"],
        dataset_context["categorical_features"],
    )
    model = build_model(model_config)
    training_pipeline = build_training_pipeline(preprocessing_pipeline, model)
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
    training_metadata = _build_training_metadata(
        config_path=config_path,
        model_config=model_config,
        dataset_context=dataset_context,
        trained_at=started_at,
        training_duration=training_duration,
        evaluation_duration=evaluation_duration,
    )

    save_model(fitted_pipeline, artifact_paths["model"])
    save_json(metrics, artifact_paths["metrics"])
    save_json(
        {"labels": [0, 1], "matrix": metrics["confusion_matrix"]},
        artifact_paths["confusion_matrix"],
    )
    save_json(config, artifact_paths["config_snapshot"])
    save_json(training_metadata, artifact_paths["training_metadata"])

    return {
        "trained_at": started_at,
        "model_type": model_config["type"],
        "metrics": {
            **metrics,
            "training_duration_seconds": training_duration,
            "evaluation_duration_seconds": evaluation_duration,
        },
        "artifacts": {name: str(path) for name, path in artifact_paths.items()},
        "training_metadata": training_metadata,
    }


def update_metadata_after_candidate_training(
    metadata: dict[str, Any],
    *,
    result: dict[str, Any],
    validation_report: dict[str, Any],
) -> dict[str, Any]:
    """Return retraining metadata updated with candidate training outputs."""
    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = CANDIDATE_TRAINED
    candidate = updated_metadata.setdefault("candidate", {})
    artifacts = result["artifacts"]
    candidate.update(
        {
            "trained_at": result["trained_at"],
            "model_type": result["model_type"],
            "model_path": artifacts["model"],
            "metrics_path": artifacts["metrics"],
            "confusion_matrix_path": artifacts["confusion_matrix"],
            "config_snapshot_path": artifacts["config_snapshot"],
            "training_metadata_path": artifacts["training_metadata"],
            "comparison_report_path": candidate.get("comparison_report_path"),
            "metrics": deepcopy(result["metrics"]),
            "validation": {
                "status": validation_report["status"],
                "schema_path": validation_report["schema_path"],
                "issue_counts": deepcopy(validation_report["issue_counts"]),
            },
        }
    )
    updated_metadata["candidate_training"] = deepcopy(result["training_metadata"])
    return updated_metadata


def _validate_candidate_can_train(metadata: dict[str, Any]) -> None:
    status = metadata.get("status")
    if status != CANDIDATE_RUN_INITIALIZED:
        raise CandidateTrainingError(
            "Candidate retraining requires status="
            f"{CANDIDATE_RUN_INITIALIZED}; got {status}."
        )


def _metadata_schema_path(metadata: dict[str, Any], config: dict[str, Any]) -> Path:
    lineage = metadata.get("lineage")
    if isinstance(lineage, dict) and lineage.get("schema_path"):
        return Path(str(lineage["schema_path"]))
    return resolve_validation_schema_path(config)


def _build_dataset_context(
    config: dict[str, Any],
    config_path: Path,
) -> dict[str, Any]:
    dataset_config = cast(dict[str, Any], config["dataset"])
    training_config = cast(dict[str, Any], config["training"])
    dataset_path = _resolve_configured_path(
        config_path,
        cast(str, dataset_config["path"]),
    )
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
        "dataset_path": str(dataset_path),
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


def _build_training_metadata(
    *,
    config_path: Path,
    model_config: dict[str, Any],
    dataset_context: dict[str, Any],
    trained_at: str,
    training_duration: float,
    evaluation_duration: float,
) -> dict[str, Any]:
    dataframe = dataset_context["dataframe"]
    features = dataset_context["features"]
    return {
        "generated_at": trained_at,
        "workflow": "candidate_retraining",
        "config_path": str(config_path),
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


def _resolve_configured_path(config_path: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return config_path.parent.parent / path


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


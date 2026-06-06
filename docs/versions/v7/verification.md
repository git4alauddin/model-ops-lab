# V7 Verification

## Checks Performed
- Verified serving dependencies are declared.
- Verified FastAPI app factory creates the service.
- Verified Uvicorn entry point exposes an importable app.
- Verified `GET /health` returns service status.
- Verified `GET /ready` returns ready when one champion exists.
- Verified `GET /ready` returns `503` when no champion exists.
- Verified readiness rejects multiple champions.
- Verified `/health` remains independent from `/ready`.
- Verified prediction request schema accepts valid inference payloads.
- Verified prediction request schema rejects missing fields, unexpected fields, invalid categorical values, and invalid numeric ranges.
- Verified prediction response schema enforces prediction metadata.
- Verified serving error response is structured.
- Verified champion model metadata resolution.
- Verified missing and multiple champion states are rejected by the model loader.
- Verified local artifact paths and MLflow-run artifact URIs resolve to model files.
- Verified model artifacts are loaded with registry metadata.
- Verified unloadable artifacts fail safely.

## Commands Executed
- `python -m pytest -q tests\test_v7_c1_serving_foundation.py`
- `python -c "from app.serve_api import app; print(app.title); print(app.version)"`
- `python -m pytest -q tests\test_v7_c2_readiness_endpoint.py`
- `python -m pytest -q tests\test_v7_c1_serving_foundation.py tests\test_v7_c2_readiness_endpoint.py`
- `python -m pytest -q tests\test_v7_c3_inference_schemas.py`
- `python -m pytest -q tests\test_v7_c4_model_loader.py`
- PowerShell-expanded V7 suite command for `tests\test_v7_*.py`
- `python -c "from app.serving.model_loader import load_champion_model; loaded = load_champion_model(); print(loaded.metadata['model_version']); print(loaded.artifact_path.name); print(type(loaded.model).__name__)"`
- `python -m pytest -q`

## Expected Output
- FastAPI app can be created.
- `/health` returns HTTP 200.
- `/health` response includes service identity and API version.
- `/ready` returns HTTP 200 when exactly one champion exists.
- `/ready` returns HTTP 503 when no champion exists.
- `/ready` returns HTTP 503 when registry state is ambiguous.
- Prediction request schema rejects invalid inference payloads.
- Prediction response schema preserves model and request metadata.
- Serving error response has a stable shape.
- Model loader resolves exactly one champion model.
- Model loader resolves model artifact references.
- Model loader raises controlled errors for unsafe serving states.
- Existing test suite remains passing.

## Actual Output
- `python -m pytest -q tests\test_v7_c1_serving_foundation.py` passed: `3 passed in 0.40s`.
- `python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `python -m pytest -q tests\test_v7_c2_readiness_endpoint.py` passed: `6 passed in 0.59s`.
- `python -m pytest -q tests\test_v7_c1_serving_foundation.py tests\test_v7_c2_readiness_endpoint.py` passed: `9 passed in 0.63s`.
- `python -m pytest -q` passed: `249 passed in 5.61s`.
- `python -m pytest -q tests\test_v7_c3_inference_schemas.py` passed: `8 passed in 0.13s`.
- PowerShell-expanded V7 suite command passed: `17 passed in 0.59s`.
- `python -m pytest -q` passed: `257 passed in 5.30s`.
- `python -m pytest -q tests\test_v7_c4_model_loader.py` passed: `8 passed in 0.27s`.
- PowerShell-expanded V7 suite command passed: `25 passed in 0.80s`.
- `python -c "from app.serving.model_loader import load_champion_model; loaded = load_champion_model(); print(loaded.metadata['model_version']); print(loaded.artifact_path.name); print(type(loaded.model).__name__)"` printed `v1-7ab8f00a`, `model.pkl`, and `Pipeline`.
- `python -m pytest -q` passed: `265 passed in 5.12s`.

## Outcome
V7-C1 creates the first serving API boundary without adding model loading or prediction behavior yet.

V7-C2 adds readiness behavior based on champion model availability in the local registry.

V7-C3 defines the inference API contract before adding prediction execution.

V7-C4 adds registry-based model loading for the future `/predict` endpoint.

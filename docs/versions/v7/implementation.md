# V7 Implementation

## V7-C1: Serving API Foundation

### Files Added

```text
app/api/__init__.py
app/api/app.py
app/api/constants.py
app/api/routes.py
app/serve_api.py
tests/test_v7_c1_serving_foundation.py
```

### Files Updated

```text
requirements.txt
docs/versions/v7/
```

### Behavior
- Added a FastAPI application factory.
- Added shared serving constants for service identity and API version.
- Added `GET /health`.
- Added an importable Uvicorn app object at `app.serve_api:app`.
- Added focused tests for app creation and health endpoint behavior.

### Local Run Command

```powershell
uvicorn app.serve_api:app --reload
```

### Health Check

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "service": "modelopslab-serving",
  "api_version": "v7"
}
```


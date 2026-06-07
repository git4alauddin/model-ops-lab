# V8 Lessons

- Docker should package the runtime environment, not local machine state.
- The serving image should start from the already-tested FastAPI entry point instead of introducing a new application path.
- `.dockerignore` is part of deployment quality because large or sensitive local files should not enter the Docker build context.
- Secrets should never be copied into an image.
- Local MLflow artifacts and model registry records are runtime inputs, not source code.
- A first Docker chunk should prove packaging before adding Compose, CI/CD, registry push, or deployment workflows.
- Docker Compose should describe how the image runs locally, not redefine the application startup already owned by the Dockerfile.
- Runtime model metadata and MLflow artifacts can be mounted read-only because serving should consume them, not mutate them.
- Logs should remain writable because serving runtime events and prediction audit records are outputs.
- Environment configuration should be explicit before CI/CD so automated pipelines validate the same runtime contract used locally.
- Deployment-facing values must satisfy the tools that consume them; Uvicorn requires lowercase log levels.
- Python can normalize environment values internally while Docker receives tool-compatible values.

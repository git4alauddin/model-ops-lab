# V8 Lessons

- Docker should package the runtime environment, not local machine state.
- The serving image should start from the already-tested FastAPI entry point instead of introducing a new application path.
- `.dockerignore` is part of deployment quality because large or sensitive local files should not enter the Docker build context.
- Secrets should never be copied into an image.
- Local MLflow artifacts and model registry records are runtime inputs, not source code.
- A first Docker chunk should prove packaging before adding Compose, CI/CD, registry push, or deployment workflows.

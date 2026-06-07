# Manual CI Run Guide

This guide explains how to run the `ci` GitHub Actions workflow manually.

The workflow is intentionally manual during the current build phase so small learning commits do not spend CI minutes automatically.

## When To Run CI
Run the workflow when:

```text
you changed shared application code
you changed Docker or Compose files
you changed CI workflow files
you want GitHub/Linux confirmation before tagging or deployment checks
```

You do not need to run it for every small documentation-only edit unless the documentation changes affect CI, Docker, deployment, or release instructions.

## How To Trigger CI From GitHub UI

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
-> Branch: main
-> Run workflow
```

The trigger behind this is:

```text
workflow_dispatch
```

That means the workflow starts only when manually requested.

## Jobs In The Workflow

```text
tests
docker-image
```

## tests Job
Purpose:

```text
prove the Python test suite passes in GitHub Actions
```

Main command:

```text
python -m pytest -q
```

If this job fails:

```text
open the failed pytest step
read the failed test name
check the assertion diff
fix the code or test
rerun CI manually
```

## docker-image Job
Purpose:

```text
prove the serving Docker image can build after tests pass
```

Main command:

```text
docker build \
  -f deployment/Dockerfile \
  -t modelopslab-serving:ci \
  -t modelopslab-serving:${{ github.sha }} \
  .
```

This job runs only after the `tests` job passes.

If this job fails:

```text
open the failed Docker build step
check whether dependency install failed
check whether Dockerfile copy/build context failed
check whether the app import/startup path changed
fix Dockerfile, .dockerignore, requirements, or source files
rerun CI manually
```

## What CI Does Not Do Yet
The workflow does not:

```text
login to Docker Hub
push images to Docker Hub
deploy to cloud
rollback deployments
use production secrets
```

Those will be added in later V8 chunks after build validation and image tagging are stable.

## How To Read A Successful Run
A successful run should show:

```text
tests        passed
docker-image passed
```

That means:

```text
Python tests pass on GitHub-hosted Linux
the Docker serving image builds in CI
the image is tagged locally inside the CI job
no image has been published externally yet
```

# Docker Hub Publish Validation

This records the completed Docker Hub publishing validation for V8.

## Validation Status
Docker Hub publishing has been validated from GitHub Actions.

Confirmed path:

```text
GitHub Actions
-> ci
-> Run workflow
-> publish_image: true
-> tests passed
-> Docker image built
-> Docker Hub secrets validated
-> Docker Hub login succeeded
-> Docker Hub image tags pushed
```

## Required External Configuration
The external configuration is complete:

```text
Docker Hub repository exists:
modelopslab-serving

GitHub Actions secrets exist:
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

## Published Tags
The workflow publishes:

```text
<dockerhub-username>/modelopslab-serving:<git-sha>
<dockerhub-username>/modelopslab-serving:ci
```

The Git SHA tag is the traceable deployment artifact.

The `ci` tag is a moving convenience tag.

## Verification In Docker Hub
Docker Hub UI path:

```text
Docker Hub
-> Repositories
-> modelopslab-serving
-> Tags
```

Expected tags:

```text
<git-sha>
ci
```

## Current Boundary
V8 validates image publishing, not live cloud deployment.

Current boundary:

```text
source code
-> tests
-> Docker image build
-> Docker Hub image publish
```

Not included in V8:

```text
Cloud Run service
public hosted API URL
post-deploy health check
live service rollback
```

Cloud Run deployment should be handled as a separate deployment chunk after V8 closure.

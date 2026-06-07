# Docker Hub Publishing Plan

This plan describes how ModelOpsLab will publish serving images to Docker Hub later.

Publishing is not enabled yet.

## Why Docker Hub
Docker Hub is a container image registry.

It lets CI store built Docker images so another environment can pull and run the exact image.

Current flow:

```text
Dockerfile
-> docker build
-> local CI image
```

Later flow:

```text
Dockerfile
-> docker build
-> docker tag
-> docker push
-> Docker Hub
-> deployment pulls image
```

## Target Image Name
Use this format:

```text
<dockerhub-username>/modelopslab-serving:<tag>
```

Examples:

```text
alaud/modelopslab-serving:${{ github.sha }}
alaud/modelopslab-serving:ci
alaud/modelopslab-serving:v8.0.0
```

The actual Docker Hub username should come from a GitHub Actions secret, not from hardcoded workflow text.

## Required GitHub Actions Secrets
Add these later in GitHub:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

GitHub UI path:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
-> New repository secret
```

## Why Token, Not Password
Use a Docker Hub access token instead of an account password.

Reason:

```text
tokens can be scoped
tokens can be revoked
tokens avoid exposing the account password
tokens are safer for CI automation
```

## Planned Push Tags
When publishing is enabled, CI should push:

```text
${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}
${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:ci
```

Release workflows may also push:

```text
${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:vX.Y.Z
```

## Safety Rules
- Do not hardcode Docker Hub credentials.
- Do not commit `.env` files with secrets.
- Do not use a Docker Hub password in CI.
- Do not publish `latest` as the only tag.
- Do not deploy an image that was not built after tests passed.

## Current Boundary
Current CI:

```text
runs tests
builds Docker image
tags image locally
does not login to Docker Hub
does not push image
```

Docker Hub publishing will be added only after this plan is reviewed and the required GitHub secrets are configured.

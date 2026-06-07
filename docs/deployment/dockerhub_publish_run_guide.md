# Docker Hub Publish Run Guide

This guide explains how to publish the serving image to Docker Hub from GitHub Actions.

Publishing is manual and off by default.

## Prerequisites
Before publishing, these GitHub Actions repository secrets must exist:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Secret setup guide:

```text
docs/deployment/dockerhub_secrets_setup.md
```

## Normal Validation Run
Use this when you only want tests and Docker image build validation.

GitHub UI path:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
-> Branch: main
-> publish_image: false
-> Run workflow
```

Behavior:

```text
runs tests
builds Docker image
does not login to Docker Hub
does not push image
```

## Publish Run
Use this only when the current commit should publish a Docker image.

GitHub UI path:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
-> Branch: main
-> publish_image: true
-> Run workflow
```

Behavior:

```text
runs tests
builds Docker image
logs in to Docker Hub
pushes Git SHA tag
pushes ci tag
```

The publish steps run only when:

```text
publish_image == true
```

## Published Tags
The workflow pushes:

```text
<dockerhub-username>/modelopslab-serving:<git-sha>
<dockerhub-username>/modelopslab-serving:ci
```

The Git SHA tag is the important traceable tag.

The `ci` tag is a moving convenience tag for the latest manually published CI image.

## Verify On Docker Hub
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

## Safety Rules
- Keep `publish_image` as `false` for normal validation.
- Use `publish_image: true` only when the image should be published.
- Do not publish if tests fail.
- Do not print Docker Hub secrets in logs.
- Prefer the Git SHA tag for traceability and rollback.

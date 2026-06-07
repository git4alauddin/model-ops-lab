# Docker Hub Secrets Setup Guide

This guide explains how to prepare Docker Hub credentials for GitHub Actions.

Publishing is still not enabled in CI.

## Goal
Create the credentials that a future CI publishing job will use to push serving images to Docker Hub.

Required GitHub Actions secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

## Step 1: Create a Docker Hub Access Token
Use a Docker Hub access token, not password.

Docker Hub UI path:

```text
Docker Hub
-> Account Settings
-> Security
-> Access Tokens
-> Generate new token
```

Recommended token scope for this project:

```text
Read, Write
```

Use the smallest scope that can push images to the target repository.

Store the generated token only long enough to paste it into GitHub Actions secrets. Docker Hub will not show the token value again after creation.

## Step 2: Add GitHub Repository Secrets
GitHub UI path:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
-> New repository secret
```

Create these secrets:

```text
Name: DOCKERHUB_USERNAME
Value: your Docker Hub username

Name: DOCKERHUB_TOKEN
Value: the Docker Hub access token
```

## Step 3: Verify Without Exposing Values
In GitHub, repository secrets are masked.

Safe verification:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
-> Repository secrets
```

Confirm that these names exist:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Do not print the token in workflow logs.

Do not paste the token into code, docs, `.env`, terminal screenshots, or commit messages.

## Why Token, Not Password
Use an access token instead of an account password because:

```text
tokens can be revoked independently
tokens can be scoped
tokens avoid exposing the main account password
tokens are safer for CI automation
```

If the token leaks, revoke it from Docker Hub and create a new one.

## What This Enables Later
After the secrets exist, a future CI chunk can safely add:

```text
docker login
docker push
```

Expected future image names:

```text
${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}
${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:ci
```

## Current Boundary
Current CI still only:

```text
runs tests
builds Docker image
tags image locally
does not login to Docker Hub
does not push image
```

Secret setup and image publishing are intentionally separate steps.

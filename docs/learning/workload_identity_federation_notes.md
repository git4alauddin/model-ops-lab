# Workload Identity Federation Notes

These notes document what was learned while connecting GitHub Actions to Google Cloud for ModelOpsLab.

This is implementation-grounded. It reflects the setup used for the live Cloud Run deployment validation.

## Why Workload Identity Federation Exists

GitHub Actions needed permission to deploy to Cloud Run.

The unsafe simple option would be:

```text
create a service account key JSON
store it as a GitHub secret
let GitHub Actions use that long-lived key
```

We avoided that.

Instead, we used Workload Identity Federation:

```text
GitHub Actions OIDC token
-> Google Workload Identity Provider
-> service account impersonation
-> temporary GCP credentials
-> Cloud Run deploy
```

Why this is better:

```text
no long-lived service account key JSON
credentials are short-lived
trust is restricted to one GitHub repository
access can be revoked from Google Cloud IAM
```

## Components We Created

### Service Account

```text
modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
```

Purpose:

```text
the identity GitHub Actions impersonates when deploying to Cloud Run
```

Roles granted on the project:

```text
roles/run.admin
roles/iam.serviceAccountUser
```

Why:

```text
Cloud Run Admin lets it create and update Cloud Run services
Service Account User lets it deploy revisions using a service account identity
```

### Workload Identity Pool

```text
projects/153930851596/locations/global/workloadIdentityPools/github-actions-pool
```

Purpose:

```text
groups external identities that Google Cloud can trust
```

In this project, the external identity source is GitHub Actions.

### Workload Identity Provider

```text
projects/153930851596/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider
```

Issuer:

```text
https://token.actions.githubusercontent.com
```

Purpose:

```text
accept GitHub's OIDC token and map its claims into Google Cloud attributes
```

Attribute mapping used:

```text
google.subject = assertion.sub
attribute.actor = assertion.actor
attribute.repository = assertion.repository
attribute.ref = assertion.ref
```

Attribute condition used:

```text
assertion.repository == "git4alauddin/model-ops-lab"
```

Why this matters:

```text
only GitHub Actions tokens from this repository are accepted by the provider
```

### Principal Binding

The service account was granted `roles/iam.workloadIdentityUser` to this principal:

```text
principalSet://iam.googleapis.com/projects/153930851596/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/git4alauddin/model-ops-lab
```

Meaning:

```text
GitHub Actions runs from git4alauddin/model-ops-lab can impersonate the deployer service account
```

This is the trust bridge.

Without this binding, GitHub could authenticate to the provider but could not act as the deployer service account.

## GitHub Secrets

The workflow stores only references, not key JSON:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

Values used:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER:
projects/153930851596/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider

GCP_SERVICE_ACCOUNT:
modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
```

The workflow also uses Docker Hub secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

## Runtime Behavior In GitHub Actions

The workflow step:

```text
google-github-actions/auth@v3
```

does this:

```text
requests a GitHub OIDC token
sends it to Google Cloud's Workload Identity Provider
receives permission to impersonate the service account
creates a temporary credentials file
exports Google Cloud auth environment variables
cleans up the credentials file after the job
```

The logs showed:

```text
Created credentials file at ".../gha-creds-<id>.json"
Removed exported credentials at ".../gha-creds-<id>.json"
```

This temporary file pattern is why the repo ignores:

```text
gha-creds-*.json
```

in both Git and Docker context.

## Mental Model

Workload Identity Federation answers this question:

```text
How can GitHub Actions prove to Google Cloud that it is allowed to act as a specific service account without storing a permanent key?
```

The answer is:

```text
GitHub proves repository identity with an OIDC token
Google verifies that token through the provider
IAM checks whether that repository principal can impersonate the service account
the workflow receives short-lived credentials
```

## Operational Lessons

- Service account roles define what the deployment identity can do.
- Workload Identity User defines who can impersonate the deployment identity.
- The provider condition should restrict trust to the exact GitHub repository.
- GitHub secrets should store provider and service account references, not service account key JSON.
- Temporary auth files should never be committed or copied into Docker images.
- Passing GCP authentication does not mean deployment will succeed; image availability, Cloud Run configuration, and health checks are separate failure surfaces.

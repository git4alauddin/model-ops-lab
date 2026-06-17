# Cloud Run Rollback And Cleanup Guide

This guide documents how to recover and clean up after Cloud Run deployments for ModelOpsLab.

This is an operations guide only. It does not perform a rollback or delete anything.

## Current Known-Good Runtime Points

Docker Hub validated Cloud Run revision:

```text
revision: modelopslab-serving-00002-fbc
image tag: 4388088e4b5f605a552ecf4e46d4edaab2a8e7fb
image digest: sha256:62ff4b9ac2487e3457972958cc4f0531bd9700ae639b265dff903a7c0127f71b
health: {"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

Artifact Registry validated Cloud Run revision:

```text
revision: modelopslab-serving-00003-zsc
image tag: ee825dad109380d7f53e4a576de0fd2b042e704a
image digest: sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b
traffic: 100
health: {"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

Current preferred image source:

```text
Artifact Registry
```

Current fallback image source:

```text
Docker Hub
```

## Rollback Option 1: Move Traffic To A Previous Revision

Use this when a previous Cloud Run revision still exists and is known-good.

GUI path:

```text
Google Cloud Console
-> Cloud Run
-> modelopslab-serving
-> Revisions
-> select or manage traffic
-> set the known-good revision to 100%
-> set the bad revision to 0%
-> Save
```

CLI shape:

```powershell
gcloud run services update-traffic modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --to-revisions <revision-name>=100
```

Example rollback to the validated Artifact Registry revision:

```powershell
gcloud run services update-traffic modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --to-revisions modelopslab-serving-00003-zsc=100
```

Verify after traffic rollback:

```powershell
Invoke-RestMethod -Uri 'https://modelopslab-serving-pv3rkohw6q-uc.a.run.app/health'
```

Expected response:

```json
{"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

Also verify:

```powershell
gcloud run services describe modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --format=json
```

Check:

```text
latestReadyRevisionName
traffic revisionName
traffic percent
container image
```

## Rollback Option 2: Redeploy A Known-Good Git SHA Image

Use this when the known-good revision no longer exists, or when you want a new revision created from a known-good image.

Preferred Artifact Registry image:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>
```

CLI shape:

```powershell
gcloud run deploy modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --image us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha> --allow-unauthenticated --port=8000
```

Example using the validated Artifact Registry Git SHA:

```powershell
gcloud run deploy modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --image us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:ee825dad109380d7f53e4a576de0fd2b042e704a --allow-unauthenticated --port=8000
```

Docker Hub fallback image:

```text
docker.io/<dockerhub-username>/modelopslab-serving:<git-sha>
```

Use Docker Hub fallback only when Artifact Registry is unavailable or the fallback is intentionally being tested.

## What Not To Roll Back Blindly

Do not blindly roll back when:

```text
the previous revision has unknown image provenance
the previous revision uses incompatible environment variables
the previous revision points to missing model artifacts
the rollback target has not passed /health
the failure is caused by external dependencies rather than the container image
```

For this project, remember:

```text
/health is validated in Cloud Run
/ready and prediction endpoints still need externalized model registry and MLflow artifacts
```

Do not treat a successful `/health` rollback as proof that `/predict` is production-ready.

## Cleanup Guidance

Cleanup should be conservative.

Keep:

```text
latest known-good Artifact Registry image
latest known-good Docker Hub fallback image
at least one previous known-good Git SHA image
documentation for every live deployment validation
```

Do not delete:

```text
Cloud Run revision currently receiving traffic
only remaining revision of the service
latest revision without understanding traffic state
Artifact Registry image digest used by the current ready revision
Git SHA tags referenced in validation docs
```

## Cloud Run Revision Cleanup

Cloud Run revisions do not need manual deletion for normal operation.

Delete a revision only when:

```text
it receives 0% traffic
it is not the latest revision
it is not the only revision
it is not a known-good rollback target
```

CLI shape:

```powershell
gcloud run revisions delete <revision-name> --region=us-central1 --project=key-component-498805-h0
```

Before deleting, verify traffic:

```powershell
gcloud run services describe modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --format=json
```

## Artifact Registry Cleanup

Artifact Registry cleanup should protect known-good Git SHA images.

Current known-good Artifact Registry image:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:ee825dad109380d7f53e4a576de0fd2b042e704a
```

Do not delete the digest:

```text
sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b
```

For future cleanup policies:

```text
use keep rules for recent versions or protected tags
use delete rules only for old unprotected images
run cleanup in dry-run mode before enforcing deletion
record any cleanup policy in docs before enabling it
```

## Docker Hub Fallback Cleanup

Docker Hub remains fallback, not the preferred Cloud Run image source.

Keep the validated fallback image:

```text
alaudddin/modelopslab-serving:4388088e4b5f605a552ecf4e46d4edaab2a8e7fb
```

Do not rely on the moving `ci` tag for rollback.

Rollback references should use immutable Git SHA tags.

## Recommended Incident Checklist

When a deployment looks bad:

```text
1. Check GitHub Actions job failure or success.
2. Check Cloud Run latest ready revision.
3. Check current traffic split.
4. Check deployed image source and digest.
5. Call /health externally.
6. Decide whether to shift traffic to a previous revision or redeploy a known-good Git SHA image.
7. Verify /health after rollback.
8. Record the rollback action in deployment notes.
```

## Source References

- Cloud Run rollbacks and traffic migration: https://cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration
- Cloud Run revision management: https://cloud.google.com/run/docs/managing/revisions
- Artifact Registry cleanup policies: https://cloud.google.com/artifact-registry/docs/repositories/cleanup-policy

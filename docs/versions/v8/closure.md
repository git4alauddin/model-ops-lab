# V8 Closure

V8 is closed as the Dockerization and deployment foundation version.

The version moved ModelOpsLab from local FastAPI serving to a validated, manually gated cloud deployment path.

## Final Status

```text
status: complete
final chunk: v8-c25
preferred registry: Artifact Registry
preferred Cloud Run image source: artifact_registry
validated live service: modelopslab-serving
validated region: us-central1
```

## Final Validated Deployment Path

The final validated V8 deployment path is:

```text
GitHub Actions manual trigger
-> pytest
-> Docker image build
-> Artifact Registry push
-> Cloud Run deploy from Artifact Registry
-> /health check
```

The live Artifact Registry Cloud Run validation is recorded here:

```text
docs/deployment/cloud_run_artifact_registry_deploy_validation.md
```

Validated live revision:

```text
modelopslab-serving-00003-zsc
```

Validated live health response:

```json
{"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

## What V8 Completed

V8 completed:

```text
Docker serving image
Docker build context control
Docker Compose serving runtime
serving runtime environment configuration
GitHub Actions manual CI
CI pytest gate
CI Docker image build gate
Docker image versioning with Git SHA tags
manual CI run guide
Docker Hub publishing plan
Docker Hub secrets setup guide
Docker Hub publish gate
Docker Hub publish validation
Docker image rollback guide
Cloud Run deployment foundation
GitHub Actions Cloud Run deploy gate
Workload Identity Federation setup and validation
manual CI trigger learning notes
live Cloud Run validation from Docker Hub
Artifact Registry foundation
Artifact Registry setup validation
Artifact Registry publish gate
Artifact Registry publish validation
Cloud Run image source selector
live Cloud Run validation from Artifact Registry
Artifact Registry as default Cloud Run image source
Cloud Run rollback and cleanup guide
```

## Final Runtime Position

Current preferred image source:

```text
Artifact Registry
```

Current preferred image path:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>
```

Docker Hub remains:

```text
explicit fallback
not the preferred GCP deployment path
```

Current known-good Artifact Registry image:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:ee825dad109380d7f53e4a576de0fd2b042e704a
```

Current known-good Artifact Registry digest:

```text
sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b
```

## Security Position

V8 uses:

```text
GitHub Actions OIDC
Google Workload Identity Federation
service account impersonation
short-lived GCP credentials
repository-level Artifact Registry Writer
```

V8 avoids:

```text
service account key JSON
committed cloud credentials
secrets inside Docker images
```

## Operational Boundary

V8 validates:

```text
/health on Cloud Run
```

V8 does not validate live:

```text
/ready
/predict
/predict/batch
```

Reason:

```text
Cloud Run still needs externalized model registry and MLflow artifacts before prediction readiness can be validated cleanly
```

## What Moves To V9

The next version should focus on production serving readiness.

Recommended V9 scope:

```text
externalize model registry artifacts for Cloud Run
externalize MLflow/model artifacts for Cloud Run
validate /ready against cloud-accessible model artifacts
validate /predict and /predict/batch live on Cloud Run
decide private/authenticated Cloud Run access
add monitoring, logging, and alerting basics
decide whether Docker Hub fallback remains or is removed
consider Cloud Run rollback automation
consider infrastructure-as-code after the manual flow is well understood
```

## Final V8 Boundary

V8 is closed with a working deployment foundation.

It intentionally stops before production hardening:

```text
no automatic deploy on push
no private Cloud Run auth path
no live prediction readiness
no monitoring or alerting
no Terraform/IaC
no rollback automation
```

Those are later engineering versions.

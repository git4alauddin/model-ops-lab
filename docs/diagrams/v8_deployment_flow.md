# V8 Deployment Flow

This diagram shows the final V8 Dockerization and deployment foundation.

It is intentionally limited to implemented V8 behavior: local Docker serving image, Docker Compose runtime, GitHub Actions manual CI, Docker image publishing, Artifact Registry, Cloud Run deployment, Workload Identity Federation, and rollback/cleanup documentation.

```mermaid
flowchart TD
    developer["Developer"]
    repo["GitHub repository<br/>git4alauddin/model-ops-lab"]

    subgraph local_runtime["Local serving runtime"]
        dockerfile["deployment/Dockerfile"]
        compose["deployment/docker-compose.yaml"]
        env[".env.example<br/>serving runtime config"]
        local_image["modelopslab-serving image"]
        local_api["FastAPI serving API<br/>/health /ready /predict"]
        local_logs["logs/<br/>runtime logs"]
    end

    subgraph github_actions["GitHub Actions manual CI"]
        trigger["workflow_dispatch<br/>manual Run workflow"]
        pytest["pytest gate"]
        docker_build["Docker image build"]
        publish_gate{"Publish image?"}
        deploy_gate{"Deploy Cloud Run?"}
    end

    subgraph registries["Container registries"]
        dockerhub["Docker Hub<br/>fallback publishing path"]
        artifact_registry["Google Artifact Registry<br/>preferred image source"]
    end

    subgraph gcp_auth["Google Cloud authentication"]
        oidc["GitHub OIDC token"]
        wif["Workload Identity Federation<br/>pool + provider"]
        service_account["Cloud Run deployer service account"]
    end

    subgraph cloud_run["Cloud Run deployment"]
        cloud_run_service["modelopslab-serving<br/>Cloud Run service"]
        revision["Cloud Run revision<br/>Git SHA image"]
        health_check["/health validation"]
        rollback_docs["rollback and cleanup guide"]
    end

    developer --> repo
    developer --> dockerfile
    dockerfile --> local_image
    compose --> local_image
    env --> local_api
    local_image --> local_api
    local_api --> local_logs

    repo --> trigger
    trigger --> pytest
    pytest --> docker_build
    docker_build --> publish_gate

    publish_gate -- Docker Hub fallback --> dockerhub
    publish_gate -- Artifact Registry preferred --> artifact_registry

    trigger --> deploy_gate
    deploy_gate -- yes --> oidc
    oidc --> wif
    wif --> service_account
    service_account --> cloud_run_service

    artifact_registry --> revision
    dockerhub -. fallback image source .-> revision
    revision --> cloud_run_service
    cloud_run_service --> health_check
    cloud_run_service --> rollback_docs
```

## Operational Meaning

V8 turns the local FastAPI serving API into a deployable containerized service.

The local path uses `deployment/Dockerfile` and `deployment/docker-compose.yaml` to prove the serving API can run inside Docker with explicit runtime configuration. The CI path uses GitHub Actions with a manual trigger, so deployment remains intentional while the project is still learning production infrastructure.

The preferred final deployment path is:

```text
GitHub Actions manual trigger
-> pytest
-> Docker image build
-> Artifact Registry push
-> Cloud Run deploy from Artifact Registry
-> /health check
```

Workload Identity Federation is the authentication bridge between GitHub Actions and Google Cloud. It avoids long-lived service account keys by allowing GitHub Actions to impersonate the Cloud Run deployer service account through short-lived credentials.

## Current Boundary

V8 is closed as the deployment foundation.

It validates Cloud Run `/health`, but it intentionally stops before production serving hardening:

```text
no automatic deploy on push
no private Cloud Run auth path
no live /ready validation with external model artifacts
no live /predict validation on Cloud Run
no monitoring or alerting
no Terraform/IaC
```

Those concerns move to later versions.

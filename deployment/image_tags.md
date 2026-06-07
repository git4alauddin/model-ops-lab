# Docker Image Tagging Contract

This project uses explicit Docker image tags so builds are traceable and rollback-friendly.

## Image Name

```text
modelopslab-serving
```

## Supported Tags

```text
modelopslab-serving:ci
modelopslab-serving:<git-sha>
modelopslab-serving:vX.Y.Z
modelopslab-serving:latest
```

## Tag Meaning

| Tag | Purpose |
|---|---|
| `ci` | Temporary CI validation tag. Useful for proving the image builds during automated checks. |
| `<git-sha>` | Traceable build tag tied to one exact commit. This is the default rollback-safe tag for CI builds. |
| `vX.Y.Z` | Human-readable release tag. This should be used when creating an intentional release. |
| `latest` | Optional convenience tag. It must never be the only deployed or published tag. |

## CI Rule

CI builds must create at least:

```text
modelopslab-serving:ci
modelopslab-serving:${{ github.sha }}
```

The Git SHA tag gives every CI-built image a direct link back to source code.

## Release Rule

Release builds should use a semantic version tag:

```text
modelopslab-serving:v8.0.0
```

The exact version should match the release decision, not the local development chunk number.

## Rollback Rule

Rollback should target an immutable tag:

```text
modelopslab-serving:<git-sha>
modelopslab-serving:vX.Y.Z
```

Avoid rollback to:

```text
modelopslab-serving:latest
```

`latest` can move over time, so it is weak for auditability and rollback.

## Current Boundary

V8-C6 defines the tagging contract and validates CI image tags.

It does not push images to Docker Hub yet.

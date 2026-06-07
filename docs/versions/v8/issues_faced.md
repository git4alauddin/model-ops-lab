# V8 Issues Faced

## Open
No open V8 issues.

## V8-C1: Docker Serving Image Foundation

### Issue
The V7 serving API worked locally, but it still depended on the developer machine and local virtual environment.

### Resolution
Added a Dockerfile and `.dockerignore` so the serving API has a reproducible image boundary while keeping local runtime state outside the image.

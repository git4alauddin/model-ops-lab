# V7 Lessons

- Serving should start with a stable API boundary before prediction behavior is added.
- Health checks only prove process availability, not model readiness.
- Readiness checks should be added separately once model loading exists.
- Keeping API app creation separate from the Uvicorn entry point makes testing simpler.
- Service identity and API version should be explicit because they will appear in responses, logs, and future monitoring.


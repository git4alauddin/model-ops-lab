"""Serving API entry point for Uvicorn."""

from app.api.app import create_app

app = create_app()


def main() -> None:
    """Run the serving API locally."""
    import uvicorn

    uvicorn.run("app.serve_api:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()

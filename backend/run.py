"""
SAR Multi-Agent Backend — CLI Runner
=====================================
Convenience script to start the uvicorn server with
settings loaded from environment variables.

Usage:
    python run.py
"""

import uvicorn

from app.config import get_settings


def main():
    """Launch the SAR backend server."""
    settings = get_settings()
    print(f"\n Starting {settings.app_name} v{settings.app_version}")
    print(f"   Environment : {settings.app_env}")
    print(f"   Listening on: http://{settings.host}:{settings.port}")
    print(f"   API Docs    : http://localhost:{settings.port}/docs")
    print(f"   Health      : http://localhost:{settings.port}/health\n")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()

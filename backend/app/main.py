"""
SAR Multi-Agent Backend — Application Entry Point
===================================================
Creates and configures the FastAPI application instance.

Run with:
    uvicorn app.main:app --reload

Features:
    • CORS middleware for cross-origin requests
    • Request-scoped correlation IDs (X-Request-ID)
    • Request/response timing (X-Process-Time)
    • Health-check endpoint at GET /health
    • Cache stats at GET /health
    • Pipeline introspection at GET /api/v1/pipeline/info
    • Automatic OpenAPI docs at /docs
    • Startup/shutdown lifecycle hooks
    • Global exception handler for SAR domain errors
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.cache import pipeline_cache
from app.core.exceptions import SARBaseException
from app.core.logger import logger
from app.core.middleware import RequestContextMiddleware
from app.routes.analyze import router as analyze_router
from app.routes.pipeline import router as pipeline_router


# ── Lifecycle ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown hooks."""
    settings = get_settings()
    logger.info(
        "🚀 %s v%s starting (env=%s, debug=%s)",
        settings.app_name,
        settings.app_version,
        settings.app_env,
        settings.debug,
    )
    yield
    # Cleanup on shutdown
    pipeline_cache.clear()
    logger.info("👋 Application shut down gracefully")


# ── App Factory ──────────────────────────────────────────

def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-ready multi-agent backend for Situation Analysis "
            "Reports (SAR).  Orchestrates a pipeline of specialised agents "
            "to transform raw input into actionable intelligence.\n\n"
            "## Pipeline Architecture\n"
            "```\n"
            "InputHandler → Preprocessing → FeatureProcessing → "
            "AnalysisEngine → OutputFormatter\n"
            "```\n\n"
            "## Key Features\n"
            "- 🔗 Sequential agent pipeline with per-agent timing\n"
            "- ⏱  Configurable per-agent timeout enforcement\n"
            "- 🔄 Retry with exponential backoff on transient failures\n"
            "- 📦 In-memory LRU cache with TTL for identical requests\n"
            "- 🆔 Request-scoped correlation IDs (X-Request-ID)\n"
            "- 📊 Pipeline introspection endpoint\n"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware (order matters: last added = first executed) ──
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ───────────────────────────────────────────
    app.include_router(analyze_router, prefix="/api/v1")
    app.include_router(pipeline_router, prefix="/api/v1")

    # ── Health Check ─────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health_check():
        """Lightweight readiness probe with cache statistics."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.app_env,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache": pipeline_cache.stats,
        }

    # ── Root ─────────────────────────────────────────────
    @app.get("/", tags=["System"])
    async def root():
        """API welcome message."""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "pipeline_info": "/api/v1/pipeline/info",
        }

    # ── Global Exception Handler ─────────────────────────
    @app.exception_handler(SARBaseException)
    async def sar_exception_handler(request: Request, exc: SARBaseException):
        """Catch any unhandled SAR-domain exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            "Unhandled SAR exception: %s (request_id=%s)",
            exc.message, request_id,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": exc.message,
                "detail": exc.details,
                "request_id": request_id,
            },
        )

    return app


# Module-level app instance for uvicorn
app = create_app()

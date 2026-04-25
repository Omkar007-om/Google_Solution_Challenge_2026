"""
SAR Multi-Agent Backend — Middleware
=====================================
Custom ASGI middleware for:
    • Request-scoped correlation IDs (X-Request-ID header)
    • Request/response timing (X-Process-Time header)
    • Structured access logging
"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Inject a unique request ID and log every request lifecycle."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── Generate or reuse request ID ─────────────────
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        logger.info(
            "→ %s %s (request_id=%s)",
            request.method,
            request.url.path,
            request_id,
        )

        start = time.perf_counter()
        response = await call_next(request)
        elapsed = round(time.perf_counter() - start, 4)

        # ── Attach tracing headers to response ───────────
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed}s"

        logger.info(
            "← %s %s → %d (%.4fs, request_id=%s)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            request_id,
        )

        return response

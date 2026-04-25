"""
SAR Multi-Agent Backend — Pipeline Service
===========================================
Business-logic layer sitting between routes and orchestrator.
Handles caching, input preparation, and response shaping.

Separation of concerns:
    Route → validates HTTP request
    Service → applies business logic (cache, orchestrator)
    Orchestrator → runs agents
"""

from __future__ import annotations

from app.config import get_settings
from app.core.cache import pipeline_cache, TTLCache
from app.core.logger import logger
from app.core.orchestrator import run_pipeline
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, PipelineMetadata


async def execute_analysis(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the full SAR pipeline, with optional cache look-up.

    Flow:
        1. Compute deterministic cache key from the request payload.
        2. If caching is enabled and a hit is found, return immediately.
        3. Otherwise run the full pipeline and cache the result.
        4. Shape the output into ``AnalyzeResponse``.

    Args:
        request: Validated user request.

    Returns:
        AnalyzeResponse with result and metadata.
    """
    settings = get_settings()

    # ── Cache check ──────────────────────────────────────
    cache_key = TTLCache.make_key(request.model_dump())

    if settings.cache_enabled:
        cached = pipeline_cache.get(cache_key)
        if cached is not None:
            logger.info("⚡ Returning cached pipeline result")
            metadata = PipelineMetadata(**cached["metadata"], cached=True)
            return AnalyzeResponse(
                success=True,
                result=cached["result"],
                metadata=metadata,
            )

    # ── Run pipeline ─────────────────────────────────────
    pipeline_output = await run_pipeline(request.input_data)

    # ── Cache store (raw dicts only, no Pydantic models) ─
    if settings.cache_enabled:
        pipeline_cache.set(cache_key, {
            "result": pipeline_output["result"],
            "metadata": pipeline_output["metadata"],
        })

    # ── Shape response ───────────────────────────────────
    metadata = PipelineMetadata(
        **pipeline_output["metadata"],
        cached=False,
    )
    return AnalyzeResponse(
        success=True,
        result=pipeline_output["result"],
        metadata=metadata,
    )

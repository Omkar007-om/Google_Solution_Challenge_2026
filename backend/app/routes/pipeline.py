"""
SAR Multi-Agent Backend — Pipeline Introspection Route
========================================================
Exposes ``GET /pipeline/info`` for inspecting the current
agent pipeline configuration without executing it.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.orchestrator import get_pipeline_info
from app.models.schemas import PipelineInfo

router = APIRouter(tags=["Pipeline"])


@router.get(
    "/pipeline/info",
    response_model=PipelineInfo,
    summary="Pipeline Configuration",
    description=(
        "Returns metadata about the currently registered agents, "
        "their execution order, retry configuration, and more. "
        "Useful for debugging and monitoring."
    ),
)
async def pipeline_info() -> PipelineInfo:
    """Return the current pipeline configuration."""
    return PipelineInfo(**get_pipeline_info())

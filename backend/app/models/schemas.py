"""
SAR Multi-Agent Backend — Pydantic Schemas
==========================================
Request / response models used by the API layer.
Strict typing ensures self-documenting endpoints and
auto-generated OpenAPI specs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Payload accepted by the ``/analyze`` endpoint.

    Attributes:
        input_data: Arbitrary JSON data to be processed by the pipeline.
        options:    Optional runtime parameters (e.g. flags, overrides).
    """

    input_data: dict[str, Any] = Field(
        ...,
        description="Raw input data to feed into the SAR analysis pipeline.",
        examples=[
            {
                "user_id": "USR-001",
                "transactions": [
                    {"amount": 15000, "type": "wire", "timestamp": "2026-04-25T10:00:00Z"},
                    {"amount": 3200, "type": "deposit", "timestamp": "2026-04-25T11:30:00Z"},
                ],
            }
        ],
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description="Optional runtime parameters passed to agents.",
        examples=[{"verbose": True}],
    )


# ── Response ─────────────────────────────────────────────

class AgentTrace(BaseModel):
    """Execution trace entry for a single agent."""

    step: int
    agent: str
    status: str
    duration_s: float
    error: str | None = None


class PipelineMetadata(BaseModel):
    """Metadata about the pipeline execution."""

    total_duration_s: float
    agents_executed: int
    trace: list[AgentTrace]
    cached: bool = False


class AnalyzeResponse(BaseModel):
    """Structured response returned by the ``/analyze`` endpoint."""

    success: bool = True
    result: Any = Field(
        ...,
        description="Final SAR output produced by the pipeline.",
    )
    metadata: PipelineMetadata


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    success: bool = False
    error: str
    detail: Any | None = None
    request_id: str | None = None


# ── Pipeline Introspection ───────────────────────────────

class AgentInfo(BaseModel):
    """Metadata about a single registered agent."""

    step: int
    name: str

    # Use Field with alias to allow `class` key in JSON
    agent_class: str = Field(..., alias="class")
    retries: int
    retry_delay: float

    model_config = {"populate_by_name": True}


class PipelineInfo(BaseModel):
    """Response for the pipeline introspection endpoint."""

    total_agents: int
    agents: list[AgentInfo]

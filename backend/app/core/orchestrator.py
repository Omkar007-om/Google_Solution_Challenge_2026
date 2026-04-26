"""
SAR Multi-Agent Backend — Pipeline Orchestrator
================================================
The orchestrator is responsible for:
  1. Registering agents in execution order
  2. Running the pipeline sequentially (output_n → input_{n+1})
  3. Collecting per-agent timing & status metadata
  4. Aborting on first failure with full trace context
  5. Providing pipeline introspection metadata

Adding / removing agents is a one-line change in ``AGENT_REGISTRY``.

Architecture:
    ┌──────────┐    ┌──────────────┐    ┌─────────────────┐    ┌────────────────┐    ┌─────────────────┐
    │  Input   │ →  │ Preprocessing│ →  │ Feature         │ →  │ Analysis       │ →  │ Output          │
    │  Handler │    │              │    │ Processing      │    │ Engine         │    │ Formatter       │
    └──────────┘    └──────────────┘    └─────────────────┘    └────────────────┘    └─────────────────┘
"""

from __future__ import annotations

import time
from typing import Any

from app.agents import (
    InputHandlerAgent,
    PreprocessingAgent,
    FeatureProcessingAgent,
    AnalysisEngineAgent,
    OutputFormatterAgent,
    ComplianceOfficerAgent,
    ReviewerAgent,
)
from app.agents.base import BaseAgent
from app.core.exceptions import AgentError, PipelineError
from app.core.logger import logger


# ── Agent Registry ───────────────────────────────────────
# Order matters — agents execute top-to-bottom.
# To add a new agent: instantiate it and insert it at the
# desired position.  To remove one: delete or comment it out.

AGENT_REGISTRY: list[BaseAgent] = [
    InputHandlerAgent(),
    PreprocessingAgent(),
    FeatureProcessingAgent(),
    AnalysisEngineAgent(),
    OutputFormatterAgent(),
    ComplianceOfficerAgent(),
    ReviewerAgent(),
]


def get_pipeline_info() -> dict[str, Any]:
    """Return metadata about the current pipeline configuration.

    Used by the ``/pipeline/info`` introspection endpoint.
    """
    return {
        "total_agents": len(AGENT_REGISTRY),
        "agents": [
            {
                "step": idx,
                "name": agent.name,
                "class": type(agent).__name__,
                "retries": agent.retries,
                "retry_delay": agent.retry_delay,
            }
            for idx, agent in enumerate(AGENT_REGISTRY, start=1)
        ],
    }


async def run_pipeline(raw_input: Any) -> dict[str, Any]:
    """Execute every registered agent sequentially.

    Args:
        raw_input: The unprocessed user payload.

    Returns:
        A dict containing:
            - ``result``:    Final SAR output from the last agent.
            - ``metadata``:  Per-agent execution trace (name, status, time).

    Raises:
        PipelineError: If any agent in the chain fails.
    """
    agent_count = len(AGENT_REGISTRY)
    logger.info("═══ Pipeline started with %d agent(s) ═══", agent_count)
    pipeline_start = time.perf_counter()

    current_data = raw_input
    trace: list[dict[str, Any]] = []

    for idx, agent in enumerate(AGENT_REGISTRY, start=1):
        step_start = time.perf_counter()

        try:
            current_data = await agent.execute(current_data)
            step_elapsed = round(time.perf_counter() - step_start, 4)
            trace.append({
                "step": idx,
                "agent": agent.name,
                "status": "success",
                "duration_s": step_elapsed,
            })

        except AgentError as exc:
            step_elapsed = round(time.perf_counter() - step_start, 4)
            trace.append({
                "step": idx,
                "agent": agent.name,
                "status": "failed",
                "duration_s": step_elapsed,
                "error": exc.message,
            })
            logger.error(
                "═══ Pipeline ABORTED at step %d/%d [%s] ═══",
                idx, agent_count, agent.name,
            )
            raise PipelineError(
                message=f"Pipeline failed at step {idx}/{agent_count} ({agent.name})",
                failed_agent=agent.name,
                details={"trace": trace, "error": exc.message},
            ) from exc

    total_elapsed = round(time.perf_counter() - pipeline_start, 4)
    logger.info("═══ Pipeline completed in %.4fs ═══", total_elapsed)

    return {
        "result": current_data,
        "metadata": {
            "total_duration_s": total_elapsed,
            "agents_executed": len(trace),
            "trace": trace,
        },
    }

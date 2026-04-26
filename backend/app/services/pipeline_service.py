"""
Nexus 2.0 — Pipeline Service
=============================
Business-logic layer for the Lightweight Sequential State pattern.
Handles caching, audit logging, and response shaping.
"""

from __future__ import annotations

from app.config import get_settings
from app.core.cache import pipeline_cache, TTLCache
from app.core.database import save_audit_log
from app.core.logger import logger
from app.core.orchestrator import run_pipeline
from app.core.state import NexusState
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, PipelineMetadata


async def execute_analysis(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the SAR pipeline with glass-box audit trail.

    Returns:
        AnalyzeResponse with result, metadata, and equilibrium_audit_log.
    """
    settings = get_settings()

    # ── Cache check ──────────────────────────────────────
    cache_key = TTLCache.make_key(request.model_dump())

    if settings.cache_enabled:
        cached = pipeline_cache.get(cache_key)
        if cached is not None:
            logger.info("⚡ Returning cached pipeline result")
            metadata = PipelineMetadata(
                total_duration_s=cached["metadata"].get("total_duration_s", 0),
                agents_executed=cached["metadata"].get("agents_executed", 0),
                trace=cached["metadata"].get("trace", []),
                cached=True,
            )
            return AnalyzeResponse(
                success=True,
                result=cached["result"],
                metadata=metadata,
                audit_log=cached.get("audit_log", []),
            )

    # ── Run pipeline ─────────────────────────────────────
    final_state: NexusState = await run_pipeline(request.input_data)

    # ── Extract result ────────────────────────────────────
    result = final_state.get("draft_sar") or final_state.get("risk_findings") or {}
    audit_log = final_state.get("equilibrium_audit_log", [])
    meta = final_state.get("metadata", {})
    case_id = result.get("report_id", "unknown") if isinstance(result, dict) else "unknown"

    # ── Persist audit log to PostgreSQL (Layer 4: Audit Brain) ─
    try:
        shap = result.get("risk_assessment", {}).get("shap_explanation") if isinstance(result, dict) else None
        await save_audit_log(
            case_id=case_id,
            pipeline_version=meta.get("pipeline_version", "2.0.0"),
            audit_entries=audit_log,
            shap_explanation=shap,
        )
    except Exception as exc:
        logger.warning("Failed to persist audit log: %s", str(exc))

    # ── Cache store ──────────────────────────────────────
    if settings.cache_enabled:
        pipeline_cache.set(cache_key, {
            "result": result,
            "metadata": {
                "total_duration_s": meta.get("total_duration_s", 0),
                "agents_executed": len(audit_log),
                "trace": [{"step": i+1, "agent": e["agent"], "status": "success", "duration_s": 0.0} for i, e in enumerate(audit_log)],
            },
            "audit_log": audit_log,
        })

    # ── Shape response ───────────────────────────────────
    metadata = PipelineMetadata(
        total_duration_s=meta.get("total_duration_s", 0),
        agents_executed=len(audit_log),
        trace=[{"step": i+1, "agent": e["agent"], "status": "success", "duration_s": 0.0} for i, e in enumerate(audit_log)],
        cached=False,
    )
    return AnalyzeResponse(
        success=True,
        result=result,
        metadata=metadata,
        audit_log=audit_log,
    )

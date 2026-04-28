"""
Nexus 2.0 — Lightweight Sequential State Orchestrator
========================================================
Pure functional state-passing pipeline using TypedDict.
No LangGraph — fast, explicit, fully auditable.

Architecture (matches handwritten 5-layer diagram):
    ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Data    │ →  │   Privacy    │ →  │    Triage    │ →  │     Risk     │ →  │     SAR      │
    │ Ingestor │    │    Guard     │    │   Firewall   │    │   Analyzer   │    │   Drafter    │
    └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
         │               │                   │                   │                   │
         └───────────────┴───────────────────┴───────────────────┴───────────────────┘
                                      ↓
                         equilibrium_audit_log (Glass-Box Trail)
"""

from __future__ import annotations

import time
from typing import Any

from app.agents.stateful_agents import (
    data_ingestor,
    privacy_guard,
    triage_firewall,
    risk_analyzer,
    sar_drafter,
    deanonymizer,
)
from app.core.state import NexusState, init_state
from app.core.exceptions import PipelineError
from app.core.logger import logger


FUNCTIONAL_AGENTS = [
    ("ingestion", data_ingestor),
    ("privacy", privacy_guard),
    ("triage", triage_firewall),
]


def get_pipeline_info() -> dict[str, Any]:
    """Return metadata about the current functional pipeline configuration."""
    return {
        "total_agents": len(FUNCTIONAL_AGENTS) + 2,
        "agents": [
            {"step": idx, "name": name, "class": "FunctionalStateAgent", "retries": 0, "retry_delay": 0.5}
            for idx, (name, _) in enumerate(FUNCTIONAL_AGENTS, start=1)
        ] + [
            {"step": 4, "name": "risk_analyzer", "class": "FunctionalStateAgent", "retries": 0, "retry_delay": 0.5},
            {"step": 5, "name": "sar_drafter", "class": "FunctionalStateAgent", "retries": 0, "retry_delay": 0.5},
        ],
        "pattern": "lightweight_sequential_state",
        "version": "2.0.0",
    }


async def run_pipeline(raw_input: dict[str, Any]) -> NexusState:
    """Execute functional agents sequentially with state passing.

    Args:
        raw_input: The unprocessed user payload with transactions.

    Returns:
        NexusState containing draft_sar, audit_log, and all intermediate state.

    Raises:
        PipelineError: If any agent in the chain fails.
    """
    logger.info("═══ Nexus 2.0 Pipeline Started (Lightweight State Pattern) ═══")
    pipeline_start = time.perf_counter()

    # Initialize state
    state = init_state(raw_input)

    try:
        # Core pipeline (always runs)
        for step_name, agent_fn in FUNCTIONAL_AGENTS:
            step_start = time.perf_counter()
            state = await agent_fn(state)
            elapsed = round(time.perf_counter() - step_start, 4)
            logger.info("✔  [%s] completed in %.4fs", step_name, elapsed)

        # Conditional branch based on triage
        triage_rec = state["triage_score"]["recommendation"]

        if triage_rec == "SKIP":
            logger.info("⚡ Triage recommends SKIP — bypassing heavy analysis")
            risk = {"score": 0, "level": "LOW", "factors": [], "shap_explanation": {}}
            
            state["risk_findings"] = {
                "features": {},
                "risk": risk,
                "reasoning": {
                    "summary": "Low risk signals — triage firewall recommended skipping full analysis.",
                    "recommended_action": "No SAR required",
                },
            }
            
            import datetime
            txns = state["masked_data"].get("transactions", [])
            
            # Populate dummy timeline and suspicious activity so frontend tabs show data
            timeline_data = [
                {
                    "timestamp": t.get("timestamp"),
                    "transaction_id": t.get("transaction_id"),
                    "headline": f"{t.get('transaction_id')}: Reviewed (Low Risk)",
                    "amount": t.get("amount")
                }
                for t in txns[:10]
            ]
            
            flags_data = [
                {
                    "transaction_id": t.get("transaction_id"),
                    "typology": "none",
                    "reason": "Normal transaction behavior",
                    "amount": t.get("amount"),
                    "from_account": t.get("from_account"),
                    "to_account": t.get("to_account"),
                    "location": t.get("location"),
                    "timestamp": t.get("timestamp")
                }
                for t in txns[:5]
            ]
            
            state["draft_sar"] = {
                "report_id": f"NO-SAR-{state['masked_data']['user_id']}",
                "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "user_id": state["masked_data"]["user_id"],
                "subject_information": {
                    "subject_account": state["masked_data"]["user_id"],
                    "total_transactions_reviewed": len(txns),
                    "total_amount_reviewed": sum(t.get("amount", 0) for t in txns),
                    "risk_level": "LOW",
                    "risk_score": 0,
                },
                "risk_assessment": state["risk_findings"]["risk"],
                "investigator_reasoning": state["risk_findings"]["reasoning"],
                "rag_context": [
                    {
                        "id": "SYS-MSG",
                        "title": "Low Risk Profile",
                        "content": "No specific AML guidance retrieved because the transaction profile did not trigger any high-risk typologies. Standard monitoring applies."
                    }
                ],
                "triage_result": state["triage_score"],
                "llm_narrative": "Triage recommended SKIP. No suspicious activity narrative generated because transactions exhibit normal behavior.",
                "suspicious_activity": flags_data,
                "timeline": timeline_data,
                "status": "No SAR Required"
            }
        else:
            # Full analysis for FAST and FULL recommendations
            step_start = time.perf_counter()
            state = await risk_analyzer(state)
            logger.info("✔  [risk_analyzer] completed in %.4fs", round(time.perf_counter() - step_start, 4))

            step_start = time.perf_counter()
            state = await sar_drafter(state)
            logger.info("✔  [sar_drafter] completed in %.4fs", round(time.perf_counter() - step_start, 4))

        # Deanonymize before returning
        step_start = time.perf_counter()
        state = await deanonymizer(state)
        logger.info("✔  [deanonymizer] completed in %.4fs", round(time.perf_counter() - step_start, 4))

    except Exception as exc:
        logger.error("═══ Pipeline ABORTED ═══")
        raise PipelineError(
            message=f"Pipeline failed: {str(exc)}",
            failed_agent="unknown",
            details={"error": str(exc), "audit_log": state.get("equilibrium_audit_log", [])},
        ) from exc

    total_elapsed = round(time.perf_counter() - pipeline_start, 4)
    logger.info("═══ Pipeline completed in %.4fs ═══", total_elapsed)

    # Add timing metadata
    state["metadata"]["total_duration_s"] = total_elapsed
    state["metadata"]["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    return state

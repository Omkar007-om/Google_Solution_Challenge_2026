"""
Nexus 2.0 — Lightweight Sequential State Pattern
================================================
Pure Python TypedDict state for agent pipeline.
No LangGraph dependency — fast, explicit, auditable.
"""

from __future__ import annotations

from typing import Any, TypedDict
from datetime import datetime


class AuditEntry(TypedDict):
    """Single entry in the glass-box audit trail."""

    step: str
    agent: str
    timestamp: str
    action: str
    evidence: list[str]
    shap_values: dict[str, Any] | None


class TriageScore(TypedDict):
    """Triage firewall scoring output."""

    severity_score: float
    rule_based_score: float
    anomaly_score: float
    typologies_detected: list[str]
    recommendation: str


class NexusState(TypedDict, total=False):
    """Pipeline state passed sequentially through agents.

    Each agent receives the state, updates its section,
    appends to equilibrium_audit_log, and returns the state.
    """

    raw_data: dict[str, Any]
    masked_data: dict[str, Any]
    triage_score: TriageScore
    risk_findings: dict[str, Any]
    draft_sar: dict[str, Any]
    equilibrium_audit_log: list[AuditEntry]
    metadata: dict[str, Any]


def init_state(raw_input: dict[str, Any]) -> NexusState:
    """Initialize fresh pipeline state."""
    return {
        "raw_data": raw_input,
        "equilibrium_audit_log": [],
        "metadata": {
            "pipeline_version": "2.0.0",
            "started_at": datetime.utcnow().isoformat(),
        },
    }


def append_audit(
    state: NexusState,
    step: str,
    agent: str,
    action: str,
    evidence: list[str],
    shap_values: dict[str, Any] | None = None,
) -> NexusState:
    """Append entry to audit log and return state."""
    entry: AuditEntry = {
        "step": step,
        "agent": agent,
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "evidence": evidence,
        "shap_values": shap_values,
    }
    state["equilibrium_audit_log"].append(entry)
    return state

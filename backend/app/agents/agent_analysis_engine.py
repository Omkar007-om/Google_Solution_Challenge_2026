"""
SAR Multi-Agent Backend — Analysis Engine Agent
=================================================
Pipeline Step 4: Performs rule-based risk scoring.

Evaluates statistical features and produces a risk assessment
with score (0–100), level (LOW / MEDIUM / HIGH / CRITICAL),
and contributing factors.
"""

from __future__ import annotations

from typing import Dict, List

from app.agents.base import BaseAgent


class AnalysisEngineAgent(BaseAgent):
    """Score risk level based on extracted features."""

    name = "AnalysisEngine"

    async def process(self, data: Dict) -> Dict:
        features = data.get("features", {})

        risk_score = 0
        factors: List[str] = []

        # ── Rule-based scoring ───────────────────────────
        if features.get("total_amount", 0) > 50_000:
            risk_score += 30
            factors.append("High cumulative transaction volume")

        if features.get("high_value_count", 0) > 3:
            risk_score += 25
            factors.append("Multiple high-value transactions")

        if features.get("avg_amount", 0) > 10_000:
            risk_score += 20
            factors.append("Elevated average transaction size")

        if features.get("max_amount", 0) > 50_000:
            risk_score += 15
            factors.append("Single very-high-value transaction")

        if features.get("total_transactions", 0) > 50:
            risk_score += 10
            factors.append("Large number of transactions")

        # Cap at 100
        risk_score = min(risk_score, 100)

        # ── Determine risk level ─────────────────────────
        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        data["analysis"] = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "contributing_factors": factors,
        }

        return data

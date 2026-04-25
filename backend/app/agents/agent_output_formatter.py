"""
SAR Multi-Agent Backend — Output Formatter Agent
==================================================
Pipeline Step 5 (final): Shapes the enriched data into the
canonical SAR report structure returned to the client.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from app.agents.base import BaseAgent


class OutputFormatterAgent(BaseAgent):
    """Format pipeline output into the final SAR report."""

    name = "OutputFormatter"

    async def process(self, data: Dict) -> Dict:
        features = data.get("features", {})
        analysis = data.get("analysis", {})

        return {
            "report_id": f"SAR-{data.get('user_id', 'unknown')}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "user_id": data.get("user_id"),
            "summary": {
                "total_transactions": features.get("total_transactions", 0),
                "total_amount": features.get("total_amount", 0),
                "avg_amount": features.get("avg_amount", 0),
                "max_amount": features.get("max_amount", 0),
                "min_amount": features.get("min_amount", 0),
                "high_value_count": features.get("high_value_count", 0),
            },
            "risk_assessment": {
                "score": analysis.get("risk_score", 0),
                "level": analysis.get("risk_level", "UNKNOWN"),
                "contributing_factors": analysis.get("contributing_factors", []),
            },
            "metadata": data.get("metadata", {}),
            "status": "SAR Generated",
        }

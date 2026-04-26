"""Pipeline Step 4: explain the suspicious behavior in plain English."""

from __future__ import annotations

from typing import Dict

from app.agents.base import BaseAgent
from app.utils.rag import retrieve_aml_context


class AnalysisEngineAgent(BaseAgent):
    """Build investigation reasoning from detected flags."""

    name = "Investigator"

    async def process(self, data: Dict) -> Dict:
        flags = data.get("analysis", {}).get("flags", [])
        risk = data.get("risk", {})
        typologies = data.get("analysis", {}).get("typologies", [])
        query = " ".join([
            "AML SAR suspicious activity",
            " ".join(typologies),
            " ".join(flag.get("reason", "") for flag in flags),
        ])
        retrieved_context = retrieve_aml_context(query=query, tags=typologies, top_k=4)

        if flags:
            primary = flags[0]
            summary = (
                f"The reviewed activity for {data.get('user_id')} shows {len(flags)} "
                f"risk indicator(s), led by {primary['typology'].replace('_', ' ')}. "
                f"The pattern is assessed as {risk.get('level', 'UNKNOWN')} risk."
            )
        else:
            summary = (
                f"The reviewed activity for {data.get('user_id')} does not show "
                "material suspicious indicators under the configured rules."
            )

        data["reasoning"] = {
            "summary": summary,
            "key_observations": [
                f"{flag['transaction_id']}: {flag['reason']} ({flag['location']}, amount {flag['amount']:,.2f})"
                for flag in flags[:10]
            ],
            "rag_context": retrieved_context,
            "grounded_rationale": [
                f"{item['title']}: {item['content']}"
                for item in retrieved_context[:3]
            ],
            "recommended_action": "File SAR" if risk.get("score", 0) >= 60 else "Review internally",
        }

        return data

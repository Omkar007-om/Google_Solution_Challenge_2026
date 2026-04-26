"""Pipeline Step 6: validate SAR completeness before final review."""

from __future__ import annotations

from typing import Dict

from app.agents.base import BaseAgent


class ComplianceOfficerAgent(BaseAgent):
    """Check the draft report for minimum compliance-ready fields."""

    name = "Compliance Officer"

    async def process(self, data: Dict) -> Dict:
        draft = data.get("sar_draft", {})
        rag_context = draft.get("rag_context", [])
        missing = []
        for field in ("report_id", "generated_at", "user_id", "summary", "risk_assessment", "formatted_report"):
            if not draft.get(field):
                missing.append(field)

        risk_score = draft.get("risk_assessment", {}).get("score", 0)
        filing_recommended = risk_score >= 60 and not missing

        data["compliance"] = {
            "valid": not missing,
            "missing_fields": missing,
            "filing_recommended": filing_recommended,
            "rag_supported": bool(rag_context),
            "rag_sources_checked": [
                item.get("id")
                for item in rag_context
                if isinstance(item, dict) and item.get("id")
            ],
            "notes": (
                "SAR draft contains the core narrative, subject, risk, evidence fields, and retrieved AML guidance."
                if not missing else
                f"SAR draft is missing: {', '.join(missing)}"
            ),
        }
        return data

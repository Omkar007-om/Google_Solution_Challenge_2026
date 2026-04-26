"""Pipeline Step 7: issue final reviewer decision and response payload."""

from __future__ import annotations

from typing import Dict

from app.agents.base import BaseAgent


class ReviewerAgent(BaseAgent):
    """Finalize the SAR output for API clients."""

    name = "Reviewer"

    async def process(self, data: Dict) -> Dict:
        draft = data.get("sar_draft", {})
        compliance = data.get("compliance", {})
        risk = draft.get("risk_assessment", {})

        if compliance.get("filing_recommended"):
            decision = "APPROVED_FOR_SAR_FILING"
            reviewer_note = "The activity is sufficiently suspicious and the SAR draft is complete."
        elif risk.get("score", 0) >= 30:
            decision = "ESCALATE_FOR_MANUAL_REVIEW"
            reviewer_note = "Some indicators are present, but the case should be reviewed before filing."
        else:
            decision = "NO_SAR_REQUIRED"
            reviewer_note = "The reviewed activity does not currently justify SAR filing."

        return {
            **draft,
            "compliance_validation": compliance,
            "review_decision": {
                "decision": decision,
                "reviewer_note": reviewer_note,
            },
            "agent_sequence": [
                "Input Processor",
                "Risk Analyst",
                "Risk Enrichment",
                "Investigator",
                "SAR Writer",
                "Compliance Officer",
                "Reviewer",
            ],
            "status": "SAR Report Finalized",
        }

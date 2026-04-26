"""Pipeline Step 5: draft a human-readable SAR report."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from app.agents.base import BaseAgent


class OutputFormatterAgent(BaseAgent):
    """Draft a formatted SAR report while preserving structured data."""

    name = "SAR Writer"

    async def process(self, data: Dict) -> Dict:
        features = data.get("features", {})
        risk = data.get("risk", {})
        reasoning = data.get("reasoning", {})
        analysis = data.get("analysis", {})
        flags = analysis.get("flags", [])
        timeline = _build_timeline(flags)
        report_id = f"SAR-{data.get('user_id', 'unknown')}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        data["sar_draft"] = {
            "report_id": report_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "user_id": data.get("user_id"),
            "subject_information": {
                "subject_account": data.get("user_id"),
                "review_period": {
                    "start": analysis.get("period", {}).get("start"),
                    "end": analysis.get("period", {}).get("end"),
                },
                "total_transactions_reviewed": features.get("total_transactions", 0),
                "total_amount_reviewed": features.get("total_amount", 0),
                "high_value_transactions": features.get("high_value_count", 0),
                "risk_level": risk.get("level", "UNKNOWN"),
                "risk_score": risk.get("score", 0),
            },
            "summary": {
                "total_transactions": features.get("total_transactions", 0),
                "total_amount": features.get("total_amount", 0),
                "avg_amount": features.get("avg_amount", 0),
                "max_amount": features.get("max_amount", 0),
                "min_amount": features.get("min_amount", 0),
                "high_value_count": features.get("high_value_count", 0),
                "flagged_transactions": features.get("flagged_transactions", 0),
            },
            "risk_assessment": {
                "score": risk.get("score", 0),
                "level": risk.get("level", "UNKNOWN"),
                "contributing_factors": risk.get("factors", []),
                "shap_explanation": risk.get("shap_explanation", {}),
            },
            "timeline": timeline,
            "suspicious_activity": flags,
            "investigator_reasoning": reasoning,
            "rag_context": reasoning.get("rag_context", []),
            "formatted_report": _build_report(report_id, data, features, risk, reasoning),
            "metadata": data.get("metadata", {}),
            "status": "Draft SAR Generated",
        }
        return data


def _build_report(report_id: str, data: Dict, features: Dict, risk: Dict, reasoning: Dict) -> str:
    flags = data.get("analysis", {}).get("flags", [])
    period = data.get("analysis", {}).get("period", {})
    factors = risk.get("factors", [])
    shap_explanation = risk.get("shap_explanation", {})
    shap_drivers = shap_explanation.get("top_drivers", [])
    rag_context = reasoning.get("rag_context", [])

    evidence_lines = [
        f"- {flag['transaction_id']}: {flag['reason']} | Amount: {flag['amount']:,.2f} | "
        f"From: {flag['from_account']} | To: {flag['to_account']} | Location: {flag['location']}"
        for flag in flags[:12]
    ] or ["- No transaction-level suspicious indicators were detected by the configured rules."]

    factor_lines = [f"- {factor}" for factor in factors] or ["- No material contributing factors detected."]
    shap_lines = [
        f"- {driver['display_name']}: +{driver['shap_value']} risk points "
        f"({driver['impact_pct']}% impact). {driver['reason']}"
        for driver in shap_drivers
    ] or ["- No positive risk drivers were available for SHAP attribution."]
    rag_lines = [
        f"- [{item.get('id', 'UNKNOWN')}] {item.get('title', 'Untitled guidance')}: {item.get('content', '')}"
        for item in rag_context
        if isinstance(item, dict) and item.get("content")
    ] or ["- No RAG knowledge snippets were retrieved for this case."]

    timeline_lines = [
        f"- {item['timestamp']}: {item['headline']}"
        for item in _build_timeline(flags)[:8]
    ] or ["- No suspicious events available for timeline."]

    return "\n".join([
        "SUSPICIOUS ACTIVITY REPORT",
        f"Report ID: {report_id}",
        f"Subject Account: {data.get('user_id')}",
        f"Review Period: {period.get('start') or 'Not available'} to {period.get('end') or 'Not available'}",
        "",
        "Subject Information",
        f"- Subject account: {data.get('user_id')}",
        f"- Transactions reviewed: {features.get('total_transactions', 0)}",
        f"- Total reviewed value: {features.get('total_amount', 0):,.2f}",
        f"- Risk profile: {risk.get('level', 'UNKNOWN')} ({risk.get('score', 0)}/100)",
        "",
        "Executive Summary",
        reasoning.get("summary", "No narrative summary available."),
        "",
        "Timeline of Material Events",
        *timeline_lines,
        "",
        "Retrieved AML Guidance",
        *rag_lines,
        "",
        "Transaction Profile",
        f"- Total transactions reviewed: {features.get('total_transactions', 0)}",
        f"- Total value reviewed: {features.get('total_amount', 0):,.2f}",
        f"- Average transaction value: {features.get('avg_amount', 0):,.2f}",
        f"- Highest transaction value: {features.get('max_amount', 0):,.2f}",
        "",
        "Risk Assessment",
        f"- Risk level: {risk.get('level', 'UNKNOWN')}",
        f"- Risk score: {risk.get('score', 0)}/100",
        *factor_lines,
        "",
        "SHAP Explainability",
        f"- Method: {shap_explanation.get('method', 'Not available')}",
        f"- Base value: {shap_explanation.get('base_value', 0)}",
        f"- Raw score before cap: {shap_explanation.get('raw_score_before_cap', risk.get('score', 0))}",
        *shap_lines,
        "",
        "Suspicious Activity Narrative",
        (
            "The activity appears inconsistent with ordinary transactional behavior because "
            "the reviewed file contains indicators commonly associated with layering, "
            "structuring, offshore movement, or unexplained high-value activity."
            if flags else
            "The activity does not currently meet the configured threshold for SAR filing, "
            "but it may be retained for internal monitoring."
        ),
        "",
        "Key Evidence",
        *evidence_lines,
        "",
        "Recommended Action",
        reasoning.get("recommended_action", "Review internally"),
    ])


def _build_timeline(flags: list[Dict]) -> list[Dict]:
    sorted_flags = sorted(flags, key=lambda f: str(f.get("timestamp") or ""))
    timeline = []
    for flag in sorted_flags:
        timeline.append({
            "timestamp": flag.get("timestamp"),
            "transaction_id": flag.get("transaction_id"),
            "headline": (
                f"{flag.get('transaction_id')}: "
                f"{flag.get('typology', 'suspicious_activity').replace('_', ' ')} - "
                f"{flag.get('reason', 'Suspicious behavior detected')}"
            ),
            "amount": flag.get("amount"),
            "location": flag.get("location"),
        })
    return timeline

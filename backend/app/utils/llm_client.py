"""
Nexus 2.0 — Layer 3: Narrative Engine (LLM API Client)
=====================================================
Async HTTP client for SAR narrative generation via LLM API.
Compatible with OpenAI, Azure OpenAI, and compatible endpoints.
"""

from __future__ import annotations

import httpx
from typing import Any

from app.config import get_settings
from app.core.logger import logger


async def generate_sar_narrative(
    subject_id: str,
    risk_level: str,
    risk_score: int,
    typologies: list[str],
    flags: list[dict],
    rag_context: list[dict],
) -> str:
    """Generate human-readable SAR narrative via LLM API.
    
    Args:
        subject_id: Subject account identifier
        risk_level: CRITICAL/HIGH/MEDIUM/LOW
        risk_score: Numeric risk score (0-100)
        typologies: Detected AML typologies
        flags: List of flagged transactions with reasons
        rag_context: Retrieved AML guidance context
        
    Returns:
        Generated SAR narrative text
    """
    settings = get_settings()
    
    if not settings.llm_enabled or not settings.llm_api_key:
        logger.warning("LLM not configured — returning fallback narrative")
        return _fallback_narrative(subject_id, risk_level, risk_score, typologies, flags)
    
    # Build prompt
    prompt = _build_prompt(subject_id, risk_level, risk_score, typologies, flags, rag_context)
    
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{settings.llm_api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert AML compliance analyst drafting Suspicious Activity Reports (SAR). "
                                "Write professional, factual narratives suitable for regulatory filing. "
                                "Be concise but thorough. Cite specific evidence. Avoid speculation."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": settings.llm_temperature,
                    "max_tokens": settings.llm_max_tokens,
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            narrative = data["choices"][0]["message"]["content"].strip()
            logger.info("LLM generated narrative (%d chars)", len(narrative))
            return narrative
            
    except httpx.TimeoutException:
        logger.error("LLM API timeout")
        return _fallback_narrative(subject_id, risk_level, risk_score, typologies, flags)
    except httpx.HTTPStatusError as exc:
        logger.error("LLM API error: %s", exc.response.text)
        return _fallback_narrative(subject_id, risk_level, risk_score, typologies, flags)
    except Exception as exc:
        logger.error("LLM call failed: %s", str(exc))
        return _fallback_narrative(subject_id, risk_level, risk_score, typologies, flags)


def _build_prompt(
    subject_id: str,
    risk_level: str,
    risk_score: int,
    typologies: list[str],
    flags: list[dict],
    rag_context: list[dict],
) -> str:
    """Build the prompt for LLM SAR generation."""
    
    # Format flags
    flag_lines = []
    for f in flags[:10]:
        flag_lines.append(
            f"- {f['transaction_id']}: {f['typology']} — {f['reason']} "
            f"(Amount: {f.get('amount', 'N/A')}, Location: {f.get('location', 'N/A')})"
        )
    flags_text = "\n".join(flag_lines) if flag_lines else "No specific transaction flags."
    
    # Format RAG context
    rag_lines = []
    for ctx in rag_context[:5]:
        rag_lines.append(f"- {ctx.get('title', 'Guidance')}: {ctx.get('content', '')[:200]}")
    rag_text = "\n".join(rag_lines) if rag_lines else "No additional AML guidance retrieved."
    
    return f"""Draft a Suspicious Activity Report (SAR) narrative for the following case:

**SUBJECT**: {subject_id}
**RISK ASSESSMENT**: {risk_level} ({risk_score}/100)
**DETECTED TYPOLOGIES**: {', '.join(typologies) if typologies else 'None'}

**FLAGGED TRANSACTIONS**:
{flags_text}

**RELEVANT AML GUIDANCE**:
{rag_text}

**INSTRUCTIONS**:
1. Write an executive summary of the suspicious activity
2. Describe the pattern of behavior observed
3. Reference specific transactions as evidence
4. Explain why this is inconsistent with normal activity
5. Conclude with the recommended action

Keep the narrative professional, factual, and suitable for regulatory filing."""


def _fallback_narrative(
    subject_id: str,
    risk_level: str,
    risk_score: int,
    typologies: list[str],
    flags: list[dict],
) -> str:
    """Generate fallback narrative when LLM is unavailable."""
    
    typology_text = ', '.join(typologies) if typologies else 'no specific typologies'
    
    evidence_summary = []
    for f in flags[:5]:
        evidence_summary.append(
            f"{f['transaction_id']} ({f['typology']}: {f['reason']})"
        )
    
    evidence_text = '; '.join(evidence_summary) if evidence_summary else 'No flagged transactions'
    
    return f"""SUSPICIOUS ACTIVITY NARRATIVE

Subject: {subject_id}
Risk Level: {risk_level} ({risk_score}/100)

SUMMARY
The reviewed activity for {subject_id} exhibits characteristics associated with {typology_text}. 

KEY EVIDENCE
{evidence_text}

ANALYSIS
Based on the transaction patterns and detected risk indicators, this activity warrants 
regulatory reporting under applicable AML regulations.

RECOMMENDED ACTION
{'File SAR immediately' if risk_score >= 60 else 'Review internally before filing'}

---
[Auto-generated fallback narrative — LLM unavailable]"""

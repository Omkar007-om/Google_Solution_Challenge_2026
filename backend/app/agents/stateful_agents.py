"""
Nexus 2.0 — Functional State-Passing Agents
============================================
Pure async functions accepting and returning NexusState.
Each agent appends {"step": "...", "action": "...", "evidence": "..."} to audit log.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from app.core.state import NexusState, append_audit, TriageScore
from app.utils.llm_client import generate_sar_narrative
from app.utils.shap_explainer import explain_risk_score
from app.utils.rag import retrieve_aml_context


async def data_ingestor(state: NexusState) -> NexusState:
    """Pipeline Step 1: Normalize raw transactions."""
    data = state["raw_data"]
    transactions = data.get("transactions") or data.get("raw_transactions")

    if not isinstance(transactions, list) or not transactions:
        raise ValueError("Input must contain a non-empty transactions list")

    cleaned: list[dict[str, Any]] = []
    for index, row in enumerate(transactions, start=1):
        if not isinstance(row, dict):
            continue
        amount = _parse_amount(_pick(row, "amount", "amt", "transaction_amount", "value"))
        if amount is None:
            continue

        timestamp = _pick(row, "timestamp", "time", "date", "datetime", "transaction_time")
        from_account = _pick(row, "from_account", "from_acc", "sender", "source", "debit_account", "account")
        to_account = _pick(row, "to_account", "to_acc", "receiver", "destination", "credit_account", "counterparty")

        cleaned.append({
            "transaction_id": str(_pick(row, "transaction_id", "txn_id", "id") or f"ROW-{index:04d}"),
            "timestamp": _normalize_timestamp(timestamp),
            "amount": amount,
            "currency": str(_pick(row, "currency") or data.get("currency") or "INR"),
            "from_account": str(from_account or "UNKNOWN"),
            "to_account": str(to_account or "UNKNOWN"),
            "location": str(_pick(row, "location", "country", "city") or "Unknown"),
            "type": str(_pick(row, "type", "transaction_type", "channel") or "unknown").lower(),
            "note": str(_pick(row, "note", "remarks", "description", "purpose") or "").strip(),
            "raw": row,
        })

    subject_account = data.get("user_id") or data.get("subject_account")
    if not subject_account:
        accounts = [txn["from_account"] for txn in cleaned if txn["from_account"] != "UNKNOWN"]
        subject_account = Counter(accounts).most_common(1)[0][0] if accounts else "UNKNOWN"

    state["masked_data"] = {
        "user_id": str(subject_account),
        "transactions": cleaned,
        "metadata": {
            **data.get("metadata", {}),
            "input_rows": len(transactions),
            "valid_rows": len(cleaned),
        },
    }

    evidence = [txn["transaction_id"] for txn in cleaned]
    return append_audit(
        state,
        step="ingestion",
        agent="data_ingestor",
        action=f"normalized {len(cleaned)} transactions from {len(transactions)} input rows",
        evidence=evidence,
    )


async def privacy_guard(state: NexusState) -> NexusState:
    """Pipeline Step 2: Mask PII before analysis."""
    data = state["masked_data"]
    transactions = data.get("transactions", [])

    masking_map: dict[str, str] = {}
    masked_transactions: list[dict[str, Any]] = []

    for txn in transactions:
        masked_txn = txn.copy()
        for field in ["from_account", "to_account"]:
            original = str(txn.get(field, ""))
            if original and original != "UNKNOWN" and original not in masking_map:
                token = f"ACCT-{len(masking_map)+1:04d}"
                masking_map[original] = token
            masked_txn[field] = masking_map.get(original, original)
        masked_transactions.append(masked_txn)

    state["masked_data"]["transactions"] = masked_transactions
    state["masked_data"]["_masking_map"] = masking_map
    state["masked_data"]["_privacy_applied"] = True

    evidence = [f"masked_{len(masking_map)}_accounts"]
    return append_audit(
        state,
        step="privacy",
        agent="privacy_guard",
        action=f"masked {len(masking_map)} unique account identifiers",
        evidence=evidence,
    )


async def triage_firewall(state: NexusState) -> NexusState:
    """Pipeline Step 3: Pre-filter alert severity before heavy LLM."""
    transactions = state["masked_data"].get("transactions", [])

    high_value_threshold = 1_000_000
    structuring_floor = 40_000
    structuring_ceiling = 50_000
    offshore_terms = {"cayman", "dubai", "uae", "panama", "mauritius", "singapore", "hong kong", "switzerland", "bvi", "british virgin"}

    rule_hits = 0
    typologies: list[str] = []

    for txn in transactions:
        if txn["amount"] >= high_value_threshold:
            rule_hits += 1
            if "large_anomaly" not in typologies:
                typologies.append("large_anomaly")
        location = txn["location"].lower()
        if any(term in location for term in offshore_terms):
            rule_hits += 1
            if "offshore_exposure" not in typologies:
                typologies.append("offshore_exposure")

    by_sender: dict[str, list[dict]] = {}
    for txn in transactions:
        if structuring_floor <= txn["amount"] <= structuring_ceiling:
            by_sender.setdefault(txn["from_account"], []).append(txn)

    for account, txns in by_sender.items():
        if len(txns) >= 3:
            rule_hits += len(txns)
            if "structuring_smurfing" not in typologies:
                typologies.append("structuring_smurfing")

    amounts = [txn["amount"] for txn in transactions]
    avg_amount = sum(amounts) / len(amounts) if amounts else 0
    variance = sum((a - avg_amount) ** 2 for a in amounts) / len(amounts) if amounts else 0
    mocked_isolation_forest_score = min(100, (variance / 1e10) * 50 + rule_hits * 10)

    rule_based_score = min(100, rule_hits * 15)
    combined_score = (rule_based_score * 0.6) + (mocked_isolation_forest_score * 0.4)

    if combined_score < 30:
        recommendation = "SKIP"
    elif combined_score < 60:
        recommendation = "FAST"
    else:
        recommendation = "FULL"

    state["triage_score"] = TriageScore(
        severity_score=round(combined_score, 2),
        rule_based_score=round(rule_based_score, 2),
        anomaly_score=round(mocked_isolation_forest_score, 2),
        typologies_detected=typologies,
        recommendation=recommendation,
    )

    evidence = typologies + [f"score_{combined_score:.1f}"]
    return append_audit(
        state,
        step="triage",
        agent="triage_firewall",
        action=f"scored {combined_score:.1f} with rec={recommendation}, typologies={typologies}",
        evidence=evidence,
    )


async def risk_analyzer(state: NexusState) -> NexusState:
    """Pipeline Step 4: Full risk analysis (conditional on triage)."""
    transactions = state["masked_data"].get("transactions", [])
    triage = state["triage_score"]
    typologies = triage["typologies_detected"]

    amounts = [txn["amount"] for txn in transactions]
    total_amount = sum(amounts)
    count = len(transactions)
    avg_amount = total_amount / count if count else 0.0
    max_amount = max(amounts) if amounts else 0.0

    high_value_txns = [txn for txn in transactions if txn["amount"] >= 1_000_000]
    counterparties = {txn["to_account"] for txn in transactions}
    locations = {txn["location"] for txn in transactions}

    features = {
        "total_transactions": count,
        "total_amount": round(total_amount, 2),
        "avg_amount": round(avg_amount, 2),
        "max_amount": round(max_amount, 2),
        "high_value_count": len(high_value_txns),
        "unique_counterparties": len(counterparties),
        "unique_locations": len(locations),
    }

    weights = {
        "large_anomaly": 25,
        "offshore_exposure": 20,
        "structuring_smurfing": 30,
        "round_tripping": 20,
        "missing_purpose": 5,
    }
    feature_values = {typology: typology in typologies for typology in weights}
    feature_values["high_cumulative_volume"] = total_amount >= 2_500_000
    feature_values["multiple_counterparties"] = len(counterparties) >= 5

    raw_score = sum(
        weights.get(f, 0) for f, active in feature_values.items() if active
    )
    score = min(raw_score, 100.0)

    shap_explanation = explain_risk_score(
        feature_values=feature_values,
        feature_metadata=_feature_metadata(weights),
        score_fn=lambda values: sum(
            weights.get(f, 0) for f, active in values.items() if active
        ),
        final_score=score,
    )

    query = " ".join(["AML SAR suspicious activity"] + typologies)
    rag_context = retrieve_aml_context(query=query, tags=typologies, top_k=4)

    if score >= 80:
        level = "CRITICAL"
    elif score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    state["risk_findings"] = {
        "features": features,
        "risk": {
            "score": int(score),
            "level": level,
            "factors": [t for t in typologies if feature_values.get(t)],
            "shap_explanation": shap_explanation,
        },
        "rag_context": rag_context,
        "reasoning": {
            "summary": f"Risk assessed as {level} ({score}/100) based on {len(typologies)} typologies.",
            "recommended_action": "File SAR" if score >= 60 else "Review internally",
        },
    }

    evidence = typologies + [f"risk_score_{score}"]
    return append_audit(
        state,
        step="risk_analysis",
        agent="risk_analyzer",
        action=f"computed risk score {score} ({level}) with SHAP explanation",
        evidence=evidence,
        shap_values=shap_explanation,
    )


async def sar_drafter(state: NexusState) -> NexusState:
    """Pipeline Step 5: Draft SAR report with LLM-generated narrative."""
    findings = state["risk_findings"]
    data = state["masked_data"]
    triage = state["triage_score"]

    report_id = f"SAR-{data['user_id']}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    # Build flags with typology info for LLM narrative
    transactions = data.get("transactions", [])
    typologies = triage.get("typologies_detected", [])
    risk = findings["risk"]
    
    # Create synthetic flags for each typology with representative transactions
    flags = []
    for txn in transactions[:5]:  # Use top 5 transactions
        # Assign typology based on transaction characteristics
        txn_flags = []
        if txn["amount"] >= 1_000_000:
            txn_flags.append("large_anomaly")
        if any(term in txn["location"].lower() for term in ["cayman", "dubai", "switzerland", "panama", "offshore"]):
            txn_flags.append("offshore_exposure")
        if not txn.get("note"):
            txn_flags.append("missing_purpose")
        
        # Use first matched typology or default
        assigned_typology = txn_flags[0] if txn_flags else (typologies[0] if typologies else "suspicious_activity")
        
        flags.append({
            "transaction_id": txn["transaction_id"],
            "typology": assigned_typology,
            "reason": f"Detected {assigned_typology.replace('_', ' ')}",
            "amount": txn["amount"],
            "from_account": txn["from_account"],
            "to_account": txn["to_account"],
            "location": txn["location"],
            "timestamp": txn["timestamp"],
        })
    
    # Generate LLM narrative (Layer 3: Narrative Engine)
    narrative = await generate_sar_narrative(
        subject_id=data["user_id"],
        risk_level=risk["level"],
        risk_score=risk["score"],
        typologies=typologies,
        flags=flags,
        rag_context=findings.get("rag_context", []),
    )

    draft = {
        "report_id": report_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "user_id": data["user_id"],
        "subject_information": {
            "subject_account": data["user_id"],
            "review_period": {"start": None, "end": None},
            "total_transactions_reviewed": findings["features"]["total_transactions"],
            "total_amount_reviewed": findings["features"]["total_amount"],
            "risk_level": risk["level"],
            "risk_score": risk["score"],
        },
        "risk_assessment": findings["risk"],
        "investigator_reasoning": findings["reasoning"],
        "rag_context": findings["rag_context"],
        "triage_result": triage,
        "llm_narrative": narrative,
        "status": "Draft SAR Generated",
    }

    state["draft_sar"] = draft

    evidence = [report_id, f"risk_{risk['level']}"]
    return append_audit(
        state,
        step="drafting",
        agent="sar_drafter",
        action=f"generated SAR draft {report_id} with LLM narrative",
        evidence=evidence,
    )


async def deanonymizer(state: NexusState) -> NexusState:
    """Pipeline Step 6: Restore PII before final response."""
    if "_masking_map" not in state["masked_data"]:
        return state

    masking_map = state["masked_data"]["_masking_map"]
    reverse_map = {v: k for k, v in masking_map.items()}

    if "draft_sar" in state:
        draft = state["draft_sar"]
        if "user_id" in draft:
            for token, original in reverse_map.items():
                draft["user_id"] = draft["user_id"].replace(token, original)

    return append_audit(
        state,
        step="deanonymization",
        agent="deanonymizer",
        action=f"restored {len(reverse_map)} masked identifiers",
        evidence=list(reverse_map.values()),
    )


# Helper functions

def _pick(row: dict[str, Any], *keys: str) -> Any:
    lookup = {str(key).strip().lower(): value for key, value in row.items()}
    for key in keys:
        value = lookup.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def _parse_amount(value: Any) -> float | None:
    if value is None:
        return None
    import re
    text = str(value).strip()
    if not text:
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", text.replace(",", ""))
    if cleaned in {"", ".", "-", "-."}:
        return None
    try:
        return round(abs(float(cleaned)), 2)
    except ValueError:
        return None


def _normalize_timestamp(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).isoformat()
        except ValueError:
            continue
    return text


def _feature_metadata(weights: dict[str, int]) -> dict[str, dict]:
    descriptions = {
        "large_anomaly": "Very high value activity increased the risk score.",
        "offshore_exposure": "Offshore or high-risk location exposure increased the risk score.",
        "structuring_smurfing": "Repeated near-threshold transactions increased the risk score.",
        "round_tripping": "Funds moving back between the same parties increased the risk score.",
        "missing_purpose": "Missing payment purpose reduced transaction transparency.",
    }
    return {
        feature: {
            "weight": weight,
            "display_name": feature.replace("_", " ").title(),
            "reason": descriptions.get(feature, "This indicator increased the risk score."),
        }
        for feature, weight in weights.items()
    }

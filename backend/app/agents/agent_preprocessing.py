"""Pipeline Step 2: detect suspicious transaction patterns with RAG-enhanced guidance."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict

from app.agents.base import BaseAgent
from app.utils.rag import retrieve_aml_context


class PreprocessingAgent(BaseAgent):
    """Detect AML typologies in normalized transactions."""

    name = "Risk Analyst"

    async def process(self, data: Dict) -> Dict:
        transactions = data.get("transactions", [])
        flags: list[dict] = []

        high_value_threshold = 1_000_000
        structuring_floor = 40_000
        structuring_ceiling = 50_000
        offshore_terms = {
            "cayman", "dubai", "uae", "panama", "mauritius", "singapore",
            "hong kong", "switzerland", "bvi", "british virgin",
        }

        for txn in transactions:
            location = txn["location"].lower()
            if txn["amount"] >= high_value_threshold:
                flags.append(_flag(txn, "large_anomaly", "Very high value transaction"))
            if any(term in location for term in offshore_terms):
                flags.append(_flag(txn, "offshore_exposure", "Offshore or high-risk location exposure"))
            if not txn.get("note"):
                flags.append(_flag(txn, "missing_purpose", "Missing transaction purpose or remarks"))

        by_sender: dict[str, list[dict]] = defaultdict(list)
        for txn in transactions:
            if structuring_floor <= txn["amount"] <= structuring_ceiling:
                by_sender[txn["from_account"]].append(txn)

        for account, txns in by_sender.items():
            if len(txns) >= 3:
                for txn in txns:
                    flags.append(_flag(
                        txn,
                        "structuring_smurfing",
                        f"{account} made repeated transactions just below review threshold",
                    ))

        for first in transactions:
            for second in transactions:
                if first["transaction_id"] == second["transaction_id"]:
                    continue
                if (
                    first["from_account"] == second["to_account"]
                    and first["to_account"] == second["from_account"]
                ):
                    flags.append(_flag(second, "round_tripping", "Funds returned between the same parties"))

        # Retrieve AML guidance for detected typologies via RAG
        typologies = sorted({flag["typology"] for flag in flags})
        rag_context = []
        if typologies:
            query = " ".join(["AML suspicious activity"] + typologies)
            rag_context = retrieve_aml_context(query=query, tags=typologies, top_k=5)

        data["analysis"] = {
            "flags": _dedupe_flags(flags),
            "typologies": typologies,
            "period": _period(transactions),
            "rag_context": rag_context,
        }
        return data


def _flag(txn: dict, typology: str, reason: str) -> dict:
    return {
        "transaction_id": txn["transaction_id"],
        "typology": typology,
        "reason": reason,
        "amount": txn["amount"],
        "from_account": txn["from_account"],
        "to_account": txn["to_account"],
        "location": txn["location"],
        "timestamp": txn["timestamp"],
    }


def _dedupe_flags(flags: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for flag in flags:
        key = (flag["transaction_id"], flag["typology"])
        if key not in seen:
            seen.add(key)
            unique.append(flag)
    return unique


def _period(transactions: list[dict]) -> dict:
    dates = []
    for txn in transactions:
        try:
            if txn.get("timestamp"):
                dates.append(datetime.fromisoformat(str(txn["timestamp"]).replace("Z", "+00:00")))
        except ValueError:
            continue
    if not dates:
        return {"start": None, "end": None}
    return {"start": min(dates).isoformat(), "end": max(dates).isoformat()}

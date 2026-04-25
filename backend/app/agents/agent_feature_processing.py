"""
SAR Multi-Agent Backend — Feature Processing Agent
====================================================
Pipeline Step 3: Extracts statistical features from cleaned data.

Computes aggregate metrics that feed the downstream analysis engine.
"""

from __future__ import annotations

from typing import Dict

from app.agents.base import BaseAgent


class FeatureProcessingAgent(BaseAgent):
    """Compute aggregate features from cleaned transaction data."""

    name = "FeatureProcessing"

    async def process(self, data: Dict) -> Dict:
        transactions = data.get("transactions", [])

        amounts = [txn["amount"] for txn in transactions]
        total_amount = sum(amounts)
        count = len(transactions)
        avg_amount = total_amount / count if count else 0.0
        max_amount = max(amounts) if amounts else 0.0
        min_amount = min(amounts) if amounts else 0.0
        high_value_txns = [txn for txn in transactions if txn["amount"] > 10_000]

        features = {
            "total_transactions": count,
            "total_amount": round(total_amount, 2),
            "avg_amount": round(avg_amount, 2),
            "max_amount": round(max_amount, 2),
            "min_amount": round(min_amount, 2),
            "high_value_count": len(high_value_txns),
        }

        data["features"] = features
        return data

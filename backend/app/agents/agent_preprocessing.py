"""
SAR Multi-Agent Backend — Preprocessing Agent
===============================================
Pipeline Step 2: Cleans and standardises transaction records.

Handles malformed data gracefully — bad records are silently
dropped with a warning count in metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.agents.base import BaseAgent
from app.core.logger import logger


class PreprocessingAgent(BaseAgent):
    """Clean raw transaction records and drop malformed entries."""

    name = "Preprocessing"

    async def process(self, data: Dict) -> Dict:
        transactions = data.get("transactions", [])

        cleaned_transactions: List[Dict] = []
        dropped = 0

        for txn in transactions:
            try:
                cleaned_txn = {
                    "amount": float(txn.get("amount", 0)),
                    "type": str(txn.get("type", "unknown")).lower(),
                    "timestamp": txn.get("timestamp"),
                }
                cleaned_transactions.append(cleaned_txn)
            except (TypeError, ValueError):
                dropped += 1
                continue  # Skip bad records

        if dropped:
            logger.warning(
                "Preprocessing dropped %d malformed record(s)", dropped
            )

        data["transactions"] = cleaned_transactions
        data.setdefault("metadata", {})["dropped_records"] = dropped

        return data

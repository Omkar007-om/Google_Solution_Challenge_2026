"""
SAR Multi-Agent Backend — Input Handler Agent
===============================================
Pipeline Step 1: Validates and normalizes raw user input.

This agent acts as the gateway — it ensures the payload has
the required structure before any downstream processing.
"""

from __future__ import annotations

from typing import Any, Dict

from app.agents.base import BaseAgent


class InputHandlerAgent(BaseAgent):
    """Validate incoming data and normalize it into a canonical schema.

    Expected input keys:
        - ``transactions`` (required): List of transaction records.
        - ``user_id``      (required): Unique user identifier.
        - ``metadata``     (optional): Arbitrary metadata dict.
    """

    name = "InputHandler"

    async def process(self, data: Any) -> Dict:
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")

        # ── Validate required fields ─────────────────────
        required_fields = ["transactions", "user_id"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required field(s): {', '.join(missing)}")

        # ── Normalize structure ──────────────────────────
        normalized = {
            "user_id": str(data["user_id"]),
            "transactions": data["transactions"],
            "metadata": data.get("metadata", {}),
        }

        return normalized

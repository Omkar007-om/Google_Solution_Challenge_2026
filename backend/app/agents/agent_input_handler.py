"""Pipeline Step 1: clean CSV/JSON transaction input into one schema."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import re
from typing import Any, Dict

from app.agents.base import BaseAgent


class InputHandlerAgent(BaseAgent):
    """Validate incoming data and normalize transactions."""

    name = "Input Processor"

    async def process(self, data: Any) -> Dict:
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")

        transactions = data.get("transactions") or data.get("raw_transactions")
        if not isinstance(transactions, list) or not transactions:
            raise ValueError("Input must contain a non-empty transactions list")

        cleaned: list[dict[str, Any]] = []
        dropped = 0

        for index, row in enumerate(transactions, start=1):
            if not isinstance(row, dict):
                dropped += 1
                continue

            amount = _parse_amount(_pick(row, "amount", "amt", "transaction_amount", "value"))
            if amount is None:
                dropped += 1
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

        if not cleaned:
            raise ValueError("No valid transaction rows found in input")

        subject_account = data.get("user_id") or data.get("subject_account")
        if not subject_account:
            accounts = [txn["from_account"] for txn in cleaned if txn["from_account"] != "UNKNOWN"]
            subject_account = Counter(accounts).most_common(1)[0][0] if accounts else "UNKNOWN"

        return {
            "user_id": str(subject_account),
            "transactions": cleaned,
            "metadata": {
                **data.get("metadata", {}),
                "dropped_records": dropped,
                "input_rows": len(transactions),
                "valid_rows": len(cleaned),
            },
        }


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
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(text, fmt).isoformat()
        except ValueError:
            continue
    return text

"""
NEXUS 2.0 — PrivacyGuard
Pre-processing layer that masks PII before data reaches the LLM,
and deanonymizes the final SAR narrative afterward.

Supports: names, SSNs, account numbers, emails, phone numbers, dates of birth.
"""

import re
import copy
import json
from typing import Any


class PrivacyGuard:
    """
    Stateful PII masker / unmasker.

    Usage:
        guard = PrivacyGuard()
        masked_data, pii_mapping = guard.mask_alert(raw_alert_dict)
        # ... send masked_data through LLM pipeline ...
        clean_text = guard.unmask_text(draft_narrative, pii_mapping)
    """

    # ── Regex patterns for PII detection ──
    PATTERNS: list[tuple[str, str, re.Pattern]] = [
        # SSN (full or last-four)
        ("SSN", "SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
        ("SSN_LAST4", "SSN", re.compile(r"(?i)(?:ssn[_\s]*(?:last[_\s]*(?:four|4))?[:\s]*)(\d{4})")),

        # Account numbers (ACCT-XXX, INTL-XXX, EXT-XXX patterns)
        ("ACCOUNT", "ACCOUNT", re.compile(r"\b(?:ACCT|INTL|EXT)[-\s]?[A-Z]*[-\s]?\d{1,6}\b")),

        # Email
        ("EMAIL", "EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),

        # US Phone numbers
        ("PHONE", "PHONE", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),

        # Date of birth (YYYY-MM-DD or MM/DD/YYYY)
        ("DOB", "DOB", re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")),

        # Transaction IDs
        ("TXN_ID", "TXN_ID", re.compile(r"\bTXN-\d{3,6}\b")),

        # Customer IDs
        ("CUST_ID", "CUST_ID", re.compile(r"\bCUST-\d{3,6}\b")),
    ]

    # ── Fields in the alert dict that contain person/entity names ──
    NAME_FIELDS = {
        "name", "from_name", "to_name", "sender_name", "receiver_name",
    }

    # ── Fields in the alert dict that contain addresses ──
    ADDRESS_FIELDS = {
        "address",
    }

    # ── Fields that contain sensitive identifiers (replaced wholesale) ──
    SENSITIVE_FIELDS = {
        "ssn_last_four", "ssn", "tax_id",
    }

    def __init__(self):
        self._counter: dict[str, int] = {}  # type -> running count

    def _next_placeholder(self, pii_type: str) -> str:
        """Generate the next placeholder token, e.g. [PERSON_1], [ACCOUNT_2]."""
        self._counter.setdefault(pii_type, 0)
        self._counter[pii_type] += 1
        return f"[{pii_type}_{self._counter[pii_type]}]"

    # ──────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────

    def mask_alert(self, raw_alert: dict) -> tuple[dict, dict]:
        """
        Mask all PII in the raw alert data.

        Returns:
            (masked_data, pii_mapping)
            pii_mapping is {placeholder: original_value} for later unmasking.
        """
        self._counter = {}
        pii_mapping: dict[str, str] = {}  # placeholder -> original

        masked = copy.deepcopy(raw_alert)
        masked = self._mask_dict(masked, pii_mapping)
        return masked, pii_mapping

    def unmask_text(self, text: str, pii_mapping: dict) -> str:
        """
        Replace all [TYPE_N] placeholders in text with their original PII values.
        Processes longest placeholders first to avoid partial replacements.
        """
        # Sort by length descending so [PERSON_10] is replaced before [PERSON_1]
        for placeholder in sorted(pii_mapping, key=len, reverse=True):
            text = text.replace(placeholder, pii_mapping[placeholder])
        return text

    # ──────────────────────────────────────────────
    #  Internal recursion
    # ──────────────────────────────────────────────

    def _mask_dict(self, obj: Any, mapping: dict) -> Any:
        """Recursively walk a dict/list and mask PII values."""
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                if isinstance(value, str):
                    new_dict[key] = self._mask_string_value(key, value, mapping)
                elif isinstance(value, (dict, list)):
                    new_dict[key] = self._mask_dict(value, mapping)
                else:
                    new_dict[key] = value
            return new_dict
        elif isinstance(obj, list):
            return [self._mask_dict(item, mapping) for item in obj]
        elif isinstance(obj, str):
            return self._mask_string_value("", obj, mapping)
        return obj

    def _mask_string_value(self, field_name: str, value: str, mapping: dict) -> str:
        """
        Mask a single string value.
        - Named fields (names, addresses) are replaced wholesale.
        - Other strings are scanned with regex patterns.
        """
        # Check if already masked (avoid double-masking)
        if value.startswith("[") and value.endswith("]") and "_" in value:
            return value

        # ── Wholesale replacement for name fields ──
        if field_name.lower() in self.NAME_FIELDS and value.strip():
            return self._get_or_create_placeholder("PERSON", value, mapping)

        # ── Wholesale replacement for address fields ──
        if field_name.lower() in self.ADDRESS_FIELDS and value.strip():
            return self._get_or_create_placeholder("ADDRESS", value, mapping)

        # ── Wholesale replacement for sensitive identifier fields ──
        if field_name.lower() in self.SENSITIVE_FIELDS and value.strip():
            return self._get_or_create_placeholder("SSN", value, mapping)

        # ── Regex-based replacement for everything else ──
        result = value
        for _name, pii_type, pattern in self.PATTERNS:
            matches = pattern.findall(result)
            for match in matches:
                # findall with groups returns the group, not the full match
                if isinstance(match, tuple):
                    match = match[0]
                if match and match not in [v for v in mapping.values()]:
                    placeholder = self._get_or_create_placeholder(pii_type, match, mapping)
                    result = result.replace(match, placeholder)

        return result

    def _get_or_create_placeholder(self, pii_type: str, original: str, mapping: dict) -> str:
        """
        Return existing placeholder if this value was already masked,
        otherwise create a new one.
        """
        # Check if we already have a placeholder for this exact value
        for placeholder, orig_val in mapping.items():
            if orig_val == original:
                return placeholder

        placeholder = self._next_placeholder(pii_type)
        mapping[placeholder] = original
        return placeholder


# ──────────────────────────────────────────────
#  Quick self-test (run: python privacy_guard.py)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    from sample_data import get_sample_alert

    guard = PrivacyGuard()
    raw = get_sample_alert("elder_exploitation")

    masked, pii_map = guard.mask_alert(raw)

    print("=" * 60)
    print("PII MAPPING")
    print("=" * 60)
    for placeholder, original in pii_map.items():
        print(f"  {placeholder:20s} -> {original}")

    print("\n" + "=" * 60)
    print("MASKED SUBJECTS (first)")
    print("=" * 60)
    print(json.dumps(masked["subjects"][0], indent=2))

    # Test unmasking
    test_narrative = f"The subject {list(pii_map.keys())[0]} transferred funds to {list(pii_map.keys())[1]}."
    restored = guard.unmask_text(test_narrative, pii_map)
    print("\n" + "=" * 60)
    print("UNMASK TEST")
    print("=" * 60)
    print(f"  Masked:   {test_narrative}")
    print(f"  Restored: {restored}")

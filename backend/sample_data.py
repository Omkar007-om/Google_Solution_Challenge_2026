"""
NEXUS 2.0 — Standalone sample alert data (plain dicts).
Decoupled from the original Pydantic schemas so the backend can run independently.
"""

SAMPLE_ALERTS = {
    "elder_exploitation": {
        "case_id": "CASE-2024-001",
        "alert_date": "2024-02-05",
        "alert_reason": "Unusual account activity - potential elder financial exploitation",
        "alert_source": "Transaction Monitoring System",
        "priority": "HIGH",
        "initial_risk_score": 0.85,
        "total_suspicious_amount": 58000.00,
        "subjects": [
            {
                "role": "victim",
                "customer_id": "CUST-001",
                "name": "Margaret Wilson",
                "date_of_birth": "1942-03-15",
                "ssn_last_four": "4521",
                "address": "123 Oak Street, Springfield, IL",
                "phone": "555-123-4567",
                "email": "mwilson@email.com",
                "occupation": "Retired",
                "annual_income": 42000.0,
                "account_id": "ACCT-001",
                "account_type": "savings",
                "account_balance": 15420.50,
                "avg_monthly_balance": 85000.0,
                "risk_rating": "LOW",
                "notes": [
                    "Long-term customer with stable account history",
                    "Recent change in transaction patterns noted",
                    "Teller reported customer appeared confused during last visit",
                ],
            },
            {
                "role": "suspect",
                "customer_id": "CUST-002",
                "name": "James Porter",
                "date_of_birth": "1985-07-22",
                "address": "456 Elm Avenue, Chicago, IL",
                "account_id": "ACCT-002",
                "account_type": "checking",
                "account_balance": 5200.00,
                "risk_rating": "HIGH",
                "notes": [
                    "Recently added as POA on victim's account",
                    "New customer with limited history",
                ],
            },
        ],
        "transactions": [
            {
                "id": "TXN-001",
                "date": "2024-01-20",
                "type": "WITHDRAWAL",
                "amount": 5000.00,
                "from_account": "ACCT-001",
                "from_name": "Margaret Wilson",
                "location": "Springfield Branch",
                "description": "Cash withdrawal",
                "risk_flags": ["unusual_amount"],
            },
            {
                "id": "TXN-002",
                "date": "2024-01-23",
                "type": "TRANSFER",
                "amount": 8500.00,
                "from_account": "ACCT-001",
                "to_account": "ACCT-002",
                "from_name": "Margaret Wilson",
                "to_name": "James Porter",
                "location": "Online",
                "description": "Transfer to James - car repairs",
                "risk_flags": ["unusual_amount", "new_recipient"],
            },
            {
                "id": "TXN-003",
                "date": "2024-01-27",
                "type": "WIRE",
                "amount": 12000.00,
                "from_account": "ACCT-001",
                "from_name": "Margaret Wilson",
                "to_name": "Unknown",
                "location": "Springfield Branch",
                "description": "Wire transfer - investment opportunity",
                "risk_flags": ["large_wire", "unknown_recipient", "investment_scam"],
            },
            {
                "id": "TXN-004",
                "date": "2024-01-30",
                "type": "WITHDRAWAL",
                "amount": 7500.00,
                "from_account": "ACCT-001",
                "from_name": "Margaret Wilson",
                "location": "Chicago Branch",
                "description": "Cash withdrawal",
                "risk_flags": ["unusual_location", "large_amount"],
            },
            {
                "id": "TXN-005",
                "date": "2024-02-03",
                "type": "TRANSFER",
                "amount": 15000.00,
                "from_account": "ACCT-001",
                "to_account": "ACCT-002",
                "from_name": "Margaret Wilson",
                "to_name": "James Porter",
                "location": "Online",
                "description": "Transfer - medical emergency help",
                "risk_flags": ["large_transfer", "urgent_language"],
            },
            {
                "id": "TXN-006",
                "date": "2024-02-04",
                "type": "WIRE",
                "amount": 10000.00,
                "from_account": "ACCT-002",
                "from_name": "James Porter",
                "to_name": "Offshore Holdings LLC",
                "country": "KY",
                "location": "Online",
                "description": "Investment transfer",
                "risk_flags": ["offshore", "rapid_movement", "tax_haven"],
            },
        ],
        "communications": [
            {
                "date": "2024-01-15",
                "type": "note",
                "content": "Teller noted customer was accompanied by unfamiliar younger male who seemed to be directing her actions.",
                "parties": ["Teller", "Margaret Wilson", "Unknown Male"],
            },
            {
                "date": "2024-01-28",
                "type": "note",
                "content": "Customer called to inquire about wire transfer limits. Seemed confused about recent transactions on her account.",
                "parties": ["Call Center", "Margaret Wilson"],
            },
        ],
        "analyst_notes": [
            "Pattern consistent with elder exploitation",
            "Rapid depletion of retirement savings",
            "New POA arrangement coincides with suspicious activity",
        ],
    },

    "structuring": {
        "case_id": "CASE-2024-002",
        "alert_date": "2024-02-04",
        "alert_reason": "Potential structuring - multiple transactions below reporting threshold",
        "alert_source": "Transaction Monitoring System",
        "priority": "HIGH",
        "initial_risk_score": 0.72,
        "total_suspicious_amount": 143250.00,
        "subjects": [
            {
                "role": "subject",
                "customer_id": "CUST-100",
                "name": "Tech Solutions Inc",
                "address": "789 Business Park, Austin, TX",
                "occupation": "Business",
                "account_id": "ACCT-100",
                "account_type": "business_checking",
                "account_balance": 125000.00,
                "avg_monthly_balance": 75000.0,
                "risk_rating": "MEDIUM",
            },
        ],
        "transactions": [
            {
                "id": f"TXN-1{i:02d}",
                "date": "2024-02-01",
                "type": "WITHDRAWAL",
                "amount": 9500.00 + (i * 10),
                "from_account": "ACCT-100",
                "from_name": "Tech Solutions Inc",
                "location": "Austin Branch",
                "description": f"Operating expense #{i + 1}",
                "risk_flags": ["structuring_pattern"],
            }
            for i in range(15)
        ],
        "analyst_notes": [
            "15 cash withdrawals in 3-day period",
            "All amounts between $9,500 and $9,650",
            "Pattern suggests structuring to avoid CTR",
        ],
    },
}


def get_sample_alert(case_type: str = "elder_exploitation") -> dict:
    """Return a sample alert dict for testing."""
    if case_type not in SAMPLE_ALERTS:
        raise ValueError(
            f"Unknown case type '{case_type}'. Available: {list(SAMPLE_ALERTS.keys())}"
        )
    return SAMPLE_ALERTS[case_type]

"""
Sample AML case data for testing Axiom.
"""

from datetime import datetime, timedelta
from data.schemas import (
    Transaction, Account, Customer, CaseData,
    CommunicationRecord, TransactionType, RiskLevel
)


def get_sample_elder_exploitation_case() -> CaseData:
    """Generate a sample elder financial exploitation case."""
    
    # Subject (victim)
    victim = Customer(
        customer_id="CUST-001",
        name="Margaret Wilson",
        date_of_birth=datetime(1942, 3, 15),
        ssn_last_four="4521",
        address="123 Oak Street",
        city="Springfield",
        state="IL",
        country="US",
        phone="555-123-4567",
        email="mwilson@email.com",
        occupation="Retired",
        annual_income=42000.0,
        customer_since=datetime(1998, 5, 1),
        risk_rating=RiskLevel.LOW,
        accounts=["ACCT-001"],
        notes=[
            "Long-term customer with stable account history",
            "Recent change in transaction patterns noted",
            "Teller reported customer appeared confused during last visit"
        ],
    )
    
    # Suspect
    suspect = Customer(
        customer_id="CUST-002",
        name="James Porter",
        date_of_birth=datetime(1985, 7, 22),
        address="456 Elm Avenue",
        city="Chicago",
        state="IL",
        country="US",
        customer_since=datetime(2024, 1, 15),
        risk_rating=RiskLevel.HIGH,
        accounts=["ACCT-002"],
        notes=[
            "Recently added as POA on victim's account",
            "New customer with limited history"
        ],
    )
    
    # Accounts
    victim_account = Account(
        account_id="ACCT-001",
        account_type="savings",
        owner_id="CUST-001",
        opened_date=datetime(1998, 5, 1),
        status="active",
        balance=15420.50,
        average_monthly_balance=85000.0,
        typical_transaction_amount=200.0,
        risk_flags=["unusual_activity", "large_withdrawals"],
    )
    
    suspect_account = Account(
        account_id="ACCT-002",
        account_type="checking",
        owner_id="CUST-002",
        opened_date=datetime(2024, 1, 15),
        status="active",
        balance=5200.00,
        risk_flags=["new_account", "rapid_movement"],
    )
    
    # Transactions
    base_date = datetime(2024, 1, 20)
    transactions = [
        Transaction(
            transaction_id="TXN-001",
            date=base_date,
            amount=5000.00,
            transaction_type=TransactionType.WITHDRAWAL,
            sender_account="ACCT-001",
            sender_name="Margaret Wilson",
            location="Springfield Branch",
            country="US",
            description="Cash withdrawal",
            risk_flags=["unusual_amount"],
        ),
        Transaction(
            transaction_id="TXN-002",
            date=base_date + timedelta(days=3),
            amount=8500.00,
            transaction_type=TransactionType.TRANSFER,
            sender_account="ACCT-001",
            receiver_account="ACCT-002",
            sender_name="Margaret Wilson",
            receiver_name="James Porter",
            location="Online",
            description="Transfer to James - car repairs",
            risk_flags=["unusual_amount", "new_recipient"],
        ),
        Transaction(
            transaction_id="TXN-003",
            date=base_date + timedelta(days=7),
            amount=12000.00,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-001",
            sender_name="Margaret Wilson",
            receiver_name="Unknown",
            location="Springfield Branch",
            country="US",
            description="Wire transfer - investment opportunity",
            risk_flags=["large_wire", "unknown_recipient", "investment_scam"],
        ),
        Transaction(
            transaction_id="TXN-004",
            date=base_date + timedelta(days=10),
            amount=7500.00,
            transaction_type=TransactionType.WITHDRAWAL,
            sender_account="ACCT-001",
            sender_name="Margaret Wilson",
            location="Chicago Branch",
            country="US",
            description="Cash withdrawal",
            risk_flags=["unusual_location", "large_amount"],
        ),
        Transaction(
            transaction_id="TXN-005",
            date=base_date + timedelta(days=14),
            amount=15000.00,
            transaction_type=TransactionType.TRANSFER,
            sender_account="ACCT-001",
            receiver_account="ACCT-002",
            sender_name="Margaret Wilson",
            receiver_name="James Porter",
            location="Online",
            description="Transfer - medical emergency help",
            risk_flags=["large_transfer", "urgent_language"],
        ),
        Transaction(
            transaction_id="TXN-006",
            date=base_date + timedelta(days=15),
            amount=10000.00,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-002",
            sender_name="James Porter",
            receiver_name="Offshore Holdings LLC",
            location="Online",
            country="KY",  # Cayman Islands
            description="Investment transfer",
            risk_flags=["offshore", "rapid_movement", "tax_haven"],
        ),
    ]
    
    # Communications
    communications = [
        CommunicationRecord(
            date=base_date - timedelta(days=5),
            type="note",
            content="Teller noted customer was accompanied by unfamiliar younger male who seemed to be directing her actions.",
            parties=["Teller", "Margaret Wilson", "Unknown Male"],
        ),
        CommunicationRecord(
            date=base_date + timedelta(days=8),
            type="note",
            content="Customer called to inquire about wire transfer limits. Seemed confused about recent transactions on her account.",
            parties=["Call Center", "Margaret Wilson"],
        ),
    ]
    
    return CaseData(
        case_id="CASE-2024-001",
        alert_date=base_date + timedelta(days=16),
        alert_reason="Unusual account activity - potential elder financial exploitation",
        alert_source="Transaction Monitoring System",
        subjects=[victim, suspect],
        accounts=[victim_account, suspect_account],
        transactions=transactions,
        communications=communications,
        total_amount=58000.00,
        date_range_start=base_date,
        date_range_end=base_date + timedelta(days=15),
        initial_risk_score=0.85,
        priority=RiskLevel.HIGH,
        notes=[
            "Pattern consistent with elder exploitation",
            "Rapid depletion of retirement savings",
            "New POA arrangement coincides with suspicious activity"
        ],
    )


def get_sample_transaction_fraud_case() -> CaseData:
    """Generate a sample transaction fraud case."""
    
    subject = Customer(
        customer_id="CUST-100",
        name="Tech Solutions Inc",
        address="789 Business Park",
        city="Austin",
        state="TX",
        country="US",
        occupation="Business",
        customer_since=datetime(2023, 6, 1),
        risk_rating=RiskLevel.MEDIUM,
        accounts=["ACCT-100"],
    )
    
    account = Account(
        account_id="ACCT-100",
        account_type="business_checking",
        owner_id="CUST-100",
        opened_date=datetime(2023, 6, 1),
        status="active",
        balance=125000.00,
        average_monthly_balance=75000.0,
        typical_transaction_amount=2500.0,
        risk_flags=["velocity_spike"],
    )
    
    base_date = datetime(2024, 2, 1)
    transactions = []
    
    # Series of structured transactions just below reporting threshold
    for i in range(15):
        transactions.append(Transaction(
            transaction_id=f"TXN-1{i:02d}",
            date=base_date + timedelta(hours=i*4),
            amount=9500.00 + (i * 10),  # Just below $10k
            transaction_type=TransactionType.WITHDRAWAL,
            sender_account="ACCT-100",
            sender_name="Tech Solutions Inc",
            location="Austin Branch",
            country="US",
            description=f"Operating expense #{i+1}",
            risk_flags=["structuring_pattern"],
        ))
    
    return CaseData(
        case_id="CASE-2024-002",
        alert_date=base_date + timedelta(days=3),
        alert_reason="Potential structuring - multiple transactions below reporting threshold",
        alert_source="Transaction Monitoring System",
        subjects=[subject],
        accounts=[account],
        transactions=transactions,
        total_amount=sum(t.amount for t in transactions),
        date_range_start=base_date,
        date_range_end=base_date + timedelta(days=3),
        initial_risk_score=0.72,
        priority=RiskLevel.HIGH,
        notes=[
            "15 cash withdrawals in 3-day period",
            "All amounts between $9,500 and $9,650",
            "Pattern suggests structuring to avoid CTR"
        ],
    )


def get_sample_money_mule_case() -> CaseData:
    """Generate a sample money mule case."""
    
    subject = Customer(
        customer_id="CUST-200",
        name="Sarah Johnson",
        date_of_birth=datetime(1995, 11, 8),
        address="321 College Ave",
        city="Boston",
        state="MA",
        country="US",
        occupation="Student",
        annual_income=15000.0,
        customer_since=datetime(2024, 1, 5),
        risk_rating=RiskLevel.MEDIUM,
        accounts=["ACCT-200"],
        notes=[
            "Account opened with minimal deposit",
            "Sudden high-value activity within first month"
        ],
    )
    
    account = Account(
        account_id="ACCT-200",
        account_type="checking",
        owner_id="CUST-200",
        opened_date=datetime(2024, 1, 5),
        status="active",
        balance=450.00,
        average_monthly_balance=500.0,
        typical_transaction_amount=50.0,
        risk_flags=["new_account", "pass_through", "crypto_activity"],
    )
    
    base_date = datetime(2024, 1, 15)
    transactions = [
        # Incoming deposits
        Transaction(
            transaction_id="TXN-201",
            date=base_date,
            amount=4500.00,
            transaction_type=TransactionType.DEPOSIT,
            receiver_account="ACCT-200",
            receiver_name="Sarah Johnson",
            sender_name="Unknown - ACH",
            description="Payment for services",
            risk_flags=["unknown_source"],
        ),
        Transaction(
            transaction_id="TXN-202",
            date=base_date + timedelta(days=1),
            amount=3800.00,
            transaction_type=TransactionType.TRANSFER,
            sender_account="ACCT-200",
            sender_name="Sarah Johnson",
            description="Transfer out",
            risk_flags=["rapid_out"],
        ),
        # Repeat pattern
        Transaction(
            transaction_id="TXN-203",
            date=base_date + timedelta(days=5),
            amount=6200.00,
            transaction_type=TransactionType.DEPOSIT,
            receiver_account="ACCT-200",
            receiver_name="Sarah Johnson",
            description="Freelance payment",
            risk_flags=["unknown_source"],
        ),
        Transaction(
            transaction_id="TXN-204",
            date=base_date + timedelta(days=6),
            amount=5500.00,
            transaction_type=TransactionType.CRYPTO,
            sender_account="ACCT-200",
            sender_name="Sarah Johnson",
            description="Bitcoin purchase",
            risk_flags=["crypto", "rapid_conversion"],
        ),
    ]
    
    return CaseData(
        case_id="CASE-2024-003",
        alert_date=base_date + timedelta(days=10),
        alert_reason="Suspicious pass-through activity on new account",
        alert_source="Transaction Monitoring System",
        subjects=[subject],
        accounts=[account],
        transactions=transactions,
        total_amount=20000.00,
        date_range_start=base_date,
        date_range_end=base_date + timedelta(days=6),
        initial_risk_score=0.78,
        priority=RiskLevel.HIGH,
        notes=[
            "New account with immediate high activity",
            "Funds received and moved within 24-48 hours",
            "Conversion to cryptocurrency suggests layering"
        ],
    )


def get_sample_romance_scam_case() -> CaseData:
    """Generate a sample romance scam / social engineering case."""
    base_date = datetime(2024, 2, 1)
    
    victim = Customer(
        customer_id="CUST-300",
        name="Patricia Chen",
        date_of_birth=datetime(1958, 11, 3),
        ssn_last_four="7823",
        address="89 Maple Lane",
        city="Portland",
        state="OR",
        country="US",
        phone="503-555-8912",
        email="pchen58@email.com",
        occupation="Retired Nurse",
        annual_income=55000.0,
        customer_since=datetime(2003, 8, 12),
        risk_rating=RiskLevel.LOW,
        accounts=["ACCT-300"],
        notes=[
            "Long-standing customer with conservative spending",
            "No prior international wire activity",
            "Branch staff reported customer seemed emotionally distressed",
        ],
    )
    
    account = Account(
        account_id="ACCT-300",
        account_type="savings",
        owner_id="CUST-300",
        opened_date=datetime(2003, 8, 12),
        balance=12000.0,
        average_monthly_balance=85000.0,
        typical_transaction_amount=500.0,
        risk_flags=["unusual_wire_activity", "sudden_account_depletion"],
    )
    
    transactions = [
        Transaction(
            transaction_id=f"TXN-30{i}",
            date=base_date + timedelta(days=i * 5),
            amount=amount,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-300",
            sender_name="Patricia Chen",
            receiver_account=recv_acct,
            receiver_name=recv_name,
            country=country,
            description=desc,
            risk_flags=flags,
        )
        for i, (amount, recv_acct, recv_name, country, desc, flags) in enumerate([
            (5000.0, "INTL-9001", "David Williams", "NG", "Personal gift", ["international", "new_beneficiary"]),
            (8000.0, "INTL-9001", "David Williams", "NG", "Emergency medical expenses", ["international", "escalating_amounts"]),
            (15000.0, "INTL-9002", "DW Investments Ltd", "GB", "Investment opportunity", ["international", "shell_company_indicators"]),
            (12000.0, "INTL-9003", "Global Travel Services", "MY", "Travel arrangements", ["international", "unfamiliar_merchant"]),
            (20000.0, "INTL-9001", "David Williams", "NG", "Business partnership", ["international", "large_amount"]),
            (10000.0, "INTL-9004", "Crypto Exchange Africa", "GH", "Bitcoin purchase", ["international", "crypto", "high_risk_jurisdiction"]),
            (18000.0, "INTL-9001", "David Williams", "NG", "Customs clearance", ["international", "escalating_amounts"]),
        ])
    ]
    
    communications = [
        CommunicationRecord(
            date=base_date - timedelta(days=5),
            type="note",
            content="Customer called to inquire about increasing wire transfer limits. "
                    "Mentioned sending money to a romantic partner overseas.",
            parties=["Patricia Chen", "Branch Manager"],
        ),
        CommunicationRecord(
            date=base_date + timedelta(days=20),
            type="note",
            content="Teller flagged: customer appeared tearful, stated she needed to send "
                    "money urgently for partner's medical emergency. Refused to provide details.",
            parties=["Patricia Chen", "Teller"],
        ),
    ]
    
    return CaseData(
        case_id="CASE-2024-004",
        alert_date=base_date + timedelta(days=25),
        alert_reason="Unusual international wire activity - potential romance scam",
        alert_source="Transaction Monitoring System",
        subjects=[victim],
        accounts=[account],
        transactions=transactions,
        communications=communications,
        total_amount=88000.0,
        date_range_start=base_date,
        date_range_end=base_date + timedelta(days=35),
        initial_risk_score=0.82,
        priority=RiskLevel.HIGH,
        notes=[
            "Elderly customer with no prior international activity",
            "Escalating wire amounts to West Africa",
            "Multiple beneficiaries suggest layering scheme",
            "Emotional distress indicators from branch staff",
            "Account depleted from $100K to $12K in 5 weeks",
        ],
    )


def get_sample_sanctions_evasion_case() -> CaseData:
    """Generate a sample sanctions evasion case."""
    base_date = datetime(2024, 3, 1)
    
    subject = Customer(
        customer_id="CUST-400",
        name="Oleg Petrov",
        date_of_birth=datetime(1975, 4, 18),
        address="1200 Park Avenue, Apt 42B",
        city="New York",
        state="NY",
        country="US",
        phone="212-555-3490",
        email="opetrov.consulting@email.com",
        occupation="Import/Export Consultant",
        employer="Eurasian Trade Consulting LLC",
        annual_income=180000.0,
        customer_since=datetime(2019, 6, 1),
        risk_rating=RiskLevel.HIGH,
        pep_status=True,
        accounts=["ACCT-400", "ACCT-401"],
        notes=[
            "PEP flagged: former trade ministry advisor",
            "Multiple business accounts with international activity",
            "Frequent travel to sanctioned jurisdictions",
        ],
    )
    
    business_account = Account(
        account_id="ACCT-400",
        account_type="business_checking",
        owner_id="CUST-400",
        opened_date=datetime(2019, 6, 15),
        balance=340000.0,
        average_monthly_balance=280000.0,
        typical_transaction_amount=25000.0,
        risk_flags=["high_risk_jurisdictions", "pep_linked", "complex_structure"],
        linked_accounts=["ACCT-401"],
    )
    
    personal_account = Account(
        account_id="ACCT-401",
        account_type="checking",
        owner_id="CUST-400",
        opened_date=datetime(2019, 6, 15),
        balance=95000.0,
        risk_flags=["pep_linked"],
        linked_accounts=["ACCT-400"],
    )
    
    transactions = [
        Transaction(
            transaction_id="TXN-401",
            date=base_date,
            amount=75000.0,
            transaction_type=TransactionType.WIRE,
            sender_account="INTL-EXT-50",
            sender_name="Meridian Trading FZE",
            receiver_account="ACCT-400",
            receiver_name="Eurasian Trade Consulting LLC",
            country="AE",
            description="Consulting services - Q1 payment",
            risk_flags=["high_risk_jurisdiction", "large_amount"],
        ),
        Transaction(
            transaction_id="TXN-402",
            date=base_date + timedelta(days=2),
            amount=70000.0,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-400",
            receiver_account="INTL-EXT-51",
            receiver_name="Caspian Logistics Ltd",
            country="TR",
            description="Logistics services payment",
            risk_flags=["near_identical_amount", "rapid_movement"],
        ),
        Transaction(
            transaction_id="TXN-403",
            date=base_date + timedelta(days=10),
            amount=120000.0,
            transaction_type=TransactionType.WIRE,
            sender_account="INTL-EXT-52",
            sender_name="Beijing Harmonious Trade Co",
            receiver_account="ACCT-400",
            country="CN",
            description="Commodity brokerage fee",
            risk_flags=["large_amount", "opaque_description"],
        ),
        Transaction(
            transaction_id="TXN-404",
            date=base_date + timedelta(days=12),
            amount=55000.0,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-400",
            receiver_account="INTL-EXT-53",
            receiver_name="GulfStar Enterprises",
            country="AE",
            description="Equipment procurement",
            risk_flags=["high_risk_jurisdiction"],
        ),
        Transaction(
            transaction_id="TXN-405",
            date=base_date + timedelta(days=12),
            amount=60000.0,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-400",
            receiver_account="INTL-EXT-54",
            receiver_name="Black Sea Shipping Co",
            country="GE",
            description="Freight forwarding services",
            risk_flags=["geographic_proximity_sanctioned"],
        ),
        Transaction(
            transaction_id="TXN-406",
            date=base_date + timedelta(days=15),
            amount=30000.0,
            transaction_type=TransactionType.TRANSFER,
            sender_account="ACCT-400",
            receiver_account="ACCT-401",
            sender_name="Eurasian Trade Consulting LLC",
            receiver_name="Oleg Petrov",
            description="Owner distribution",
            risk_flags=["business_to_personal"],
        ),
    ]
    
    return CaseData(
        case_id="CASE-2024-005",
        alert_date=base_date + timedelta(days=18),
        alert_reason="PEP account with high-risk jurisdiction wire activity pattern",
        alert_source="Sanctions Screening System",
        subjects=[subject],
        accounts=[business_account, personal_account],
        transactions=transactions,
        total_amount=410000.0,
        date_range_start=base_date,
        date_range_end=base_date + timedelta(days=15),
        initial_risk_score=0.91,
        priority=RiskLevel.CRITICAL,
        notes=[
            "PEP with former government advisory role in sanctioned region",
            "Pass-through pattern: funds in from UAE/China, out to Turkey/Georgia",
            "Companies involved have minimal web presence (shell indicators)",
            "Geographic proximity to sanctioned jurisdictions (Russia, Belarus)",
            "Business-to-personal transfers suggest commingling",
        ],
    )


def get_sample_crypto_layering_case() -> CaseData:
    """Generate a sample cryptocurrency layering / mixing case."""
    base_date = datetime(2024, 4, 1)
    
    subject = Customer(
        customer_id="CUST-500",
        name="Marcus Rivera",
        date_of_birth=datetime(1992, 8, 25),
        address="567 Tech Boulevard, Unit 8",
        city="Austin",
        state="TX",
        country="US",
        phone="512-555-7734",
        email="m.rivera.dev@email.com",
        occupation="Software Developer",
        employer="Self-employed",
        annual_income=95000.0,
        customer_since=datetime(2022, 3, 1),
        risk_rating=RiskLevel.MEDIUM,
        accounts=["ACCT-500", "ACCT-501"],
        notes=[
            "Self-reported crypto trader",
            "Multiple rapid deposits and withdrawals",
            "Account opened 2 years ago, activity surged recently",
        ],
    )
    
    checking = Account(
        account_id="ACCT-500",
        account_type="checking",
        owner_id="CUST-500",
        opened_date=datetime(2022, 3, 1),
        balance=5200.0,
        average_monthly_balance=15000.0,
        typical_transaction_amount=2000.0,
        risk_flags=["crypto_patterns", "rapid_movement", "structuring_indicators"],
        linked_accounts=["ACCT-501"],
    )
    
    savings = Account(
        account_id="ACCT-501",
        account_type="savings",
        owner_id="CUST-500",
        opened_date=datetime(2022, 3, 1),
        balance=42000.0,
        risk_flags=["aggregation_account"],
        linked_accounts=["ACCT-500"],
    )
    
    transactions = [
        # Deposits below $10K (structuring)
        Transaction(
            transaction_id="TXN-501",
            date=base_date,
            amount=9500.0,
            transaction_type=TransactionType.DEPOSIT,
            receiver_account="ACCT-500",
            receiver_name="Marcus Rivera",
            description="Cash deposit",
            risk_flags=["just_below_ctr", "cash"],
        ),
        Transaction(
            transaction_id="TXN-502",
            date=base_date + timedelta(days=1),
            amount=9800.0,
            transaction_type=TransactionType.DEPOSIT,
            receiver_account="ACCT-500",
            receiver_name="Marcus Rivera",
            description="Cash deposit",
            risk_flags=["just_below_ctr", "cash", "consecutive_day"],
        ),
        Transaction(
            transaction_id="TXN-503",
            date=base_date + timedelta(days=2),
            amount=9200.0,
            transaction_type=TransactionType.DEPOSIT,
            receiver_account="ACCT-500",
            receiver_name="Marcus Rivera",
            description="Cash deposit",
            risk_flags=["just_below_ctr", "cash", "consecutive_day"],
        ),
        # Transfer to savings (aggregation)
        Transaction(
            transaction_id="TXN-504",
            date=base_date + timedelta(days=3),
            amount=28000.0,
            transaction_type=TransactionType.TRANSFER,
            sender_account="ACCT-500",
            receiver_account="ACCT-501",
            description="Savings transfer",
            risk_flags=["aggregation"],
        ),
        # Crypto purchases (layering)
        Transaction(
            transaction_id="TXN-505",
            date=base_date + timedelta(days=4),
            amount=9900.0,
            transaction_type=TransactionType.CRYPTO,
            sender_account="ACCT-500",
            sender_name="Marcus Rivera",
            receiver_name="CryptoMixer Exchange",
            description="BTC purchase",
            risk_flags=["crypto", "mixing_service_indicators"],
        ),
        Transaction(
            transaction_id="TXN-506",
            date=base_date + timedelta(days=5),
            amount=9700.0,
            transaction_type=TransactionType.CRYPTO,
            sender_account="ACCT-500",
            sender_name="Marcus Rivera",
            receiver_name="DeFi Swap Protocol",
            description="ETH purchase via DEX",
            risk_flags=["crypto", "defi", "layering"],
        ),
        # Wire to overseas exchange
        Transaction(
            transaction_id="TXN-507",
            date=base_date + timedelta(days=7),
            amount=15000.0,
            transaction_type=TransactionType.WIRE,
            sender_account="ACCT-501",
            sender_name="Marcus Rivera",
            receiver_account="INTL-EXT-70",
            receiver_name="Pacific Digital Assets Ltd",
            country="SG",
            description="Crypto investment",
            risk_flags=["international", "crypto", "high_value"],
        ),
        # Incoming from unknown source
        Transaction(
            transaction_id="TXN-508",
            date=base_date + timedelta(days=10),
            amount=25000.0,
            transaction_type=TransactionType.ACH,
            sender_account="EXT-ACH-999",
            sender_name="Anonymous P2P Payment",
            receiver_account="ACCT-500",
            receiver_name="Marcus Rivera",
            description="P2P transfer received",
            risk_flags=["unknown_source", "large_incoming"],
        ),
        # Rapid withdrawal
        Transaction(
            transaction_id="TXN-509",
            date=base_date + timedelta(days=11),
            amount=9500.0,
            transaction_type=TransactionType.WITHDRAWAL,
            sender_account="ACCT-500",
            sender_name="Marcus Rivera",
            description="ATM withdrawal",
            risk_flags=["just_below_ctr", "cash", "rapid_movement"],
        ),
        Transaction(
            transaction_id="TXN-510",
            date=base_date + timedelta(days=11),
            amount=9900.0,
            transaction_type=TransactionType.WITHDRAWAL,
            sender_account="ACCT-500",
            sender_name="Marcus Rivera",
            location="Different branch",
            description="Counter withdrawal",
            risk_flags=["just_below_ctr", "cash", "same_day_multiple"],
        ),
    ]
    
    return CaseData(
        case_id="CASE-2024-006",
        alert_date=base_date + timedelta(days=12),
        alert_reason="Structuring pattern with cryptocurrency conversion",
        alert_source="Transaction Monitoring System",
        subjects=[subject],
        accounts=[checking, savings],
        transactions=transactions,
        total_amount=135500.0,
        date_range_start=base_date,
        date_range_end=base_date + timedelta(days=11),
        initial_risk_score=0.88,
        priority=RiskLevel.HIGH,
        notes=[
            "Multiple cash deposits just below $10,000 CTR threshold",
            "Rapid conversion to cryptocurrency on mixing/DEX platforms",
            "Cross-account aggregation before international wire",
            "Unknown P2P source for $25K incoming",
            "Same-day cash withdrawals from different locations",
        ],
    )


from data.synthetic_dataset import (
    case_structuring_smurfing,
    case_trade_based_ml,
    case_funnel_account,
    case_pep_corruption,
    case_crypto_mixing,
    case_human_trafficking,
    case_insider_threat,
    case_terrorist_financing,
    case_ransomware_laundering,
    case_elder_romance_scam,
    case_real_estate_laundering,
    case_payroll_fraud,
    case_drug_proceeds,
    case_ponzi_scheme,
    case_sanctions_transshipment,
    case_check_kiting,
    case_illegal_gambling,
    case_bec_fraud,
    case_loan_fraud,
    case_account_takeover,
)


SAMPLE_CASES = {
    # ── Original sample cases ──
    "elder_exploitation": get_sample_elder_exploitation_case,
    "transaction_fraud": get_sample_transaction_fraud_case,
    "money_mule": get_sample_money_mule_case,
    "romance_scam": get_sample_romance_scam_case,
    "sanctions_evasion": get_sample_sanctions_evasion_case,
    "crypto_layering": get_sample_crypto_layering_case,
    # ── Synthetic dataset (20 cases) ──
    "structuring_smurfing": case_structuring_smurfing,
    "trade_based_ml": case_trade_based_ml,
    "funnel_account": case_funnel_account,
    "pep_corruption": case_pep_corruption,
    "crypto_mixing": case_crypto_mixing,
    "human_trafficking": case_human_trafficking,
    "insider_threat": case_insider_threat,
    "terrorist_financing": case_terrorist_financing,
    "ransomware_laundering": case_ransomware_laundering,
    "elder_romance_scam": case_elder_romance_scam,
    "real_estate_laundering": case_real_estate_laundering,
    "payroll_fraud": case_payroll_fraud,
    "drug_proceeds": case_drug_proceeds,
    "ponzi_scheme": case_ponzi_scheme,
    "sanctions_transshipment": case_sanctions_transshipment,
    "check_kiting": case_check_kiting,
    "illegal_gambling": case_illegal_gambling,
    "bec_fraud": case_bec_fraud,
    "loan_fraud": case_loan_fraud,
    "account_takeover": case_account_takeover,
}


def get_sample_case(case_type: str) -> CaseData:
    """Get a sample case by type."""
    if case_type not in SAMPLE_CASES:
        raise ValueError(f"Unknown case type: {case_type}. Available: {list(SAMPLE_CASES.keys())}")
    return SAMPLE_CASES[case_type]()

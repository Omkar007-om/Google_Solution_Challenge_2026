"""Quick smoke test for the mask_pii_node."""
from nodes import mask_pii_node
from sample_data import get_sample_alert

state = {
    "case_id": "TEST",
    "raw_alert_data": get_sample_alert("elder_exploitation"),
    "masked_data": {},
    "pii_mapping": {},
    "detected_typology": "",
    "typology_analysis": "",
    "draft_sar_masked": "",
    "final_sar_clean": "",
    "compliance_score": 0,
    "audit_log": [],
}

result = mask_pii_node(state)
print(f"Masked {len(result['pii_mapping'])} PII entities")
print(f"Audit log entries: {len(result['audit_log'])}")
print(f"First subject name: {result['masked_data']['subjects'][0]['name']}")
print(f"Audit entry: {result['audit_log'][0]}")
print("\nPHASE 3 SMOKE TEST PASSED")

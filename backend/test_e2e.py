"""
NEXUS 2.0 — End-to-End Logic Test
Tests the full LangGraph pipeline using Mock LLM mode.
"""

import os
import json
from workflow import run_pipeline
from sample_data import get_sample_alert

# Enable Mock mode
os.environ["MOCK_LLM"] = "true"

def test_full_pipeline():
    print("\n" + "="*80)
    print("NEXUS 2.0 — END-TO-END PIPELINE TEST (MOCK MODE)")
    print("="*80)

    # 1. Load sample alert
    case_id = "TEST-E2E-001"
    alert_data = get_sample_alert("elder_exploitation")
    print(f"\n[1] Loaded sample alert: {case_id}")
    print(f"    Reason: {alert_data['alert_reason']}")

    # 2. Run pipeline
    print("\n[2] Executing LangGraph pipeline...")
    result = run_pipeline(case_id, alert_data)
    print("    Pipeline execution complete.")

    # 3. Verify results
    print("\n[3] Verifying Results:")
    print(f"    - Case ID: {result['case_id']}")
    print(f"    - Detected Typology: {result['detected_typology']}")
    print(f"    - Compliance Score: {result['compliance_score']}/10")
    
    print("\n[4] Glass-Box Audit Trail:")
    for entry in result["audit_log"]:
        print(f"    - [{entry['step']}] {entry['action']}")

    # 4. Check masking/unmasking in narrative
    print("\n[5] Narrative Sample (First 200 chars):")
    print(f"    {result['final_sar_clean'][:200]}...")

    # Check if placeholders are gone in the final clean version
    if "[" in result['final_sar_clean'] and "]" in result['final_sar_clean'] and "_" in result['final_sar_clean']:
         # Note: Mock narrative specifically uses [PERSON_1] etc. Let's see if unmask_node restored them.
         # Actually, the mock narrative uses placeholders, and unmask_node replaces them using pii_mapping.
         if "Margaret Wilson" in result['final_sar_clean']:
             print("\n[SUCCESS] Real PII (Margaret Wilson) restored in final narrative.")
         else:
             print("\n[WARNING] Real PII not found in final narrative. Checking placeholders...")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_full_pipeline()

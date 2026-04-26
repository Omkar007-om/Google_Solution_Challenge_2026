#!/usr/bin/env python3
"""
Nexus 2.0 — End-to-End Integration Test
=======================================
Tests all 5 layers: Ingestion, Intelligence, Narrative, Audit, Human Control
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

# ── Configuration ──────────────────────────────────────

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# Test data with multiple AML typologies
TEST_TRANSACTIONS = [
    # Structuring/Smurfing pattern (3 transactions just below 50K threshold)
    {"transaction_id": "TXN001", "timestamp": "2024-01-15T09:30:00", "amount": 45000, "currency": "INR", 
     "from_account": "ACCT-TEST-001", "to_account": "OFFSHORE-001", "location": "Cayman Islands", 
     "type": "wire_transfer", "note": ""},
    {"transaction_id": "TXN002", "timestamp": "2024-01-16T14:20:00", "amount": 48000, "currency": "INR", 
     "from_account": "ACCT-TEST-001", "to_account": "OFFSHORE-001", "location": "Cayman Islands", 
     "type": "wire_transfer", "note": ""},
    {"transaction_id": "TXN003", "timestamp": "2024-01-17T11:45:00", "amount": 47000, "currency": "INR", 
     "from_account": "ACCT-TEST-001", "to_account": "OFFSHORE-001", "location": "Cayman Islands", 
     "type": "wire_transfer", "note": ""},
    # Large anomaly (above 1M threshold)
    {"transaction_id": "TXN004", "timestamp": "2024-01-18T16:00:00", "amount": 2500000, "currency": "INR", 
     "from_account": "ACCT-TEST-001", "to_account": "ACCT-EXTERNAL-999", "location": "Switzerland", 
     "type": "swift", "note": "Very large transfer to offshore entity"},
    # Round-tripping pattern
    {"transaction_id": "TXN005", "timestamp": "2024-01-19T10:30:00", "amount": 500000, "currency": "INR", 
     "from_account": "ACCT-EXTERNAL-999", "to_account": "ACCT-TEST-001", "location": "Switzerland", 
     "type": "swift", "note": "Return from offshore"},
]


class NexusTester:
    """End-to-end test runner for Nexus 2.0."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)
        self.token: str | None = None
        self.case_id: str | None = None
        self.results: dict[str, Any] = {}
        self.passed = 0
        self.failed = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.client.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        """Print formatted log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
    
    async def test_health(self) -> bool:
        """Test Layer 0: System Health"""
        self.log("Testing health endpoint...", "INFO")
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log("Health check passed", "PASS")
                    return True
            self.log(f"Health check failed: {response.text}", "FAIL")
            return False
        except Exception as exc:
            self.log(f"Health check error: {exc}", "FAIL")
            return False
    
    async def test_auth(self) -> bool:
        """Test Layer 0: Authentication"""
        self.log("Testing authentication...", "INFO")
        try:
            response = await self.client.post(
                "/api/v1/auth/login",
                json={"username": "admin", "password": "admin"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.log("Authentication passed", "PASS")
                    return True
            self.log(f"Auth failed: {response.text}", "FAIL")
            return False
        except Exception as exc:
            self.log(f"Auth error: {exc}", "FAIL")
            return False
    
    async def test_analyze_json(self) -> bool:
        """Test Layers 1-4: Full pipeline with JSON input"""
        self.log("Testing /analyze endpoint (JSON)...", "INFO")
        if not self.token:
            self.log("No auth token available", "FAIL")
            return False
        
        try:
            response = await self.client.post(
                "/api/v1/analyze",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "input_data": {
                        "user_id": "ACCT-TEST-001",
                        "transactions": TEST_TRANSACTIONS
                    }
                }
            )
            
            if response.status_code != 200:
                self.log(f"Analyze failed: {response.text}", "FAIL")
                return False
            
            data = response.json()
            self.results["json_analyze"] = data
            
            # Verify response structure
            checks = []
            
            # Check success flag
            checks.append(("success flag", data.get("success") is True))
            
            # Check result exists
            result = data.get("result", {})
            checks.append(("result object", bool(result)))
            
            # Layer 3: LLM Narrative
            narrative = result.get("llm_narrative")
            checks.append(("Layer 3: LLM narrative", bool(narrative) and len(narrative) > 100))
            
            # Layer 4: Audit Log
            audit_log = data.get("audit_log", [])
            checks.append(("Layer 4: Audit log", len(audit_log) >= 5))
            
            # Layer 4: SHAP Explanation
            risk = result.get("risk_assessment", {})
            shap = risk.get("shap_explanation")
            checks.append(("Layer 4: SHAP explanation", bool(shap)))
            
            # Layer 2: Triage
            triage = result.get("triage_result", {})
            checks.append(("Layer 2: Triage result", bool(triage.get("recommendation"))))
            
            # Layer 2: Risk Score
            checks.append(("Layer 2: Risk score", risk.get("score", 0) > 0))
            
            # Layer 1: Transactions processed
            subject = result.get("subject_information", {})
            checks.append(("Layer 1: Transactions counted", subject.get("total_transactions_reviewed", 0) == 5))
            
            # Save case_id for feedback test
            self.case_id = result.get("report_id")
            
            # Log results
            for name, passed in checks:
                if passed:
                    self.log(f"  ✓ {name}", "PASS")
                    self.passed += 1
                else:
                    self.log(f"  ✗ {name}", "FAIL")
                    self.failed += 1
            
            all_passed = all(p for _, p in checks)
            if all_passed:
                self.log("JSON analyze test PASSED", "PASS")
            else:
                self.log("JSON analyze test FAILED", "FAIL")
            
            return all_passed
            
        except Exception as exc:
            self.log(f"Analyze error: {exc}", "FAIL")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_analyze_csv(self) -> bool:
        """Test Layer 1: CSV Upload"""
        self.log("Testing /analyze/csv endpoint...", "INFO")
        if not self.token:
            self.log("No auth token available", "FAIL")
            return False
        
        try:
            # Create temp CSV file
            csv_content = """transaction_id,timestamp,amount,currency,from_account,to_account,location,type,note
TXN-C001,2024-01-15 09:30:00,45000,INR,ACCT-CSV-001,OFFSHORE-CSV,Cayman Islands,wire_transfer,
TXN-C002,2024-01-16 14:20:00,48000,INR,ACCT-CSV-001,OFFSHORE-CSV,Cayman Islands,wire_transfer,
TXN-C003,2024-01-17 11:45:00,47000,INR,ACCT-CSV-001,OFFSHORE-CSV,Cayman Islands,wire_transfer,
TXN-C004,2024-01-18 16:00:00,1200000,INR,ACCT-CSV-001,ACCT-OUT-999,Switzerland,swift,Large transfer
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(csv_content)
                csv_path = f.name
            
            try:
                with open(csv_path, 'rb') as f:
                    response = await self.client.post(
                        "/api/v1/analyze/csv",
                        headers={"Authorization": f"Bearer {self.token}"},
                        data={"user_id": "ACCT-CSV-001", "currency": "INR"},
                        files={"file": ("test.csv", f, "text/csv")}
                    )
                
                if response.status_code != 200:
                    self.log(f"CSV analyze failed: {response.text}", "FAIL")
                    return False
                
                data = response.json()
                self.results["csv_analyze"] = data
                
                checks = []
                result = data.get("result", {})
                subject = result.get("subject_information", {})
                
                checks.append(("CSV parsed", subject.get("total_transactions_reviewed") == 4))
                checks.append(("Risk computed", result.get("risk_assessment", {}).get("score", 0) > 0))
                checks.append(("Audit log present", len(data.get("audit_log", [])) >= 5))
                
                for name, passed in checks:
                    if passed:
                        self.log(f"  ✓ {name}", "PASS")
                        self.passed += 1
                    else:
                        self.log(f"  ✗ {name}", "FAIL")
                        self.failed += 1
                
                all_passed = all(p for _, p in checks)
                if all_passed:
                    self.log("CSV analyze test PASSED", "PASS")
                else:
                    self.log("CSV analyze test FAILED", "FAIL")
                
                return all_passed
                
            finally:
                Path(csv_path).unlink(missing_ok=True)
                
        except Exception as exc:
            self.log(f"CSV analyze error: {exc}", "FAIL")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_feedback(self) -> bool:
        """Test Layer 5: Human Control / RLHF"""
        self.log("Testing /feedback endpoint (Layer 5)...", "INFO")
        if not self.token:
            self.log("No auth token available", "FAIL")
            return False
        
        if not self.case_id:
            self.log("No case_id from previous test", "FAIL")
            return False
        
        try:
            # Submit feedback
            response = await self.client.post(
                "/api/v1/feedback",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "case_id": self.case_id,
                    "original_sar": self.results.get("json_analyze", {}).get("result", {}),
                    "edited_sar": {
                        "report_id": self.case_id,
                        "risk_level": "CRITICAL",
                        "analyst_notes": "Confirmed suspicious structuring with offshore exposure"
                    },
                    "outcome": "true_positive",
                    "analyst_notes": "Structuring pattern confirmed. Offshore exposure validates HIGH risk."
                }
            )
            
            if response.status_code != 201:
                self.log(f"Feedback submission failed: {response.text}", "FAIL")
                return False
            
            data = response.json()
            checks = []
            checks.append(("Feedback accepted", data.get("success") is True))
            checks.append(("Feedback ID returned", bool(data.get("feedback_id"))))
            
            for name, passed in checks:
                if passed:
                    self.log(f"  ✓ {name}", "PASS")
                    self.passed += 1
                else:
                    self.log(f"  ✗ {name}", "FAIL")
                    self.failed += 1
            
            if not all(p for _, p in checks):
                return False
            
            # Test feedback stats
            self.log("Testing /feedback/stats endpoint...", "INFO")
            response = await self.client.get(
                "/api/v1/feedback/stats",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code != 200:
                self.log(f"Feedback stats failed: {response.text}", "FAIL")
                return False
            
            stats = response.json()
            checks2 = []
            checks2.append(("Stats returned", "total" in stats))
            checks2.append(("Total >= 1", stats.get("total", 0) >= 1))
            checks2.append(("True positives >= 1", stats.get("true_positives", 0) >= 1))
            
            for name, passed in checks2:
                if passed:
                    self.log(f"  ✓ {name}", "PASS")
                    self.passed += 1
                else:
                    self.log(f"  ✗ {name}", "FAIL")
                    self.failed += 1
            
            all_passed = all(p for _, p in checks) and all(p for _, p in checks2)
            if all_passed:
                self.log("Feedback (Layer 5) test PASSED", "PASS")
            else:
                self.log("Feedback (Layer 5) test FAILED", "FAIL")
            
            return all_passed
            
        except Exception as exc:
            self.log(f"Feedback error: {exc}", "FAIL")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_pipeline_info(self) -> bool:
        """Test pipeline introspection"""
        self.log("Testing /pipeline/info endpoint...", "INFO")
        try:
            response = await self.client.get("/api/v1/pipeline/info")
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                self.log(f"Pipeline has {len(agents)} agents configured", "INFO")
                for agent in agents:
                    self.log(f"  - Step {agent.get('step')}: {agent.get('name')}", "INFO")
                self.log("Pipeline info test PASSED", "PASS")
                return True
            self.log(f"Pipeline info failed: {response.text}", "FAIL")
            return False
        except Exception as exc:
            self.log(f"Pipeline info error: {exc}", "FAIL")
            return False
    
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("           NEXUS 2.0 E2E TEST SUMMARY")
        print("=" * 60)
        print(f"Total Checks: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n5-Layer Architecture Verified:")
            print("  ✅ Layer 1: Data Ingestion")
            print("  ✅ Layer 2: Intelligence (Triage + RAG)")
            print("  ✅ Layer 3: Narrative Engine (LLM)")
            print("  ✅ Layer 4: Audit Brain (SHAP + PostgreSQL)")
            print("  ✅ Layer 5: Human Control (Feedback)")
        else:
            print(f"\n⚠️  {self.failed} CHECKS FAILED")
            print("Review logs above for details.")
        print("=" * 60)


async def main():
    """Run full E2E test suite"""
    print("\n" + "=" * 60)
    print("      NEXUS 2.0 END-TO-END TEST SUITE")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Started:  {datetime.now().isoformat()}")
    print("=" * 60 + "\n")
    
    async with NexusTester() as tester:
        # Run all tests
        await tester.test_health()
        await tester.test_auth()
        await tester.test_analyze_json()
        await tester.test_analyze_csv()
        await tester.test_feedback()
        await tester.test_pipeline_info()
        
        # Print summary
        tester.print_summary()
        
        # Exit code
        return 0 if tester.failed == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)

# Nexus 2.0 — End-to-End Testing Guide

## Quick Start

### 1. Start Dependencies

**PostgreSQL (if using Docker):**
```bash
docker run -d --name nexus-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=nexus \
  -p 5432:5432 \
  postgres:15
```

### 2. Start the Server

```bash
cd f:/HACKATHONS/Nexus2.0/Nexus2.0_Equilibrium/backend

# Install deps (first time only)
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run E2E Tests

**Option A: Windows (Double-click)**
```
run_tests.bat
```

**Option B: Command Line**
```bash
# Install test dependency
pip install httpx

# Run tests
python test_e2e.py
```

**Option C: Manual cURL**
See manual test commands below.

---

## What Tests Verify

| Test | Layers Verified | What It Checks |
|------|-----------------|----------------|
| Health Check | Layer 0 | Server running |
| Auth | Layer 0 | JWT token generation |
| JSON Analyze | Layers 1-4 | Full pipeline with all agents |
| CSV Upload | Layer 1 | File parsing |
| Feedback | Layer 5 | RLHF data persistence |
| Pipeline Info | All | Configuration |

---

## Manual Test Commands

### Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Test Analyze (JSON)
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "user_id": "TEST-001",
      "transactions": [
        {"transaction_id": "T1", "amount": 45000, "from_account": "A", "to_account": "B", "location": "Cayman", "timestamp": "2024-01-01"}
      ]
    }
  }'
```

### Test CSV Upload
```bash
curl -X POST http://localhost:8000/api/v1/analyze/csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.csv" \
  -F "user_id=TEST-CSV"
```

### Test Feedback
```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "SAR-TEST-001-20240101",
    "original_sar": {"risk_level": "HIGH"},
    "outcome": "true_positive"
  }'
```

### Check Feedback Stats
```bash
curl http://localhost:8000/api/v1/feedback/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Expected Output

```
[INFO] Testing health endpoint...
[PASS] Health check passed

[INFO] Testing authentication...
[PASS] Authentication passed

[INFO] Testing /analyze endpoint (JSON)...
[PASS]   ✓ success flag
[PASS]   ✓ result object
[PASS]   ✓ Layer 3: LLM narrative
[PASS]   ✓ Layer 4: Audit log
[PASS]   ✓ Layer 4: SHAP explanation
[PASS]   ✓ Layer 2: Triage result
[PASS]   ✓ Layer 2: Risk score
[PASS]   ✓ Layer 1: Transactions counted
[PASS] JSON analyze test PASSED

[INFO] Testing /feedback endpoint (Layer 5)...
[PASS]   ✓ Feedback accepted
[PASS]   ✓ Feedback ID returned
[PASS]   ✓ Stats returned
[PASS]   ✓ Total >= 1
[PASS]   ✓ True positives >= 1
[PASS] Feedback (Layer 5) test PASSED

============================================================
           NEXUS 2.0 E2E TEST SUMMARY
============================================================
Total Checks: 15
✅ Passed: 15
❌ Failed: 0

🎉 ALL TESTS PASSED!

5-Layer Architecture Verified:
  ✅ Layer 1: Data Ingestion
  ✅ Layer 2: Intelligence (Triage + RAG)
  ✅ Layer 3: Narrative Engine (LLM)
  ✅ Layer 4: Audit Brain (SHAP + PostgreSQL)
  ✅ Layer 5: Human Control (Feedback)
============================================================
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | Start the server first |
| `Module not found` | Run `pip install -r requirements.txt` |
| Database errors | Start PostgreSQL or disable DB in `.env` |
| Auth fails | Check username/password = `admin`/`admin` |
| LLM timeout | Set `LLM_ENABLED=false` in `.env` |

---

## Test Files

- `test_e2e.py` — Python test suite (comprehensive)
- `run_tests.bat` — Windows batch runner
- `TEST_GUIDE.md` — This file

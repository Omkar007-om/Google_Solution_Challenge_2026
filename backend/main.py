"""
NEXUS 2.0 — FastAPI Application Entry Point
SAR Narrative Generator with Glass-Box Audit Trail
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, insert_case, get_case, get_all_cases
from models import AlertSubmission, SARResult, CaseSummary
from sample_data import get_sample_alert

# ── Initialise app ──
app = FastAPI(
    title="NEXUS 2.0 — SAR Narrative Generator",
    description="Multi-agent LangGraph pipeline with FinCEN-compliant SAR generation and glass-box audit trail.",
    version="0.1.0",
)

# ── CORS (allow React dev server) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Lifecycle ──
@app.on_event("startup")
def on_startup():
    init_db()
    print("[NEXUS] Database initialised. Server ready.")


# ──────────────────────────────────────────────
#  Health & Utility
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "nexus-2.0"}


@app.get("/sample-alert/{case_type}")
def sample_alert(case_type: str = "elder_exploitation"):
    """Return a sample alert payload for testing / demo."""
    try:
        data = get_sample_alert(case_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return data


# ──────────────────────────────────────────────
#  SAR Pipeline Endpoints
# ──────────────────────────────────────────────

@app.post("/api/generate-sar", response_model=SARResult)
def generate_sar(submission: AlertSubmission):
    """
    Submit an alert to the SAR generation pipeline.
    Phase 4 will wire this up to the LangGraph workflow.
    For now, it stores the case and returns a stub.
    """
    # Check for duplicate
    existing = get_case(submission.case_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Case {submission.case_id} already exists. Use GET /api/cases/{{case_id}} to retrieve it.",
        )

    # Persist to DB
    row = insert_case(submission.case_id, submission.alert_data)

    # TODO (Phase 4): invoke LangGraph workflow here
    return SARResult(
        case_id=row["case_id"],
        status=row["status"],
        audit_log=[
            {"step": "intake", "action": "Case received and persisted", "data": f"case_id={row['case_id']}"}
        ],
    )


@app.get("/api/cases", response_model=list[CaseSummary])
def list_cases():
    """List all SAR cases (summary view)."""
    return get_all_cases()


@app.get("/api/cases/{case_id}", response_model=SARResult)
def get_sar_case(case_id: str):
    """Retrieve full SAR result + audit trail for a case."""
    row = get_case(case_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found.")
    return SARResult(
        case_id=row["case_id"],
        detected_typology=row.get("detected_typology", ""),
        typology_analysis=row.get("typology_analysis", ""),
        draft_sar_masked=row.get("draft_sar_masked", ""),
        final_sar_clean=row.get("final_sar_clean", ""),
        compliance_score=row.get("compliance_score", 0),
        audit_log=row.get("audit_log", []),
        status=row.get("status", "pending"),
    )


# ──────────────────────────────────────────────
#  Run with: uvicorn main:app --reload --port 8000
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""
Healthcare Agentic AI System — FastAPI Application.

Main entry point for the API server. Provides endpoints for:
- Patient inquiry submission
- System metrics dashboard
- Audit log retrieval
- Health checks
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import config
from src.models.schemas import (
    InquiryRequest, InquiryResponse, MetricsSummary,
    PatientInquiry, SystemHealthStatus,
)
from src.monitoring.alerts import get_active_alerts, get_alert_summary
from src.monitoring.logger import get_audit_logs, get_log_count
from src.monitoring.metrics import get_metrics_summary
from src.orchestrator.router import Orchestrator

# Track startup time
_startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print(f"🏥 {config.app_name} v{config.version} starting up...")
    print(f"📊 Orchestrator initialized with {len(orchestrator.agents)} specialized agents")
    print(f"🛡️  Guardrails: medical_safety, privacy_pii, safety_emergency")
    print(f"📡 Monitoring: audit_logger, metrics_tracker, alert_system")
    print(f"🚀 Server ready at http://{config.host}:{config.port}")
    yield
    print("👋 Shutting down Healthcare AI System...")


# Initialize orchestrator
orchestrator = Orchestrator()

# Create FastAPI app
app = FastAPI(
    title=config.app_name,
    version=config.version,
    description=(
        "Agentic AI system for healthcare patient inquiry management. "
        "Routes inquiries to specialized agents with guardrails and monitoring."
    ),
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── API Endpoints ───────────────────────────────────────────────────────────


@app.post("/api/inquiry", response_model=InquiryResponse)
async def submit_inquiry(request: InquiryRequest):
    """
    Submit a patient inquiry for processing.

    The orchestrator will:
    1. Check for emergency keywords
    2. Classify the intent
    3. Route to the appropriate agent
    4. Run guardrails on the response
    5. Log everything for compliance
    """
    try:
        inquiry = PatientInquiry(
            inquiry_text=request.inquiry_text,
            patient_id=request.patient_id,
            channel=request.channel,
        )
        response = orchestrator.process_inquiry(inquiry)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/api/metrics", response_model=MetricsSummary)
async def get_metrics():
    """Get current system metrics summary."""
    summary = get_metrics_summary()
    summary.active_alerts = get_alert_summary()["total_active"]
    return summary


@app.get("/api/logs")
async def get_logs(
    session_id: str | None = None,
    event_type: str | None = None,
    limit: int = 50,
):
    """
    Retrieve audit logs with optional filtering.

    All logs have PII redacted for compliance.
    """
    logs = get_audit_logs(session_id=session_id, event_type=event_type, limit=limit)
    return {
        "total_logs": get_log_count(),
        "returned": len(logs),
        "logs": [log.model_dump(mode="json") for log in logs],
    }


@app.get("/api/alerts")
async def get_alerts():
    """Get active alerts and alert summary."""
    active = get_active_alerts()
    return {
        "summary": get_alert_summary(),
        "active_alerts": [a.model_dump(mode="json") for a in active],
    }


@app.get("/api/health", response_model=SystemHealthStatus)
async def health_check():
    """System health check endpoint."""
    uptime = time.time() - _startup_time
    metrics = get_metrics_summary()

    return SystemHealthStatus(
        status="healthy",
        active_sessions=0,
        total_inquiries_processed=metrics.total_inquiries,
        uptime_seconds=round(uptime, 2),
        agents_status={
            "appointment": "active",
            "prescription": "active",
            "lab_report": "active",
            "escalation": "active",
        },
        guardrails_status={
            "medical_safety": "active",
            "privacy_pii": "active",
            "safety_emergency": "active",
        },
    )


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "system": config.app_name,
        "version": config.version,
        "status": "operational",
        "endpoints": {
            "submit_inquiry": "POST /api/inquiry",
            "get_metrics": "GET /api/metrics",
            "get_logs": "GET /api/logs",
            "get_alerts": "GET /api/alerts",
            "health_check": "GET /api/health",
            "api_docs": "GET /docs",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)

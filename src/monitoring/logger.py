"""
Structured Audit Logger.

Provides HIPAA-compliant structured logging with PII redaction.
Every decision, escalation, and guardrail check is logged.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from src.guardrails.privacy_guardrail import redact_pii
from src.models.schemas import (
    AgentType, AuditLogEntry, GuardrailResult, IntentClassification,
)

# Configure structured logger
logger = logging.getLogger("healthcare_ai_audit")
logger.setLevel(logging.INFO)

# In-memory audit log store (production: persistent database)
_audit_log: list[AuditLogEntry] = []


def log_inquiry_received(session_id: str, inquiry_text: str) -> AuditLogEntry:
    """Log when a patient inquiry is received."""
    entry = AuditLogEntry(
        session_id=session_id,
        event_type="inquiry_received",
        anonymized_inquiry=redact_pii(inquiry_text),
    )
    _store_entry(entry)
    logger.info(f"[INQUIRY] session={session_id} text_length={len(inquiry_text)}")
    return entry


def log_agent_routed(
    session_id: str, agent_type: AgentType,
    intent: IntentClassification,
) -> AuditLogEntry:
    """Log when an inquiry is routed to a specific agent."""
    entry = AuditLogEntry(
        session_id=session_id,
        event_type="agent_routed",
        agent_type=agent_type,
        intent_classification=intent,
        details={
            "confidence": intent.confidence,
            "matched_keywords": intent.matched_keywords,
        },
    )
    _store_entry(entry)
    logger.info(
        f"[ROUTED] session={session_id} agent={agent_type.value} "
        f"confidence={intent.confidence:.2f}"
    )
    return entry


def log_guardrail_check(
    session_id: str, results: list[GuardrailResult],
) -> AuditLogEntry:
    """Log the results of guardrail checks."""
    entry = AuditLogEntry(
        session_id=session_id,
        event_type="guardrail_check",
        guardrail_results=results,
        details={
            "total_checks": len(results),
            "passed": sum(1 for r in results if r.status.value == "passed"),
            "blocked": sum(1 for r in results if r.status.value == "blocked"),
            "warnings": sum(1 for r in results if r.status.value == "warning"),
        },
    )
    _store_entry(entry)

    for result in results:
        if result.status.value != "passed":
            logger.warning(
                f"[GUARDRAIL-{result.status.value.upper()}] "
                f"session={session_id} guardrail={result.guardrail_name} "
                f"violations={len(result.violations)}"
            )

    return entry


def log_response_sent(
    session_id: str, agent_type: AgentType,
    response_time_ms: float, was_escalated: bool,
) -> AuditLogEntry:
    """Log when a response is sent to the patient."""
    entry = AuditLogEntry(
        session_id=session_id,
        event_type="response_sent",
        agent_type=agent_type,
        response_time_ms=response_time_ms,
        details={"was_escalated": was_escalated},
    )
    _store_entry(entry)
    logger.info(
        f"[RESPONSE] session={session_id} agent={agent_type.value} "
        f"time_ms={response_time_ms:.1f} escalated={was_escalated}"
    )
    return entry


def log_escalation(
    session_id: str, agent_type: AgentType,
    priority: str, reason: str,
) -> AuditLogEntry:
    """Log an escalation event."""
    entry = AuditLogEntry(
        session_id=session_id,
        event_type="escalation",
        agent_type=agent_type,
        details={
            "priority": priority,
            "reason": redact_pii(reason),
        },
    )
    _store_entry(entry)
    logger.warning(
        f"[ESCALATION] session={session_id} priority={priority} "
        f"agent={agent_type.value}"
    )
    return entry


def get_audit_logs(
    session_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
) -> list[AuditLogEntry]:
    """Retrieve audit logs with optional filtering."""
    logs = _audit_log

    if session_id:
        logs = [l for l in logs if l.session_id == session_id]
    if event_type:
        logs = [l for l in logs if l.event_type == event_type]

    return logs[-limit:]


def get_log_count() -> int:
    """Get total number of audit log entries."""
    return len(_audit_log)


def _store_entry(entry: AuditLogEntry) -> None:
    """Store an audit log entry (in-memory for prototype)."""
    _audit_log.append(entry)

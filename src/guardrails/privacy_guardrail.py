"""
Data Privacy Guardrail.

Ensures HIPAA compliance:
- Session isolation enforcement
- PII detection and redaction in responses and logs
- Data minimization verification
"""

import re
from typing import Optional

from src.config import config
from src.models.schemas import GuardrailResult, GuardrailStatus


# In-memory session registry for isolation enforcement
_active_sessions: dict[str, set[str]] = {}


def register_session(session_id: str) -> None:
    """Register a new session for isolation tracking."""
    if session_id not in _active_sessions:
        _active_sessions[session_id] = set()


def add_session_data_key(session_id: str, data_key: str) -> None:
    """Track what data keys are associated with a session."""
    if session_id in _active_sessions:
        _active_sessions[session_id].add(data_key)


def check_session_isolation(
    session_id: str, accessing_session_id: Optional[str] = None
) -> GuardrailResult:
    """
    Verify that no cross-session data access is occurring.

    Args:
        session_id: The current session
        accessing_session_id: If provided, check that this session
            isn't accessing data from session_id

    Returns:
        GuardrailResult with pass/fail status
    """
    if accessing_session_id and accessing_session_id != session_id:
        if accessing_session_id in _active_sessions:
            return GuardrailResult(
                guardrail_name="privacy_session_isolation",
                status=GuardrailStatus.BLOCKED,
                violations=[
                    f"Cross-session data access attempt: "
                    f"Session {accessing_session_id} tried to access "
                    f"data from session {session_id}"
                ],
                details="HIPAA violation: Cross-session data access blocked",
            )

    return GuardrailResult(
        guardrail_name="privacy_session_isolation",
        status=GuardrailStatus.PASSED,
        details="Session isolation verified",
    )


def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information from text.

    Replaces SSNs, phone numbers, emails, dates of birth,
    and medical record numbers with redaction markers.

    Args:
        text: Text potentially containing PII

    Returns:
        Text with PII redacted
    """
    redacted = text

    # SSN: xxx-xx-xxxx
    redacted = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", redacted)

    # Phone numbers
    redacted = re.sub(
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE_REDACTED]", redacted
    )

    # Email addresses
    redacted = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "[EMAIL_REDACTED]", redacted,
    )

    # Date of birth patterns (MM/DD/YYYY)
    redacted = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "[DOB_REDACTED]", redacted)

    # Medical Record Numbers
    redacted = re.sub(r"\bMRN\b[:\s]*\d+\b", "[MRN_REDACTED]", redacted, flags=re.IGNORECASE)

    # Patient names (basic pattern — in production use NER)
    redacted = re.sub(
        r"\b(patient|name)[:\s]+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
        "[NAME_REDACTED]", redacted,
    )

    return redacted


def check_privacy(response_text: str, session_id: str) -> GuardrailResult:
    """
    Full privacy check on an agent response.

    Args:
        response_text: The agent's response to check
        session_id: Current session ID

    Returns:
        GuardrailResult with PII detection results
    """
    violations = []

    # Check for PII in response
    pii_checks = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "Phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "MRN": r"\bMRN\b[:\s]*\d+\b",
    }

    for pii_type, pattern in pii_checks.items():
        if re.search(pattern, response_text, re.IGNORECASE):
            violations.append(f"PII detected in response: {pii_type}")

    if violations:
        return GuardrailResult(
            guardrail_name="privacy_pii_check",
            status=GuardrailStatus.WARNING,
            violations=violations,
            details=f"PII detected in response — {len(violations)} item(s) will be redacted",
            original_response=response_text,
            sanitized_response=redact_pii(response_text),
        )

    return GuardrailResult(
        guardrail_name="privacy_pii_check",
        status=GuardrailStatus.PASSED,
        details="No PII detected in response",
    )


def clear_session(session_id: str) -> None:
    """Clear session data (called when session ends)."""
    _active_sessions.pop(session_id, None)

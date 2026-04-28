"""
Real-time Alert System.

Monitors system behavior and triggers alerts for:
- Critical escalations (life-threatening)
- Privacy breach attempts
- High escalation rates
- Guardrail trigger spikes
- Low confidence trends
- Response time degradation
"""

from datetime import datetime
from typing import Optional

from src.config import config
from src.models.schemas import AlertEvent, AlertSeverity, AgentType


# In-memory alert store
_alerts: list[AlertEvent] = []
_alert_counts_by_type: dict[str, int] = {}


def trigger_alert(
    severity: AlertSeverity,
    title: str,
    description: str,
    session_id: Optional[str] = None,
    agent_type: Optional[AgentType] = None,
) -> AlertEvent:
    """
    Trigger a new alert.

    Args:
        severity: Alert severity level
        title: Short alert title
        description: Detailed description
        session_id: Associated session (if applicable)
        agent_type: Associated agent (if applicable)

    Returns:
        The created AlertEvent
    """
    alert = AlertEvent(
        severity=severity,
        title=title,
        description=description,
        session_id=session_id,
        agent_type=agent_type,
    )
    _alerts.append(alert)

    # Track counts by type
    _alert_counts_by_type[title] = _alert_counts_by_type.get(title, 0) + 1

    return alert


def alert_critical_escalation(session_id: str, reason: str) -> AlertEvent:
    """Alert for life-threatening situations requiring immediate attention."""
    return trigger_alert(
        severity=AlertSeverity.CRITICAL,
        title="Critical Escalation",
        description=f"Life-threatening situation detected. Reason: {reason}",
        session_id=session_id,
    )


def alert_privacy_breach(session_id: str, details: str) -> AlertEvent:
    """Alert for privacy/HIPAA violation attempts."""
    return trigger_alert(
        severity=AlertSeverity.CRITICAL,
        title="Privacy Breach Attempt",
        description=f"Potential HIPAA violation detected. Details: {details}",
        session_id=session_id,
    )


def alert_high_escalation_rate(current_rate: float) -> AlertEvent:
    """Alert when escalation rate exceeds threshold."""
    return trigger_alert(
        severity=AlertSeverity.HIGH,
        title="High Escalation Rate",
        description=(
            f"Escalation rate ({current_rate:.1f}%) exceeds threshold "
            f"({config.monitoring.escalation_rate_alert_threshold * 100:.0f}%)"
        ),
    )


def alert_guardrail_spike(guardrail_name: str, trigger_count: int) -> AlertEvent:
    """Alert when guardrail triggers exceed normal rate."""
    return trigger_alert(
        severity=AlertSeverity.HIGH,
        title="Guardrail Trigger Spike",
        description=f"Guardrail '{guardrail_name}' triggered {trigger_count} times (above normal)",
    )


def alert_response_time_degradation(p95_ms: float) -> AlertEvent:
    """Alert when response times degrade."""
    return trigger_alert(
        severity=AlertSeverity.MEDIUM,
        title="Response Time Degradation",
        description=f"P95 response time ({p95_ms:.0f}ms) exceeds threshold ({config.monitoring.p95_response_time_alert_ms:.0f}ms)",
    )


def get_active_alerts(severity: Optional[AlertSeverity] = None) -> list[AlertEvent]:
    """Get all active (unresolved) alerts, optionally filtered by severity."""
    alerts = [a for a in _alerts if not a.resolved]
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    return alerts


def resolve_alert(alert_id: str) -> bool:
    """Mark an alert as resolved."""
    for alert in _alerts:
        if alert.alert_id == alert_id:
            alert.resolved = True
            return True
    return False


def get_alert_summary() -> dict:
    """Get a summary of alert counts by severity."""
    active = [a for a in _alerts if not a.resolved]
    return {
        "total_active": len(active),
        "critical": sum(1 for a in active if a.severity == AlertSeverity.CRITICAL),
        "high": sum(1 for a in active if a.severity == AlertSeverity.HIGH),
        "medium": sum(1 for a in active if a.severity == AlertSeverity.MEDIUM),
        "low": sum(1 for a in active if a.severity == AlertSeverity.LOW),
        "total_all_time": len(_alerts),
    }

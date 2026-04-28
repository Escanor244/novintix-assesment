"""
Success Metrics Tracker.

Tracks the 6 key success metrics defined in the system design:
1. First Response Time (FRT)
2. First Contact Resolution Rate (FCR)
3. Guardrail Compliance Rate
4. Patient Satisfaction Score (CSAT)
5. Escalation Appropriateness Rate
6. Zero PHI Leakage
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.models.schemas import InquiryCategory, MetricsSummary


@dataclass
class MetricsStore:
    """In-memory metrics storage (production: time-series DB)."""
    response_times_ms: list[float] = field(default_factory=list)
    total_inquiries: int = 0
    resolved_without_escalation: int = 0
    escalated_inquiries: int = 0
    guardrail_checks_total: int = 0
    guardrail_checks_passed: int = 0
    phi_leakage_incidents: int = 0
    inquiries_by_category: dict = field(default_factory=dict)
    _created_at: datetime = field(default_factory=datetime.utcnow)


# Singleton metrics store
_metrics = MetricsStore()


def record_inquiry(category: InquiryCategory) -> None:
    """Record a new inquiry."""
    _metrics.total_inquiries += 1
    cat = category.value
    _metrics.inquiries_by_category[cat] = _metrics.inquiries_by_category.get(cat, 0) + 1


def record_response_time(time_ms: float) -> None:
    """Record response time for an inquiry."""
    _metrics.response_times_ms.append(time_ms)


def record_resolution(escalated: bool) -> None:
    """Record whether an inquiry was resolved without escalation."""
    if escalated:
        _metrics.escalated_inquiries += 1
    else:
        _metrics.resolved_without_escalation += 1


def record_guardrail_check(passed: bool) -> None:
    """Record a guardrail check result."""
    _metrics.guardrail_checks_total += 1
    if passed:
        _metrics.guardrail_checks_passed += 1


def record_phi_leakage() -> None:
    """Record a PHI leakage incident (should always be 0)."""
    _metrics.phi_leakage_incidents += 1


def get_metrics_summary() -> MetricsSummary:
    """Calculate and return current metrics summary."""
    total = _metrics.total_inquiries or 1  # avoid division by zero

    # Average response time
    avg_rt = (
        sum(_metrics.response_times_ms) / len(_metrics.response_times_ms)
        if _metrics.response_times_ms else 0.0
    )

    # First Contact Resolution Rate
    fcr = _metrics.resolved_without_escalation / total * 100

    # Escalation rate
    esc_rate = _metrics.escalated_inquiries / total * 100

    # Guardrail compliance rate
    gc_total = _metrics.guardrail_checks_total or 1
    gc_rate = _metrics.guardrail_checks_passed / gc_total * 100

    return MetricsSummary(
        total_inquiries=_metrics.total_inquiries,
        avg_response_time_ms=round(avg_rt, 2),
        first_contact_resolution_rate=round(fcr, 2),
        escalation_rate=round(esc_rate, 2),
        guardrail_compliance_rate=round(gc_rate, 2),
        inquiries_by_category=_metrics.inquiries_by_category.copy(),
        period="since_startup",
    )


def reset_metrics() -> None:
    """Reset all metrics (for testing)."""
    global _metrics
    _metrics = MetricsStore()

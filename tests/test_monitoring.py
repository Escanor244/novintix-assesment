"""Tests for the monitoring system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.monitoring.logger import (
    log_inquiry_received, log_agent_routed, log_guardrail_check,
    log_response_sent, get_audit_logs,
)
from src.monitoring.metrics import (
    record_inquiry, record_response_time, record_resolution,
    record_guardrail_check as record_gc, get_metrics_summary, reset_metrics,
)
from src.monitoring.alerts import (
    trigger_alert, get_active_alerts, resolve_alert, get_alert_summary,
)
from src.models.schemas import (
    AgentType, AlertSeverity, GuardrailResult, GuardrailStatus,
    InquiryCategory, IntentClassification,
)


class TestAuditLogger:
    def test_log_inquiry(self):
        entry = log_inquiry_received("test-session-1", "Schedule an appointment")
        assert entry.session_id == "test-session-1"
        assert entry.event_type == "inquiry_received"
        assert entry.anonymized_inquiry is not None

    def test_pii_redacted_in_log(self):
        entry = log_inquiry_received("test-session-2", "My SSN is 123-45-6789")
        assert "123-45-6789" not in (entry.anonymized_inquiry or "")

    def test_log_agent_routed(self):
        intent = IntentClassification(
            category=InquiryCategory.APPOINTMENT, confidence=0.9
        )
        entry = log_agent_routed("test-session-3", AgentType.APPOINTMENT, intent)
        assert entry.event_type == "agent_routed"
        assert entry.agent_type == AgentType.APPOINTMENT

    def test_log_guardrail_check(self):
        results = [
            GuardrailResult(
                guardrail_name="medical_safety",
                status=GuardrailStatus.PASSED,
            )
        ]
        entry = log_guardrail_check("test-session-4", results)
        assert entry.event_type == "guardrail_check"
        assert entry.details["passed"] == 1

    def test_retrieve_logs_by_session(self):
        log_inquiry_received("filter-session", "Test inquiry")
        logs = get_audit_logs(session_id="filter-session")
        assert len(logs) >= 1
        assert all(l.session_id == "filter-session" for l in logs)


class TestMetrics:
    @pytest.fixture(autouse=True)
    def reset(self):
        reset_metrics()
        yield

    def test_record_inquiry(self):
        record_inquiry(InquiryCategory.APPOINTMENT)
        record_inquiry(InquiryCategory.PRESCRIPTION)
        summary = get_metrics_summary()
        assert summary.total_inquiries == 2

    def test_response_time(self):
        record_inquiry(InquiryCategory.APPOINTMENT)
        record_response_time(150.0)
        record_response_time(250.0)
        summary = get_metrics_summary()
        assert summary.avg_response_time_ms == 200.0

    def test_resolution_rate(self):
        record_inquiry(InquiryCategory.APPOINTMENT)
        record_inquiry(InquiryCategory.PRESCRIPTION)
        record_inquiry(InquiryCategory.ESCALATION)
        record_resolution(False)  # resolved
        record_resolution(False)  # resolved
        record_resolution(True)   # escalated
        summary = get_metrics_summary()
        assert summary.first_contact_resolution_rate > 60

    def test_guardrail_compliance(self):
        record_gc(True)
        record_gc(True)
        record_gc(False)
        summary = get_metrics_summary()
        assert 60 < summary.guardrail_compliance_rate < 70

    def test_inquiries_by_category(self):
        record_inquiry(InquiryCategory.APPOINTMENT)
        record_inquiry(InquiryCategory.APPOINTMENT)
        record_inquiry(InquiryCategory.PRESCRIPTION)
        summary = get_metrics_summary()
        assert summary.inquiries_by_category["appointment"] == 2
        assert summary.inquiries_by_category["prescription"] == 1


class TestAlerts:
    def test_trigger_alert(self):
        alert = trigger_alert(
            AlertSeverity.CRITICAL, "Test Alert", "Test description"
        )
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.resolved is False

    def test_get_active_alerts(self):
        trigger_alert(AlertSeverity.HIGH, "Active Alert", "Still active")
        active = get_active_alerts()
        assert len(active) > 0

    def test_resolve_alert(self):
        alert = trigger_alert(AlertSeverity.LOW, "Resolvable", "Will resolve")
        result = resolve_alert(alert.alert_id)
        assert result is True
        assert alert.resolved is True

    def test_alert_summary(self):
        summary = get_alert_summary()
        assert "total_active" in summary
        assert "critical" in summary

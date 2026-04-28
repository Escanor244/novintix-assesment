"""Tests for the Orchestrator — intent classification and routing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.orchestrator.router import Orchestrator
from src.models.schemas import (
    InquiryCategory, PatientInquiry, EscalationPriority,
)


@pytest.fixture
def orchestrator():
    return Orchestrator()


class TestIntentClassification:
    """Test intent classification accuracy."""

    def test_appointment_intent(self, orchestrator):
        result = orchestrator.classify_intent("I need to schedule an appointment")
        assert result.category == InquiryCategory.APPOINTMENT
        assert result.confidence >= 0.7

    def test_prescription_intent(self, orchestrator):
        result = orchestrator.classify_intent("I need to refill my medication")
        assert result.category == InquiryCategory.PRESCRIPTION
        assert result.confidence >= 0.7

    def test_lab_result_intent(self, orchestrator):
        result = orchestrator.classify_intent("What do my blood test results mean?")
        assert result.category == InquiryCategory.LAB_RESULT
        assert result.confidence >= 0.7

    def test_insurance_intent(self, orchestrator):
        result = orchestrator.classify_intent("What does my insurance coverage include?")
        assert result.category == InquiryCategory.INSURANCE

    def test_escalation_intent(self, orchestrator):
        result = orchestrator.classify_intent("I want to talk to a real person")
        assert result.category == InquiryCategory.ESCALATION

    def test_unknown_intent(self, orchestrator):
        result = orchestrator.classify_intent("asdfghjkl random text")
        assert result.category == InquiryCategory.UNKNOWN
        assert result.requires_escalation is True

    def test_low_confidence_triggers_escalation(self, orchestrator):
        result = orchestrator.classify_intent("maybe something about stuff")
        assert result.requires_escalation is True


class TestInquiryRouting:
    """Test end-to-end inquiry processing."""

    def test_appointment_routing(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="I want to schedule a checkup appointment")
        response = orchestrator.process_inquiry(inquiry)
        assert response.category == InquiryCategory.APPOINTMENT
        assert response.response_text  # Response is not empty
        assert response.response_time_ms > 0

    def test_prescription_routing(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="I need a refill for my lisinopril medication")
        response = orchestrator.process_inquiry(inquiry)
        assert response.category == InquiryCategory.PRESCRIPTION

    def test_lab_result_routing(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="Can you explain my CBC blood test results?")
        response = orchestrator.process_inquiry(inquiry)
        assert response.category == InquiryCategory.LAB_RESULT

    def test_emergency_routing(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="I'm having severe chest pain right now")
        response = orchestrator.process_inquiry(inquiry)
        assert response.was_escalated is True
        assert response.escalation_priority == EscalationPriority.P1_IMMEDIATE

    def test_human_request_routing(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="Let me talk to a real person please")
        response = orchestrator.process_inquiry(inquiry)
        assert response.was_escalated is True

    def test_controlled_substance_escalation(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="I need a refill for my oxycodone prescription")
        response = orchestrator.process_inquiry(inquiry)
        assert response.was_escalated is True

    def test_session_id_assigned(self, orchestrator):
        inquiry = PatientInquiry(inquiry_text="Schedule an appointment")
        response = orchestrator.process_inquiry(inquiry)
        assert response.session_id is not None
        assert len(response.session_id) > 0

"""Tests for specialized agents."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.agents.appointment_agent import AppointmentAgent
from src.agents.prescription_agent import PrescriptionAgent
from src.agents.lab_report_agent import LabReportAgent
from src.agents.escalation_agent import EscalationAgent
from src.models.schemas import (
    AgentType, EscalationPriority, InquiryCategory,
    IntentClassification, PatientInquiry,
)


@pytest.fixture
def appointment_agent():
    return AppointmentAgent()


@pytest.fixture
def prescription_agent():
    return PrescriptionAgent()


@pytest.fixture
def lab_agent():
    return LabReportAgent()


@pytest.fixture
def escalation_agent():
    return EscalationAgent()


def make_inquiry(text: str) -> PatientInquiry:
    return PatientInquiry(inquiry_text=text)


def make_intent(category: InquiryCategory, confidence: float = 0.9) -> IntentClassification:
    return IntentClassification(category=category, confidence=confidence)


class TestAppointmentAgent:
    def test_can_handle(self, appointment_agent):
        intent = make_intent(InquiryCategory.APPOINTMENT)
        assert appointment_agent.can_handle(intent) is True

    def test_cannot_handle_prescription(self, appointment_agent):
        intent = make_intent(InquiryCategory.PRESCRIPTION)
        assert appointment_agent.can_handle(intent) is False

    def test_schedule_response(self, appointment_agent):
        inquiry = make_inquiry("I want to schedule an appointment")
        intent = make_intent(InquiryCategory.APPOINTMENT)
        response = appointment_agent.process(inquiry, intent)
        assert response.agent_type == AgentType.APPOINTMENT
        assert "schedule" in response.response_text.lower() or "time" in response.response_text.lower()

    def test_cancel_triggers_escalation(self, appointment_agent):
        inquiry = make_inquiry("I want to cancel my appointment")
        intent = make_intent(InquiryCategory.APPOINTMENT)
        response = appointment_agent.process(inquiry, intent)
        assert response.requires_escalation is True

    def test_check_appointment(self, appointment_agent):
        inquiry = make_inquiry("When is my next appointment?")
        intent = make_intent(InquiryCategory.APPOINTMENT)
        response = appointment_agent.process(inquiry, intent)
        assert response.requires_escalation is False


class TestPrescriptionAgent:
    def test_can_handle(self, prescription_agent):
        intent = make_intent(InquiryCategory.PRESCRIPTION)
        assert prescription_agent.can_handle(intent) is True

    def test_refill_known_medication(self, prescription_agent):
        inquiry = make_inquiry("I need to refill my lisinopril")
        intent = make_intent(InquiryCategory.PRESCRIPTION)
        response = prescription_agent.process(inquiry, intent)
        assert "lisinopril" in response.response_text.lower()

    def test_controlled_substance_escalation(self, prescription_agent):
        inquiry = make_inquiry("I need more oxycodone")
        intent = make_intent(InquiryCategory.PRESCRIPTION)
        response = prescription_agent.process(inquiry, intent)
        assert response.requires_escalation is True
        assert response.escalation_priority == EscalationPriority.P2_URGENT

    def test_pharmacy_info(self, prescription_agent):
        inquiry = make_inquiry("Where is the pharmacy?")
        intent = make_intent(InquiryCategory.PRESCRIPTION)
        response = prescription_agent.process(inquiry, intent)
        assert "pharmacy" in response.response_text.lower()


class TestLabReportAgent:
    def test_can_handle(self, lab_agent):
        intent = make_intent(InquiryCategory.LAB_RESULT)
        assert lab_agent.can_handle(intent) is True

    def test_explain_cbc(self, lab_agent):
        inquiry = make_inquiry("Explain my CBC results")
        intent = make_intent(InquiryCategory.LAB_RESULT)
        response = lab_agent.process(inquiry, intent)
        assert "complete blood count" in response.response_text.lower()

    def test_critical_value_escalation(self, lab_agent):
        inquiry = make_inquiry("My results show critical abnormal values")
        intent = make_intent(InquiryCategory.LAB_RESULT)
        response = lab_agent.process(inquiry, intent)
        assert response.requires_escalation is True
        assert response.escalation_priority == EscalationPriority.P1_IMMEDIATE

    def test_diagnosis_request_redirect(self, lab_agent):
        inquiry = make_inquiry("Do I have diabetes based on my results?")
        intent = make_intent(InquiryCategory.LAB_RESULT)
        response = lab_agent.process(inquiry, intent)
        assert "diagnos" in response.response_text.lower() or "provider" in response.response_text.lower()


class TestEscalationAgent:
    def test_can_handle(self, escalation_agent):
        intent = make_intent(InquiryCategory.ESCALATION)
        assert escalation_agent.can_handle(intent) is True

    def test_always_escalates(self, escalation_agent):
        inquiry = make_inquiry("I want to speak to a human")
        intent = make_intent(InquiryCategory.ESCALATION)
        response = escalation_agent.process(inquiry, intent)
        assert response.requires_escalation is True

    def test_emergency_gets_p1(self, escalation_agent):
        inquiry = make_inquiry("I'm having chest pain and difficulty breathing")
        intent = make_intent(InquiryCategory.ESCALATION, confidence=0.3)
        response = escalation_agent.process(inquiry, intent)
        assert response.escalation_priority == EscalationPriority.P1_IMMEDIATE

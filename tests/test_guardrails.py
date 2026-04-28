"""Tests for guardrail enforcement."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.guardrails.medical_guardrail import check_medical_safety
from src.guardrails.privacy_guardrail import (
    check_privacy, redact_pii, check_session_isolation,
    register_session,
)
from src.guardrails.safety_guardrail import (
    check_emergency_keywords, check_critical_lab_values,
    check_negative_sentiment,
)
from src.models.schemas import GuardrailStatus


class TestMedicalGuardrail:
    def test_safe_response_passes(self):
        result = check_medical_safety(
            "Here are your available appointment times for next week."
        )
        assert result.status == GuardrailStatus.PASSED

    def test_diagnosis_blocked(self):
        result = check_medical_safety(
            "Based on your results, you have a disease called diabetes."
        )
        assert result.status == GuardrailStatus.BLOCKED
        assert len(result.violations) > 0

    def test_treatment_recommendation_blocked(self):
        result = check_medical_safety(
            "You should take 500mg of this medication daily."
        )
        assert result.status == GuardrailStatus.BLOCKED

    def test_dosage_change_blocked(self):
        result = check_medical_safety(
            "I recommend you increase your dosage of medication."
        )
        assert result.status == GuardrailStatus.BLOCKED

    def test_safe_educational_content_passes(self):
        result = check_medical_safety(
            "A CBC measures several components of your blood including "
            "red blood cells and white blood cells. Please consult your "
            "healthcare provider for interpretation."
        )
        assert result.status == GuardrailStatus.PASSED


class TestPrivacyGuardrail:
    def test_clean_response_passes(self):
        result = check_privacy("Your appointment is on Monday.", "session-1")
        assert result.status == GuardrailStatus.PASSED

    def test_ssn_detected(self):
        result = check_privacy("Your SSN is 123-45-6789", "session-1")
        assert result.status == GuardrailStatus.WARNING
        assert len(result.violations) > 0

    def test_pii_redaction_ssn(self):
        redacted = redact_pii("Patient SSN: 123-45-6789")
        assert "123-45-6789" not in redacted
        assert "[SSN_REDACTED]" in redacted

    def test_pii_redaction_email(self):
        redacted = redact_pii("Contact: john@example.com")
        assert "john@example.com" not in redacted
        assert "[EMAIL_REDACTED]" in redacted

    def test_pii_redaction_mrn(self):
        redacted = redact_pii("MRN: 12345678")
        assert "12345678" not in redacted

    def test_session_isolation(self):
        register_session("session-a")
        register_session("session-b")
        result = check_session_isolation("session-a", "session-b")
        assert result.status == GuardrailStatus.BLOCKED

    def test_same_session_access_passes(self):
        register_session("session-c")
        result = check_session_isolation("session-c", "session-c")
        assert result.status == GuardrailStatus.PASSED


class TestSafetyGuardrail:
    def test_normal_text_passes(self):
        result = check_emergency_keywords("I want to schedule an appointment")
        assert result.status == GuardrailStatus.PASSED

    def test_chest_pain_detected(self):
        result = check_emergency_keywords("I'm having chest pain")
        assert result.status == GuardrailStatus.BLOCKED

    def test_suicidal_ideation_detected(self):
        result = check_emergency_keywords("I'm feeling suicidal")
        assert result.status == GuardrailStatus.BLOCKED

    def test_difficulty_breathing_detected(self):
        result = check_emergency_keywords("I can't breathe properly, difficulty breathing")
        assert result.status == GuardrailStatus.BLOCKED

    def test_critical_lab_high_potassium(self):
        result = check_critical_lab_values({"potassium": 7.5})
        assert result.status == GuardrailStatus.BLOCKED
        assert "CRITICAL HIGH" in result.violations[0]

    def test_critical_lab_low_glucose(self):
        result = check_critical_lab_values({"glucose": 30})
        assert result.status == GuardrailStatus.BLOCKED
        assert "CRITICAL LOW" in result.violations[0]

    def test_normal_lab_passes(self):
        result = check_critical_lab_values({"potassium": 4.0, "glucose": 100})
        assert result.status == GuardrailStatus.PASSED

    def test_negative_sentiment_single_keyword(self):
        result = check_negative_sentiment("I'm frustrated with the wait")
        assert result.status == GuardrailStatus.PASSED  # Single keyword = no warning

    def test_negative_sentiment_multiple_keywords(self):
        result = check_negative_sentiment("This is terrible and unacceptable service")
        assert result.status == GuardrailStatus.WARNING

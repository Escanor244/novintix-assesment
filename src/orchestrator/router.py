"""
Orchestrator — Central Request Router.

The orchestrator is the central nervous system of the agentic AI system:
1. Classifies patient inquiry intent
2. Routes to the appropriate specialized agent
3. Enforces guardrails on every response
4. Manages session isolation
5. Logs every decision for compliance
"""

import time
from typing import Optional

from src.agents.appointment_agent import AppointmentAgent
from src.agents.escalation_agent import EscalationAgent
from src.agents.lab_report_agent import LabReportAgent
from src.agents.prescription_agent import PrescriptionAgent
from src.agents.base_agent import BaseAgent
from src.config import config
from src.guardrails.medical_guardrail import check_medical_safety
from src.guardrails.privacy_guardrail import (
    check_privacy, register_session, clear_session, redact_pii,
)
from src.guardrails.safety_guardrail import (
    check_emergency_keywords, check_negative_sentiment,
)
from src.llm.client import LLMClient
from src.models.schemas import (
    AgentResponse, AgentType, EscalationPriority,
    GuardrailResult, GuardrailStatus,
    InquiryCategory, InquiryResponse,
    IntentClassification, PatientInquiry,
)
from src.monitoring import logger as audit_logger
from src.monitoring.alerts import (
    alert_critical_escalation, alert_privacy_breach,
)
from src.monitoring.metrics import (
    record_guardrail_check, record_inquiry,
    record_resolution, record_response_time,
)


class Orchestrator:
    """
    Central orchestrator that manages the entire inquiry lifecycle.

    Flow:
    1. Receive inquiry
    2. Pre-flight safety check (emergency keywords)
    3. Classify intent
    4. Route to agent
    5. Run guardrails on response
    6. Return response (or escalate)
    7. Log everything
    """

    # Intent classification keywords
    INTENT_KEYWORDS = {
        InquiryCategory.APPOINTMENT: [
            "appointment", "schedule", "reschedule", "cancel appointment",
            "book", "visit", "checkup", "check-up", "see the doctor",
            "availability", "available slots", "when can i come",
        ],
        InquiryCategory.PRESCRIPTION: [
            "prescription", "medication", "medicine", "refill", "drug",
            "pharmacy", "dosage", "pill", "tablet", "rx",
        ],
        InquiryCategory.LAB_RESULT: [
            "lab", "test result", "blood work", "blood test", "results",
            "report", "panel", "cbc", "metabolic", "lipid", "a1c",
            "thyroid test",
        ],
        InquiryCategory.INSURANCE: [
            "insurance", "coverage", "claim", "copay", "deductible",
            "authorization", "billing", "payment",
        ],
        InquiryCategory.ESCALATION: [
            "human", "real person", "agent", "representative", "operator",
            "talk to someone", "speak to someone", "help me",
        ],
    }

    def __init__(self):
        # Initialize specialized agents
        self.agents: dict[InquiryCategory, BaseAgent] = {
            InquiryCategory.APPOINTMENT: AppointmentAgent(),
            InquiryCategory.PRESCRIPTION: PrescriptionAgent(),
            InquiryCategory.LAB_RESULT: LabReportAgent(),
            InquiryCategory.ESCALATION: EscalationAgent(),
        }
        self.escalation_agent = EscalationAgent()
        self.llm = LLMClient(config.llm)

    def process_inquiry(self, inquiry: PatientInquiry) -> InquiryResponse:
        """
        Process a patient inquiry through the full pipeline.

        Args:
            inquiry: The patient's inquiry

        Returns:
            InquiryResponse with the final response
        """
        start_time = time.time()

        # Register session for isolation
        register_session(inquiry.session_id)

        # Log inquiry received
        audit_logger.log_inquiry_received(inquiry.session_id, inquiry.inquiry_text)

        # Step 1: Pre-flight safety check
        emergency_check = check_emergency_keywords(inquiry.inquiry_text)
        if emergency_check.status == GuardrailStatus.BLOCKED:
            return self._handle_emergency(inquiry, emergency_check, start_time)

        # Step 2: Classify intent
        intent = self.classify_intent(inquiry.inquiry_text)

        # Step 3: Route to agent
        agent_response = self._route_to_agent(inquiry, intent)

        # Log routing
        audit_logger.log_agent_routed(
            inquiry.session_id, agent_response.agent_type, intent
        )

        # Step 4: Run guardrails on response
        guardrail_results = self._run_guardrails(
            agent_response.response_text, inquiry.session_id
        )

        # Log guardrail checks
        audit_logger.log_guardrail_check(inquiry.session_id, guardrail_results)

        # Record guardrail metrics
        all_passed = all(r.status == GuardrailStatus.PASSED for r in guardrail_results)
        record_guardrail_check(all_passed)

        # Step 5: Apply guardrail results
        final_response_text = self._apply_guardrails(
            agent_response.response_text, guardrail_results
        )

        # Check if escalation is needed
        was_escalated = agent_response.requires_escalation
        if any(r.status == GuardrailStatus.BLOCKED for r in guardrail_results):
            was_escalated = True

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Record metrics
        record_inquiry(intent.category)
        record_response_time(response_time_ms)
        record_resolution(was_escalated)

        # Log response
        audit_logger.log_response_sent(
            inquiry.session_id, agent_response.agent_type,
            response_time_ms, was_escalated,
        )

        if was_escalated:
            audit_logger.log_escalation(
                inquiry.session_id, agent_response.agent_type,
                (agent_response.escalation_priority or EscalationPriority.P3_STANDARD).value,
                agent_response.escalation_reason or "Guardrail blocked response",
            )

        # Clean up session
        clear_session(inquiry.session_id)

        return InquiryResponse(
            session_id=inquiry.session_id,
            response_text=final_response_text,
            category=intent.category,
            was_escalated=was_escalated,
            escalation_priority=agent_response.escalation_priority,
            response_time_ms=round(response_time_ms, 2),
            guardrails_passed=all_passed,
        )

    def classify_intent(self, text: str) -> IntentClassification:
        """
        Classify the intent of a patient inquiry.

        Uses keyword matching with confidence scoring.
        In production, this would use an ML model.

        Args:
            text: The inquiry text

        Returns:
            IntentClassification with category and confidence
        """
        if config.llm.enabled:
            llm_intent = self.llm.classify_intent(text)
            if llm_intent:
                return llm_intent

        text_lower = text.lower()
        scores: dict[InquiryCategory, float] = {}
        matched: dict[InquiryCategory, list[str]] = {}

        for category, keywords in self.INTENT_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                # Score based on number of keyword matches
                scores[category] = min(len(matches) * 0.3 + 0.4, 0.95)
                matched[category] = matches

        if not scores:
            return IntentClassification(
                category=InquiryCategory.UNKNOWN,
                confidence=0.1,
                requires_escalation=True,
                escalation_reason="Could not classify inquiry intent",
            )

        # Select highest scoring category
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]

        # Check if confidence is below threshold
        requires_escalation = confidence < config.orchestrator.high_confidence_threshold

        return IntentClassification(
            category=best_category,
            confidence=confidence,
            matched_keywords=matched.get(best_category, []),
            requires_escalation=requires_escalation,
            escalation_reason=(
                f"Low confidence ({confidence:.2f}) for category {best_category.value}"
                if requires_escalation else None
            ),
        )

    def _route_to_agent(
        self, inquiry: PatientInquiry, intent: IntentClassification
    ) -> AgentResponse:
        """Route inquiry to the appropriate agent."""
        # If confidence is too low, escalate directly
        if intent.confidence < config.orchestrator.low_confidence_threshold:
            return self.escalation_agent.process(inquiry, intent)

        # If category requires escalation or is unknown
        if intent.requires_escalation or intent.category == InquiryCategory.UNKNOWN:
            return self.escalation_agent.process(inquiry, intent)

        # Insurance inquiries escalate (no dedicated agent in prototype)
        if intent.category == InquiryCategory.INSURANCE:
            intent_for_escalation = IntentClassification(
                category=InquiryCategory.ESCALATION,
                confidence=intent.confidence,
                matched_keywords=intent.matched_keywords,
                requires_escalation=True,
                escalation_reason="Insurance inquiries require human specialist",
            )
            return self.escalation_agent.process(inquiry, intent_for_escalation)

        # Route to specialized agent
        agent = self.agents.get(intent.category)
        if agent and agent.can_handle(intent):
            return agent.process(inquiry, intent)

        # Fallback to escalation
        return self.escalation_agent.process(inquiry, intent)

    def _run_guardrails(
        self, response_text: str, session_id: str
    ) -> list[GuardrailResult]:
        """Run all guardrails on an agent response."""
        results = []

        # 1. Medical safety check
        medical_result = check_medical_safety(response_text)
        results.append(medical_result)

        # 2. Privacy check
        privacy_result = check_privacy(response_text, session_id)
        results.append(privacy_result)

        # 3. Negative sentiment check (on original inquiry isn't available here,
        #    but we check the response for inappropriate content)
        sentiment_result = check_negative_sentiment(response_text)
        results.append(sentiment_result)

        return results

    def _apply_guardrails(
        self, response_text: str, results: list[GuardrailResult]
    ) -> str:
        """Apply guardrail results to the response text."""
        final_text = response_text

        for result in results:
            if result.status == GuardrailStatus.BLOCKED and result.sanitized_response:
                # If blocked, use the sanitized response
                final_text = result.sanitized_response
                break  # Use the first blocking guardrail's response
            elif result.status == GuardrailStatus.WARNING and result.sanitized_response:
                # If warning with sanitization, apply it
                final_text = result.sanitized_response

        return final_text

    def _handle_emergency(
        self, inquiry: PatientInquiry,
        emergency_check: GuardrailResult, start_time: float,
    ) -> InquiryResponse:
        """Handle emergency situations with immediate escalation."""
        response_time_ms = (time.time() - start_time) * 1000

        # Trigger critical alert
        alert_critical_escalation(
            inquiry.session_id,
            "; ".join(emergency_check.violations),
        )

        # Record metrics
        record_inquiry(InquiryCategory.ESCALATION)
        record_response_time(response_time_ms)
        record_resolution(True)
        record_guardrail_check(True)  # Guardrail worked correctly

        # Log
        audit_logger.log_escalation(
            inquiry.session_id, AgentType.ORCHESTRATOR,
            EscalationPriority.P1_IMMEDIATE.value,
            "Emergency keywords detected in inquiry",
        )

        clear_session(inquiry.session_id)

        return InquiryResponse(
            session_id=inquiry.session_id,
            response_text=emergency_check.sanitized_response or (
                "⚠️ If you are experiencing a medical emergency, "
                "please call 911 immediately. I'm connecting you "
                "with our clinical team now."
            ),
            category=InquiryCategory.ESCALATION,
            was_escalated=True,
            escalation_priority=EscalationPriority.P1_IMMEDIATE,
            response_time_ms=round(response_time_ms, 2),
            guardrails_passed=True,
        )

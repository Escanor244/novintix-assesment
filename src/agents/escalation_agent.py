"""
Human Escalation Agent.

Manages handoff to human agents by packaging context,
determining priority, and routing to the appropriate team.
"""

from src.agents.base_agent import BaseAgent
from src.config import config
from src.models.schemas import (
    AgentResponse, AgentType, EscalationPriority,
    InquiryCategory, IntentClassification, PatientInquiry,
)


class EscalationAgent(BaseAgent):
    """Specialized agent for human escalation and handoff."""

    HUMAN_REQUEST_KEYWORDS = [
        "human", "real person", "agent", "representative",
        "talk to someone", "speak to someone", "operator",
    ]

    def __init__(self):
        super().__init__(AgentType.ESCALATION)

    def can_handle(self, intent: IntentClassification) -> bool:
        return intent.category == InquiryCategory.ESCALATION

    def process(self, inquiry: PatientInquiry, intent: IntentClassification) -> AgentResponse:
        text_lower = inquiry.inquiry_text.lower()

        # Determine escalation priority
        priority = self._determine_priority(text_lower, intent)

        # Build context summary for human agent
        context = self._build_context_summary(inquiry, intent, priority)

        # Generate appropriate response
        if priority == EscalationPriority.P1_IMMEDIATE:
            return self._handle_p1(inquiry, context)
        elif priority == EscalationPriority.P2_URGENT:
            return self._handle_p2(inquiry, context)
        else:
            return self._handle_standard(inquiry, context, priority)

    def _determine_priority(self, text: str, intent: IntentClassification) -> EscalationPriority:
        """Determine escalation priority based on content analysis."""
        # P1: Life-threatening
        for kw in config.guardrails.emergency_keywords:
            if kw in text:
                return EscalationPriority.P1_IMMEDIATE

        # P2: Controlled substances, high distress
        for kw in config.guardrails.controlled_substances:
            if kw in text:
                return EscalationPriority.P2_URGENT

        for kw in config.guardrails.negative_sentiment_keywords:
            if kw in text:
                return EscalationPriority.P2_URGENT

        # P3: Low confidence, explicit human request, or default
        if intent.confidence < config.orchestrator.low_confidence_threshold:
            return EscalationPriority.P3_STANDARD

        return EscalationPriority.P3_STANDARD

    def _build_context_summary(
        self, inquiry: PatientInquiry, intent: IntentClassification,
        priority: EscalationPriority,
    ) -> str:
        """Build a structured context summary for the human agent."""
        return (
            f"Session: {inquiry.session_id}\n"
            f"Priority: {priority.value}\n"
            f"Category: {intent.category.value}\n"
            f"Confidence: {intent.confidence:.2f}\n"
            f"Inquiry: {inquiry.inquiry_text}\n"
            f"Matched keywords: {', '.join(intent.matched_keywords)}"
        )

    def _handle_p1(self, inquiry: PatientInquiry, context: str) -> AgentResponse:
        """Handle P1 (immediate) escalations — life-threatening situations."""
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "⚠️ **If you are experiencing a medical emergency, please call 911 immediately.**\n\n"
                "I'm connecting you with our clinical team right now. "
                "A healthcare professional will be with you momentarily. "
                "Please do not hang up."
            ),
            actions=["emergency_detected", "p1_escalation_initiated", "clinical_team_alerted"],
            confidence=1.0,
            requires_escalation=True,
            escalation_priority=EscalationPriority.P1_IMMEDIATE,
            escalation_reason="Life-threatening keywords detected — immediate clinical review required",
            metadata={"context_summary": context},
        )

    def _handle_p2(self, inquiry: PatientInquiry, context: str) -> AgentResponse:
        """Handle P2 (urgent) escalations."""
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I understand this is important to you. I'm connecting you "
                "with a member of our healthcare team who can assist you "
                "directly. Expected wait time is under 15 minutes.\n\n"
                "Your inquiry has been flagged as a priority and a team "
                "member will reach out to you shortly."
            ),
            actions=["p2_escalation_initiated", "priority_queue_assigned"],
            confidence=0.95,
            requires_escalation=True,
            escalation_priority=EscalationPriority.P2_URGENT,
            escalation_reason="Urgent inquiry requiring human specialist attention",
            metadata={"context_summary": context},
        )

    def _handle_standard(
        self, inquiry: PatientInquiry, context: str,
        priority: EscalationPriority,
    ) -> AgentResponse:
        """Handle P3/P4 (standard/review) escalations."""
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I'm connecting you with a member of our team who can "
                "help you with this request. A staff member will be "
                "available to assist you shortly.\n\n"
                "Your conversation context has been shared so you "
                "won't need to repeat your question. Thank you for your patience."
            ),
            actions=["standard_escalation_initiated", "context_packaged"],
            confidence=0.9,
            requires_escalation=True,
            escalation_priority=priority,
            escalation_reason="Inquiry requires human assistance",
            metadata={"context_summary": context},
        )

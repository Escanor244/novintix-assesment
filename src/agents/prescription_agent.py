"""
Prescription Validation Agent.

Handles prescription refills, medication info, pharmacy queries.
SAFETY: Never provides dosage changes, never handles controlled
substances without human oversight.
"""

from src.agents.base_agent import BaseAgent
from src.config import config
from src.models.schemas import (
    AgentResponse, AgentType, EscalationPriority,
    InquiryCategory, IntentClassification, PatientInquiry,
)


class PrescriptionAgent(BaseAgent):
    """Specialized agent for prescription-related inquiries."""

    APPROVED_MEDICATIONS = {
        "lisinopril": {"category": "ACE Inhibitor", "common_use": "blood pressure management", "refill_eligible": True},
        "metformin": {"category": "Antidiabetic", "common_use": "blood sugar management", "refill_eligible": True},
        "atorvastatin": {"category": "Statin", "common_use": "cholesterol management", "refill_eligible": True},
        "levothyroxine": {"category": "Thyroid Hormone", "common_use": "thyroid hormone replacement", "refill_eligible": True},
        "amlodipine": {"category": "Calcium Channel Blocker", "common_use": "blood pressure management", "refill_eligible": True},
        "omeprazole": {"category": "Proton Pump Inhibitor", "common_use": "acid reflux management", "refill_eligible": True},
        "sertraline": {"category": "SSRI", "common_use": "mental health support", "refill_eligible": True},
    }

    REFILL_KEYWORDS = ["refill", "renew", "run out", "running low", "need more"]
    INFO_KEYWORDS = ["what is", "what does", "side effect", "how to take", "information about"]
    PHARMACY_KEYWORDS = ["pharmacy", "pick up", "transfer", "drugstore"]

    def __init__(self):
        super().__init__(AgentType.PRESCRIPTION)

    def can_handle(self, intent: IntentClassification) -> bool:
        return intent.category == InquiryCategory.PRESCRIPTION

    def process(self, inquiry: PatientInquiry, intent: IntentClassification) -> AgentResponse:
        text_lower = inquiry.inquiry_text.lower()

        # SAFETY: Detect controlled substances first
        detected = self._detect_controlled_substances(text_lower)
        if detected:
            return self._escalate_controlled(inquiry, detected)

        if any(kw in text_lower for kw in self.REFILL_KEYWORDS):
            return self._handle_refill(inquiry, text_lower)
        elif any(kw in text_lower for kw in self.PHARMACY_KEYWORDS):
            return self._handle_pharmacy(inquiry)
        elif any(kw in text_lower for kw in self.INFO_KEYWORDS):
            return self._handle_info(inquiry, text_lower)
        else:
            return self._handle_general(inquiry)

    def _detect_controlled_substances(self, text: str) -> list[str]:
        return [s for s in config.guardrails.controlled_substances if s in text]

    def _escalate_controlled(self, inquiry: PatientInquiry, substances: list[str]) -> AgentResponse:
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I understand you have a question about your medication. "
                "For your safety, inquiries involving certain medications "
                "require direct assistance from our pharmacy team. "
                "I'm connecting you with a pharmacist who can help right away."
            ),
            actions=["controlled_substance_detected", "escalated_to_pharmacist"],
            confidence=0.95,
            requires_escalation=True,
            escalation_priority=EscalationPriority.P2_URGENT,
            escalation_reason=f"Controlled substance inquiry: {', '.join(substances)}",
            metadata={"sub_intent": "controlled_substance", "detected_substances": substances},
        )

    def _handle_refill(self, inquiry: PatientInquiry, text: str) -> AgentResponse:
        identified_med = next((m for m in self.APPROVED_MEDICATIONS if m in text), None)

        if identified_med:
            med = self.APPROVED_MEDICATIONS[identified_med]
            response = (
                f"I've located your prescription for **{identified_med.title()}** "
                f"({med['category']}) used for {med['common_use']}.\n\n"
                f"✅ Your refill request has been submitted to your pharmacy. "
                f"You should be able to pick it up within 24-48 hours.\n\n"
                f"If your provider has made any changes, the pharmacy will contact you."
            )
            actions = ["medication_identified", "refill_submitted"]
        else:
            response = (
                "I'd be happy to help with a prescription refill. "
                "Could you provide the name of the medication you'd like to refill?"
            )
            actions = ["refill_requested", "awaiting_medication_name"]

        return self._create_response(
            session_id=inquiry.session_id, response_text=response,
            actions=actions, confidence=0.85 if identified_med else 0.7,
            metadata={"sub_intent": "refill", "identified_medication": identified_med},
        )

    def _handle_info(self, inquiry: PatientInquiry, text: str) -> AgentResponse:
        identified_med = next((m for m in self.APPROVED_MEDICATIONS if m in text), None)

        if identified_med:
            med = self.APPROVED_MEDICATIONS[identified_med]
            response = (
                f"Here's general information about **{identified_med.title()}**:\n\n"
                f"  💊 Category: {med['category']}\n"
                f"  📋 Common use: {med['common_use']}\n\n"
                f"For specific questions about dosage or side effects, "
                f"please consult your healthcare provider or pharmacist."
            )
        else:
            response = (
                "Could you tell me the name of the medication you're asking about? "
                "For detailed dosage or side effect questions, I recommend speaking "
                "with your healthcare provider or pharmacist."
            )

        return self._create_response(
            session_id=inquiry.session_id, response_text=response,
            actions=["medication_info_provided"], confidence=0.85,
            metadata={"sub_intent": "info", "identified_medication": identified_med},
        )

    def _handle_pharmacy(self, inquiry: PatientInquiry) -> AgentResponse:
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "Pharmacy information:\n\n"
                "  🏥 **Main Clinic Pharmacy**: Mon-Fri 8AM-6PM, Sat 9AM-1PM\n"
                "  📞 **Phone**: (555) 123-4567\n"
                "  💊 **Mail Order**: Available for maintenance medications\n\n"
                "I can connect you with our pharmacy team for transfers."
            ),
            actions=["pharmacy_info_provided"], confidence=0.9,
            metadata={"sub_intent": "pharmacy"},
        )

    def _handle_general(self, inquiry: PatientInquiry) -> AgentResponse:
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I can assist with:\n\n"
                "  • 💊 Prescription refills\n"
                "  • ℹ️ General medication information\n"
                "  • 🏥 Pharmacy hours and locations\n\n"
                "What do you need help with?"
            ),
            actions=["general_prescription_inquiry"], confidence=0.75,
            metadata={"sub_intent": "general"},
        )

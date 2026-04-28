"""
Lab Report Explanation Agent.

Explains lab results in plain language using approved templates.
SAFETY: Never provides diagnoses. Critical values trigger
immediate escalation with no AI interpretation.
"""

from src.agents.base_agent import BaseAgent
from src.config import config
from src.models.schemas import (
    AgentResponse, AgentType, EscalationPriority,
    InquiryCategory, IntentClassification, PatientInquiry,
)


class LabReportAgent(BaseAgent):
    """Specialized agent for lab report explanation."""

    # Approved educational content templates
    LAB_EXPLANATIONS = {
        "cbc": {
            "full_name": "Complete Blood Count (CBC)",
            "description": (
                "A CBC measures several components of your blood including red blood cells, "
                "white blood cells, and platelets. It helps your doctor assess your overall "
                "health and detect a wide range of conditions."
            ),
            "common_components": ["White Blood Cells (WBC)", "Red Blood Cells (RBC)", "Hemoglobin", "Platelets"],
        },
        "blood": {
            "full_name": "Blood Panel",
            "description": (
                "A blood panel is a group of tests that measures various substances in your blood. "
                "The specific tests depend on what your doctor ordered. Results are compared against "
                "reference ranges to identify any values outside the normal range."
            ),
            "common_components": ["Glucose", "Cholesterol", "Electrolytes", "Liver enzymes"],
        },
        "metabolic": {
            "full_name": "Comprehensive Metabolic Panel (CMP)",
            "description": (
                "A CMP measures 14 substances in your blood that give information about your "
                "metabolism, including kidney function, liver function, blood sugar, and electrolyte balance."
            ),
            "common_components": ["Glucose", "Calcium", "Sodium", "Potassium", "BUN", "Creatinine"],
        },
        "lipid": {
            "full_name": "Lipid Panel",
            "description": (
                "A lipid panel measures the fats and fatty substances in your blood. "
                "It's commonly used to assess your risk for cardiovascular disease."
            ),
            "common_components": ["Total Cholesterol", "LDL", "HDL", "Triglycerides"],
        },
        "thyroid": {
            "full_name": "Thyroid Function Tests",
            "description": (
                "Thyroid tests measure how well your thyroid gland is working. "
                "The thyroid produces hormones that regulate your body's metabolism."
            ),
            "common_components": ["TSH", "Free T4", "Free T3"],
        },
        "a1c": {
            "full_name": "Hemoglobin A1C",
            "description": (
                "The A1C test measures your average blood sugar levels over the past 2-3 months. "
                "It's commonly used to monitor blood sugar control."
            ),
            "common_components": ["HbA1c percentage"],
        },
    }

    CRITICAL_KEYWORDS = ["critical", "panic", "urgent", "dangerous", "emergency", "abnormal high", "abnormal low"]
    RESULT_KEYWORDS = ["result", "report", "test", "lab", "blood work", "blood test", "panel"]
    EXPLAIN_KEYWORDS = ["explain", "mean", "understand", "what does", "what do", "interpret", "normal"]

    def __init__(self):
        super().__init__(AgentType.LAB_REPORT)

    def can_handle(self, intent: IntentClassification) -> bool:
        return intent.category == InquiryCategory.LAB_RESULT

    def process(self, inquiry: PatientInquiry, intent: IntentClassification) -> AgentResponse:
        text_lower = inquiry.inquiry_text.lower()

        # SAFETY: Check for critical value mentions
        if any(kw in text_lower for kw in self.CRITICAL_KEYWORDS):
            return self._escalate_critical(inquiry)

        # Check for diagnosis requests (guardrail)
        diagnosis_keywords = ["do i have", "am i sick", "diagnose", "diagnosis", "what's wrong"]
        if any(kw in text_lower for kw in diagnosis_keywords):
            return self._handle_diagnosis_request(inquiry)

        # Try to identify specific lab type
        matched_lab = None
        for lab_key in self.LAB_EXPLANATIONS:
            if lab_key in text_lower:
                matched_lab = lab_key
                break

        if matched_lab:
            return self._explain_lab(inquiry, matched_lab)
        else:
            return self._handle_general_lab(inquiry)

    def _escalate_critical(self, inquiry: PatientInquiry) -> AgentResponse:
        """Immediately escalate critical lab value concerns."""
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I see you have concerns about a critical lab result. "
                "For your safety, I'm immediately connecting you with "
                "a healthcare professional who can review your results "
                "and provide appropriate guidance. Please stay on the line."
            ),
            actions=["critical_value_detected", "immediate_escalation"],
            confidence=0.95,
            requires_escalation=True,
            escalation_priority=EscalationPriority.P1_IMMEDIATE,
            escalation_reason="Patient reporting critical/abnormal lab values — requires immediate clinical review",
            metadata={"sub_intent": "critical_value"},
        )

    def _handle_diagnosis_request(self, inquiry: PatientInquiry) -> AgentResponse:
        """Redirect diagnosis requests — AI cannot diagnose."""
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I understand you're looking for answers about your health. "
                "While I can help explain what lab tests measure and what "
                "reference ranges mean, I'm not able to provide diagnoses "
                "or interpret your specific results in a clinical context.\n\n"
                "Your healthcare provider is the best person to review your "
                "results with you. Would you like me to help you schedule "
                "a follow-up appointment to discuss your results?"
            ),
            actions=["diagnosis_request_redirected"],
            confidence=0.9,
            metadata={"sub_intent": "diagnosis_redirect"},
        )

    def _explain_lab(self, inquiry: PatientInquiry, lab_key: str) -> AgentResponse:
        """Provide approved educational content about a lab test."""
        lab = self.LAB_EXPLANATIONS[lab_key]
        components = "\n".join(f"  • {c}" for c in lab["common_components"])

        response = (
            f"📊 **{lab['full_name']}**\n\n"
            f"{lab['description']}\n\n"
            f"**Common components measured:**\n{components}\n\n"
            f"📌 **Important**: Your healthcare provider will review your "
            f"specific results and discuss any values outside the normal "
            f"range with you. This information is for general education only.\n\n"
            f"Would you like to schedule a follow-up to discuss your results?"
        )

        return self._create_response(
            session_id=inquiry.session_id, response_text=response,
            actions=["lab_explanation_provided"],
            confidence=0.9,
            metadata={"sub_intent": "explain", "lab_type": lab_key},
        )

    def _handle_general_lab(self, inquiry: PatientInquiry) -> AgentResponse:
        """Handle general lab result inquiries."""
        available_labs = ", ".join(
            info["full_name"] for info in self.LAB_EXPLANATIONS.values()
        )
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I can help you understand your lab results! "
                "I have educational information about:\n\n"
                f"  {available_labs}\n\n"
                "Which test would you like to learn about? "
                "Or if you'd prefer to discuss your specific results, "
                "I can help you schedule an appointment with your provider."
            ),
            actions=["general_lab_inquiry"],
            confidence=0.8,
            metadata={"sub_intent": "general"},
        )

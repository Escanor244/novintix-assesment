"""
Appointment Scheduling Agent.

Handles patient inquiries related to:
- Scheduling new appointments
- Rescheduling existing appointments
- Cancelling appointments
- Checking availability
- Appointment reminders and confirmations
"""

import random
from datetime import datetime, timedelta

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentResponse,
    AgentType,
    EscalationPriority,
    InquiryCategory,
    IntentClassification,
    PatientInquiry,
)


class AppointmentAgent(BaseAgent):
    """
    Specialized agent for appointment scheduling operations.

    Uses simulated calendar data for the prototype. In production,
    this would integrate with the EHR/scheduling system API.
    """

    # Simulated available time slots
    AVAILABLE_SLOTS = [
        "Monday 9:00 AM", "Monday 2:00 PM",
        "Tuesday 10:00 AM", "Tuesday 3:30 PM",
        "Wednesday 9:30 AM", "Wednesday 1:00 PM",
        "Thursday 11:00 AM", "Thursday 4:00 PM",
        "Friday 9:00 AM", "Friday 2:30 PM",
    ]

    APPOINTMENT_TYPES = [
        "General Checkup", "Follow-up Visit", "Specialist Consultation",
        "Lab Work", "Vaccination", "Physical Exam",
    ]

    # Keywords for sub-intent classification
    SCHEDULE_KEYWORDS = ["schedule", "book", "make", "set up", "new appointment", "see the doctor"]
    RESCHEDULE_KEYWORDS = ["reschedule", "change", "move", "different time", "another date"]
    CANCEL_KEYWORDS = ["cancel", "remove", "delete", "don't need", "won't be coming"]
    CHECK_KEYWORDS = ["when", "what time", "next appointment", "upcoming", "check", "confirm"]

    def __init__(self):
        super().__init__(AgentType.APPOINTMENT)

    def can_handle(self, intent: IntentClassification) -> bool:
        """This agent handles appointment-related inquiries."""
        return intent.category == InquiryCategory.APPOINTMENT

    def process(
        self, inquiry: PatientInquiry, intent: IntentClassification
    ) -> AgentResponse:
        """Process an appointment-related inquiry."""
        text_lower = inquiry.inquiry_text.lower()

        # Determine sub-intent
        if any(kw in text_lower for kw in self.CANCEL_KEYWORDS):
            return self._handle_cancellation(inquiry)
        elif any(kw in text_lower for kw in self.RESCHEDULE_KEYWORDS):
            return self._handle_reschedule(inquiry)
        elif any(kw in text_lower for kw in self.CHECK_KEYWORDS):
            return self._handle_check(inquiry)
        else:
            return self._handle_scheduling(inquiry)

    def _handle_scheduling(self, inquiry: PatientInquiry) -> AgentResponse:
        """Handle a new appointment scheduling request."""
        # Select random available slots for the demo
        available = random.sample(self.AVAILABLE_SLOTS, min(3, len(self.AVAILABLE_SLOTS)))
        slots_text = "\n".join(f"  • {slot}" for slot in available)

        response_text = (
            f"I'd be happy to help you schedule an appointment! "
            f"Here are the next available time slots:\n\n"
            f"{slots_text}\n\n"
            f"Please let me know which time works best for you, "
            f"or if you need to see a specific provider."
        )

        return self._create_response(
            session_id=inquiry.session_id,
            response_text=response_text,
            actions=["retrieved_available_slots", "presented_options"],
            confidence=0.9,
            metadata={"sub_intent": "schedule", "available_slots": available},
        )

    def _handle_reschedule(self, inquiry: PatientInquiry) -> AgentResponse:
        """Handle an appointment rescheduling request."""
        # Simulated current appointment
        current_date = (datetime.utcnow() + timedelta(days=3)).strftime("%A, %B %d")
        new_slots = random.sample(self.AVAILABLE_SLOTS, min(3, len(self.AVAILABLE_SLOTS)))
        slots_text = "\n".join(f"  • {slot}" for slot in new_slots)

        response_text = (
            f"I can help you reschedule your appointment. "
            f"I see you currently have an appointment on {current_date}.\n\n"
            f"Here are alternative time slots available:\n"
            f"{slots_text}\n\n"
            f"Which time would you prefer? I'll update your appointment right away."
        )

        return self._create_response(
            session_id=inquiry.session_id,
            response_text=response_text,
            actions=["found_existing_appointment", "retrieved_alternatives"],
            confidence=0.85,
            metadata={"sub_intent": "reschedule", "current_date": current_date},
        )

    def _handle_cancellation(self, inquiry: PatientInquiry) -> AgentResponse:
        """
        Handle an appointment cancellation request.
        Cancellations require human confirmation (guardrail: irreversible action).
        """
        return self._create_response(
            session_id=inquiry.session_id,
            response_text=(
                "I understand you'd like to cancel your appointment. "
                "For your protection, appointment cancellations require "
                "confirmation from our scheduling team. "
                "I'm connecting you with a staff member who can process "
                "this cancellation and discuss any rescheduling options."
            ),
            actions=["cancellation_requested", "escalated_for_confirmation"],
            confidence=0.9,
            requires_escalation=True,
            escalation_priority=EscalationPriority.P3_STANDARD,
            escalation_reason="Appointment cancellation requires human confirmation (irreversible action)",
            metadata={"sub_intent": "cancel"},
        )

    def _handle_check(self, inquiry: PatientInquiry) -> AgentResponse:
        """Handle an appointment check/confirmation request."""
        # Simulated upcoming appointment
        apt_date = (datetime.utcnow() + timedelta(days=5)).strftime("%A, %B %d")
        apt_time = random.choice(["9:00 AM", "10:30 AM", "2:00 PM", "3:30 PM"])
        apt_type = random.choice(self.APPOINTMENT_TYPES)

        response_text = (
            f"Here are your upcoming appointment details:\n\n"
            f"  📅 Date: {apt_date}\n"
            f"  🕐 Time: {apt_time}\n"
            f"  📋 Type: {apt_type}\n"
            f"  📍 Location: Main Clinic, Room 204\n\n"
            f"Would you like to reschedule, or is there anything else I can help with?"
        )

        return self._create_response(
            session_id=inquiry.session_id,
            response_text=response_text,
            actions=["retrieved_appointment_details"],
            confidence=0.95,
            metadata={
                "sub_intent": "check",
                "appointment_date": apt_date,
                "appointment_time": apt_time,
                "appointment_type": apt_type,
            },
        )

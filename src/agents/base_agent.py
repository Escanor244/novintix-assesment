"""
Abstract base agent for the Agentic AI Healthcare System.

All specialized agents inherit from BaseAgent and implement
the process() method. Provides common functionality for
guardrail integration, logging, and response formatting.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from src.models.schemas import (
    AgentResponse,
    AgentType,
    EscalationPriority,
    IntentClassification,
    PatientInquiry,
)


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.

    Every agent must implement:
    - process(): Handle the inquiry and generate a response
    - can_handle(): Determine if this agent can handle a given intent

    The base class provides:
    - Standard response formatting
    - Escalation request creation
    - Common validation logic
    """

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self._created_at = datetime.utcnow()

    @abstractmethod
    def process(
        self, inquiry: PatientInquiry, intent: IntentClassification
    ) -> AgentResponse:
        """
        Process a patient inquiry and generate a response.

        Args:
            inquiry: The patient's inquiry
            intent: The classified intent from the orchestrator

        Returns:
            AgentResponse with the agent's response and any actions taken
        """
        pass

    @abstractmethod
    def can_handle(self, intent: IntentClassification) -> bool:
        """
        Determine if this agent can handle the given intent.

        Args:
            intent: The classified intent

        Returns:
            True if this agent is appropriate for the intent
        """
        pass

    def _create_response(
        self,
        session_id: str,
        response_text: str,
        actions: list[str] | None = None,
        confidence: float = 1.0,
        requires_escalation: bool = False,
        escalation_priority: EscalationPriority | None = None,
        escalation_reason: str | None = None,
        metadata: dict | None = None,
    ) -> AgentResponse:
        """Create a standardized agent response."""
        return AgentResponse(
            session_id=session_id,
            agent_type=self.agent_type,
            response_text=response_text,
            actions_taken=actions or [],
            confidence=confidence,
            requires_escalation=requires_escalation,
            escalation_priority=escalation_priority,
            escalation_reason=escalation_reason,
            metadata=metadata or {},
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.agent_type.value}>"

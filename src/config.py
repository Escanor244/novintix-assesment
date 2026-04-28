"""
Configuration module for the Agentic AI Healthcare System.

Manages environment-based configuration including thresholds,
feature flags, and system parameters.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator's routing behavior."""
    high_confidence_threshold: float = 0.7
    low_confidence_threshold: float = 0.4
    max_retries_before_escalation: int = 3
    session_timeout_minutes: int = 30


@dataclass
class GuardrailConfig:
    """Configuration for guardrail thresholds and behavior."""
    # Medical safety
    blocked_medical_terms: list = field(default_factory=lambda: [
        "diagnose", "diagnosis", "you have", "you suffer from",
        "take this medication", "increase your dosage", "decrease your dosage",
        "stop taking", "you should take", "prescribed"
    ])

    # Emergency keywords that trigger immediate escalation
    emergency_keywords: list = field(default_factory=lambda: [
        "chest pain", "heart attack", "stroke", "can't breathe",
        "difficulty breathing", "severe bleeding", "unconscious",
        "seizure", "suicidal", "self-harm", "want to die",
        "kill myself", "overdose", "poisoning", "anaphylaxis",
        "allergic reaction severe"
    ])

    # Critical lab values (simplified thresholds)
    critical_lab_values: dict = field(default_factory=lambda: {
        "potassium": {"low": 2.5, "high": 6.0, "unit": "mEq/L"},
        "sodium": {"low": 120, "high": 160, "unit": "mEq/L"},
        "glucose": {"low": 40, "high": 500, "unit": "mg/dL"},
        "hemoglobin": {"low": 5.0, "high": 20.0, "unit": "g/dL"},
        "platelet_count": {"low": 20, "high": 1000, "unit": "K/uL"},
    })

    # Controlled substances (Schedule II-V)
    controlled_substances: list = field(default_factory=lambda: [
        "oxycodone", "hydrocodone", "morphine", "fentanyl",
        "adderall", "ritalin", "xanax", "valium", "ambien",
        "codeine", "tramadol", "oxycontin", "vicodin",
        "percocet", "methadone", "suboxone"
    ])

    # PII patterns for redaction
    pii_patterns: list = field(default_factory=lambda: [
        r"\b\d{3}-\d{2}-\d{4}\b",          # SSN
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{2}/\d{2}/\d{4}\b",          # DOB format
        r"\bMRN\b[:\s]*\d+\b",             # Medical Record Number
    ])

    # Negative sentiment keywords
    negative_sentiment_keywords: list = field(default_factory=lambda: [
        "angry", "frustrated", "terrible", "worst", "horrible",
        "unacceptable", "complaint", "sue", "lawyer", "malpractice",
        "negligent", "incompetent", "ridiculous", "disgusted"
    ])


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and alerting."""
    escalation_rate_alert_threshold: float = 0.30  # 30% in 1-hour window
    guardrail_trigger_spike_multiplier: float = 2.0
    avg_confidence_alert_threshold: float = 0.6
    p95_response_time_alert_ms: float = 5000.0
    log_retention_years: int = 7  # HIPAA requirement


@dataclass
class LLMConfig:
    """Configuration for optional LLM usage."""
    enabled: bool = False
    provider: str = "gemini"  # gemini | ollama
    gemini_model: str = "gemini-1.5-flash"
    gemini_api_key: str | None = None
    ollama_model: str = "llama3.2"
    ollama_host: str = "http://localhost:11434"
    timeout_seconds: float = 8.0


@dataclass
class AppConfig:
    """Main application configuration."""
    app_name: str = "Healthcare Agentic AI System"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    guardrails: GuardrailConfig = field(default_factory=GuardrailConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        load_dotenv()
        config = cls()
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.host = os.getenv("HOST", "0.0.0.0")
        config.port = int(os.getenv("PORT", "8000"))

        threshold = os.getenv("CONFIDENCE_THRESHOLD")
        if threshold:
            config.orchestrator.high_confidence_threshold = float(threshold)

        config.llm.enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
        config.llm.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        config.llm.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        config.llm.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        config.llm.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        config.llm.timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "8"))

        config.llm.gemini_api_key = (
            os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        )

        # Avoid external calls during tests
        if os.getenv("PYTEST_CURRENT_TEST"):
            config.llm.enabled = False

        return config


# Singleton configuration instance
config = AppConfig.from_env()

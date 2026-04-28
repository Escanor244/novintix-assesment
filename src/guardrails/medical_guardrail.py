"""
Medical Safety Guardrail.

Ensures no agent provides unauthorized medical advice:
- Blocks diagnostic language
- Blocks treatment recommendations
- Blocks dosage guidance
- Enforces approved-content-only responses
"""

import re

from src.models.schemas import GuardrailResult, GuardrailStatus


# Patterns that indicate unauthorized medical advice
DIAGNOSIS_PATTERNS = [
    r"\byou have\b.*\b(disease|condition|disorder|syndrome|infection)\b",
    r"\byou are\b.*\b(diagnosed|suffering)\b",
    r"\bdiagnosis\b.*\bis\b",
    r"\byou('re| are)\b.*\b(diabetic|hypertensive|anemic)\b",
    r"\bthis means you have\b",
    r"\byour condition is\b",
]

TREATMENT_PATTERNS = [
    r"\btake\b.*\b(mg|milligrams|pills?|tablets?|capsules?)\b",
    r"\bincrease\b.*\b(dose|dosage|medication)\b",
    r"\bdecrease\b.*\b(dose|dosage|medication)\b",
    r"\bstop taking\b",
    r"\bstart taking\b",
    r"\byou should take\b",
    r"\bi recommend\b.*\b(treatment|medication|drug|therapy)\b",
    r"\bprescribe\b",
    r"\bswitch to\b.*\b(medication|drug)\b",
]

SEVERITY_PATTERNS = [
    r"\bnothing to worry about\b",
    r"\bthis is (serious|dangerous|life.?threatening)\b",
    r"\byou('ll| will) be fine\b",
    r"\bno need to see a doctor\b",
    r"\byou don't need\b.*\b(treatment|medical)\b",
]


def check_medical_safety(response_text: str) -> GuardrailResult:
    """
    Check an agent response for unauthorized medical advice.

    Scans for diagnostic language, treatment recommendations,
    and severity assessments that only licensed providers should make.

    Args:
        response_text: The agent's response text to check

    Returns:
        GuardrailResult with pass/fail status and any violations found
    """
    violations = []
    text_lower = response_text.lower()

    # Check for diagnostic language
    for pattern in DIAGNOSIS_PATTERNS:
        if re.search(pattern, text_lower):
            violations.append(f"Diagnostic language detected: pattern '{pattern}'")

    # Check for treatment recommendations
    for pattern in TREATMENT_PATTERNS:
        if re.search(pattern, text_lower):
            violations.append(f"Treatment recommendation detected: pattern '{pattern}'")

    # Check for severity assessments
    for pattern in SEVERITY_PATTERNS:
        if re.search(pattern, text_lower):
            violations.append(f"Severity assessment detected: pattern '{pattern}'")

    if violations:
        return GuardrailResult(
            guardrail_name="medical_safety",
            status=GuardrailStatus.BLOCKED,
            violations=violations,
            details=f"Response blocked: {len(violations)} medical safety violation(s) detected",
            original_response=response_text,
            sanitized_response=(
                "I'm not able to provide medical advice on this matter. "
                "Please consult with your healthcare provider for "
                "personalized medical guidance. Would you like me to "
                "help you schedule an appointment?"
            ),
        )

    return GuardrailResult(
        guardrail_name="medical_safety",
        status=GuardrailStatus.PASSED,
        details="No medical safety violations detected",
    )

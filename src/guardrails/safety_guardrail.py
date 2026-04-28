"""
Critical Health Safety Guardrail.

Detects emergency situations and critical health keywords
that require immediate human intervention. This guardrail
ensures no critical health query is resolved without verification.
"""

from src.config import config
from src.models.schemas import GuardrailResult, GuardrailStatus, EscalationPriority


def check_emergency_keywords(text: str) -> GuardrailResult:
    """
    Scan text for emergency/critical health keywords.

    If detected, the response MUST be escalated to a human
    regardless of which agent processed it.

    Args:
        text: Text to scan (typically the patient inquiry)

    Returns:
        GuardrailResult — BLOCKED if emergency keywords found
    """
    text_lower = text.lower()
    detected = []

    for keyword in config.guardrails.emergency_keywords:
        if keyword in text_lower:
            detected.append(keyword)

    if detected:
        return GuardrailResult(
            guardrail_name="safety_emergency_detection",
            status=GuardrailStatus.BLOCKED,
            violations=[f"Emergency keyword detected: '{kw}'" for kw in detected],
            details=(
                f"CRITICAL: {len(detected)} emergency keyword(s) detected. "
                f"Immediate human escalation required. Keywords: {', '.join(detected)}"
            ),
            sanitized_response=(
                "⚠️ **If you are experiencing a medical emergency, please call 911 immediately.**\n\n"
                "I'm connecting you with our clinical team right now for immediate assistance."
            ),
        )

    return GuardrailResult(
        guardrail_name="safety_emergency_detection",
        status=GuardrailStatus.PASSED,
        details="No emergency keywords detected",
    )


def check_critical_lab_values(lab_data: dict) -> GuardrailResult:
    """
    Check lab values against critical thresholds.

    If any value falls in the critical range, escalation is mandatory
    and no AI interpretation should be provided.

    Args:
        lab_data: Dict of {test_name: value} pairs

    Returns:
        GuardrailResult — BLOCKED if critical values found
    """
    violations = []
    critical_thresholds = config.guardrails.critical_lab_values

    for test_name, value in lab_data.items():
        test_key = test_name.lower().replace(" ", "_")
        if test_key in critical_thresholds:
            thresholds = critical_thresholds[test_key]
            if value < thresholds["low"]:
                violations.append(
                    f"CRITICAL LOW: {test_name} = {value} {thresholds['unit']} "
                    f"(critical threshold: < {thresholds['low']})"
                )
            elif value > thresholds["high"]:
                violations.append(
                    f"CRITICAL HIGH: {test_name} = {value} {thresholds['unit']} "
                    f"(critical threshold: > {thresholds['high']})"
                )

    if violations:
        return GuardrailResult(
            guardrail_name="safety_critical_lab_values",
            status=GuardrailStatus.BLOCKED,
            violations=violations,
            details=(
                f"CRITICAL: {len(violations)} critical lab value(s) detected. "
                f"Immediate clinical review required. No AI interpretation permitted."
            ),
            sanitized_response=(
                "Your lab results include values that require immediate "
                "attention from your healthcare provider. I'm connecting "
                "you with our clinical team right now."
            ),
        )

    return GuardrailResult(
        guardrail_name="safety_critical_lab_values",
        status=GuardrailStatus.PASSED,
        details="No critical lab values detected",
    )


def check_negative_sentiment(text: str) -> GuardrailResult:
    """
    Detect negative sentiment / complaint indicators.

    Patients expressing strong dissatisfaction need human empathy,
    not automated responses.

    Args:
        text: Text to analyze

    Returns:
        GuardrailResult — WARNING if negative sentiment detected
    """
    text_lower = text.lower()
    detected = []

    for keyword in config.guardrails.negative_sentiment_keywords:
        if keyword in text_lower:
            detected.append(keyword)

    if len(detected) >= 2:  # Multiple negative indicators = strong signal
        return GuardrailResult(
            guardrail_name="safety_sentiment_check",
            status=GuardrailStatus.WARNING,
            violations=[f"Negative sentiment indicator: '{kw}'" for kw in detected],
            details=f"Patient distress detected ({len(detected)} indicators). Consider escalation.",
        )

    return GuardrailResult(
        guardrail_name="safety_sentiment_check",
        status=GuardrailStatus.PASSED,
        details="No significant negative sentiment detected",
    )

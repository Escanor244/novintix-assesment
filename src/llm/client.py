"""LLM client with Gemini primary and Ollama fallback."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import httpx

from src.config import LLMConfig
from src.models.schemas import InquiryCategory, IntentClassification


class LLMClient:
    """Lightweight LLM client for intent classification."""

    def __init__(self, config: LLMConfig):
        self.config = config

    def classify_intent(self, text: str) -> Optional[IntentClassification]:
        """Classify inquiry intent with Gemini primary and Ollama fallback."""
        result = None

        if self.config.provider in {"gemini", "auto"}:
            result = self._classify_with_gemini(text)
            if result:
                return result

        if self.config.provider in {"ollama", "auto", "gemini"}:
            result = self._classify_with_ollama(text)
            if result:
                return result

        return None

    def _classify_with_gemini(self, text: str) -> Optional[IntentClassification]:
        if not self.config.gemini_api_key:
            return None

        prompt = _build_prompt(text)
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.config.gemini_model}:generateContent"
        )
        params = {"key": self.config.gemini_api_key}
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 256,
            },
        }

        try:
            resp = httpx.post(
                url,
                params=params,
                json=payload,
                timeout=self.config.timeout_seconds,
            )
            resp.raise_for_status()
            data = resp.json()
            text_out = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            return _parse_intent(text_out)
        except Exception:
            return None

    def _classify_with_ollama(self, text: str) -> Optional[IntentClassification]:
        prompt = _build_prompt(text)
        url = f"{self.config.ollama_host}/api/generate"
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        }

        try:
            resp = httpx.post(url, json=payload, timeout=self.config.timeout_seconds)
            resp.raise_for_status()
            data = resp.json()
            text_out = data.get("response", "")
            return _parse_intent(text_out)
        except Exception:
            return None


def _build_prompt(text: str) -> str:
    return (
        "Classify the patient inquiry into one of these categories: "
        "appointment, prescription, lab_result, insurance, escalation, unknown. "
        "Return JSON only with keys: category, confidence, matched_keywords, "
        "requires_escalation, escalation_reason. Confidence is 0 to 1.\n\n"
        f"Inquiry: {text}\n"
    )


def _parse_intent(raw_text: str) -> Optional[IntentClassification]:
    if not raw_text:
        return None

    json_text = _extract_json(raw_text)
    if not json_text:
        return None

    try:
        payload = json.loads(json_text)
    except Exception:
        return None

    category_raw = str(payload.get("category", "")).lower().strip()
    category_map = {
        "appointment": InquiryCategory.APPOINTMENT,
        "prescription": InquiryCategory.PRESCRIPTION,
        "lab_result": InquiryCategory.LAB_RESULT,
        "insurance": InquiryCategory.INSURANCE,
        "escalation": InquiryCategory.ESCALATION,
        "unknown": InquiryCategory.UNKNOWN,
    }
    category = category_map.get(category_raw)
    if not category:
        return None

    confidence = float(payload.get("confidence", 0.0) or 0.0)
    confidence = min(max(confidence, 0.0), 1.0)

    matched_keywords = payload.get("matched_keywords") or []
    if not isinstance(matched_keywords, list):
        matched_keywords = []

    requires_escalation = bool(payload.get("requires_escalation", False))
    escalation_reason = payload.get("escalation_reason")

    return IntentClassification(
        category=category,
        confidence=confidence,
        matched_keywords=[str(k) for k in matched_keywords],
        requires_escalation=requires_escalation,
        escalation_reason=escalation_reason,
    )


def _extract_json(text: str) -> Optional[str]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

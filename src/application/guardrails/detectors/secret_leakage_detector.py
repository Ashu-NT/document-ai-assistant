from __future__ import annotations

from src.application.guardrails.models.detector_match import DetectorMatch
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity

_SECRET_REQUEST_MARKERS = (
    ".env",
    "environment variables",
    "env vars",
    "api key",
    "api keys",
    "access token",
    "secret key",
    "password",
    "print your env",
    "show your env",
    "show api keys",
)


class SecretLeakageDetector:
    def detect(self, user_input: str) -> DetectorMatch:
        normalized = " ".join(user_input.strip().lower().split())
        if not normalized:
            return DetectorMatch(matched=False)
        matched_terms = [
            marker for marker in _SECRET_REQUEST_MARKERS if marker in normalized
        ]
        if not matched_terms:
            return DetectorMatch(matched=False)
        return DetectorMatch(
            matched=True,
            reason="Request asks for secrets, credentials, or environment configuration.",
            matched_terms=matched_terms,
            severity=GuardrailSeverity.CRITICAL,
        )

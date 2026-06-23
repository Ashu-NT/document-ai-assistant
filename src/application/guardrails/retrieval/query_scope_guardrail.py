from __future__ import annotations

import re

from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.enterprise_guardrail_policy import (
    EnterpriseGuardrailPolicy,
)

_OFF_TOPIC_MARKERS: frozenset[str] = frozenset(
    [
        "weather",
        "temperature outside",
        "will it rain",
        "rain today",
        "weather forecast",
        "who won",
        "game score",
        "sports team",
        "football match",
        "basketball game",
        "soccer match",
        "baseball game",
        "tennis match",
        "movie review",
        "film review",
        "actor",
        "actress",
        "celebrity",
        "recipe",
        "cooking tips",
        "restaurant",
        "stock price",
        "cryptocurrency",
        "bitcoin",
        "tell me a joke",
        "joke about",
        "how are you",
        "what is your name",
        "who are you",
        "election results",
        "political party",
        "news today",
        "current events",
    ]
)

_AMBIGUOUS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"^(tell me about (it|this|that)|what does that mean|explain this|can you help( me)?)[\?\.\s]*$",
        re.IGNORECASE,
    ),
    re.compile(r"^(what|how|why|when|where|who)\??$", re.IGNORECASE),
    re.compile(r"^(it|this|that|these|those)[\?\.\s]*$", re.IGNORECASE),
]

_MIN_MEANINGFUL_WORDS = 2


class QueryScopeGuardrail:
    def __init__(self, policy: EnterpriseGuardrailPolicy | None = None) -> None:
        self._policy = policy or EnterpriseGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        text = (context.query_text or "").strip()

        if self._is_ambiguous(text):
            return GuardrailResult(
                decision=GuardrailDecision.NEEDS_CLARIFICATION,
                allowed=False,
                reason="Query is too vague to retrieve relevant documents.",
                confidence=ConfidenceLevel.HIGH,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.AMBIGUOUS_QUERY,
                        message="Query does not contain enough context to identify relevant information.",
                    )
                ],
                safe_user_message=(
                    "Your question is too broad. Please provide more detail, "
                    "such as the equipment name, part number, or specific procedure."
                ),
            )

        if self._policy.block_out_of_scope_queries and self._is_off_topic(text):
            return GuardrailResult(
                decision=GuardrailDecision.OUT_OF_SCOPE,
                allowed=False,
                reason="Query is unrelated to the document knowledge base.",
                confidence=ConfidenceLevel.HIGH,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.UNRELATED_QUERY,
                        message="Query does not relate to technical documentation, equipment, or procedures.",
                    )
                ],
                safe_user_message=(
                    "I can only answer questions about technical documentation, "
                    "equipment, maintenance procedures, and specifications."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="Query is within scope.",
        )

    @staticmethod
    def _is_ambiguous(text: str) -> bool:
        if not text:
            return True
        words = text.split()
        if len(words) < _MIN_MEANINGFUL_WORDS:
            return True
        return any(pattern.match(text) for pattern in _AMBIGUOUS_PATTERNS)

    @staticmethod
    def _is_off_topic(text: str) -> bool:
        lower = text.lower()
        return any(marker in lower for marker in _OFF_TOPIC_MARKERS)

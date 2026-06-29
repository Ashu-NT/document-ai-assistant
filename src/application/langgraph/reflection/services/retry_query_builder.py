from __future__ import annotations

import re

from src.application.langgraph.reflection.models import ReflectionDecision, RetryPlan
from src.application.services.answer_generation.intent.answer_intent import AnswerIntent

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_INTENT_EXPANSIONS = {
    "maintenance": [
        "maintenance schedule",
        "preventive maintenance",
        "service interval",
        "inspection",
        "lubrication",
    ],
    "specification": [
        "technical data",
        "design pressure",
        "test pressure",
        "dimensions",
        "rating",
    ],
    "procedure": [
        "procedure",
        "steps",
        "remove",
        "install",
        "operate",
    ],
    "safety": ["warning", "caution", "danger", "hazard"],
    "troubleshooting": ["fault", "troubleshooting", "problem", "cause", "remedy"],
}


def _tokenize(value: str) -> set[str]:
    return set(_TOKEN_RE.findall((value or "").lower()))


class RetryQueryBuilder:
    def build(
        self,
        *,
        original_user_question: str,
        answer_intent: str | None,
        selected_document_id: str | None,
        reflection_decision: ReflectionDecision,
        top_k: int | None,
    ) -> RetryPlan:
        retry_query = reflection_decision.retry_query
        if retry_query and self._is_related(
            original_user_question=original_user_question,
            retry_query=retry_query,
        ):
            final_query = retry_query
        else:
            final_query = self._fallback_query(
                original_user_question=original_user_question,
                answer_intent=answer_intent,
                missing_information=reflection_decision.missing_information,
            )
        return RetryPlan(
            retry_query=final_query,
            document_id=selected_document_id,
            top_k=top_k,
            reason=reflection_decision.reason,
        )

    @staticmethod
    def _is_related(
        *,
        original_user_question: str,
        retry_query: str,
    ) -> bool:
        question_tokens = _tokenize(original_user_question)
        retry_tokens = _tokenize(retry_query)
        if not question_tokens or not retry_tokens:
            return False
        overlap = question_tokens.intersection(retry_tokens)
        return len(overlap) >= min(2, len(question_tokens))

    def _fallback_query(
        self,
        *,
        original_user_question: str,
        answer_intent: str | None,
        missing_information: list[str],
    ) -> str:
        parts = [original_user_question.strip()]
        normalized_intent = (answer_intent or "").lower()
        for marker, expansions in _INTENT_EXPANSIONS.items():
            if marker in normalized_intent or marker in original_user_question.lower():
                parts.extend(expansions)
        parts.extend(item for item in missing_information if item)
        return " ".join(dict.fromkeys(" ".join(parts).split()))

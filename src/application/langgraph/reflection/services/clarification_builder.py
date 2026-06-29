from __future__ import annotations

from src.application.langgraph.reflection.models import (
    ClarificationPlan,
    ReflectionDecision,
)
from src.application.langgraph.reflection.constants import REFLECTION_CLARIFICATION_KIND
from src.application.langgraph.routing import RouteType


class ClarificationBuilder:
    def build(
        self,
        *,
        decision: ReflectionDecision,
        original_user_input: str,
        answer_intent: str | None,
        selected_document_id: str | None,
    ) -> ClarificationPlan:
        options = self._resolve_options(
            original_user_input=original_user_input,
            answer_intent=answer_intent,
            missing_information=decision.missing_information,
        )
        question = (
            decision.clarification_question
            or "I need one clarification before answering."
        ).strip()
        return ClarificationPlan(
            question=question,
            options=options,
            original_user_input=original_user_input,
            reason=decision.reason,
            resume_route=RouteType.ANSWER_QUESTION.value,
            resume_payload={
                "kind": REFLECTION_CLARIFICATION_KIND,
                "original_user_input": original_user_input,
                "selected_document_id": selected_document_id,
            },
        )

    @staticmethod
    def _resolve_options(
        *,
        original_user_input: str,
        answer_intent: str | None,
        missing_information: list[str],
    ) -> list[str]:
        normalized_question = original_user_input.lower()
        normalized_intent = (answer_intent or "").lower()
        if "maintenance" in normalized_question or "maintenance" in normalized_intent:
            return [
                "maintenance tasks",
                "maintenance intervals",
                "maintenance procedures",
            ]
        if "spec" in normalized_question or "specification" in normalized_question:
            return [
                "technical specifications",
                "operating limits",
                "dimensions or ratings",
            ]
        if missing_information:
            return missing_information[:3]
        return ["the exact section", "the exact procedure", "the exact specification"]

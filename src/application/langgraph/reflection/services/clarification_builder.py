from __future__ import annotations

from src.application.langgraph.reflection.models import (
    ClarificationPlan,
    ReflectionDecision,
)
from src.application.langgraph.reflection.constants import REFLECTION_CLARIFICATION_KIND
from src.application.langgraph.reflection.strategies.clarification import (
    ClarificationContext,
    ClarificationStrategyRegistry,
)
from src.application.langgraph.routing import RouteType


class ClarificationBuilder:
    def __init__(
        self,
        *,
        strategy_registry: ClarificationStrategyRegistry | None = None,
    ) -> None:
        self._strategy_registry = strategy_registry or ClarificationStrategyRegistry()

    def build(
        self,
        *,
        decision: ReflectionDecision,
        original_user_input: str,
        answer_intent: str | None,
        selected_document_id: str | None,
        retrieval_query_intent: str | None = None,
    ) -> ClarificationPlan:
        options = self._strategy_registry.build_options(
            retrieval_query_intent=retrieval_query_intent,
            context=ClarificationContext(
                original_user_input=original_user_input,
                answer_intent=answer_intent,
                selected_document_id=selected_document_id,
                missing_information=decision.missing_information,
            ),
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

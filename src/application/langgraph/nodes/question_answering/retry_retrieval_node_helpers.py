from __future__ import annotations

from typing import Any

from src.application.langgraph.common.answer_intent_resolver import (
    resolve_answer_intent,
)
from src.application.langgraph.state import AgentState


def decision_from_state(payload: dict[str, Any], reason: str):
    from src.application.langgraph.reflection.models import (
        ReflectionDecision,
        ReflectionDecisionType,
    )

    decision_value = str(payload.get("decision") or "RETRIEVE_AGAIN").upper()
    try:
        decision_type = ReflectionDecisionType(decision_value)
    except ValueError:
        decision_type = ReflectionDecisionType.RETRIEVE_AGAIN
    return ReflectionDecision(
        decision=decision_type,
        confidence=float(payload.get("confidence") or 0.0),
        reason=reason,
        retry_query=str(payload.get("retry_query") or "").strip() or None,
        clarification_question=str(payload.get("clarification_question") or "").strip()
        or None,
        missing_information=[
            str(item).strip()
            for item in (payload.get("missing_information") or [])
            if str(item).strip()
        ],
    )


def extract_answer_intent(state: AgentState) -> str | None:
    return resolve_answer_intent(
        (state.get("tool_results", {}).get("answer_question") or {}).get("data")
    )


def current_primary_strategy(state: AgentState):
    decision = state.get("retrieval_strategy_decision")
    if not isinstance(decision, dict):
        return None
    value = decision.get("primary_strategy")
    try:
        from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy

        return RetrievalStrategy(str(value))
    except Exception:
        return None

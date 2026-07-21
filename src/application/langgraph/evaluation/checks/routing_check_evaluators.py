from __future__ import annotations

from src.application.langgraph.common.value_coercion import optional_str
from src.application.langgraph.evaluation.models.agent_eval_result import AgentTurnResult
from src.application.langgraph.evaluation.models.agent_test_case import AgentExpectedBehavior


def evaluate_document_selection(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    checks_required = (
        expected.selected_document_contains is not None
        or expected.selected_document_id is not None
    )
    if not checks_required:
        return None

    if (
        expected.selected_document_id is not None
        and final_turn.selected_document_id != expected.selected_document_id
    ):
        return False

    if expected.selected_document_contains is None:
        return True

    haystack = " ".join(
        value
        for value in (
            final_turn.selected_document_title,
            final_turn.selected_document_id,
            optional_str(final_turn.diagnostics.get("selected_document_file_name")),
            final_turn.response_text,
        )
        if value
    ).lower()
    return expected.selected_document_contains.lower() in haystack


def turn_requires_clarification(turn_result: AgentTurnResult) -> bool:
    return bool(
        turn_result.diagnostics.get("graph_diagnostics", {}).get(
            "needs_clarification",
            False,
        )
        or turn_result.diagnostics.get("pending_clarification")
        or turn_result.diagnostics.get("clarification_options")
    )

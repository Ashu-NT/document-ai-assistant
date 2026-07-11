from __future__ import annotations

from src.application.langgraph.evaluation.agent_eval_result import AgentTurnResult
from src.application.langgraph.evaluation.agent_test_case import AgentExpectedBehavior


def evaluate_tool_policy(
    expected: AgentExpectedBehavior,
    *,
    tool_names: list[str],
) -> bool | None:
    if not expected.required_tools and not expected.forbidden_tools:
        return None
    if any(tool_name not in tool_names for tool_name in expected.required_tools):
        return False
    if any(tool_name in tool_names for tool_name in expected.forbidden_tools):
        return False
    return True


def evaluate_plan_policy(
    expected: AgentExpectedBehavior,
    *,
    plan_tool_names: list[str],
) -> bool | None:
    if not expected.required_plan_tools and not expected.forbidden_plan_tools:
        return None
    if any(
        tool_name not in plan_tool_names for tool_name in expected.required_plan_tools
    ):
        return False
    if any(
        tool_name in plan_tool_names for tool_name in expected.forbidden_plan_tools
    ):
        return False
    return True


def evaluate_answer_expectations(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not expected.answer_must_contain and not expected.answer_must_not_contain:
        return None
    answer_text = (final_turn.response_text or "").lower()
    if any(fragment.lower() not in answer_text for fragment in expected.answer_must_contain):
        return False
    if any(fragment.lower() in answer_text for fragment in expected.answer_must_not_contain):
        return False
    return True

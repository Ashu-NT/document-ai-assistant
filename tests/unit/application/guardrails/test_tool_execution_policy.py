from src.application.guardrails.models.guardrail_context import GuardrailContext
from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.policies.tool_execution_policy import (
    ToolExecutionPolicy,
)
from src.application.guardrails.services.pre_tool_guardrail_service import (
    PreToolGuardrailService,
)


def test_tool_execution_policy_blocks_mutating_tools_by_default() -> None:
    policy = ToolExecutionPolicy()

    assert "answer_question" in policy.allowed_tools
    assert "delete_document" in policy.blocked_tools
    assert policy.require_registered_tools is True


def test_pre_tool_guardrail_service_blocks_unregistered_tool() -> None:
    service = PreToolGuardrailService()

    result = service.check(
        GuardrailContext(
            requested_tool="unknown_tool",
            requested_action="run unknown tool",
            route="planned_task",
        ),
        available_tool_names={"answer_question", "retrieve_chunks"},
    )

    assert result.allowed is False
    assert result.decision == GuardrailDecision.BLOCK
    assert result.blocked_tools == ["unknown_tool"]


def test_pre_tool_guardrail_service_allows_registered_safe_tool() -> None:
    service = PreToolGuardrailService()

    result = service.check(
        GuardrailContext(
            requested_tool="answer_question",
            requested_action="answer a question",
            route="answer_question",
        ),
        available_tool_names={"answer_question", "retrieve_chunks"},
    )

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW

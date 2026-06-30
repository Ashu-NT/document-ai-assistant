from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation
from src.application.guardrails.models.violation_type import ViolationType
from src.application.guardrails.tracing.guardrail_trace import GuardrailTrace


def test_guardrail_trace_records_policy_layer_and_terms() -> None:
    trace = GuardrailTrace(trace_id="trace-123")
    result = GuardrailResult(
        decision=GuardrailDecision.BLOCK,
        allowed=False,
        reason="Unsafe destructive request.",
        severity=GuardrailSeverity.CRITICAL,
        violations=[
            GuardrailViolation(
                violation_type=ViolationType.UNSAFE_DESTRUCTIVE,
                description="Unsafe destructive request.",
                matched_terms=["delete all documents"],
                policy_name="unsafe_action_policy",
                severity=GuardrailSeverity.CRITICAL,
            )
        ],
    )

    traced_result = trace.append(
        layer="pre_route",
        policy="unsafe_action_policy",
        result=result,
        route="answer_question",
        blocked_tool="delete_document",
    )

    assert traced_result.trace_id == "trace-123"
    assert traced_result.diagnostics["guardrail_trace_id"] == "trace-123"
    entry = traced_result.diagnostics["guardrail_trace"][0]
    assert entry["layer"] == "pre_route"
    assert entry["policy"] == "unsafe_action_policy"
    assert entry["matched_terms"] == ["delete all documents"]
    assert entry["blocked_tool"] == "delete_document"

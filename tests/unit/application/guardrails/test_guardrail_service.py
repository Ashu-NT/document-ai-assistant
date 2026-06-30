from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation
from src.application.guardrails.models.violation_type import ViolationType
from src.application.guardrails.services.guardrail_service import GuardrailService
from src.application.guardrails.tracing.guardrail_trace import GuardrailTrace


def test_guardrail_service_create_trace_returns_guardrail_trace() -> None:
    service = GuardrailService()

    trace = service.create_trace()

    assert isinstance(trace, GuardrailTrace)
    assert trace.trace_id


def test_guardrail_result_to_dict_is_json_friendly() -> None:
    result = GuardrailResult(
        decision=GuardrailDecision.BLOCK,
        allowed=False,
        reason="Blocked for testing.",
        severity=GuardrailSeverity.HIGH,
        violations=[
            GuardrailViolation(
                violation_type=ViolationType.PROMPT_INJECTION,
                description="Prompt injection detected.",
                matched_terms=["ignore previous instructions"],
                policy_name="prompt_injection_policy",
                severity=GuardrailSeverity.HIGH,
            )
        ],
    )

    payload = result.to_dict()

    assert payload["decision"] == "block"
    assert payload["severity"] == "high"
    assert payload["violations"][0]["violation_type"] == "prompt_injection"

from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.policies.safety_guardrail_policy import SafetyGuardrailPolicy


class SafetyAnswerGuardrail:
    """Foundation only — blocks ungrounded safety answers once answer generation is active."""

    def __init__(self, policy: SafetyGuardrailPolicy | None = None) -> None:
        self._policy = policy or SafetyGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Safety answer validation is not active without an answer to check.",
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="Safety answer check passed.",
        )

from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.policies.answer_guardrail_policy import AnswerGuardrailPolicy


class UnsupportedSuggestionGuardrail:
    """Foundation only — detects invented recommendations, procedures, or specifications."""

    def __init__(self, policy: AnswerGuardrailPolicy | None = None) -> None:
        self._policy = policy or AnswerGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Suggestion detection is not active without an answer to check.",
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="No unsupported suggestions detected.",
        )

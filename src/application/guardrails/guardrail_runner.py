from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult


class GuardrailRunner:
    """Chains a sequence of guardrails and returns the first blocking result.

    Returns None when all guardrails pass, signalling no issue to the caller.
    Future services that need the passing result can inspect individual guardrails.
    """

    def __init__(self, guardrails: list[Guardrail]) -> None:
        self._guardrails = guardrails

    def run(self, context: GuardrailContext) -> GuardrailResult | None:
        for guardrail in self._guardrails:
            result = guardrail.check(context)
            if not result.allowed:
                return result
        return None

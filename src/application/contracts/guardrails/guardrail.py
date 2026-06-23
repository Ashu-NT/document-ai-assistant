from typing import Protocol

from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult


class Guardrail(Protocol):
    def check(self, context: GuardrailContext) -> GuardrailResult: ...

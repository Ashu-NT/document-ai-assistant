from __future__ import annotations

from src.application.guardrails.messages.guardrail_message_builder import (
    GuardrailMessageBuilder,
)
from src.application.guardrails.tracing.guardrail_trace import GuardrailTrace


class GuardrailService:
    def __init__(
        self,
        *,
        message_builder: GuardrailMessageBuilder | None = None,
        trace_factory=GuardrailTrace,
    ) -> None:
        self.message_builder = message_builder or GuardrailMessageBuilder()
        self.trace_factory = trace_factory

    def create_trace(self) -> GuardrailTrace:
        return self.trace_factory()

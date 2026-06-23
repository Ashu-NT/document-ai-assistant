from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.policies.enterprise_guardrail_policy import (
    EnterpriseGuardrailPolicy,
)

_CHARS_PER_TOKEN = 4


class ContextBudgetGuardrail:
    def __init__(self, policy: EnterpriseGuardrailPolicy | None = None) -> None:
        self._policy = policy or EnterpriseGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        chunks = context.approved_chunks or context.retrieved_chunks
        if not chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No chunks to apply budget to.",
            )

        max_tokens = self._policy.max_context_tokens
        max_chars = max_tokens * _CHARS_PER_TOKEN

        approved_ids: list[str] = []
        trimmed_ids: list[str] = []
        char_budget = max_chars

        for chunk in chunks:
            chunk_chars = len(chunk.content)
            if char_budget >= chunk_chars:
                approved_ids.append(chunk.chunk_id)
                char_budget -= chunk_chars
            else:
                trimmed_ids.append(chunk.chunk_id)

        if trimmed_ids:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW_WITH_CAUTION,
                allowed=True,
                reason=(
                    f"{len(approved_ids)} chunk(s) fit within the token budget; "
                    f"{len(trimmed_ids)} chunk(s) were trimmed."
                ),
                approved_chunk_ids=approved_ids,
                rejected_chunk_ids=trimmed_ids,
                evidence_summary=(
                    f"Context trimmed to {len(approved_ids)} chunk(s) "
                    f"to stay within {max_tokens} token budget."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=f"All {len(chunks)} chunk(s) fit within the token budget.",
            approved_chunk_ids=approved_ids,
        )

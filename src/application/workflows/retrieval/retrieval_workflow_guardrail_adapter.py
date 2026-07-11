from __future__ import annotations

from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.retrieval import RetrievalQuery


class RetrievalWorkflowGuardrailAdapter:
    """Builds guardrail contexts and runs guardrail chains for RetrievalWorkflow."""

    def __init__(self, *, min_evidence_chunks: int) -> None:
        self.min_evidence_chunks = min_evidence_chunks

    def build_guardrail_context(
        self,
        working_query: RetrievalQuery,
        *,
        intent: RetrievalQueryIntent,
        retrieved_chunks: list | None = None,
    ) -> GuardrailContext:
        return GuardrailContext(
            query_text=working_query.query_text,
            document_id=working_query.document_id,
            detected_identifiers=list(working_query.detected_identifiers),
            query_intent=str(intent),
            query_chunk_types=[ct.value for ct in working_query.chunk_types],
            retrieved_chunks=retrieved_chunks or [],
            min_evidence_chunks=self.min_evidence_chunks,
        )

    @staticmethod
    def run_guardrail_chain(
        guardrails: list[Guardrail],
        context: GuardrailContext,
    ) -> GuardrailResult | None:
        for guardrail in guardrails:
            result = guardrail.check(context)
            if not result.allowed:
                return result
        return None

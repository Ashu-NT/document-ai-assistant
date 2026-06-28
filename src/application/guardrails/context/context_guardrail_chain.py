from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class ContextGuardrailChain:
    """Runs context guardrails sequentially, threading approved_chunks forward.

    Unlike GuardrailRunner (which stops at the first blocker), each guardrail
    here may also filter the chunk list. The approved_chunk_ids from one step
    become the approved_chunks input for the next, so budget and quality checks
    always operate on already-filtered chunks.
    """

    def __init__(self, guardrails: list[Guardrail]) -> None:
        self._guardrails = guardrails

    def run(
        self,
        retrieved_chunks: list[RetrievedChunk],
        query_text: str = "",
        document_id: str | None = None,
    ) -> tuple[list[RetrievedChunk], GuardrailResult | None]:
        """Return (approved_chunks, None) on success or ([], blocking_result) on block."""
        if not self._guardrails:
            return list(retrieved_chunks), None

        chunk_by_id: dict[str, RetrievedChunk] = {
            c.chunk_id: c for c in retrieved_chunks
        }
        context = GuardrailContext(
            query_text=query_text,
            document_id=document_id,
            retrieved_chunks=retrieved_chunks,
            approved_chunks=list(retrieved_chunks),
        )

        for guardrail in self._guardrails:
            result = guardrail.check(context)

            if not result.allowed:
                return [], result

            # Only update approved_chunks when the guardrail explicitly set them.
            # A guardrail that does not track chunk IDs (returns empty approved_chunk_ids)
            # is treated as a pass-through — the current approved list is preserved.
            if result.approved_chunk_ids:
                context.approved_chunks = [
                    chunk_by_id[cid]
                    for cid in result.approved_chunk_ids
                    if cid in chunk_by_id
                ]

        return context.approved_chunks, None

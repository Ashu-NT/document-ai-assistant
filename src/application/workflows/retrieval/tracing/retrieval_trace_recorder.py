from __future__ import annotations

import time
from typing import TYPE_CHECKING

from src.application.workflows.retrieval.tracing.retrieval_trace import (
    RetrievalTrace,
    TracedChunk,
    TracedGuardrailOutcome,
    TracedQueryAnalysis,
)
from src.domain.common import new_id

if TYPE_CHECKING:
    from src.application.contracts.guardrails.guardrail_result import GuardrailResult
    from src.domain.retrieval import RetrievalQuery, RetrievedChunk


def _chunk_to_traced(chunk: RetrievedChunk) -> TracedChunk:
    meta = chunk.metadata or {}
    return TracedChunk(
        chunk_id=chunk.chunk_id,
        document_id=chunk.document_id,
        chunk_type=chunk.chunk_type.value if chunk.chunk_type else "unknown",
        score=chunk.score,
        fused_score=meta.get("fused_score"),
        best_source_score=meta.get("best_source_score"),
        retrieval_sources=list(meta.get("retrieval_sources", [])),
        section_path=list(chunk.section_path or []),
        page_start=getattr(chunk.source, "page_start", None),
        page_end=getattr(chunk.source, "page_end", None),
        dedup_reason=meta.get("dedup_reason"),
        dedup_collapsed_ids=list(meta.get("dedup_collapsed_chunk_ids", [])),
        dedup_group_size=meta.get("dedup_group_size"),
        dedup_representative_selection_reason=meta.get(
            "dedup_representative_selection_reason"
        ),
    )


class RetrievalTraceRecorder:
    def __init__(self) -> None:
        self._trace_id = new_id("tr")
        self._start_time = time.monotonic()
        self._query_analysis: TracedQueryAnalysis | None = None
        self._pre_guardrail: TracedGuardrailOutcome | None = None
        self._post_guardrail: TracedGuardrailOutcome | None = None
        self._candidate_count: int = 0
        self._retrieved_chunks: list[TracedChunk] = []
        self._dedup_removed_count: int = 0
        self._context_chunk_ids: list[str] = []

    def record_query_analysis(self, working_query: RetrievalQuery) -> None:
        from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
            RetrievalQueryIntentInferer,
        )

        intent = RetrievalQueryIntentInferer().infer(working_query)
        self._query_analysis = TracedQueryAnalysis(
            raw_query=working_query.query_text,
            rewritten_query=getattr(working_query, "rewritten_query", None),
            detected_intent=str(intent),
            detected_identifiers=list(working_query.detected_identifiers or []),
            selected_chunk_types=[ct.value for ct in (working_query.chunk_types or [])],
        )

    def record_pre_guardrail(self, result: GuardrailResult | None) -> None:
        if result is None:
            return
        self._pre_guardrail = TracedGuardrailOutcome(
            phase="pre_retrieval",
            allowed=result.allowed,
            decision=str(result.decision) if result.decision else None,
            safe_user_message=getattr(result, "safe_user_message", None),
        )

    def record_candidates(self, chunks: list[RetrievedChunk]) -> None:
        self._candidate_count = len(chunks)

    def record_dedup(
        self,
        before_count: int,
        after_chunks: list[RetrievedChunk],
    ) -> None:
        self._retrieved_chunks = [_chunk_to_traced(c) for c in after_chunks]
        self._dedup_removed_count = before_count - len(after_chunks)

    def record_context_expansion(self, chunks: list[RetrievedChunk]) -> None:
        self._context_chunk_ids = [c.chunk_id for c in chunks]

    def record_post_guardrail(self, result: GuardrailResult | None) -> None:
        if result is None:
            return
        self._post_guardrail = TracedGuardrailOutcome(
            phase="post_retrieval",
            allowed=result.allowed,
            decision=str(result.decision) if result.decision else None,
            safe_user_message=getattr(result, "safe_user_message", None),
        )

    def build(self, query_id: str, timestamp_iso: str) -> RetrievalTrace:
        duration_ms = (time.monotonic() - self._start_time) * 1000
        analysis = self._query_analysis or TracedQueryAnalysis(
            raw_query="",
            rewritten_query=None,
            detected_intent="unknown",
            detected_identifiers=[],
            selected_chunk_types=[],
        )
        return RetrievalTrace(
            trace_id=self._trace_id,
            query_id=query_id,
            timestamp_iso=timestamp_iso,
            duration_ms=round(duration_ms, 2),
            query_analysis=analysis,
            pre_guardrail=self._pre_guardrail,
            candidate_count=self._candidate_count,
            retrieved_chunks=self._retrieved_chunks,
            dedup_removed_count=self._dedup_removed_count,
            context_chunk_count=len(self._context_chunk_ids),
            context_chunk_ids=self._context_chunk_ids,
            post_guardrail=self._post_guardrail,
            final_chunk_count=len(self._retrieved_chunks),
        )

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TracedQueryAnalysis:
    raw_query: str
    rewritten_query: str | None
    detected_intent: str
    detected_identifiers: list[str]
    selected_chunk_types: list[str]


@dataclass(frozen=True, slots=True)
class TracedChunk:
    chunk_id: str
    document_id: str
    chunk_type: str
    score: float | None
    fused_score: float | None
    best_source_score: float | None
    retrieval_sources: list[str]
    section_path: list[str]
    page_start: int | None
    page_end: int | None
    dedup_reason: str | None
    dedup_collapsed_ids: list[str]
    dedup_group_size: int | None
    dedup_representative_selection_reason: str | None


@dataclass(frozen=True, slots=True)
class TracedGuardrailOutcome:
    phase: str
    allowed: bool
    decision: str | None
    safe_user_message: str | None


@dataclass(frozen=True)
class RetrievalTrace:
    trace_id: str
    query_id: str
    timestamp_iso: str
    duration_ms: float
    query_analysis: TracedQueryAnalysis
    candidate_count: int
    retrieved_chunks: list[TracedChunk]
    dedup_removed_count: int
    context_chunk_count: int
    context_chunk_ids: list[str]
    final_chunk_count: int
    pre_guardrail: TracedGuardrailOutcome | None = None
    post_guardrail: TracedGuardrailOutcome | None = None
    metadata: dict[str, object] = field(default_factory=dict)

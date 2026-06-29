from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class GuardrailContext:
    query_text: str

    document_id: str | None = None
    detected_identifiers: list[str] = field(default_factory=list)
    query_intent: str | None = None
    query_chunk_types: list[str] = field(default_factory=list)
    answer_intent: str | None = None

    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)
    approved_chunks: list[RetrievedChunk] = field(default_factory=list)

    min_evidence_chunks: int = 1
    answer_text: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

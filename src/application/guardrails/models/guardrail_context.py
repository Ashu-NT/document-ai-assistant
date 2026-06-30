from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class GuardrailContext:
    user_input: str = ""
    query_text: str = ""

    route: str | None = None
    document_id: str | None = None
    selected_document_id: str | None = None
    selected_document_title: str | None = None

    detected_identifiers: list[str] = field(default_factory=list)
    query_intent: str | None = None
    query_chunk_types: list[str] = field(default_factory=list)
    answer_intent: str | None = None

    requested_tool: str | None = None
    requested_action: str | None = None
    tool_arguments: dict[str, Any] = field(default_factory=dict)
    blocked_tools: list[str] = field(default_factory=list)
    plan: dict[str, Any] | None = None

    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)
    approved_chunks: list[RetrievedChunk] = field(default_factory=list)
    retrieval_context: list[Any] = field(default_factory=list)
    evidence_chunks: list[Any] = field(default_factory=list)

    citations: list[dict[str, Any]] = field(default_factory=list)
    answer_text: str | None = None
    min_evidence_chunks: int = 1

    runtime_mode: str | None = None
    user_requested_debug: bool = False
    session_id: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.user_input and self.query_text:
            self.user_input = self.query_text
        if not self.query_text and self.user_input:
            self.query_text = self.user_input
        if self.selected_document_id is None and self.document_id is not None:
            self.selected_document_id = self.document_id

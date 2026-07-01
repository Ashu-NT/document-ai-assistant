from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PlanPolicy:
    allowed_tools: set[str] = field(default_factory=lambda: set(_DEFAULT_ALLOWED_TOOLS))
    blocked_tools: set[str] = field(default_factory=lambda: set(_DEFAULT_BLOCKED_TOOLS))
    max_steps: int = 5
    allow_mutating_tools: bool = False
    require_document_scope_for_qa: bool = True
    allow_corpus_wide_retrieval: bool = True
    allow_ingestion: bool = False
    allow_delete: bool = False
    allow_reingestion: bool = False
    max_tool_arg_chars: int = 2000

    @classmethod
    def default(cls) -> "PlanPolicy":
        return cls()


_DEFAULT_ALLOWED_TOOLS = (
    "list_documents",
    "find_document",
    "document_details",
    "explore_document",
    "retrieve_chunks",
    "retrieve_identifiers",
    "answer_question",
    "run_quality_gate",
    "retrieval_trace",
)

_DEFAULT_BLOCKED_TOOLS = (
    "ingest_document",
    "reingest_document",
    "delete_document",
)

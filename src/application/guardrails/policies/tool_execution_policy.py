from __future__ import annotations

from dataclasses import dataclass, field


_DEFAULT_ALLOWED_TOOLS = (
    "list_documents",
    "find_document",
    "document_details",
    "explore_document",
    "retrieve_chunks",
    "retrieve_tables",
    "retrieve_figures",
    "retrieve_identifiers",
    "answer_question",
    "run_quality_gate",
    "retrieval_trace",
)
_DEFAULT_BLOCKED_TOOLS = (
    "delete_document",
    "reingest_document",
    "bulk_delete",
    "vector_delete",
    "database_reset",
    "arbitrary_shell",
)


@dataclass(slots=True, frozen=True)
class ToolExecutionPolicy:
    allowed_tools: tuple[str, ...] = field(default_factory=lambda: _DEFAULT_ALLOWED_TOOLS)
    blocked_tools: tuple[str, ...] = field(default_factory=lambda: _DEFAULT_BLOCKED_TOOLS)
    block_mutating_tools_in_demo: bool = True
    require_registered_tools: bool = True

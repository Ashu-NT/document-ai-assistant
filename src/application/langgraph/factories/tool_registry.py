from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.application.langgraph.common import GraphError


@dataclass(slots=True, kw_only=True)
class ToolRegistry:
    list_documents_tool: Any | None = None
    find_document_tool: Any | None = None
    document_details_tool: Any | None = None
    explore_document_tool: Any | None = None
    retrieve_chunks_tool: Any | None = None
    answer_question_tool: Any | None = None
    run_quality_gate_tool: Any | None = None
    retrieval_trace_tool: Any | None = None

    def get(self, name: str) -> Any | None:
        return self._tool_map().get(name)

    def maybe(self, name: str) -> Any | None:
        return self.get(name)

    def require(self, name: str) -> Any:
        tool = self.get(name)
        if tool is None:
            raise GraphError(
                "Requested application tool is not configured.",
                error_code="tool_not_available",
                details={"tool_name": name},
            )
        return tool

    def _tool_map(self) -> dict[str, Any | None]:
        return {
            "list_documents": self.list_documents_tool,
            "find_document": self.find_document_tool,
            "document_details": self.document_details_tool,
            "explore_document": self.explore_document_tool,
            "retrieve_chunks": self.retrieve_chunks_tool,
            "answer_question": self.answer_question_tool,
            "run_quality_gate": self.run_quality_gate_tool,
            "retrieval_trace": self.retrieval_trace_tool,
        }

from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document_exploration import (
    DocumentExplorationService,
    DocumentNotFoundError,
)
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.tools.retrieval.retrieve_chunks_tool import (
    RetrieveChunksRequest,
    RetrieveChunksTool,
)
from src.domain.common import ChunkType
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class RetrieveFiguresRequest(ToolRequest):
    query_text: str | None = None
    document_id: str | None = None
    top_k: int = 5
    trace: bool = False


class RetrieveFiguresTool:
    metadata = ToolMetadata(
        tool_name="retrieve_figures",
        category="retrieval",
        description="Retrieve figure-oriented chunks or list document figure assets.",
        mutates_state=False,
        supports_trace=True,
    )

    def __init__(
        self,
        retrieve_chunks_tool: RetrieveChunksTool,
        exploration_service: DocumentExplorationService,
    ) -> None:
        self.retrieve_chunks_tool = retrieve_chunks_tool
        self.exploration_service = exploration_service

    def run(self, request: RetrieveFiguresRequest) -> ToolResult:
        if request.query_text and request.query_text.strip():
            result = self.retrieve_chunks_tool.run(
                RetrieveChunksRequest(
                    query_text=request.query_text,
                    document_id=request.document_id,
                    top_k=request.top_k,
                    chunk_types=[ChunkType.DRAWING_REFERENCE],
                    trace=request.trace,
                )
            )
            result.metadata = self.metadata
            return result

        if not request.document_id:
            return invalid_request_result(
                "Provide query_text or document_id.",
                metadata=self.metadata,
            )

        try:
            result = self.exploration_service.explore(request.document_id)
        except DocumentNotFoundError:
            return ToolResult.fail(
                "Document was not found.",
                error_code="document_not_found",
                diagnostics={"document_id": request.document_id},
                metadata=self.metadata,
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        return ToolResult.ok(data=result.assets, metadata=self.metadata)

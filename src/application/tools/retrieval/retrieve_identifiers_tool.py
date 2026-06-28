from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document import DocumentLookupService
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
class RetrieveIdentifiersRequest(ToolRequest):
    document_id: str | None = None
    identifier_value: str | None = None
    query_text: str | None = None
    top_k: int = 5
    trace: bool = False


class RetrieveIdentifiersTool:
    metadata = ToolMetadata(
        tool_name="retrieve_identifiers",
        category="retrieval",
        description="Find identifiers exactly or retrieve identifier-heavy chunks.",
        mutates_state=False,
        supports_trace=True,
    )

    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        exploration_service: DocumentExplorationService,
        retrieve_chunks_tool: RetrieveChunksTool,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.exploration_service = exploration_service
        self.retrieve_chunks_tool = retrieve_chunks_tool

    def run(self, request: RetrieveIdentifiersRequest) -> ToolResult:
        if request.identifier_value and request.identifier_value.strip():
            try:
                identifiers = self.document_lookup_service.search_identifiers(
                    request.identifier_value
                )
            except ApplicationError as exc:
                return application_error_result(exc, metadata=self.metadata)
            return ToolResult.ok(data=identifiers, metadata=self.metadata)

        if request.query_text and request.query_text.strip():
            result = self.retrieve_chunks_tool.run(
                RetrieveChunksRequest(
                    query_text=request.query_text,
                    document_id=request.document_id,
                    top_k=request.top_k,
                    chunk_types=[
                        ChunkType.TECHNICAL_SPECIFICATION,
                        ChunkType.SPARE_PARTS_TABLE,
                        ChunkType.CERTIFICATION_INFO,
                        ChunkType.DRAWING_REFERENCE,
                    ],
                    trace=request.trace,
                )
            )
            result.metadata = self.metadata
            return result

        if request.document_id:
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
            return ToolResult.ok(data=result.identifiers, metadata=self.metadata)

        return invalid_request_result(
            "Provide identifier_value, query_text, or document_id.",
            metadata=self.metadata,
        )

from __future__ import annotations

from dataclasses import dataclass
import re

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
from src.domain.common import ChunkType, IdentifierType
from src.domain.document.entities.identifier import Identifier
from src.shared.exceptions import ApplicationError

_IDENTIFIER_INVENTORY_VERBS = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
_IDENTIFIER_INVENTORY_MARKERS: dict[IdentifierType, tuple[str, ...]] = {
    IdentifierType.PART_NUMBER: ("part number", "part numbers", "part"),
    IdentifierType.SERIAL_NUMBER: ("serial number", "serial numbers", "serial"),
    IdentifierType.MODEL_NUMBER: ("model number", "model numbers", "model"),
    IdentifierType.DRAWING_NUMBER: ("drawing number", "drawing numbers", "drawing"),
    IdentifierType.COMPONENT_CODE: (
        "order code",
        "order codes",
        "order number",
        "order numbers",
        "component code",
        "component codes",
        "tag",
        "tags",
    ),
    IdentifierType.CERTIFICATE_NUMBER: (
        "certificate number",
        "certificate numbers",
        "certificate",
        "approval number",
        "approval numbers",
    ),
    IdentifierType.MANUFACTURER_NAME: (
        "manufacturer",
        "manufacturers",
        "supplier",
        "suppliers",
    ),
}
_IDENTIFIER_VALUE_PATTERN = re.compile(
    r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+)\b",
    re.IGNORECASE,
)


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
            chunk_result = self.retrieve_chunks_tool.run(
                RetrieveChunksRequest(
                    query_text=request.identifier_value.strip(),
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
            chunks: list = []
            if chunk_result.success and isinstance(chunk_result.data, dict):
                chunks = (
                    chunk_result.data.get("context_chunks")
                    or chunk_result.data.get("chunks")
                    or []
                )
            return ToolResult.ok(
                data={"chunks": chunks, "context_chunks": chunks, "identifiers": identifiers},
                metadata=self.metadata,
            )

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
            inventory_identifiers = self._load_inventory_identifiers(request)
            if not inventory_identifiers:
                result.metadata = self.metadata
                return result
            chunks: list = []
            if result.success and isinstance(result.data, dict):
                chunks = (
                    result.data.get("context_chunks")
                    or result.data.get("chunks")
                    or []
                )
            return ToolResult.ok(
                data={
                    "chunks": chunks,
                    "context_chunks": chunks,
                    "identifiers": inventory_identifiers,
                },
                diagnostics={"inventory_identifier_count": len(inventory_identifiers)},
                metadata=self.metadata,
            )

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

    def _load_inventory_identifiers(
        self,
        request: RetrieveIdentifiersRequest,
    ) -> list[Identifier]:
        if not request.document_id or not self._is_identifier_inventory_query(
            request.query_text
        ):
            return []
        try:
            exploration = self.exploration_service.explore(request.document_id)
        except (ApplicationError, DocumentNotFoundError):
            return []

        requested_types = self._requested_identifier_types(request.query_text)
        identifiers: list[Identifier] = []
        for entry in exploration.identifiers:
            identifier_type = self._identifier_type_from_value(entry.identifier_type)
            if identifier_type is None:
                continue
            if requested_types and identifier_type not in requested_types:
                continue
            identifiers.append(
                Identifier(
                    identifier_id=entry.identifier_id,
                    document_id=exploration.document_id,
                    raw_value=entry.raw_value,
                    identifier_type=identifier_type,
                    normalized_value=entry.normalized_value,
                )
            )
        return identifiers

    @staticmethod
    def _is_identifier_inventory_query(query_text: str | None) -> bool:
        normalized = " ".join((query_text or "").strip().lower().split())
        if not normalized:
            return False
        if _IDENTIFIER_VALUE_PATTERN.search(normalized):
            return False
        if not any(marker in normalized for marker in _IDENTIFIER_INVENTORY_VERBS):
            return False
        return any(
            marker in normalized
            for markers in _IDENTIFIER_INVENTORY_MARKERS.values()
            for marker in markers
        )

    @staticmethod
    def _requested_identifier_types(query_text: str | None) -> set[IdentifierType]:
        normalized = " ".join((query_text or "").strip().lower().split())
        requested: set[IdentifierType] = set()
        for identifier_type, markers in _IDENTIFIER_INVENTORY_MARKERS.items():
            if any(marker in normalized for marker in markers):
                requested.add(identifier_type)
        return requested

    @staticmethod
    def _identifier_type_from_value(value: str | None) -> IdentifierType | None:
        try:
            identifier_type = IdentifierType(str(value or IdentifierType.UNKNOWN.value))
        except ValueError:
            return None
        if identifier_type == IdentifierType.UNKNOWN:
            return None
        return identifier_type

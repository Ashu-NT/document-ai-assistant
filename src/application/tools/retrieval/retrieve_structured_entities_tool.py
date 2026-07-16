from __future__ import annotations

from dataclasses import dataclass

from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.services.extraction import ExtractionService
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.workflows.retrieval.structured import (
    StructuredEntityResolver,
)
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class RetrieveStructuredEntitiesRequest(ToolRequest):
    entity_type: str = ""
    document_id: str | None = None
    query_text: str | None = None
    top_k: int = 20


class RetrieveStructuredEntitiesTool:
    """Reads back the structured entities extracted during ingestion
    (manufacturers, suppliers, spare parts, equipment, maintenance tasks)
    directly from their DB tables, so a question can be answered from the
    full extracted row (e.g. a manufacturer's website/country) instead of
    only the bare name/value that reaches the Identifier table."""

    metadata = ToolMetadata(
        tool_name="retrieve_structured_entities",
        category="retrieval",
        description=(
            "Look up extracted structured entities (manufacturers, suppliers, "
            "contact points, spare parts, equipment, maintenance tasks, procedures, "
            "specifications, safety warnings, maintenance intervals, "
            "troubleshooting entries) by document and/or search text."
        ),
        mutates_state=False,
        supports_trace=False,
    )

    def __init__(
        self,
        extraction_service: ExtractionService,
        entity_resolver: StructuredEntityResolver | None = None,
    ) -> None:
        self.extraction_service = extraction_service
        self.entity_resolver = entity_resolver or StructuredEntityResolver(
            extraction_service
        )

    def run(self, request: RetrieveStructuredEntitiesRequest) -> ToolResult:
        try:
            entity_type = ExtractionPromptType(request.entity_type)
        except ValueError:
            return invalid_request_result(
                "entity_type must be one of: "
                + ", ".join(member.value for member in ExtractionPromptType),
                metadata=self.metadata,
                diagnostics={"entity_type": request.entity_type},
            )

        query_text = (request.query_text or "").strip()
        document_id = request.document_id

        if not query_text and not document_id:
            return invalid_request_result(
                "Provide document_id and/or query_text.",
                metadata=self.metadata,
            )

        try:
            items = self.entity_resolver.resolve(
                entity_type,
                query_text=query_text,
                document_id=document_id,
                top_k=None,
                fallback_to_list=document_id is not None,
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        returned_items = items[: max(request.top_k, 0)]

        return ToolResult.ok(
            data={
                "entity_type": entity_type.value,
                "items": returned_items,
            },
            diagnostics={
                "total_matches": len(items),
                "returned": len(returned_items),
            },
            metadata=self.metadata,
        )

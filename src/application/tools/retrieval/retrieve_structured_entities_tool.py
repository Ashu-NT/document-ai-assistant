from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import StrEnum
from typing import Any

from src.application.services.extraction import ExtractionService
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.shared.exceptions import ApplicationError


class StructuredEntityType(StrEnum):
    MANUFACTURER = "manufacturer"
    SUPPLIER = "supplier"
    SPARE_PART = "spare_part"
    EQUIPMENT = "equipment"
    MAINTENANCE_TASK = "maintenance_task"
    PROCEDURE = "procedure"
    SPECIFICATION = "specification"
    SAFETY_WARNING = "safety_warning"
    MAINTENANCE_INTERVAL = "maintenance_interval"
    TROUBLESHOOTING = "troubleshooting"


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
            "spare parts, equipment, maintenance tasks, procedures, "
            "specifications, safety warnings, maintenance intervals, "
            "troubleshooting entries) by document and/or search text."
        ),
        mutates_state=False,
        supports_trace=False,
    )

    _SEARCH_METHODS: dict[StructuredEntityType, str] = {
        StructuredEntityType.MANUFACTURER: "search_manufacturers",
        StructuredEntityType.SUPPLIER: "search_suppliers",
        StructuredEntityType.SPARE_PART: "search_spare_parts",
        StructuredEntityType.EQUIPMENT: "search_equipment",
        StructuredEntityType.MAINTENANCE_TASK: "search_maintenance_tasks",
        StructuredEntityType.PROCEDURE: "search_procedures",
        StructuredEntityType.SPECIFICATION: "search_specifications",
        StructuredEntityType.SAFETY_WARNING: "search_safety_warnings",
        StructuredEntityType.MAINTENANCE_INTERVAL: "search_maintenance_intervals",
        StructuredEntityType.TROUBLESHOOTING: "search_troubleshooting_entries",
    }
    _LIST_METHODS: dict[StructuredEntityType, str] = {
        StructuredEntityType.MANUFACTURER: "list_manufacturers",
        StructuredEntityType.SUPPLIER: "list_suppliers",
        StructuredEntityType.SPARE_PART: "list_spare_parts",
        StructuredEntityType.EQUIPMENT: "list_equipment",
        StructuredEntityType.MAINTENANCE_TASK: "list_maintenance_tasks",
        StructuredEntityType.PROCEDURE: "list_procedures",
        StructuredEntityType.SPECIFICATION: "list_specifications",
        StructuredEntityType.SAFETY_WARNING: "list_safety_warnings",
        StructuredEntityType.MAINTENANCE_INTERVAL: "list_maintenance_intervals",
        StructuredEntityType.TROUBLESHOOTING: "list_troubleshooting_entries",
    }

    def __init__(self, extraction_service: ExtractionService) -> None:
        self.extraction_service = extraction_service

    def run(self, request: RetrieveStructuredEntitiesRequest) -> ToolResult:
        try:
            entity_type = StructuredEntityType(request.entity_type)
        except ValueError:
            return invalid_request_result(
                "entity_type must be one of: "
                + ", ".join(member.value for member in StructuredEntityType),
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
            if query_text:
                method_name = self._SEARCH_METHODS[entity_type]
                method = getattr(self.extraction_service, method_name)
                items = method(query_text, document_id)
            else:
                method_name = self._LIST_METHODS[entity_type]
                method = getattr(self.extraction_service, method_name)
                items = method(document_id)
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        truncated = list(items)[: max(request.top_k, 0)]

        return ToolResult.ok(
            data={
                "entity_type": entity_type.value,
                "items": [self._serialize(item) for item in truncated],
            },
            diagnostics={"total_matches": len(items), "returned": len(truncated)},
            metadata=self.metadata,
        )

    @staticmethod
    def _serialize(item: Any) -> dict[str, Any]:
        if is_dataclass(item) and not isinstance(item, type):
            return asdict(item)
        return dict(vars(item))

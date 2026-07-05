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
from src.domain.extraction import SemanticEntityType
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

    # `StructuredEntityType` and `SemanticEntityType` share string values for
    # every member except TROUBLESHOOTING ("troubleshooting" here vs.
    # "troubleshooting_entry" on the semantic side), so this cannot be a
    # value-equality lookup and needs an explicit mapping both ways.
    _SEMANTIC_ENTITY_TYPES: dict[StructuredEntityType, SemanticEntityType] = {
        StructuredEntityType.MANUFACTURER: SemanticEntityType.MANUFACTURER,
        StructuredEntityType.SUPPLIER: SemanticEntityType.SUPPLIER,
        StructuredEntityType.SPARE_PART: SemanticEntityType.SPARE_PART,
        StructuredEntityType.EQUIPMENT: SemanticEntityType.EQUIPMENT,
        StructuredEntityType.MAINTENANCE_TASK: SemanticEntityType.MAINTENANCE_TASK,
        StructuredEntityType.PROCEDURE: SemanticEntityType.PROCEDURE,
        StructuredEntityType.SPECIFICATION: SemanticEntityType.SPECIFICATION,
        StructuredEntityType.SAFETY_WARNING: SemanticEntityType.SAFETY_WARNING,
        StructuredEntityType.MAINTENANCE_INTERVAL: SemanticEntityType.MAINTENANCE_INTERVAL,
        StructuredEntityType.TROUBLESHOOTING: SemanticEntityType.TROUBLESHOOTING_ENTRY,
    }
    _STRUCTURED_ENTITY_TYPES: dict[SemanticEntityType, StructuredEntityType] = {
        semantic_type: structured_type
        for structured_type, semantic_type in _SEMANTIC_ENTITY_TYPES.items()
    }
    _ID_FIELDS: dict[StructuredEntityType, str] = {
        StructuredEntityType.MANUFACTURER: "manufacturer_id",
        StructuredEntityType.SUPPLIER: "supplier_id",
        StructuredEntityType.SPARE_PART: "spare_part_id",
        StructuredEntityType.EQUIPMENT: "equipment_id",
        StructuredEntityType.MAINTENANCE_TASK: "task_id",
        StructuredEntityType.PROCEDURE: "procedure_id",
        StructuredEntityType.SPECIFICATION: "specification_id",
        StructuredEntityType.SAFETY_WARNING: "safety_warning_id",
        StructuredEntityType.MAINTENANCE_INTERVAL: "maintenance_interval_id",
        StructuredEntityType.TROUBLESHOOTING: "troubleshooting_id",
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

        serialized_items = [self._serialize(item) for item in truncated]
        for serialized_item in serialized_items:
            serialized_item["related_entities"] = []
        self._attach_related_entities(serialized_items, entity_type=entity_type)

        return ToolResult.ok(
            data={
                "entity_type": entity_type.value,
                "items": serialized_items,
            },
            diagnostics={"total_matches": len(items), "returned": len(truncated)},
            metadata=self.metadata,
        )

    def _attach_related_entities(
        self,
        serialized_items: list[dict[str, Any]],
        *,
        entity_type: StructuredEntityType,
    ) -> None:
        """Enrich each item with the `SemanticRelationship` links discovered
        by `SemanticLinkingWorkflow`, so a retrieved task/equipment/etc. also
        surfaces its linked procedure, spare parts, safety warnings, etc.
        instead of just its own bare row.

        Grouped by each item's own `document_id` (not the request's, which
        may be absent for a cross-document `query_text` search) since
        relationships are only ever looked up within a single document.
        """
        semantic_type = self._SEMANTIC_ENTITY_TYPES[entity_type]
        id_field = self._ID_FIELDS[entity_type]

        items_by_document: dict[str, dict[str, dict[str, Any]]] = {}
        for item in serialized_items:
            item_id = item.get(id_field)
            item_document_id = item.get("document_id")
            if not item_id or not item_document_id:
                continue
            items_by_document.setdefault(item_document_id, {})[item_id] = item

        for document_id, items_by_id in items_by_document.items():
            self._attach_related_entities_for_document(
                items_by_id,
                semantic_type=semantic_type,
                document_id=document_id,
            )

    def _attach_related_entities_for_document(
        self,
        items_by_id: dict[str, dict[str, Any]],
        *,
        semantic_type: SemanticEntityType,
        document_id: str,
    ) -> None:
        try:
            relationships = self.extraction_service.list_semantic_relationships(
                document_id
            )
        except ApplicationError:
            return

        # item_id -> [(direction, related_entity_type, related_entity_id, relationship)]
        links: dict[str, list[tuple[str, SemanticEntityType, str, Any]]] = {}
        for relationship in relationships:
            if (
                relationship.source_entity_type == semantic_type
                and relationship.source_entity_id in items_by_id
            ):
                links.setdefault(relationship.source_entity_id, []).append(
                    (
                        "outgoing",
                        relationship.target_entity_type,
                        relationship.target_entity_id,
                        relationship,
                    )
                )
            if (
                relationship.target_entity_type == semantic_type
                and relationship.target_entity_id in items_by_id
            ):
                links.setdefault(relationship.target_entity_id, []).append(
                    (
                        "incoming",
                        relationship.source_entity_type,
                        relationship.source_entity_id,
                        relationship,
                    )
                )

        if not links:
            return

        related_types = {
            related_type
            for entries in links.values()
            for _, related_type, _, _ in entries
        }
        related_entities = self._load_entities_by_type_and_id(
            related_types, document_id
        )

        for item_id, entries in links.items():
            items_by_id[item_id]["related_entities"] = [
                {
                    "relationship_type": relationship.relationship_type.value,
                    "direction": direction,
                    "status": relationship.status.value,
                    "confidence_score": relationship.confidence_score,
                    "entity_type": self._STRUCTURED_ENTITY_TYPES[related_type].value,
                    "entity_id": related_id,
                    "entity": related_entities.get(related_type, {}).get(related_id),
                }
                for direction, related_type, related_id, relationship in entries
            ]

    def _load_entities_by_type_and_id(
        self,
        semantic_types: set[SemanticEntityType],
        document_id: str,
    ) -> dict[SemanticEntityType, dict[str, dict[str, Any]]]:
        loaded: dict[SemanticEntityType, dict[str, dict[str, Any]]] = {}
        for semantic_type in semantic_types:
            structured_type = self._STRUCTURED_ENTITY_TYPES.get(semantic_type)
            if structured_type is None:
                continue

            id_field = self._ID_FIELDS[structured_type]
            method = getattr(self.extraction_service, self._LIST_METHODS[structured_type])
            try:
                entities = method(document_id)
            except ApplicationError:
                continue

            serialized = (self._serialize(entity) for entity in entities)
            loaded[semantic_type] = {
                entity[id_field]: entity
                for entity in serialized
                if entity.get(id_field)
            }
        return loaded

    @staticmethod
    def _serialize(item: Any) -> dict[str, Any]:
        if is_dataclass(item) and not isinstance(item, type):
            return asdict(item)
        return dict(vars(item))

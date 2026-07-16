from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from src.application.services.extraction import ExtractionService
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.domain.extraction import SemanticEntityType
from src.shared.exceptions import ApplicationError


class StructuredEntityResolver:
    _SEARCH_METHODS: dict[ExtractionPromptType, str] = {
        ExtractionPromptType.MANUFACTURER: "search_manufacturers",
        ExtractionPromptType.SUPPLIER: "search_suppliers",
        ExtractionPromptType.CONTACT_POINT: "search_contact_points",
        ExtractionPromptType.SPARE_PART: "search_spare_parts",
        ExtractionPromptType.EQUIPMENT: "search_equipment",
        ExtractionPromptType.MAINTENANCE_TASK: "search_maintenance_tasks",
        ExtractionPromptType.PROCEDURE: "search_procedures",
        ExtractionPromptType.SPECIFICATION: "search_specifications",
        ExtractionPromptType.SAFETY_WARNING: "search_safety_warnings",
        ExtractionPromptType.MAINTENANCE_INTERVAL: "search_maintenance_intervals",
        ExtractionPromptType.TROUBLESHOOTING: "search_troubleshooting_entries",
    }
    _LIST_METHODS: dict[ExtractionPromptType, str] = {
        ExtractionPromptType.MANUFACTURER: "list_manufacturers",
        ExtractionPromptType.SUPPLIER: "list_suppliers",
        ExtractionPromptType.CONTACT_POINT: "list_contact_points",
        ExtractionPromptType.SPARE_PART: "list_spare_parts",
        ExtractionPromptType.EQUIPMENT: "list_equipment",
        ExtractionPromptType.MAINTENANCE_TASK: "list_maintenance_tasks",
        ExtractionPromptType.PROCEDURE: "list_procedures",
        ExtractionPromptType.SPECIFICATION: "list_specifications",
        ExtractionPromptType.SAFETY_WARNING: "list_safety_warnings",
        ExtractionPromptType.MAINTENANCE_INTERVAL: "list_maintenance_intervals",
        ExtractionPromptType.TROUBLESHOOTING: "list_troubleshooting_entries",
    }
    _SEMANTIC_ENTITY_TYPES: dict[ExtractionPromptType, SemanticEntityType] = {
        ExtractionPromptType.MANUFACTURER: SemanticEntityType.MANUFACTURER,
        ExtractionPromptType.SUPPLIER: SemanticEntityType.SUPPLIER,
        ExtractionPromptType.CONTACT_POINT: SemanticEntityType.CONTACT_POINT,
        ExtractionPromptType.SPARE_PART: SemanticEntityType.SPARE_PART,
        ExtractionPromptType.EQUIPMENT: SemanticEntityType.EQUIPMENT,
        ExtractionPromptType.MAINTENANCE_TASK: SemanticEntityType.MAINTENANCE_TASK,
        ExtractionPromptType.PROCEDURE: SemanticEntityType.PROCEDURE,
        ExtractionPromptType.SPECIFICATION: SemanticEntityType.SPECIFICATION,
        ExtractionPromptType.SAFETY_WARNING: SemanticEntityType.SAFETY_WARNING,
        ExtractionPromptType.MAINTENANCE_INTERVAL: SemanticEntityType.MAINTENANCE_INTERVAL,
        ExtractionPromptType.TROUBLESHOOTING: SemanticEntityType.TROUBLESHOOTING_ENTRY,
    }
    _STRUCTURED_ENTITY_TYPES: dict[SemanticEntityType, ExtractionPromptType] = {
        semantic_type: structured_type
        for structured_type, semantic_type in _SEMANTIC_ENTITY_TYPES.items()
    }
    _ID_FIELDS: dict[ExtractionPromptType, str] = {
        ExtractionPromptType.MANUFACTURER: "manufacturer_id",
        ExtractionPromptType.SUPPLIER: "supplier_id",
        ExtractionPromptType.CONTACT_POINT: "contact_point_id",
        ExtractionPromptType.SPARE_PART: "spare_part_id",
        ExtractionPromptType.EQUIPMENT: "equipment_id",
        ExtractionPromptType.MAINTENANCE_TASK: "task_id",
        ExtractionPromptType.PROCEDURE: "procedure_id",
        ExtractionPromptType.SPECIFICATION: "specification_id",
        ExtractionPromptType.SAFETY_WARNING: "safety_warning_id",
        ExtractionPromptType.MAINTENANCE_INTERVAL: "maintenance_interval_id",
        ExtractionPromptType.TROUBLESHOOTING: "troubleshooting_id",
    }

    def __init__(self, extraction_service: ExtractionService) -> None:
        self.extraction_service = extraction_service

    def resolve(
        self,
        entity_type: ExtractionPromptType,
        *,
        query_text: str | None = None,
        document_id: str | None = None,
        top_k: int | None = None,
        fallback_to_list: bool = False,
    ) -> list[dict[str, Any]]:
        items = self._load_items(
            entity_type,
            query_text=query_text,
            document_id=document_id,
            fallback_to_list=fallback_to_list,
        )
        serialized_items = [self._serialize(item) for item in items]
        if top_k is not None:
            serialized_items = serialized_items[: max(top_k, 0)]
        for item in serialized_items:
            item["related_entities"] = []
        self._attach_related_entities(serialized_items, entity_type=entity_type)
        return serialized_items

    def entity_id_field(self, entity_type: ExtractionPromptType) -> str:
        return self._ID_FIELDS[entity_type]

    def _load_items(
        self,
        entity_type: ExtractionPromptType,
        *,
        query_text: str | None,
        document_id: str | None,
        fallback_to_list: bool,
    ) -> list[Any]:
        query_text = (query_text or "").strip()
        if query_text:
            method = getattr(self.extraction_service, self._SEARCH_METHODS[entity_type])
            items = list(method(query_text, document_id))
            if items or not fallback_to_list or document_id is None:
                return items
        method = getattr(self.extraction_service, self._LIST_METHODS[entity_type])
        return list(method(document_id))

    def _attach_related_entities(
        self,
        serialized_items: list[dict[str, Any]],
        *,
        entity_type: ExtractionPromptType,
    ) -> None:
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

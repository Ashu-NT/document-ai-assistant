from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
    AnswerRelationship,
    AnswerStructuredEntity,
)

# Mirrors the per-entity-type id field names already used by
# StructuredEntityResolver._ID_FIELDS and
# QuestionAnsweringWorkflow._deduplicate_structured_entities' own fallback
# lookup -- the raw resolved-entity dicts don't carry a uniform "id" key,
# so every consumer that needs "this entity's id" tries the same known
# field names in order.
_ENTITY_ID_FIELDS: tuple[str, ...] = (
    "manufacturer_id",
    "supplier_id",
    "contact_point_id",
    "spare_part_id",
    "equipment_id",
    "task_id",
    "procedure_id",
    "specification_id",
    "safety_warning_id",
    "maintenance_interval_id",
    "troubleshooting_id",
)
_BOOKKEEPING_KEYS = frozenset({"_entity_type", "related_entities"})


class StructuredEvidenceViewBuilder:
    """Converts the raw resolved-structured-entity dicts (produced by
    StructuredEntityResolver/StructuredEvidenceResolver) into typed
    AnswerStructuredEntity/AnswerRelationship views, so a resolved
    relationship (e.g. a maintenance task's linked procedure, complete with
    its steps) survives into StructuredAnswerContext instead of only ever
    reaching the answer through AnswerKeyValue's single string value --
    see plan sections 4.2, 4.16, 9.2, 9.3."""

    def build(self, entities: list[dict]) -> list[AnswerStructuredEntity]:
        built: list[AnswerStructuredEntity] = []
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            entity_type = entity.get("_entity_type")
            if not entity_type:
                continue
            built.append(
                AnswerStructuredEntity(
                    entity_type=str(entity_type),
                    entity_id=self._entity_id(entity),
                    fields={
                        key: value
                        for key, value in entity.items()
                        if key not in _BOOKKEEPING_KEYS
                    },
                    source_chunk_id=(
                        str(entity["source_chunk_id"])
                        if entity.get("source_chunk_id")
                        else None
                    ),
                    relationships=self._relationships(entity),
                )
            )
        return built

    @staticmethod
    def _entity_id(entity: dict) -> str:
        for field_name in _ENTITY_ID_FIELDS:
            value = entity.get(field_name)
            if value:
                return str(value)
        source_chunk_id = entity.get("source_chunk_id")
        return str(source_chunk_id) if source_chunk_id else ""

    @staticmethod
    def _relationships(entity: dict) -> list[AnswerRelationship]:
        relationships: list[AnswerRelationship] = []
        for related in entity.get("related_entities", []):
            if not isinstance(related, dict):
                continue
            relationships.append(
                AnswerRelationship(
                    relationship_type=str(related.get("relationship_type") or ""),
                    direction=str(related.get("direction") or ""),
                    status=str(related.get("status") or ""),
                    confidence_score=related.get("confidence_score"),
                    target_entity_type=str(related.get("entity_type") or ""),
                    target_entity_id=str(related.get("entity_id") or ""),
                    target_entity_fields=dict(related.get("entity") or {}),
                )
            )
        return relationships

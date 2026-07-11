from __future__ import annotations

from src.application.workflows.question_answering.answer_context.structured_entity_field_labels import (
    field_labels_for_entity,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
)
from src.domain.document.entities.identifier import Identifier


class StructuredFactKeyValueBuilder:
    """Turns already-resolved structured facts (Identifier rows, extracted
    entity rows) into AnswerKeyValue entries that join the same generation
    context as chunk-derived key-values, instead of only ever reaching the
    user through a deterministic bypass renderer."""

    def build_from_identifiers(
        self,
        identifiers: list[Identifier],
        *,
        source_number_by_chunk_id: dict[str, int],
    ) -> list[AnswerKeyValue]:
        key_values: list[AnswerKeyValue] = []
        for identifier in identifiers:
            source_number = source_number_by_chunk_id.get(identifier.chunk_id or "")
            if source_number is None or not identifier.raw_value:
                continue
            key_values.append(
                AnswerKeyValue(
                    key=self._identifier_label(identifier.identifier_type),
                    value=identifier.raw_value.strip(),
                    unit=None,
                    source_number=source_number,
                    confidence=identifier.confidence_score,
                )
            )
        return key_values

    def build_from_structured_entities(
        self,
        entity_type: str,
        entities: list[dict],
        *,
        source_number_by_chunk_id: dict[str, int],
    ) -> list[AnswerKeyValue]:
        key_values: list[AnswerKeyValue] = []
        seen: set[tuple[str, str, int]] = set()
        for candidate_type, entity in self._iter_entities_with_related(
            entity_type, entities
        ):
            source_number = source_number_by_chunk_id.get(
                entity.get("source_chunk_id") or ""
            )
            if source_number is None:
                continue
            for field_name, label in field_labels_for_entity(candidate_type, entity):
                value = entity.get(field_name)
                if value is None or not str(value).strip():
                    continue
                dedup_key = (label, str(value).strip(), source_number)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                key_values.append(
                    AnswerKeyValue(
                        key=label,
                        value=str(value).strip(),
                        unit=None,
                        source_number=source_number,
                        confidence=entity.get("confidence_score"),
                    )
                )
        return key_values

    @classmethod
    def _iter_entities_with_related(
        cls,
        entity_type: str,
        entities: list[dict],
    ):
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            yield entity_type, entity
            for related in entity.get("related_entities", []):
                if not isinstance(related, dict):
                    continue
                related_type = related.get("entity_type")
                related_entity = related.get("entity")
                if not related_type or not isinstance(related_entity, dict):
                    continue
                yield str(related_type), related_entity

    @staticmethod
    def _identifier_label(identifier_type: object) -> str:
        return str(identifier_type).replace("_", " ").title()

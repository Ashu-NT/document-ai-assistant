from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models import (
    PromptEntityView,
)
from src.application.workflows.question_answering.answer_context.structured_entity_field_labels import (
    field_labels_for_entity,
)


class EntityKeyValueFingerprintBuilder:
    def build(
        self,
        entities: list[PromptEntityView],
        *,
        source_number_by_chunk_id: dict[str, int],
    ) -> set[tuple[str, str, int]]:
        fingerprints: set[tuple[str, str, int]] = set()
        for entity in entities:
            source_number = source_number_by_chunk_id.get(entity.source_chunk_id or "")
            if source_number is None:
                continue
            fingerprints.update(
                self._entity_fingerprints(
                    entity.entity_type,
                    entity.fields,
                    source_number=source_number,
                )
            )
            for relationship in entity.relationships:
                fingerprints.update(
                    self._entity_fingerprints(
                        relationship.target_entity_type,
                        relationship.target_entity_fields,
                        source_number=source_number,
                    )
                )
        return fingerprints

    @staticmethod
    def _entity_fingerprints(
        entity_type: str,
        fields: dict[str, object],
        *,
        source_number: int,
    ) -> set[tuple[str, str, int]]:
        fingerprints: set[tuple[str, str, int]] = set()
        for field_name, label in field_labels_for_entity(entity_type, fields):
            value = fields.get(field_name)
            normalized_value = " ".join(str(value or "").split()).strip()
            if not normalized_value:
                continue
            fingerprints.add((label.lower(), normalized_value.lower(), source_number))
        return fingerprints

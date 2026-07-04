from __future__ import annotations

from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerKeyValue,
)
from src.domain.document.entities.identifier import Identifier

_ENTITY_FIELD_LABELS: dict[str, tuple[tuple[str, str], ...]] = {
    "manufacturer": (
        ("name", "Manufacturer Name"),
        ("website", "Manufacturer Website"),
        ("country", "Manufacturer Country"),
    ),
    "supplier": (
        ("name", "Supplier Name"),
        ("website", "Supplier Website"),
        ("country", "Supplier Country"),
    ),
    "spare_part": (
        ("part_number", "Part Number"),
        ("description", "Part Description"),
        ("quantity", "Part Quantity"),
        ("component_name", "Part Component"),
    ),
    "equipment": (
        ("name", "Equipment Name"),
        ("model_number", "Equipment Model Number"),
        ("serial_number", "Equipment Serial Number"),
    ),
    "maintenance_task": (
        ("title", "Maintenance Task"),
        ("interval", "Maintenance Interval"),
        ("component_name", "Maintenance Component"),
    ),
}


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
        field_labels = _ENTITY_FIELD_LABELS.get(entity_type, ())
        key_values: list[AnswerKeyValue] = []
        for entity in entities:
            source_number = source_number_by_chunk_id.get(
                entity.get("source_chunk_id") or ""
            )
            if source_number is None:
                continue
            for field_name, label in field_labels:
                value = entity.get(field_name)
                if value is None or not str(value).strip():
                    continue
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

    @staticmethod
    def _identifier_label(identifier_type: object) -> str:
        return str(identifier_type).replace("_", " ").title()

from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
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
    "contact_point": (
        ("owner_name", "Contact Owner"),
        ("label", "Contact Label"),
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
            for field_name, label in self._field_labels_for_entity(candidate_type, entity):
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

    @classmethod
    def _field_labels_for_entity(
        cls,
        entity_type: str,
        entity: dict,
    ) -> tuple[tuple[str, str], ...]:
        if entity_type != "contact_point":
            return _ENTITY_FIELD_LABELS.get(entity_type, ())

        contact_label = cls._contact_value_label(entity)
        return (
            ("value", contact_label),
            *_ENTITY_FIELD_LABELS["contact_point"],
        )

    @staticmethod
    def _contact_value_label(entity: dict) -> str:
        owner_entity_type = str(entity.get("owner_entity_type") or "").strip().lower()
        owner_prefix = {
            "manufacturer": "Manufacturer",
            "supplier": "Supplier",
        }.get(owner_entity_type, "Contact")
        contact_type = str(entity.get("contact_type") or "").strip().lower()
        contact_suffix = {
            "phone_number": "Phone Number",
            "fax_number": "Fax Number",
            "email_address": "Email Address",
            "url": "Website",
        }.get(contact_type, "Value")
        return f"{owner_prefix} {contact_suffix}"

    @staticmethod
    def _identifier_label(identifier_type: object) -> str:
        return str(identifier_type).replace("_", " ").title()

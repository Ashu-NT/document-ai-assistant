from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from src.application.workflows.question_answering.answer_pipeline.structured_fact_join.structured_evidence_scope import (
    StructuredEvidenceScope,
)
from src.domain.document.entities.identifier import Identifier


class StructuredEvidenceScopeFilter:
    def __init__(self, scope: StructuredEvidenceScope) -> None:
        self._scope = scope

    def filter_identifiers(
        self,
        identifiers: Sequence[Identifier],
    ) -> list[Identifier]:
        return [
            identifier
            for identifier in identifiers
            if self._identifier_is_in_scope(identifier)
        ]

    def filter_entities(
        self,
        entities: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for entity in entities:
            if not self._entity_is_in_scope(entity):
                continue
            filtered.append(
                {
                    **entity,
                    "related_entities": self._filtered_related_entities(
                        entity.get("related_entities", [])
                    ),
                }
            )
        return filtered

    def _filtered_related_entities(
        self,
        related_entities: object,
    ) -> list[dict[str, Any]]:
        if not isinstance(related_entities, list):
            return []
        filtered: list[dict[str, Any]] = []
        for related in related_entities:
            if not isinstance(related, dict):
                continue
            related_entity = related.get("entity")
            if not isinstance(related_entity, dict):
                continue
            if not self._has_provenance(related_entity):
                filtered.append({**related, "entity": dict(related_entity)})
                continue
            if not self._entity_is_in_scope(related_entity):
                continue
            filtered.append({**related, "entity": dict(related_entity)})
        return filtered

    def _identifier_is_in_scope(self, identifier: Identifier) -> bool:
        if (
            identifier.document_id
            and self._scope.document_ids
            and identifier.document_id not in self._scope.document_ids
        ):
            return False
        if self._scope.contains_chunk_id(identifier.chunk_id):
            return True
        return self._scope.overlaps_pages(
            page_start=identifier.page_start,
            page_end=identifier.page_end,
        )

    def _entity_is_in_scope(self, entity: dict[str, Any]) -> bool:
        document_id = _normalized_string(entity.get("document_id"))
        source_chunk_id = _normalized_string(entity.get("source_chunk_id"))
        source_metadata = (
            entity.get("source_metadata")
            if isinstance(entity.get("source_metadata"), dict)
            else {}
        )
        metadata_document_id = _normalized_string(source_metadata.get("document_id"))
        metadata_chunk_id = _normalized_string(source_metadata.get("chunk_id"))
        metadata_table_id = _normalized_string(source_metadata.get("table_id"))
        page_start = _normalized_int(source_metadata.get("page_start"))
        page_end = _normalized_int(source_metadata.get("page_end"))

        candidate_document_id = document_id or metadata_document_id
        if (
            candidate_document_id
            and self._scope.document_ids
            and candidate_document_id not in self._scope.document_ids
        ):
            return False

        if self._scope.contains_chunk_id(source_chunk_id):
            return True
        if self._scope.contains_chunk_id(metadata_chunk_id):
            return True
        if self._scope.contains_table_id(metadata_table_id):
            return True
        return self._scope.overlaps_pages(
            page_start=page_start,
            page_end=page_end,
        )

    @staticmethod
    def _has_provenance(entity: dict[str, Any]) -> bool:
        source_chunk_id = _normalized_string(entity.get("source_chunk_id"))
        if source_chunk_id is not None:
            return True
        source_metadata = (
            entity.get("source_metadata")
            if isinstance(entity.get("source_metadata"), dict)
            else {}
        )
        return any(
            (
                _normalized_string(source_metadata.get("chunk_id")),
                _normalized_string(source_metadata.get("table_id")),
                _normalized_int(source_metadata.get("page_start")),
                _normalized_int(source_metadata.get("page_end")),
            )
        )


def _normalized_string(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalized_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

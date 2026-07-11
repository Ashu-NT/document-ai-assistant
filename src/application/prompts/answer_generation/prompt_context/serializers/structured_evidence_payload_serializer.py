import json
from dataclasses import asdict

from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)


class StructuredEvidencePayloadSerializer:
    def serialize(self, context: PromptContextBundle | None) -> str:
        if context is None:
            return ""
        payload = {
            "answer_intent": context.answer_intent_value,
            "source_count": context.source_count,
            "sources": [self._source_payload(source) for source in context.sources],
            "key_values": [asdict(item) for item in context.key_values],
            "maintenance_entries": [
                self._maintenance_entry_payload(entry)
                for entry in context.maintenance_entries
            ],
            "structured_entities": [
                self._entity_payload(entity) for entity in context.entities
            ],
            "relationship_edges": [
                asdict(edge) for edge in context.relationship_edges
            ],
            "relationship_families": [
                asdict(family) for family in context.relationship_families
            ],
            "source_groups": [asdict(group) for group in context.source_groups],
            "section_groups": [asdict(group) for group in context.section_groups],
        }
        return json.dumps(payload, indent=2, ensure_ascii=True)

    @staticmethod
    def _source_payload(source) -> dict[str, object]:
        return {
            "source_number": source.source_number,
            "chunk_id": source.chunk_id,
            "chunk_name": source.chunk_name,
            "chunk_type": source.chunk_type,
            "document_title": source.document_title,
            "section_path": source.section_path,
            "page_start": source.page_start,
            "page_end": source.page_end,
            "retrieval_source": source.retrieval_source,
            "content": source.content,
            "table_rows": source.table_rows,
            "identifier_values": source.identifier_values,
            "collapsed_chunk_ids": source.collapsed_chunk_ids,
        }

    @staticmethod
    def _entity_payload(entity) -> dict[str, object]:
        return {
            "entity_type": entity.entity_type,
            "entity_id": entity.entity_id,
            "fields": dict(entity.fields),
            "source_chunk_id": entity.source_chunk_id,
        }

    @staticmethod
    def _maintenance_entry_payload(entry) -> dict[str, object]:
        return {
            "task": entry.task,
            "interval": entry.interval or "Not specified",
            "component": entry.component or "Not specified",
            "notes": entry.notes,
            "source_number": entry.source_number,
            "description": entry.description,
            "references": [asdict(reference) for reference in entry.references],
        }

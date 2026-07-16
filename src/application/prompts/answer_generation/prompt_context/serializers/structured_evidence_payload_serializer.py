import json
from dataclasses import asdict

from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)
from src.config.settings import prompt_context_settings


class StructuredEvidencePayloadSerializer:
    def serialize(self, context: PromptContextBundle | None) -> str:
        if context is None:
            return ""
        payload = {
            "answer_intent": context.answer_intent_value,
            "source_count": context.source_count,
            "sources": [
                self._source_payload(source)
                for source in self._capped(context.sources)
            ],
            "key_values": [
                asdict(item) for item in self._capped(context.key_values)
            ],
            "maintenance_entries": [
                self._maintenance_entry_payload(entry)
                for entry in self._capped(context.maintenance_entries)
            ],
            "tables": [asdict(table) for table in self._capped(context.tables)],
            "structured_entities": [
                self._entity_payload(entity)
                for entity in self._capped(context.entities)
            ],
            "relationship_edges": [
                asdict(edge) for edge in self._capped(context.relationship_edges)
            ],
            "relationship_families": [
                asdict(family)
                for family in self._capped(context.relationship_families)
            ],
            "source_families": [
                asdict(family) for family in self._capped(context.source_families)
            ],
            "section_topology": [
                asdict(section)
                for section in self._capped(context.section_topology)
            ],
        }
        return json.dumps(payload, ensure_ascii=True, default=str)

    @staticmethod
    def _capped(items: list, *, limit: int | None = None) -> list:
        cap = limit if limit is not None else prompt_context_settings.max_items_per_array
        return items[:cap]

    @staticmethod
    def _source_payload(source) -> dict[str, object]:
        payload: dict[str, object] = {
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
            "identifier_values": source.identifier_values,
            "collapsed_chunk_ids": source.collapsed_chunk_ids,
            "table_shape": source.table_shape,
            "table_structure_quality": source.table_structure_quality,
            "table_header_paths": [list(path) for path in source.table_header_paths],
            "table_axis_summary": dict(source.table_axis_summary),
        }
        if prompt_context_settings.include_source_table_rows and source.table_rows:
            payload["table_rows"] = StructuredEvidencePayloadSerializer._capped(
                source.table_rows,
                limit=prompt_context_settings.max_table_rows_per_source,
            )
        return payload

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

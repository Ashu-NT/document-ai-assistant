import json
from dataclasses import asdict

from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)
from src.config.settings import prompt_context_settings


def _truncation_entry(
    *, total_count: int, selected_count: int, reason: str
) -> dict[str, object]:
    return {
        "total_count": total_count,
        "selected_count": selected_count,
        "omitted_count": total_count - selected_count,
        "truncated": True,
        "truncation_reason": reason,
    }


class StructuredEvidencePayloadSerializer:
    def serialize(self, context: PromptContextBundle | None) -> str:
        payload_json, _diagnostics = self.serialize_with_diagnostics(context)
        return payload_json

    def serialize_with_diagnostics(
        self, context: PromptContextBundle | None
    ) -> tuple[str, dict[str, object]]:
        """Same as `serialize()`, but also returns truncation diagnostics
        for every array this method silently caps via `_capped()`, plus
        each table's row cap -- PR 8, W6,
        answering_flow_weakness_remediation_plan.md. `serialize()` stays a
        thin wrapper so its existing callers/tests don't need to change."""
        if context is None:
            return "", {}
        return self._serialize(context), self._truncation_diagnostics(context)

    def _serialize(self, context: PromptContextBundle) -> str:
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
            "tables": [
                self._table_payload(table) for table in self._capped(context.tables)
            ],
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
    def _truncation_diagnostics(context: PromptContextBundle) -> dict[str, object]:
        max_items = prompt_context_settings.max_items_per_array
        array_fields = {
            "sources": context.sources,
            "key_values": context.key_values,
            "maintenance_entries": context.maintenance_entries,
            "tables": context.tables,
            "structured_entities": context.entities,
            "relationship_edges": context.relationship_edges,
            "relationship_families": context.relationship_families,
            "source_families": context.source_families,
            "section_topology": context.section_topology,
        }
        array_truncation = {
            name: _truncation_entry(
                total_count=len(items),
                selected_count=max_items,
                reason="max_items_per_array",
            )
            for name, items in array_fields.items()
            if len(items) > max_items
        }
        table_row_truncation = {
            table.table_id: _truncation_entry(
                total_count=len(table.rows),
                selected_count=prompt_context_settings.max_rows_per_table,
                reason="max_rows_per_table",
            )
            for table in context.tables
            if len(table.rows) > prompt_context_settings.max_rows_per_table
        }
        return {
            "prompt_payload_array_truncation": array_truncation,
            "prompt_payload_table_row_truncation": table_row_truncation,
            "prompt_payload_truncated": bool(array_truncation)
            or bool(table_row_truncation),
        }

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
    def _table_payload(table) -> dict[str, object]:
        payload = asdict(table)
        payload["rows"] = payload["rows"][: prompt_context_settings.max_rows_per_table]
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
            "references": [
                asdict(reference)
                for reference in StructuredEvidencePayloadSerializer._capped(
                    entry.references
                )
            ],
        }

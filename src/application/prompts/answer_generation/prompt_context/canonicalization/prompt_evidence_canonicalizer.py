from __future__ import annotations

from dataclasses import replace

from src.application.prompts.answer_generation.prompt_context.canonicalization.entity_key_value_fingerprint_builder import (
    EntityKeyValueFingerprintBuilder,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptSourceView,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


class PromptEvidenceCanonicalizer:
    def __init__(
        self,
        entity_key_value_fingerprint_builder: EntityKeyValueFingerprintBuilder
        | None = None,
    ) -> None:
        self.entity_key_value_fingerprint_builder = (
            entity_key_value_fingerprint_builder
            or EntityKeyValueFingerprintBuilder()
        )

    def canonicalize(
        self,
        context: PromptContextBundle | None,
    ) -> PromptContextBundle | None:
        if context is None:
            return None
        appendix_sources = list(context.appendix_sources or context.sources)
        source_number_by_chunk_id = {
            source.chunk_id: source.source_number
            for source in appendix_sources
            if source.chunk_id
        }
        entity_fingerprints = self.entity_key_value_fingerprint_builder.build(
            context.entities,
            source_number_by_chunk_id=source_number_by_chunk_id,
        )
        key_values, key_values_removed = self._canonicalize_key_values(
            context,
            entity_fingerprints=entity_fingerprints,
        )
        key_value_source_numbers = {item.source_number for item in key_values}
        maintenance_source_numbers = {
            reference.source_number
            for entry in context.maintenance_entries
            for reference in entry.references
        }
        entity_source_numbers = {
            source_number_by_chunk_id[entity.source_chunk_id]
            for entity in context.entities
            if entity.source_chunk_id in source_number_by_chunk_id
        }
        table_source_numbers = {table.source_number for table in context.tables}
        payload_sources, table_rows_removed = self._canonicalize_sources(
            context,
            table_source_numbers=table_source_numbers,
            key_value_source_numbers=key_value_source_numbers,
            maintenance_source_numbers=maintenance_source_numbers,
            entity_source_numbers=entity_source_numbers,
        )
        diagnostics = dict(context.diagnostics)
        diagnostics.update(
            {
                "prompt_canonicalized_key_values_removed": key_values_removed,
                "prompt_payload_sources_content_omitted": len(payload_sources),
                "prompt_payload_table_rows_removed": table_rows_removed,
            }
        )
        return replace(
            context,
            sources=payload_sources,
            appendix_sources=appendix_sources,
            key_values=key_values,
            diagnostics=diagnostics,
        )

    @staticmethod
    def _canonicalize_key_values(
        context: PromptContextBundle,
        *,
        entity_fingerprints: set[tuple[str, str, int]],
    ) -> tuple[list, int]:
        kept = []
        seen: set[tuple[str, str, int]] = set()
        removed = 0
        for item in context.key_values:
            fingerprint = (
                item.key.strip().lower(),
                item.value.strip().lower(),
                item.source_number,
            )
            if fingerprint in seen:
                removed += 1
                continue
            if fingerprint in entity_fingerprints:
                removed += 1
                continue
            seen.add(fingerprint)
            kept.append(item)
        return kept, removed

    def _canonicalize_sources(
        self,
        context: PromptContextBundle,
        *,
        table_source_numbers: set[int],
        key_value_source_numbers: set[int],
        maintenance_source_numbers: set[int],
        entity_source_numbers: set[int],
    ) -> tuple[list[PromptSourceView], int]:
        payload_sources: list[PromptSourceView] = []
        table_rows_removed = 0
        for source in context.sources:
            keep_table_rows = self._should_keep_table_rows(
                source=source,
                table_source_numbers=table_source_numbers,
                key_value_source_numbers=key_value_source_numbers,
                maintenance_source_numbers=maintenance_source_numbers,
                entity_source_numbers=entity_source_numbers,
            )
            if source.table_rows and not keep_table_rows:
                table_rows_removed += 1
            payload_sources.append(
                replace(
                    source,
                    content="",
                    table_rows=source.table_rows if keep_table_rows else None,
                )
            )
        return payload_sources, table_rows_removed

    @staticmethod
    def _should_keep_table_rows(
        *,
        source: PromptSourceView,
        table_source_numbers: set[int],
        key_value_source_numbers: set[int],
        maintenance_source_numbers: set[int],
        entity_source_numbers: set[int],
    ) -> bool:
        if not source.table_rows:
            return False
        if source.source_number in table_source_numbers:
            return False
        source_has_richer_facts = source.source_number in (
            key_value_source_numbers
            | maintenance_source_numbers
            | entity_source_numbers
        )
        return not source_has_richer_facts

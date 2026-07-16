from __future__ import annotations

from dataclasses import replace

from src.application.prompts.answer_generation.prompt_context.canonicalization.entity_key_value_fingerprint_builder import (
    EntityKeyValueFingerprintBuilder,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptSourceView,
)
from src.config.settings import prompt_context_settings


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
        table_source_numbers = {table.source_number for table in context.tables}
        captured_values_by_source = self._captured_values_by_source(
            key_values, entity_fingerprints
        )
        payload_sources, table_rows_removed = self._canonicalize_sources(
            context,
            table_source_numbers=table_source_numbers,
            captured_values_by_source=captured_values_by_source,
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
        captured_values_by_source: dict[int, set[str]],
    ) -> tuple[list[PromptSourceView], int]:
        payload_sources: list[PromptSourceView] = []
        table_rows_removed = 0
        for source in context.sources:
            kept_rows, removed_count = self._filter_table_rows(
                source=source,
                table_source_numbers=table_source_numbers,
                captured_values=captured_values_by_source.get(
                    source.source_number, set()
                ),
            )
            table_rows_removed += removed_count
            payload_sources.append(
                replace(source, content="", table_rows=kept_rows)
            )
        return payload_sources, table_rows_removed

    @staticmethod
    def _captured_values_by_source(
        key_values,
        entity_fingerprints: set[tuple[str, str, int]],
    ) -> dict[int, set[str]]:
        """Value strings already captured (surfaced elsewhere in the JSON
        payload) per source_number, from key_values and entity fields.
        Used by `_filter_table_rows` to keep row-level fidelity: a raw table
        row is only worth dropping if every one of its cell values is
        verifiably represented by a captured key-value/entity fact for that
        same source -- not merely because the source has *some* richer
        representation elsewhere (see `_filter_table_rows`).
        """
        captured: dict[int, set[str]] = {}
        for item in key_values:
            normalized_value = " ".join(str(item.value or "").split()).strip().lower()
            if not normalized_value:
                continue
            captured.setdefault(item.source_number, set()).add(normalized_value)
        for _label, value, source_number in entity_fingerprints:
            captured.setdefault(source_number, set()).add(value)
        return captured

    @staticmethod
    def _filter_table_rows(
        *,
        source: PromptSourceView,
        table_source_numbers: set[int],
        captured_values: set[str],
    ) -> tuple[list[list[str]] | None, int]:
        if not source.table_rows:
            return None, 0
        if (
            not prompt_context_settings.include_source_table_rows
            and source.source_number in table_source_numbers
        ):
            # This source's raw rows are already fully represented (headers
            # included) in the top-level `tables` array built from the same
            # source.table_rows -- dropping the duplicate here is
            # deduplication, not data loss, regardless of row count. When
            # `include_source_table_rows` is on, the whole point is to keep
            # the raw rows source-local too (machine-exact, colocated with
            # the source that produced them) rather than relying solely on
            # the separate `tables` array -- so this dedup step is skipped
            # in that mode, falling through to the (still-legitimate,
            # unrelated) captured-key-value dedup below.
            return None, len(source.table_rows)
        if not captured_values:
            return list(source.table_rows), 0
        kept_rows: list[list[str]] = []
        removed = 0
        for row in source.table_rows:
            if PromptEvidenceCanonicalizer._row_is_fully_captured(
                row, captured_values
            ):
                removed += 1
            else:
                kept_rows.append(row)
        return (kept_rows or None), removed

    @staticmethod
    def _row_is_fully_captured(row: list[str], captured_values: set[str]) -> bool:
        normalized_cells = [
            " ".join(str(cell).split()).strip().lower()
            for cell in row
            if str(cell).strip()
        ]
        if not normalized_cells:
            return True
        return all(cell in captured_values for cell in normalized_cells)

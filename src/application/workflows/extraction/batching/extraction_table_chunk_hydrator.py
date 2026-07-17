from __future__ import annotations

from dataclasses import replace as dataclass_replace

from src.application.workflows.parsing.tables.families import (
    LogicalTableFamilyAssetComposer,
    LogicalTableFamilyLookup,
)
from src.application.workflows.parsing.tables.rendering import (
    TableAssetStructuredTextRenderer,
)
from src.application.workflows.parsing.tables.structure import (
    TableStructureContextRenderer,
)
from src.application.workflows.extraction.batching.table_payload import (
    ExtractionTablePayloadRenderer,
)
from src.domain.assets import TableAsset
from src.domain.document import DocumentChunk

_STRUCTURE_CONTEXT_RENDERER = TableStructureContextRenderer()
_TABLE_PAYLOAD_RENDERER = ExtractionTablePayloadRenderer()
_FAMILY_ASSET_COMPOSER = LogicalTableFamilyAssetComposer()
_STRUCTURED_TEXT_RENDERER = TableAssetStructuredTextRenderer()


def _table_text_with_structured_rows(
    table: TableAsset,
    *,
    chunk_type: str | None,
) -> str:
    parts: list[str] = []
    structure_context = _STRUCTURE_CONTEXT_RENDERER.render(table)
    if structure_context:
        parts.append(structure_context)
    structured_payload = _TABLE_PAYLOAD_RENDERER.render(table, chunk_type=chunk_type)
    if structured_payload:
        parts.append(structured_payload)
    parts.append(table.to_embedding_text())
    structured_rows = _STRUCTURED_TEXT_RENDERER.render(table)
    if structured_rows and not structured_payload:
        parts.append(structured_rows)
    return "\n\n".join(parts)


def hydrate_table_chunks(
    chunks: list[DocumentChunk],
    tables: dict[str, TableAsset],
) -> list[DocumentChunk]:
    """Replaces a chunk's (possibly partial) content with the complete
    table markdown whenever the chunk references a table.

    The chunker can split a large table's rows across several chunks to
    stay within a token budget. Extracting spare parts, specifications,
    maintenance intervals, etc. from only a fragment of a table risks
    splitting a single row's fields across two separate LLM calls with
    no way to reassemble them. Hydrating restores the full table text on
    the first chunk that references it and drops the other chunks that
    reference the same table (their content is now redundant), so the
    extraction model always sees complete table rows.
    """
    family_lookup = LogicalTableFamilyLookup.from_tables(tables)
    seen_group_keys: set[str] = set()
    hydrated: list[DocumentChunk] = []
    for chunk in chunks:
        if not chunk.table_ids:
            hydrated.append(chunk)
            continue

        family_id = chunk.logical_table_family_id or family_lookup.family_id_for_table_ids(
            chunk.table_ids
        )
        group_key = family_id or ",".join(sorted(chunk.table_ids))
        if group_key in seen_group_keys:
            # Every table this chunk references was already hydrated in
            # full by an earlier chunk; this chunk is now redundant.
            continue
        seen_group_keys.add(group_key)

        member_tables = family_lookup.members_for_table_ids(chunk.table_ids)
        composed_table = _FAMILY_ASSET_COMPOSER.compose(
            member_tables,
            family_id=family_id,
        )
        if composed_table is None or not composed_table.has_content():
            hydrated.append(chunk)
            continue

        hydrated.append(
            dataclass_replace(
                chunk,
                content=_table_text_with_structured_rows(
                    composed_table,
                    chunk_type=chunk.chunk_type,
                ),
                table_ids=[table.table_id for table in member_tables],
                logical_table_family_id=family_id,
                table_category=chunk.table_category
                or next(
                    (
                        table.table_category
                        for table in member_tables
                        if table.table_category
                    ),
                    None,
                ),
                table_category_confidence=chunk.table_category_confidence
                or next(
                    (
                        table.table_category_confidence
                        for table in member_tables
                        if table.table_category_confidence is not None
                    ),
                    None,
                ),
                table_row_start=1
                if composed_table.rows and len(composed_table.rows) > 1
                else None,
                table_row_end=(len(composed_table.rows) - 1)
                if composed_table.rows and len(composed_table.rows) > 1
                else None,
            )
        )
    return hydrated

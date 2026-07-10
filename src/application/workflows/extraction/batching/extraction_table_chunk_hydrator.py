from __future__ import annotations

from dataclasses import replace as dataclass_replace

from src.domain.assets import TableAsset
from src.domain.document import DocumentChunk


def _table_text_with_structured_rows(table: TableAsset) -> str:
    parts = [table.to_embedding_text()]
    structured_rows = table.to_structured_row_text()
    if structured_rows:
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
    seen_table_ids: set[str] = set()
    hydrated: list[DocumentChunk] = []
    for chunk in chunks:
        if not chunk.table_ids:
            hydrated.append(chunk)
            continue

        unseen_table_ids = [
            table_id for table_id in chunk.table_ids if table_id not in seen_table_ids
        ]
        if not unseen_table_ids:
            # Every table this chunk references was already hydrated in
            # full by an earlier chunk; this chunk is now redundant.
            continue
        seen_table_ids.update(unseen_table_ids)

        table_texts = [
            _table_text_with_structured_rows(tables[table_id])
            for table_id in unseen_table_ids
            if table_id in tables and tables[table_id].has_content()
        ]
        if not table_texts:
            hydrated.append(chunk)
            continue

        hydrated.append(
            dataclass_replace(chunk, content="\n\n".join(table_texts))
        )
    return hydrated

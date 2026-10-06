from __future__ import annotations

from src.application.workflows.parsing.tables.families import (
    LogicalTableFamilyAssetComposer,
    LogicalTableFamilyLookup,
)
from src.domain.assets import TableAsset
from src.domain.document import DocumentChunk

# Re-derives the SAME composed TableAsset `hydrate_table_chunks` already
# builds internally for a hydrated chunk, using the EXACT SAME composition
# classes (LogicalTableFamilyLookup/LogicalTableFamilyAssetComposer) - pure,
# read-only, no change to hydration itself. hydrate_table_chunks does not
# expose its composed table separately (only the rendered text ends up on
# the chunk), so anything downstream that needs the structured TableAsset
# (row-windowing) re-resolves it from the original `tables` dict plus the
# hydrated chunk's own table_ids/logical_table_family_id - both of which
# hydration already sets and preserves on the chunk it returns.


def resolve_composed_table(
    chunk: DocumentChunk,
    tables: dict[str, TableAsset],
) -> TableAsset | None:
    if not chunk.table_ids or not tables:
        return None

    family_lookup = LogicalTableFamilyLookup.from_tables(tables)
    family_id = chunk.logical_table_family_id or family_lookup.family_id_for_table_ids(
        chunk.table_ids
    )
    member_tables = family_lookup.members_for_table_ids(chunk.table_ids)
    if not member_tables:
        return None

    return LogicalTableFamilyAssetComposer().compose(member_tables, family_id=family_id)

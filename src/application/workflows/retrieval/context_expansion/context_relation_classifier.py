from src.application.workflows.shared.section_path_utils import is_path_prefix
from src.domain.common import ChunkType


def classify_context_relation(
    *,
    anchor_document_chunk,
    document_chunk,
    neighbor_window: int,
) -> tuple[str | None, int]:
    distance = abs(
        document_chunk.sequence_number - anchor_document_chunk.sequence_number
    )

    if _shares_chunk_family(anchor_document_chunk, document_chunk):
        return "same_section_part", max(1, distance)
    if _is_ancestor_overview(anchor_document_chunk, document_chunk):
        return "ancestor_overview", max(1, distance)
    if _shares_assets(anchor_document_chunk, document_chunk):
        return "asset_companion", max(1, distance)
    if _is_descendant_detail(anchor_document_chunk, document_chunk):
        return "descendant_detail", max(1, distance)
    if _is_same_parent_path(anchor_document_chunk, document_chunk):
        return "sibling_section", max(1, distance)
    if 0 < distance <= neighbor_window:
        return "neighbor", distance

    return None, distance


def _shares_chunk_family(anchor_document_chunk, document_chunk) -> bool:
    return (
        anchor_document_chunk.section_id is not None
        and anchor_document_chunk.section_id == document_chunk.section_id
        and max(
            anchor_document_chunk.chunk_total,
            document_chunk.chunk_total,
        ) > 1
    )


def _shares_assets(anchor_document_chunk, document_chunk) -> bool:
    if (
        anchor_document_chunk.logical_table_family_id is not None
        and anchor_document_chunk.logical_table_family_id
        == document_chunk.logical_table_family_id
    ):
        return True

    return bool(
        set(anchor_document_chunk.table_ids) & set(document_chunk.table_ids)
        or set(anchor_document_chunk.picture_ids) & set(document_chunk.picture_ids)
    )


def _is_ancestor_overview(anchor_document_chunk, document_chunk) -> bool:
    return (
        document_chunk.chunk_type == ChunkType.OVERVIEW
        and is_path_prefix(
            document_chunk.section_path,
            anchor_document_chunk.section_path,
        )
        and document_chunk.section_path != anchor_document_chunk.section_path
    )


def _is_descendant_detail(anchor_document_chunk, document_chunk) -> bool:
    return (
        anchor_document_chunk.chunk_type == ChunkType.OVERVIEW
        and document_chunk.chunk_type != ChunkType.OVERVIEW
        and is_path_prefix(
            anchor_document_chunk.section_path,
            document_chunk.section_path,
        )
        and anchor_document_chunk.section_path != document_chunk.section_path
    )


def _is_same_parent_path(anchor_document_chunk, document_chunk) -> bool:
    if len(anchor_document_chunk.section_path) <= 1:
        return False
    if len(anchor_document_chunk.section_path) != len(document_chunk.section_path):
        return False
    return (
        anchor_document_chunk.section_path[:-1]
        == document_chunk.section_path[:-1]
        and anchor_document_chunk.section_path[-1]
        != document_chunk.section_path[-1]
    )

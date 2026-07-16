from __future__ import annotations

import json

from src.application.workflows.shared.table_category import TableCategory
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk

_SPARE_PARTS_TABLE_CONTENT_MARKERS: tuple[str, ...] = (
    "position no",
    "pos.",
    "pos nr",
    "qty",
    "quantity",
    "designation",
    "denomination",
    "part no",
    "spare part no",
    "article no",
    "material no",
    "order no",
    "p&id",
    "service function",
)


def has_direct_table_evidence(chunk: RetrievedChunk) -> bool:
    if chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE:
        return True
    if chunk.metadata.get("logical_table_family_id"):
        return True
    if chunk.metadata.get("table_category"):
        return True
    if chunk.metadata.get("table_row_start") or chunk.metadata.get("table_row_end"):
        return True
    if _has_table_ids(chunk):
        return True
    return "|" in chunk.content


def has_spare_parts_table_evidence(chunk: RetrievedChunk) -> bool:
    table_category = str(chunk.metadata.get("table_category", "")).strip().lower()
    if table_category == TableCategory.SPARE_PARTS_TABLE:
        return True

    text = chunk.content
    lower = text.lower()
    if "|" not in text and not any(
        marker in lower for marker in _SPARE_PARTS_TABLE_CONTENT_MARKERS
    ):
        return False

    has_marker = any(marker in lower for marker in _SPARE_PARTS_TABLE_CONTENT_MARKERS)
    has_digit = any(character.isdigit() for character in text)
    return has_marker and has_digit


def _has_table_ids(chunk: RetrievedChunk) -> bool:
    raw_value = chunk.metadata.get("hydrated_table_ids") or chunk.metadata.get("table_ids")
    if not raw_value:
        return False
    if raw_value.startswith("["):
        try:
            decoded = json.loads(raw_value)
        except ValueError:
            return False
        return isinstance(decoded, list) and any(str(value).strip() for value in decoded)
    return any(part.strip() for part in raw_value.split(","))

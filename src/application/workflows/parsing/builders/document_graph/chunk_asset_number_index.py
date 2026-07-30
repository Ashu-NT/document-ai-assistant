from __future__ import annotations

import re
from collections import defaultdict

from src.domain.assets import PictureAsset, TableAsset
from src.domain.document.entities.chunk import DocumentChunk

# A table/figure caption, when the source document numbers them at all, is
# consistently "<label> N[.N...]. <text>" or "<label> N[.N...]: <text>"
# (e.g. "Table 3. Spare parts list", "Fig. 2.1: Oil filter assembly").
# Documents that don't caption their tables/figures with a number simply
# produce no index entries, which is an expected, non-error outcome.
_LEADING_TABLE_NUMBER_PATTERN = re.compile(
    r"^\s*table\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE
)
_LEADING_FIGURE_NUMBER_PATTERN = re.compile(
    r"^\s*fig(?:ure)?\.?\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE
)


def extract_leading_table_number(caption: str) -> str | None:
    match = _LEADING_TABLE_NUMBER_PATTERN.match(caption.strip())
    return match.group(1) if match else None


def extract_leading_figure_number(caption: str) -> str | None:
    match = _LEADING_FIGURE_NUMBER_PATTERN.match(caption.strip())
    return match.group(1) if match else None


class ChunkAssetNumberIndex:
    """Maps each distinct captioned table/figure number (e.g. "3" extracted
    from a table caption like "Table 3. Spare parts") to every chunk that
    contains that asset, built once per document so
    `ChunkAssetReferenceResolver` doesn't re-scan every chunk for each
    detected table/figure reference in the document."""

    def __init__(
        self,
        *,
        chunks: list[DocumentChunk],
        tables: dict[str, TableAsset],
        pictures: dict[str, PictureAsset],
    ) -> None:
        self._table_chunks_by_label: dict[str, list[DocumentChunk]] = defaultdict(list)
        self._figure_chunks_by_label: dict[str, list[DocumentChunk]] = defaultdict(list)

        for chunk in chunks:
            for table_id in chunk.table_ids:
                table = tables.get(table_id)
                if table is None or not table.metadata.caption:
                    continue
                label = extract_leading_table_number(table.metadata.caption)
                if label:
                    self._table_chunks_by_label[label].append(chunk)

            for picture_id in chunk.picture_ids:
                picture = pictures.get(picture_id)
                if picture is None or not picture.metadata.caption:
                    continue
                label = extract_leading_figure_number(picture.metadata.caption)
                if label:
                    self._figure_chunks_by_label[label].append(chunk)

    def table_matches(self, label: str) -> list[DocumentChunk]:
        return list(self._table_chunks_by_label.get(label, ()))

    def figure_matches(self, label: str) -> list[DocumentChunk]:
        return list(self._figure_chunks_by_label.get(label, ()))


__all__ = [
    "ChunkAssetNumberIndex",
    "extract_leading_figure_number",
    "extract_leading_table_number",
]

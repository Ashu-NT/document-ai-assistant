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


# Same page-adjacency window used elsewhere for asset-related heuristics
# (see LogicalTableFamilyResolver's max_continuation_page_gap) -- a
# proximity guess more than one page away from the reference is more likely
# to be wrong than helpful.
_MAX_PROXIMITY_PAGE_GAP = 1


class ChunkAssetNumberIndex:
    """Maps each distinct captioned table/figure number (e.g. "3" extracted
    from a table caption like "Table 3. Spare parts") to every chunk that
    contains that asset, built once per document so
    `ChunkAssetReferenceResolver` doesn't re-scan every chunk for each
    detected table/figure reference in the document.

    Also separately tracks every table/figure-bearing chunk regardless of
    whether its caption carries a number, so a reference to an uncaptioned
    or differently-numbered asset can still fall back to a page-proximity
    guess instead of going unresolved outright."""

    def __init__(
        self,
        *,
        chunks: list[DocumentChunk],
        tables: dict[str, TableAsset],
        pictures: dict[str, PictureAsset],
    ) -> None:
        self._table_chunks_by_label: dict[str, list[DocumentChunk]] = defaultdict(list)
        self._figure_chunks_by_label: dict[str, list[DocumentChunk]] = defaultdict(list)
        self._table_chunks: list[DocumentChunk] = []
        self._figure_chunks: list[DocumentChunk] = []

        for chunk in chunks:
            for table_id in chunk.table_ids:
                table = tables.get(table_id)
                if table is None:
                    continue
                self._table_chunks.append(chunk)
                if not table.metadata.caption:
                    continue
                label = extract_leading_table_number(table.metadata.caption)
                if label:
                    self._table_chunks_by_label[label].append(chunk)

            for picture_id in chunk.picture_ids:
                picture = pictures.get(picture_id)
                if picture is None:
                    continue
                self._figure_chunks.append(chunk)
                if not picture.metadata.caption:
                    continue
                label = extract_leading_figure_number(picture.metadata.caption)
                if label:
                    self._figure_chunks_by_label[label].append(chunk)

    def table_matches(self, label: str) -> list[DocumentChunk]:
        return list(self._table_chunks_by_label.get(label, ()))

    def figure_matches(self, label: str) -> list[DocumentChunk]:
        return list(self._figure_chunks_by_label.get(label, ()))

    def nearest_table_chunk(self, source_page: int | None) -> DocumentChunk | None:
        return self._nearest_chunk(self._table_chunks, source_page)

    def nearest_figure_chunk(self, source_page: int | None) -> DocumentChunk | None:
        return self._nearest_chunk(self._figure_chunks, source_page)

    @staticmethod
    def _nearest_chunk(
        candidates: list[DocumentChunk],
        source_page: int | None,
    ) -> DocumentChunk | None:
        if source_page is None or not candidates:
            return None

        best_chunk: DocumentChunk | None = None
        best_distance: int | None = None
        for candidate in candidates:
            candidate_page = candidate.source.page_start or candidate.source.page_end
            if candidate_page is None:
                continue
            distance = abs(candidate_page - source_page)
            if distance > _MAX_PROXIMITY_PAGE_GAP:
                continue
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_chunk = candidate

        return best_chunk


__all__ = [
    "ChunkAssetNumberIndex",
    "extract_leading_figure_number",
    "extract_leading_table_number",
]

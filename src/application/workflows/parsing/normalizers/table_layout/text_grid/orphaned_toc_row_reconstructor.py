from __future__ import annotations

import re
from dataclasses import dataclass

from src.application.workflows.parsing.normalizers.table_rows.docling_toc_table_row_reconstructor import (
    TOC_PAGE_NUMBER_PATTERN,
    DoclingTocTableRowReconstructor,
)
from src.application.workflows.parsing.normalizers.table_layout.text_grid.geometric_row_clusterer import (
    GeometricRowClusterer,
    GridElement,
)
from src.domain.common import BoundingBox

_DOT_LEADER_ELEMENT_PATTERN = re.compile(r"^[.\s]{2,}$")

_MIN_DOT_LEADER_ELEMENTS = 4
_MIN_DOT_LEADER_FRACTION = 0.15


@dataclass(frozen=True, slots=True)
class OrphanedTocResult:
    rows: list[list[str]]
    consumed_indices: frozenset[int]
    bbox: BoundingBox


class OrphanedTocRowReconstructor:
    """Recovers a table-of-contents list from loose text elements that
    Docling never grouped into a table at all -- a different failure shape
    than `TextGridTableDetector` targets. That detector recovers a regular
    record grid (every row populates the same set of column slots); this
    one targets a dot-leader-heavy TOC list, where row structure is
    irregular (2-4 populated elements per row) and a title/number can
    itself be split across several tiny text runs (confirmed on a real
    document: "2.7 E3000-C-500" arrived as 6 separate elements: "2.7",
    "E3000", "-", "C", "-", "500").

    Confirmed on the same real document: this content survives in the
    persisted chunk store, but reads as scrambled dot-leader noise with no
    correlation between a title and its page number.

    Approach: cluster elements into visual rows the same way
    `TextGridTableDetector` does (shared `GeometricRowClusterer`). Per row,
    classify each element as a dot-leader run (discarded), a page number
    (the page's own dominant, consistently-positioned page-number x-band --
    deliberately NOT "any digit/roman-shaped token", since a row's own
    section numbering can itself incidentally look page-number-shaped, e.g.
    a lone "3" from a character-split "3.3"), or title/numbering text
    (concatenated left to right). The resulting raw `[title_text,
    page_text]` rows are handed to the existing
    `DoclingTocTableRowReconstructor`, reusing its numbering-extraction/
    dot-collapsing/cleanup logic rather than duplicating it.
    """

    MIN_ROWS = 3

    def __init__(
        self,
        *,
        toc_reconstructor: DoclingTocTableRowReconstructor | None = None,
    ) -> None:
        self.toc_reconstructor = toc_reconstructor or DoclingTocTableRowReconstructor()

    def reconstruct(self, elements: list[GridElement]) -> OrphanedTocResult | None:
        if not self._looks_like_orphaned_toc(elements):
            return None

        page_number_band = self._find_page_number_band(elements)
        if page_number_band is None:
            return None

        rows = GeometricRowClusterer.cluster_rows(elements)
        raw_rows: list[list[str]] = []
        consumed_indices: set[int] = set()
        contributing_elements: list[GridElement] = []

        for row in rows:
            page_element: GridElement | None = None
            title_parts: list[GridElement] = []
            for element in row:
                text = element.text.strip()
                if _DOT_LEADER_ELEMENT_PATTERN.fullmatch(text):
                    continue
                if page_element is None and self._in_band(element, page_number_band):
                    page_element = element
                    continue
                title_parts.append(element)

            if page_element is None or not title_parts:
                continue

            title_text = " ".join(part.text.strip() for part in title_parts)
            raw_rows.append([title_text, page_element.text.strip()])
            contributing_elements.extend(title_parts)
            contributing_elements.append(page_element)
            consumed_indices.update(part.index for part in title_parts)
            consumed_indices.add(page_element.index)

        if len(raw_rows) < self.MIN_ROWS:
            return None

        reconstructed_rows = self.toc_reconstructor.reconstruct(raw_rows)
        if reconstructed_rows == raw_rows:
            # The reconstructor's own safety net decided this doesn't look
            # sufficiently TOC-shaped after all -- don't force a result.
            return None

        return OrphanedTocResult(
            rows=reconstructed_rows,
            consumed_indices=frozenset(consumed_indices),
            bbox=self._union_bbox(contributing_elements),
        )

    @classmethod
    def _looks_like_orphaned_toc(cls, elements: list[GridElement]) -> bool:
        if len(elements) < _MIN_DOT_LEADER_ELEMENTS:
            return False
        dot_leader_count = sum(
            1
            for element in elements
            if _DOT_LEADER_ELEMENT_PATTERN.fullmatch(element.text.strip())
        )
        return (
            dot_leader_count >= _MIN_DOT_LEADER_ELEMENTS
            and dot_leader_count / len(elements) >= _MIN_DOT_LEADER_FRACTION
        )

    @classmethod
    def _find_page_number_band(
        cls,
        elements: list[GridElement],
    ) -> tuple[float, float] | None:
        candidates = [
            element
            for element in elements
            if not _DOT_LEADER_ELEMENT_PATTERN.fullmatch(element.text.strip())
            and TOC_PAGE_NUMBER_PATTERN.fullmatch(element.text.strip())
        ]
        if len(candidates) < cls.MIN_ROWS:
            return None

        ordered = sorted(
            candidates, key=lambda element: GeometricRowClusterer.x_center(element.bbox)
        )
        widths = sorted(element.bbox.x2 - element.bbox.x1 for element in ordered)
        median_width = widths[len(widths) // 2]
        x_range = GeometricRowClusterer.x_center(
            ordered[-1].bbox
        ) - GeometricRowClusterer.x_center(ordered[0].bbox)
        gap_threshold = max(x_range * 0.06, median_width * 1.4, 18.0)

        bands: list[list[GridElement]] = [[ordered[0]]]
        previous_center = GeometricRowClusterer.x_center(ordered[0].bbox)
        for element in ordered[1:]:
            center = GeometricRowClusterer.x_center(element.bbox)
            if center - previous_center > gap_threshold:
                bands.append([element])
            else:
                bands[-1].append(element)
            previous_center = center

        # The dominant band -- the one most rows agree on -- is the real
        # page-number column. Stray digit-shaped tokens that are actually
        # part of a title/section-number (e.g. a lone "3" from a
        # character-split "3.3") occur at most once or twice at some other
        # x-position and never form the dominant band.
        dominant_band = max(bands, key=len)
        if len(dominant_band) < cls.MIN_ROWS:
            return None

        return (
            min(element.bbox.x1 for element in dominant_band),
            max(element.bbox.x2 for element in dominant_band),
        )

    @staticmethod
    def _in_band(element: GridElement, band: tuple[float, float]) -> bool:
        band_min, band_max = band
        center = GeometricRowClusterer.x_center(element.bbox)
        return band_min - 5.0 <= center <= band_max + 5.0

    @staticmethod
    def _union_bbox(elements: list[GridElement]) -> BoundingBox:
        return BoundingBox(
            x1=min(element.bbox.x1 for element in elements),
            y1=max(element.bbox.y1 for element in elements),
            x2=max(element.bbox.x2 for element in elements),
            y2=min(element.bbox.y2 for element in elements),
        )

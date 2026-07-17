from __future__ import annotations

from collections import defaultdict

from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.normalizers.table_layout.orphaned_toc_row_reconstructor import (
    OrphanedTocResult,
    OrphanedTocRowReconstructor,
)
from src.application.workflows.parsing.normalizers.table_layout.text_grid_table_detector import (
    GridElement,
    TextGridTableDetector,
    TextGridTableResult,
)
from src.domain.common import BoundingBox, ElementType


class TextGridTableFallbackApplier:
    """Synthesizes a TABLE canonical element from loose text elements that
    Docling's own table-detection model never recognized as a table at all.
    Runs once per page, over that page's TEXT elements not already covered
    by an existing TABLE element's bounding box, so it never interferes
    with tables Docling already extracted correctly.

    Tries two strategies per page, in order:
    1. `TextGridTableDetector` -- a regular record grid (every row
       populates the same set of column slots).
    2. `OrphanedTocRowReconstructor` -- a dot-leader-heavy TOC list (an
       irregular shape the grid detector correctly does not match), tried
       only when the first strategy finds nothing for that page.
    """

    def __init__(
        self,
        *,
        detector: TextGridTableDetector | None = None,
        toc_reconstructor: OrphanedTocRowReconstructor | None = None,
    ) -> None:
        self.detector = detector or TextGridTableDetector()
        self.toc_reconstructor = toc_reconstructor or OrphanedTocRowReconstructor()

    def apply(self, elements: list[CanonicalElement]) -> list[CanonicalElement]:
        elements_by_page: dict[int, list[int]] = defaultdict(list)
        for position, element in enumerate(elements):
            if element.page_start is not None:
                elements_by_page[element.page_start].append(position)

        positions_to_remove: set[int] = set()
        synthetic_by_position: dict[int, CanonicalElement] = {}

        for page_number, positions in elements_by_page.items():
            table_bboxes = [
                elements[position].bbox
                for position in positions
                if elements[position].element_type == ElementType.TABLE
                and elements[position].bbox is not None
            ]
            candidate_positions = [
                position
                for position in positions
                if self._is_candidate(elements[position], table_bboxes)
            ]
            if len(candidate_positions) < self.detector.MIN_ROWS * self.detector.MIN_COLUMNS:
                continue

            grid_elements = [
                GridElement(
                    index=position,
                    text=elements[position].text.strip(),
                    bbox=elements[position].bbox,
                )
                for position in candidate_positions
            ]
            result = self.detector.detect(grid_elements)
            tier = "text_grid_fallback"
            if result is None:
                result = self.toc_reconstructor.reconstruct(grid_elements)
                tier = "orphaned_toc_reconstruction"
            if result is None:
                continue

            anchor_position = min(result.consumed_indices)
            synthetic_by_position[anchor_position] = self._build_table_element(
                anchor_element=elements[anchor_position],
                page_number=page_number,
                result=result,
                tier=tier,
            )
            positions_to_remove.update(result.consumed_indices)

        if not positions_to_remove:
            return elements

        rebuilt: list[CanonicalElement] = []
        for position, element in enumerate(elements):
            if position in synthetic_by_position:
                rebuilt.append(synthetic_by_position[position])
                continue
            if position in positions_to_remove:
                continue
            rebuilt.append(element)

        for index, element in enumerate(rebuilt, start=1):
            element.order_index = index
        return rebuilt

    @staticmethod
    def _is_candidate(
        element: CanonicalElement,
        table_bboxes: list[BoundingBox],
    ) -> bool:
        if element.element_type != ElementType.TEXT:
            return False
        if element.bbox is None or not element.text or not element.text.strip():
            return False
        return not TextGridTableFallbackApplier._overlaps_any(element.bbox, table_bboxes)

    @staticmethod
    def _overlaps_any(bbox: BoundingBox, table_bboxes: list[BoundingBox]) -> bool:
        return any(
            TextGridTableFallbackApplier._overlaps(bbox, table_bbox)
            for table_bbox in table_bboxes
        )

    @staticmethod
    def _overlaps(a: BoundingBox, b: BoundingBox) -> bool:
        # BOTTOMLEFT-origin convention used throughout this pipeline: y1 is
        # the top edge (larger value), y2 is the bottom edge (smaller value).
        horizontal_overlap = a.x1 < b.x2 and b.x1 < a.x2
        vertical_overlap = a.y2 < b.y1 and b.y2 < a.y1
        return horizontal_overlap and vertical_overlap

    def _build_table_element(
        self,
        *,
        anchor_element: CanonicalElement,
        page_number: int,
        result: TextGridTableResult | OrphanedTocResult,
        tier: str,
    ) -> CanonicalElement:
        markdown = self._rows_to_markdown(result.rows)
        metadata = {
            "table_rows": result.rows,
            "table_structure_tier": tier,
            "row_count": len(result.rows),
            "column_count": max((len(row) for row in result.rows), default=0),
            "markdown": markdown,
        }
        return CanonicalElement(
            element_id=f"{anchor_element.element_id}_text_grid_table",
            document_id=anchor_element.document_id,
            element_type=ElementType.TABLE,
            text=markdown,
            page_start=page_number,
            page_end=page_number,
            bbox=result.bbox,
            order_index=anchor_element.order_index,
            section_title=anchor_element.section_title,
            section_path=list(anchor_element.section_path),
            parent_section_id=anchor_element.parent_section_id,
            raw_ref=None,
            metadata=metadata,
        )

    @staticmethod
    def _rows_to_markdown(rows: list[list[str]]) -> str:
        if not rows:
            return ""
        header = rows[0]
        body = rows[1:]
        header_line = "| " + " | ".join(header) + " |"
        separator = "| " + " | ".join("---" for _ in header) + " |"
        body_lines = ["| " + " | ".join(row) + " |" for row in body]
        return "\n".join([header_line, separator, *body_lines])

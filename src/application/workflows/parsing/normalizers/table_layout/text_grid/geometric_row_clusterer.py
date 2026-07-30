from __future__ import annotations

from dataclasses import dataclass

from src.domain.common import BoundingBox


@dataclass(frozen=True, slots=True)
class GridElement:
    """One loose, unstructured element considered as a candidate cell in a
    structure Docling's own layout model never grouped for us.

    `index` is the caller's own identifier for the source element (e.g. its
    position in a canonical-element list) so the caller can tell which
    elements were consumed once a structure is recovered.
    """

    index: int
    text: str
    bbox: BoundingBox


class GeometricRowClusterer:
    """Shared row-grouping primitive for recovering structure from loose
    canonical elements that Docling's own layout model never grouped for
    us. Used by both `TextGridTableDetector` (regular row/column grids) and
    `OrphanedTocRowReconstructor` (dot-leader TOC remnants) -- both need the
    same "which elements share a visual row" answer, just interpret each
    row's members differently afterwards.
    """
    ROW_OVERLAP_FRACTION = 0.3

    @classmethod
    def cluster_rows(
        cls,
        elements: list[GridElement],
    ) -> list[list[GridElement]]:
        ordered = sorted(elements, key=lambda element: -cls.y_center(element.bbox))
        rows: list[list[GridElement]] = []
        for element in ordered:
            placed = False
            for row in rows:
                if (
                    cls.y_overlap_fraction(row[0].bbox, element.bbox)
                    >= cls.ROW_OVERLAP_FRACTION
                ):
                    row.append(element)
                    placed = True
                    break
            if not placed:
                rows.append([element])

        for row in rows:
            row.sort(key=lambda element: cls.x_center(element.bbox))
        return rows

    @staticmethod
    def x_center(bbox: BoundingBox) -> float:
        return (bbox.x1 + bbox.x2) / 2.0

    @staticmethod
    def y_center(bbox: BoundingBox) -> float:
        return (bbox.y1 + bbox.y2) / 2.0

    @staticmethod
    def y_overlap_fraction(a: BoundingBox, b: BoundingBox) -> float:
        top = min(a.y1, b.y1)
        bottom = max(a.y2, b.y2)
        intersection = top - bottom
        if intersection <= 0:
            return 0.0
        smaller_height = min(a.y1 - a.y2, b.y1 - b.y2)
        if smaller_height <= 0:
            return 0.0
        return intersection / smaller_height

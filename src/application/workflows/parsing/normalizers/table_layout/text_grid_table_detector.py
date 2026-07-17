from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from src.domain.common import BoundingBox


@dataclass(frozen=True, slots=True)
class GridElement:
    """One loose, unstructured element considered as a candidate grid cell.

    `index` is the caller's own identifier for the source element (e.g. its
    position in a canonical-element list) so the caller can tell which
    elements this detector consumed once a table is recovered.
    """

    index: int
    text: str
    bbox: BoundingBox


@dataclass(frozen=True, slots=True)
class TextGridTableResult:
    rows: list[list[str]]
    consumed_indices: frozenset[int]
    bbox: BoundingBox


class TextGridTableDetector:
    """Recovers tabular data from loose text elements that Docling's own
    table-detection model never recognized as a table region at all.

    Confirmed on a real document: a dense record grid (e.g. a
    "pos | door-number | location" block) came through purely as
    individual short text elements, in Docling's own bottom-to-top
    emission order, with no positional correlation between a row's values
    once flattened to plain text -- the record-per-row relationship the
    visual table encodes was destroyed. This has nothing to do with any of
    this codebase's own table-reconstruction bugs: there is no Docling
    table object to extract from in this case.

    Detection is purely geometric (row/column bounding-box alignment) --
    deliberately no vocabulary, keyword, or language signal, so it behaves
    identically regardless of document language or content domain,
    matching this codebase's document-agnostic design constraint. A
    header row is deliberately NOT synthesized here (best-effort header
    matching for scattered label text is fragile and low-value compared to
    the actual data-row recovery) -- callers get a table with a blank
    header row, consistent with how downstream code already expects
    `table_rows[0]` to be a header row.
    """

    MIN_ROWS = 3
    MIN_COLUMNS = 2
    # Fraction of the smaller element's height that two elements' Y-ranges
    # must overlap by to be considered part of the same visual row. Chosen
    # low enough to tolerate a few points of baseline jitter between
    # same-row cells (confirmed against real data: same-row cells commonly
    # differ in height by a point or two) while still cleanly separating
    # adjacent real rows, whose Y-ranges do not overlap at all on a normal,
    # regularly-spaced grid.
    ROW_OVERLAP_FRACTION = 0.3

    def detect(self, elements: list[GridElement]) -> TextGridTableResult | None:
        if len(elements) < self.MIN_ROWS * self.MIN_COLUMNS:
            return None

        rows = self._cluster_rows(elements)
        slots = self._cluster_columns(elements)
        if len(slots) < self.MIN_COLUMNS:
            return None

        slot_centers = [self._mean_x(slot) for slot in slots]
        row_assignments = [
            (row, assignment)
            for row in rows
            for assignment in [self._assign_row_to_slots(row, slot_centers)]
            if assignment is not None
        ]

        dominant_signature = self._dominant_signature(row_assignments)
        if dominant_signature is None:
            return None

        qualifying = [
            (row, assignment)
            for row, assignment in row_assignments
            if frozenset(assignment) == dominant_signature
        ]
        if len(qualifying) < self.MIN_ROWS:
            return None

        ordered_slot_indices = sorted(dominant_signature)
        data_rows: list[list[str]] = []
        consumed_indices: set[int] = set()
        for _, assignment in qualifying:
            data_rows.append(
                [assignment[slot_index].text for slot_index in ordered_slot_indices]
            )
            consumed_indices.update(
                assignment[slot_index].index for slot_index in ordered_slot_indices
            )

        blank_header = ["" for _ in ordered_slot_indices]
        bbox = self._union_bbox(
            assignment[slot_index]
            for _, assignment in qualifying
            for slot_index in ordered_slot_indices
        )
        return TextGridTableResult(
            rows=[blank_header, *data_rows],
            consumed_indices=frozenset(consumed_indices),
            bbox=bbox,
        )

    @classmethod
    def _cluster_rows(
        cls,
        elements: list[GridElement],
    ) -> list[list[GridElement]]:
        ordered = sorted(elements, key=lambda element: -cls._y_center(element.bbox))
        rows: list[list[GridElement]] = []
        for element in ordered:
            placed = False
            for row in rows:
                if (
                    cls._y_overlap_fraction(row[0].bbox, element.bbox)
                    >= cls.ROW_OVERLAP_FRACTION
                ):
                    row.append(element)
                    placed = True
                    break
            if not placed:
                rows.append([element])

        for row in rows:
            row.sort(key=lambda element: cls._x_center(element.bbox))
        return rows

    @classmethod
    def _cluster_columns(
        cls,
        elements: list[GridElement],
    ) -> list[list[GridElement]]:
        ordered = sorted(elements, key=lambda element: cls._x_center(element.bbox))
        widths = sorted(element.bbox.x2 - element.bbox.x1 for element in ordered)
        median_width = widths[len(widths) // 2]
        x_range = cls._x_center(ordered[-1].bbox) - cls._x_center(ordered[0].bbox)
        # Mirrors the gap-clustering approach already used for Docling's own
        # parallel-lane detection (`ParallelTableStreamClusterer`), scaled by
        # both the overall spread and the typical cell width so it adapts to
        # different page sizes and font scales rather than a fixed pixel
        # count. Validated against real column gaps (a ~50-115pt gap between
        # genuinely distinct columns vs <5pt jitter within one column).
        gap_threshold = max(x_range * 0.06, median_width * 1.4, 18.0)

        slots: list[list[GridElement]] = [[ordered[0]]]
        previous_center = cls._x_center(ordered[0].bbox)
        for element in ordered[1:]:
            center = cls._x_center(element.bbox)
            if center - previous_center > gap_threshold:
                slots.append([element])
            else:
                slots[-1].append(element)
            previous_center = center
        return slots

    @classmethod
    def _assign_row_to_slots(
        cls,
        row: list[GridElement],
        slot_centers: list[float],
    ) -> dict[int, GridElement] | None:
        assignment: dict[int, GridElement] = {}
        for element in row:
            center = cls._x_center(element.bbox)
            nearest_index = min(
                range(len(slot_centers)),
                key=lambda index: abs(slot_centers[index] - center),
            )
            if nearest_index in assignment:
                # Two of this row's own elements map to the same column
                # slot -- this row does not fit the grid cleanly, so it is
                # excluded rather than guessed at.
                return None
            assignment[nearest_index] = element
        return assignment

    @classmethod
    def _dominant_signature(
        cls,
        row_assignments: list[tuple[list[GridElement], dict[int, GridElement]]],
    ) -> frozenset[int] | None:
        candidate_signatures = [
            frozenset(assignment)
            for _, assignment in row_assignments
            if len(assignment) >= cls.MIN_COLUMNS
        ]
        if not candidate_signatures:
            return None
        signature, count = Counter(candidate_signatures).most_common(1)[0]
        if count < cls.MIN_ROWS:
            return None
        return signature

    @staticmethod
    def _mean_x(elements: list[GridElement]) -> float:
        centers = [TextGridTableDetector._x_center(element.bbox) for element in elements]
        return sum(centers) / len(centers)

    @staticmethod
    def _x_center(bbox: BoundingBox) -> float:
        return (bbox.x1 + bbox.x2) / 2.0

    @staticmethod
    def _y_center(bbox: BoundingBox) -> float:
        return (bbox.y1 + bbox.y2) / 2.0

    @staticmethod
    def _y_overlap_fraction(a: BoundingBox, b: BoundingBox) -> float:
        top = min(a.y1, b.y1)
        bottom = max(a.y2, b.y2)
        intersection = top - bottom
        if intersection <= 0:
            return 0.0
        smaller_height = min(a.y1 - a.y2, b.y1 - b.y2)
        if smaller_height <= 0:
            return 0.0
        return intersection / smaller_height

    @staticmethod
    def _union_bbox(elements: Iterable[GridElement]) -> BoundingBox:
        elements = list(elements)
        return BoundingBox(
            x1=min(element.bbox.x1 for element in elements),
            y1=max(element.bbox.y1 for element in elements),
            x2=max(element.bbox.x2 for element in elements),
            y2=min(element.bbox.y2 for element in elements),
        )

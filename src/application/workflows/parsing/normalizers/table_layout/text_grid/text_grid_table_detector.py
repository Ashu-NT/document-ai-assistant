from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from src.application.workflows.parsing.normalizers.table_layout.text_grid.geometric_row_clusterer import (
    GeometricRowClusterer,
    GridElement,
)
from src.domain.common import BoundingBox

__all__ = ["GridElement", "TextGridTableDetector", "TextGridTableResult"]


@dataclass(frozen=True, slots=True)
class TextGridTableResult:
    rows: list[list[str]]
    consumed_indices: frozenset[int]
    bbox: BoundingBox


class TextGridTableDetector:
    """Recovers tabular data from loose text elements that Docling's own
    table-detection model never recognized as a table region at all.
    """

    MIN_ROWS = 3
    MIN_COLUMNS = 2

    def detect(self, elements: list[GridElement]) -> TextGridTableResult | None:
        if len(elements) < self.MIN_ROWS * self.MIN_COLUMNS:
            return None

        rows = GeometricRowClusterer.cluster_rows(elements)
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
    def _cluster_columns(
        cls,
        elements: list[GridElement],
    ) -> list[list[GridElement]]:
        ordered = sorted(elements, key=lambda element: GeometricRowClusterer.x_center(element.bbox))
        widths = sorted(element.bbox.x2 - element.bbox.x1 for element in ordered)
        median_width = widths[len(widths) // 2]
        x_range = GeometricRowClusterer.x_center(
            ordered[-1].bbox
        ) - GeometricRowClusterer.x_center(ordered[0].bbox)
        # Mirrors the gap-clustering approach already used for Docling's own
        # parallel-lane detection (`ParallelTableStreamClusterer`), scaled by
        # both the overall spread and the typical cell width so it adapts to
        # different page sizes and font scales rather than a fixed pixel
        # count. Validated against real column gaps (a ~50-115pt gap between
        # genuinely distinct columns vs <5pt jitter within one column).
        gap_threshold = max(x_range * 0.06, median_width * 1.4, 18.0)

        slots: list[list[GridElement]] = [[ordered[0]]]
        previous_center = GeometricRowClusterer.x_center(ordered[0].bbox)
        for element in ordered[1:]:
            center = GeometricRowClusterer.x_center(element.bbox)
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
            center = GeometricRowClusterer.x_center(element.bbox)
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
        centers = [GeometricRowClusterer.x_center(element.bbox) for element in elements]
        return sum(centers) / len(centers)

    @staticmethod
    def _union_bbox(elements: Iterable[GridElement]) -> BoundingBox:
        elements = list(elements)
        return BoundingBox(
            x1=min(element.bbox.x1 for element in elements),
            y1=max(element.bbox.y1 for element in elements),
            x2=max(element.bbox.x2 for element in elements),
            y2=min(element.bbox.y2 for element in elements),
        )

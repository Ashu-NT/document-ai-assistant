from __future__ import annotations

from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)


class LayoutRegionSegmenter:
    _MIN_VERTICAL_GAP = 48.0
    _GAP_MULTIPLIER = 1.35

    def segment(
        self,
        candidates: list[PageLayoutCandidate],
    ) -> tuple[tuple[PageLayoutCandidate, ...], ...]:
        if len(candidates) < 2:
            return (tuple(candidates),) if candidates else ()

        threshold = self._gap_threshold(candidates)
        segments: list[list[PageLayoutCandidate]] = [[candidates[0]]]
        previous = candidates[0]
        previous_role_key = self._role_key(previous)

        for candidate in candidates[1:]:
            current_role_key = self._role_key(candidate)
            if self._should_split(
                previous=previous,
                current=candidate,
                previous_role_key=previous_role_key,
                current_role_key=current_role_key,
                threshold=threshold,
            ):
                segments.append([candidate])
            else:
                segments[-1].append(candidate)
            previous = candidate
            previous_role_key = current_role_key

        return tuple(tuple(segment) for segment in segments if segment)

    def _should_split(
        self,
        *,
        previous: PageLayoutCandidate,
        current: PageLayoutCandidate,
        previous_role_key: str,
        current_role_key: str,
        threshold: float,
    ) -> bool:
        if previous_role_key != current_role_key:
            return True

        previous_bottom = previous.bottom_y()
        current_top = current.top_y()
        if previous_bottom is None or current_top is None:
            return False
        return (previous_bottom - current_top) > threshold

    def _gap_threshold(
        self,
        candidates: list[PageLayoutCandidate],
    ) -> float:
        heights = [
            candidate.height()
            for candidate in candidates
            if candidate.height() is not None
        ]
        if not heights:
            return self._MIN_VERTICAL_GAP
        return max(self._MIN_VERTICAL_GAP, self._median(heights) * self._GAP_MULTIPLIER)

    @staticmethod
    def _role_key(candidate: PageLayoutCandidate) -> str:
        label = candidate.label.strip().lower()
        if "table" in label or label == "document_index":
            return "table"
        if "picture" in label or "image" in label or "figure" in label:
            return "picture"
        return "flow"

    @staticmethod
    def _median(values: list[float]) -> float:
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2 == 1:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2.0

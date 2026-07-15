from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)


class LayoutReadingOrderResolver:
    def sort_candidates(
        self,
        candidates: list[PageLayoutCandidate],
    ) -> list[PageLayoutCandidate]:
        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.top_y() or 0.0,
                candidate.center_x() or 0.0,
                candidate.element_ref,
            ),
        )

    def build_reading_order(
        self,
        candidates: list[PageLayoutCandidate],
    ) -> dict[str, int]:
        ordered = self.sort_candidates(candidates)
        return {
            candidate.element_ref: index
            for index, candidate in enumerate(ordered, start=1)
        }

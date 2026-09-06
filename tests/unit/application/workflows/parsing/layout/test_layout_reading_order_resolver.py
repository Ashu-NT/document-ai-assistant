from src.application.workflows.parsing.layout.layout_reading_order_resolver import (
    LayoutReadingOrderResolver,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.domain.common import BoundingBox


def _candidate(element_ref: str, bbox: BoundingBox) -> PageLayoutCandidate:
    return PageLayoutCandidate(
        element_ref=element_ref,
        page_number=1,
        bbox=bbox,
        label="text",
    )


def test_sort_candidates_uses_docling_bottom_left_coordinates() -> None:
    lower_table = _candidate("table", BoundingBox(100, 100, 900, 300))
    upper_heading = _candidate("heading", BoundingBox(100, 900, 900, 940))

    ordered = LayoutReadingOrderResolver().sort_candidates(
        [lower_table, upper_heading]
    )

    assert [candidate.element_ref for candidate in ordered] == ["heading", "table"]

from types import SimpleNamespace

from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.application.workflows.parsing.layout.page_furniture import (
    PageFurnitureRole,
    RecurringPageFurnitureDetector,
)
from src.application.workflows.parsing.layout.page_layout_analyzer import (
    PageLayoutAnalyzer,
)
from src.domain.common import BoundingBox


def _candidate(
    ref: str,
    page: int,
    text: str,
    *,
    y1: float,
    y2: float,
    label: str = "text",
) -> PageLayoutCandidate:
    return PageLayoutCandidate(
        element_ref=ref,
        page_number=page,
        bbox=BoundingBox(x1=50, y1=y1, x2=550, y2=y2),
        label=label,
        text=text,
    )


def _page_sizes(count: int) -> dict[int, tuple[float, float]]:
    return {page: (600.0, 1000.0) for page in range(1, count + 1)}


def test_detects_repeated_headers_and_variable_page_number_footers() -> None:
    candidates = []
    for page in range(1, 11):
        candidates.extend(
            [
                _candidate(
                    f"header_{page}",
                    page,
                    "Compressor Operating Manual",
                    y1=940,
                    y2=970,
                    label="section_header",
                ),
                _candidate(
                    f"footer_{page}",
                    page,
                    f"Document A-104 | {page}/10 | 2026-09-07",
                    y1=15,
                    y2=35,
                ),
            ]
        )

    result = RecurringPageFurnitureDetector().detect(
        candidates=candidates,
        page_sizes=_page_sizes(10),
    )

    assert result["header_1"] == PageFurnitureRole.RUNNING_HEADER
    assert result["header_10"] == PageFurnitureRole.RUNNING_HEADER
    assert result["footer_1"] == PageFurnitureRole.RUNNING_FOOTER
    assert result["footer_10"] == PageFurnitureRole.RUNNING_FOOTER


def test_does_not_treat_body_headings_or_sparse_edge_warnings_as_furniture() -> None:
    candidates = [
        _candidate(
            f"body_{page}",
            page,
            "Maintenance",
            y1=500,
            y2=540,
            label="section_header",
        )
        for page in (2, 5, 8)
    ]
    candidates.extend(
        _candidate(
            f"warning_{page}",
            page,
            "Warning",
            y1=940,
            y2=970,
            label="section_header",
        )
        for page in (1, 5, 10)
    )

    result = RecurringPageFurnitureDetector().detect(
        candidates=candidates,
        page_sizes=_page_sizes(10),
    )

    assert result == {}


def test_layout_analyzer_serializes_detected_furniture_metadata() -> None:
    pages = {
        page: SimpleNamespace(size=SimpleNamespace(width=600, height=1000))
        for page in range(1, 7)
    }
    candidates = [
        _candidate(
            f"header_{page}",
            page,
            "Service Manual",
            y1=940,
            y2=970,
            label="section_header",
        )
        for page in range(1, 7)
    ]

    metadata = PageLayoutAnalyzer().analyze_and_serialize(
        raw_document=SimpleNamespace(pages=pages),
        candidates=candidates,
    )

    assert metadata["header_3"]["layout_is_page_furniture"] is True
    assert metadata["header_3"]["layout_page_furniture_role"] == "running_header"

from src.application.workflows.parsing.builders.section_hierarchy import (
    TocPageRangeStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


def make_element(
    element_id: str,
    element_type: ElementType,
    text: str,
    page: int,
    order_index: int,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order_index,
    )


def test_toc_strategy_parses_entries_and_assigns_top_levels_and_children() -> None:
    elements = [
        make_element("hdr_cover", ElementType.SECTION_HEADER, "Oscilloscope Fundamentals", 1, 1),
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Table of Contents", 2, 2),
        make_element(
            "tbl_toc",
            ElementType.TABLE,
            "| Introduction ................................ 3 |\n| Chapter Two ................................ 5 |",
            2,
            3,
        ),
        make_element("hdr_intro", ElementType.SECTION_HEADER, "Introduction", 3, 4),
        make_element("hdr_overview", ElementType.SECTION_HEADER, "Overview", 4, 5),
        make_element("hdr_ch2", ElementType.SECTION_HEADER, "Chapter Two", 5, 6),
        make_element("hdr_deep", ElementType.SECTION_HEADER, "Deep Dive", 6, 7),
    ]
    headers = [element for element in elements if element.element_type == ElementType.SECTION_HEADER]
    strategy = TocPageRangeStrategy()

    levels = strategy.assign_levels(headers, elements)

    assert strategy.can_apply(headers, elements) is True
    assert levels["hdr_toc"] == 1
    assert levels["hdr_intro"] == 1
    assert levels["hdr_overview"] == 2
    assert levels["hdr_ch2"] == 1
    assert levels["hdr_deep"] == 2

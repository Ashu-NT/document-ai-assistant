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
    metadata: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order_index,
        metadata=metadata or {},
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


def test_toc_strategy_detects_contents_and_structured_document_index_rows() -> None:
    elements = [
        make_element("hdr_cover", ElementType.SECTION_HEADER, "DP Lab", 1, 1),
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 3, 2),
        make_element(
            "tbl_toc",
            ElementType.TABLE,
            "",
            3,
            3,
            metadata={
                "item_label": "document_index",
                "table_rows": [
                    ["1 Sampling and quantization", "", "", "5"],
                    ["", "1.2", "Lab preparation", "5"],
                    ["", "", "1.2.1 Interrupt handler and bit manipulation", "6"],
                ],
            },
        ),
        make_element("hdr_root", ElementType.SECTION_HEADER, "Sampling and quantization", 5, 4),
        make_element("hdr_child", ElementType.SECTION_HEADER, "1.2 Lab preparation", 5, 5),
        make_element(
            "hdr_grandchild",
            ElementType.SECTION_HEADER,
            "1.2.1 Interrupt handler and bit manipulation",
            6,
            6,
        ),
    ]
    headers = [element for element in elements if element.element_type == ElementType.SECTION_HEADER]
    strategy = TocPageRangeStrategy()

    outline = strategy.build_outline(headers, elements)
    levels = strategy.assign_levels(headers, elements)

    assert strategy.can_apply(headers, elements) is True
    assert outline.header_numberings["hdr_root"] == "1"
    assert outline.header_numberings["hdr_child"] == "1.2"
    assert levels["hdr_root"] == 1
    assert levels["hdr_child"] == 2
    assert levels["hdr_grandchild"] == 3

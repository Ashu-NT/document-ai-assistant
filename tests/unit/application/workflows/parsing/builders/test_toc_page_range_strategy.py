from src.application.workflows.parsing.builders.section_hierarchy.strategies.toc_page_range_strategy import (
    TocPageRangeStrategy,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.domain.common import ElementType


def make_element(
    element_id: str,
    element_type: ElementType,
    text: str,
    page: int,
    order_index: int,
    metadata: dict | None = None,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
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


def test_toc_strategy_merges_split_toc_tables_across_adjacent_pages() -> None:
    elements = [
        make_element("hdr_cover", ElementType.SECTION_HEADER, "Service Manual", 1, 1),
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 2, 2),
        make_element(
            "tbl_toc_a",
            ElementType.TABLE,
            "",
            2,
            3,
            metadata={
                "item_label": "document_index",
                "table_rows": [
                    ["1", "Introduction", "3"],
                    ["1.1", "Overview", "4"],
                ],
            },
        ),
        make_element(
            "tbl_toc_b",
            ElementType.TABLE,
            "",
            3,
            4,
            metadata={
                "item_label": "document_index",
                "table_rows": [
                    ["2", "Operation", "6"],
                    ["2.1", "Startup", "7"],
                ],
            },
        ),
        make_element("hdr_intro", ElementType.SECTION_HEADER, "Introduction", 3, 5),
        make_element("hdr_overview", ElementType.SECTION_HEADER, "Overview", 4, 6),
        make_element("hdr_operation", ElementType.SECTION_HEADER, "Operation", 6, 7),
        make_element("hdr_startup", ElementType.SECTION_HEADER, "Startup", 7, 8),
    ]
    headers = [element for element in elements if element.element_type == ElementType.SECTION_HEADER]
    strategy = TocPageRangeStrategy()

    outline = strategy.build_outline(headers, elements)
    levels = strategy.assign_levels(headers, elements)

    assert len(outline.entries) == 4
    assert outline.header_numberings["hdr_intro"] == "1"
    assert outline.header_numberings["hdr_overview"] == "1.1"
    assert outline.header_numberings["hdr_operation"] == "2"
    assert outline.header_numberings["hdr_startup"] == "2.1"
    assert levels["hdr_intro"] == 1
    assert levels["hdr_overview"] == 2
    assert levels["hdr_operation"] == 1
    assert levels["hdr_startup"] == 2


def test_toc_strategy_collects_a_relative_six_page_toc_starting_on_page_five() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Table of Contents", 5, 1),
    ]
    for index, page in enumerate(range(5, 11), start=1):
        elements.append(
            make_element(
                f"toc_{index}",
                ElementType.TABLE,
                "",
                page,
                index + 1,
                metadata={
                    "item_label": "document_index",
                    "table_rows": [[str(index), f"Chapter {index}", str(page + 10)]],
                },
            )
        )
    elements.extend(
        make_element(
            f"body_{index}",
            ElementType.SECTION_HEADER,
            f"{index} Chapter {index}",
            page + 10,
            index + 20,
        )
        for index, page in enumerate(range(5, 11), start=1)
    )
    headers = [
        element
        for element in elements
        if element.element_type == ElementType.SECTION_HEADER
    ]

    outline = TocPageRangeStrategy().build_outline(headers, elements)

    assert len(outline.entries) == 6
    assert {entry.numbering for entry in outline.entries} == {
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
    }


def test_toc_strategy_assembles_wrapped_prefix_reported_after_table() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 5, 1),
        make_element(
            "toc_table",
            ElementType.TABLE,
            "",
            5,
            2,
            metadata={
                "item_label": "document_index",
                "table_rows": [["Marine applications", "13"]],
            },
        ),
        make_element(
            "toc_prefix",
            ElementType.TEXT,
            "2.2 Intended use of engines and systems in",
            5,
            3,
        ),
        make_element(
            "body",
            ElementType.SECTION_HEADER,
            "2.2 Intended use of engines and systems in Marine applications",
            13,
            4,
        ),
    ]
    headers = [elements[0], elements[-1]]

    outline = TocPageRangeStrategy().build_outline(headers, elements)

    assert outline.entries[0].numbering == "2.2"
    assert outline.entries[0].title == (
        "Intended use of engines and systems in Marine applications"
    )
    assert outline.matched_entries["body"] == outline.entries[0]


def test_toc_strategy_keeps_parallel_column_streams_independent() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 2, 1),
        make_element(
            "toc_table",
            ElementType.TABLE,
            "",
            2,
            2,
            metadata={
                "item_label": "document_index",
                "table_parallel_stream_rows": [
                    [["1", "Introduction", "3"], ["1.1", "Scope", "4"]],
                    [["6", "Maintenance", "67"], ["7", "Operation", "69"]],
                ],
            },
        ),
    ]

    outline = TocPageRangeStrategy().build_outline([elements[0]], elements)

    assert [(entry.numbering, entry.title) for entry in outline.entries] == [
        ("1", "Introduction"),
        ("1.1", "Scope"),
        ("6", "Maintenance"),
        ("7", "Operation"),
    ]


def test_toc_strategy_matches_repeated_titles_by_expected_page() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 2, 1),
        make_element("toc", ElementType.TEXT, "Operation .... 70", 2, 2),
        make_element("early", ElementType.SECTION_HEADER, "Operation", 20, 3),
        make_element("expected", ElementType.SECTION_HEADER, "Operation", 70, 4),
    ]
    headers = [elements[0], elements[2], elements[3]]

    outline = TocPageRangeStrategy().build_outline(headers, elements)

    assert "expected" in outline.matched_entries
    assert "early" not in outline.matched_entries


def test_toc_strategy_leaves_materially_ambiguous_titles_unmatched() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 2, 1),
        make_element("toc", ElementType.TEXT, "Overview .... 8", 2, 2),
        make_element("first", ElementType.SECTION_HEADER, "Overview", 8, 3),
        make_element("second", ElementType.SECTION_HEADER, "Overview", 8, 4),
    ]
    headers = [elements[0], elements[2], elements[3]]

    outline = TocPageRangeStrategy().build_outline(headers, elements)

    assert outline.matched_entries == {}
    assert [entry.title for entry in outline.unmatched_entries] == ["Overview"]

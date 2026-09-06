from src.application.workflows.parsing.builders.section_hierarchy.strategies.toc_page_range_strategy import (
    TocPageRangeStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc import (
    TocVisualLineAssembler,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import BoundingBox, ElementType


def make_element(
    element_id: str,
    text: str,
    *,
    order: int,
    page: int = 5,
    bbox: BoundingBox | None = None,
    element_type: ElementType = ElementType.TEXT,
    metadata: dict | None = None,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order,
        bbox=bbox,
        metadata=metadata or {},
    )


def test_visual_line_assembler_recovers_split_number_title_and_page() -> None:
    elements = [
        make_element("number", "4.2", order=1, bbox=BoundingBox(40, 700, 60, 690)),
        make_element("title", "Installation requirements", order=2, bbox=BoundingBox(70, 700, 240, 690)),
        make_element("page", "37", order=3, bbox=BoundingBox(280, 700, 295, 690)),
    ]

    entries = TocVisualLineAssembler().assemble(elements)

    assert [(entry.numbering, entry.title, entry.start_page) for entry in entries] == [
        ("4.2", "Installation requirements", 37)
    ]


def test_visual_line_assembler_never_combines_fragments_across_pages() -> None:
    elements = [
        make_element("number", "4.2", order=1, page=5, bbox=BoundingBox(40, 700, 60, 690)),
        make_element(
            "title",
            "Installation requirements",
            order=2,
            page=6,
            bbox=BoundingBox(70, 700, 240, 690),
        ),
        make_element("page", "37", order=3, page=6, bbox=BoundingBox(280, 700, 295, 690)),
    ]

    entries = TocVisualLineAssembler().assemble(elements)

    assert [(entry.numbering, entry.title) for entry in entries] == [
        (None, "Installation requirements")
    ]


def test_toc_ignores_rotated_marginal_document_control_text() -> None:
    elements = [
        make_element(
            "toc_header",
            "Contents",
            order=1,
            element_type=ElementType.SECTION_HEADER,
        ),
        make_element("toc", "2.2 Intended use 13", order=2),
        make_element(
            "vertical_footer",
            "Document control: 0000067352 - 001",
            order=3,
            page=6,
            bbox=BoundingBox(554, 186, 558, 133),
        ),
        make_element(
            "body",
            "2.2 Intended use",
            order=4,
            page=13,
            element_type=ElementType.SECTION_HEADER,
        ),
    ]

    outline = TocPageRangeStrategy().build_outline(
        [elements[0], elements[-1]],
        elements,
    )

    assert [entry.title for entry in outline.entries] == ["Intended use"]


def test_toc_wrapped_fragment_ignores_number_only_and_short_chapter_noise() -> None:
    elements = [
        make_element(
            "toc_header",
            "Contents",
            order=1,
            element_type=ElementType.SECTION_HEADER,
        ),
        make_element("number_only", "1", order=2),
        make_element("short_chapter", "2 Safety", order=3),
        make_element(
            "continuations",
            "",
            order=4,
            element_type=ElementType.TABLE,
            metadata={
                "item_label": "document_index",
                "table_rows": [["Offshore applications", "23"]],
            },
        ),
        make_element(
            "wrapped_prefix",
            "4.2 Installation requirements for",
            order=5,
        ),
        make_element(
            "body",
            "4.2 Installation requirements for Offshore applications",
            order=6,
            page=23,
            element_type=ElementType.SECTION_HEADER,
        ),
    ]
    headers = [elements[0], elements[-1]]

    outline = TocPageRangeStrategy().build_outline(headers, elements)

    assert [(entry.numbering, entry.title) for entry in outline.entries] == [
        ("4.2", "Installation requirements for Offshore applications")
    ]
    assert outline.header_numberings["body"] == "4.2"


def test_toc_exact_long_title_beats_same_number_partial_title() -> None:
    elements = [
        make_element(
            "toc_header",
            "Contents",
            order=1,
            element_type=ElementType.SECTION_HEADER,
        ),
        make_element("toc", "4.2 Installation requirements for offshore systems 23", order=2),
        make_element(
            "full_title",
            "Installation requirements for offshore systems",
            order=3,
            page=23,
            element_type=ElementType.SECTION_HEADER,
        ),
        make_element(
            "partial_title",
            "4.2 Installation requirements",
            order=4,
            page=23,
            element_type=ElementType.SECTION_HEADER,
        ),
    ]

    outline = TocPageRangeStrategy().build_outline(
        [elements[0], *elements[2:]],
        elements,
    )

    assert "full_title" in outline.matched_entries
    assert "partial_title" not in outline.matched_entries


def test_toc_matcher_rejects_conflicting_number_and_distant_title() -> None:
    elements = [
        make_element(
            "toc_header",
            "Contents",
            order=1,
            element_type=ElementType.SECTION_HEADER,
        ),
        make_element("toc", "2.5 Safety requirements 17", order=2),
        make_element(
            "wrong_number",
            "2 Safety requirements",
            order=3,
            page=17,
            element_type=ElementType.SECTION_HEADER,
        ),
        make_element(
            "distant",
            "Safety requirements",
            order=4,
            page=70,
            element_type=ElementType.SECTION_HEADER,
        ),
    ]

    outline = TocPageRangeStrategy().build_outline(
        [elements[0], *elements[2:]],
        elements,
    )

    assert outline.matched_entries == {}
    assert [entry.numbering for entry in outline.unmatched_entries] == ["2.5"]

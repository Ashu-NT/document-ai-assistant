from src.application.workflows.parsing.builders.section_hierarchy.section_header_filter import (
    SectionHeaderFilter,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.domain.common import ElementType


def make_header(element_id: str, text: str, order_index: int = 1) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        page_start=1,
        page_end=1,
        order_index=order_index,
    )


def test_section_header_filter_drops_default_branding_header() -> None:
    header = make_header("hdr_1", "Environmentally Responsible Solutions Engineered")

    result = SectionHeaderFilter().filter([header])

    assert result == []


def test_section_header_filter_keeps_a_real_heading() -> None:
    header = make_header("hdr_1", "1 Introduction")

    result = SectionHeaderFilter().filter([header])

    assert result == [header]


def test_section_header_filter_uses_injected_branding_headers_override() -> None:
    header = make_header("hdr_1", "custom vendor boilerplate")
    filter_ = SectionHeaderFilter(branding_headers=frozenset({"custom vendor boilerplate"}))

    assert filter_.filter([header]) == []
    # The default corpus header isn't in the injected override, so it's
    # treated as a real heading instead of being dropped.
    other_header = make_header(
        "hdr_2", "Environmentally Responsible Solutions Engineered"
    )
    assert filter_.filter([other_header]) == [other_header]

from src.application.workflows.parsing.builders.section_hierarchy import (
    SectionHierarchyResolver,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


def make_element(
    element_id: str,
    element_type: ElementType,
    text: str,
    order_index: int,
    page: int,
    metadata: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        order_index=order_index,
        page_start=page,
        page_end=page,
        metadata=metadata or {},
    )


def test_resolver_uses_docling_levels_when_they_are_useful() -> None:
    elements = [
        make_element("hdr_1", ElementType.SECTION_HEADER, "Introduction", 1, 1, {"heading_level": 1}),
        make_element("hdr_2", ElementType.SECTION_HEADER, "Overview", 2, 1, {"heading_level": 2}),
        make_element("hdr_3", ElementType.SECTION_HEADER, "Details", 3, 1, {"heading_level": 3}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels == {
        "hdr_1": 1,
        "hdr_2": 2,
        "hdr_3": 3,
    }
    assert resolution.sources["hdr_2"] == "docling_level"


def test_resolver_falls_back_to_toc_when_all_docling_levels_are_one() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Table of Contents", 1, 2, {"heading_level": 1}),
        make_element("tbl_toc", ElementType.TABLE, "| Introduction .... 3 |\n| Chapter Two .... 5 |", 2, 2),
        make_element("hdr_intro", ElementType.SECTION_HEADER, "Introduction", 3, 3, {"heading_level": 1}),
        make_element("hdr_child", ElementType.SECTION_HEADER, "Overview", 4, 4, {"heading_level": 1}),
        make_element("hdr_root_2", ElementType.SECTION_HEADER, "Chapter Two", 5, 5, {"heading_level": 1}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels["hdr_intro"] == 1
    assert resolution.effective_levels["hdr_child"] == 2
    assert resolution.sources["hdr_child"] == "toc_page_range"


def test_resolver_applies_layout_refinement_inside_toc_ranges() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Table of Contents", 1, 2, {"heading_level": 1}),
        make_element("tbl_toc", ElementType.TABLE, "| Oscilloscope Probes .... 26 |", 2, 2),
        make_element("hdr_root", ElementType.SECTION_HEADER, "Oscilloscope Probes", 3, 26, {"heading_level": 1}),
        make_element("hdr_child", ElementType.SECTION_HEADER, "Loading", 4, 26, {"heading_level": 1}),
        make_element("hdr_grandchild", ElementType.SECTION_HEADER, "Resistive loading", 5, 26, {"heading_level": 1}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels["hdr_root"] == 1
    assert resolution.effective_levels["hdr_child"] == 2
    assert resolution.effective_levels["hdr_grandchild"] == 3
    assert resolution.sources["hdr_grandchild"] == "layout_heuristic"

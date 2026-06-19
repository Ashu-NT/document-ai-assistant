from src.application.workflows.parsing.builders.section_hierarchy import (
    SectionStackBuilder,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


def make_header(element_id: str, text: str, order_index: int) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        order_index=order_index,
    )


def test_section_stack_builder_populates_parent_ids_and_paths() -> None:
    headers = [
        make_header("hdr_1", "Introduction", 1),
        make_header("hdr_2", "Overview", 2),
        make_header("hdr_3", "Details", 3),
    ]
    builder = SectionStackBuilder(IdGenerator())

    sections, header_section_ids = builder.build(
        "doc_001",
        headers,
        {
            "hdr_1": 1,
            "hdr_2": 2,
            "hdr_3": 3,
        },
    )

    assert len(sections) == 3
    assert header_section_ids["hdr_1"] == sections[0].section_id
    assert sections[1].parent_section_id == sections[0].section_id
    assert sections[2].parent_section_id == sections[1].section_id
    assert sections[2].section_path == ["Introduction", "Overview", "Details"]


def test_section_stack_builder_clears_stale_stack_when_returning_to_root() -> None:
    headers = [
        make_header("hdr_1", "Root A", 1),
        make_header("hdr_2", "Child A", 2),
        make_header("hdr_3", "Grandchild A", 3),
        make_header("hdr_4", "Root B", 4),
        make_header("hdr_5", "Child B", 5),
    ]
    builder = SectionStackBuilder(IdGenerator())

    sections, _ = builder.build(
        "doc_001",
        headers,
        {
            "hdr_1": 1,
            "hdr_2": 2,
            "hdr_3": 3,
            "hdr_4": 1,
            "hdr_5": 2,
        },
    )

    assert sections[4].parent_section_id == sections[3].section_id
    assert sections[4].parent_section_id != sections[2].section_id
    assert sections[4].section_path == ["Root B", "Child B"]

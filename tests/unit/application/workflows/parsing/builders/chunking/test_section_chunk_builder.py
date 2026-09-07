from src.application.workflows.parsing.builders.chunking.builders.section_chunk.section_chunk_builder import (
    SectionChunkBuilder,
)
from src.domain.common import ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def make_section(
    *,
    section_id: str = "sec_001",
    title: str,
    section_path: list[str],
    page: int = 5,
    parent_section_id: str | None = "sec_parent",
    sequence_number: int = 1,
) -> DocumentSection:
    # parent_section_id defaults to a non-None placeholder so
    # SectionChunkSkipper's front-matter branch (which only applies to
    # top-level, parent-less sections) never accidentally engages in tests
    # that aren't specifically about it.
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        level=2 if parent_section_id is not None else 1,
        parent_section_id=parent_section_id,
        section_path=section_path,
        source=SourceLocation(page_start=page, page_end=page),
        sequence_number=sequence_number,
    )


def make_element(
    *,
    element_id: str,
    text: str,
    page: int = 5,
    reading_order: int = 1,
    element_type: ElementType = ElementType.TEXT,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        reading_order=reading_order,
        source=SourceLocation(page_start=page, page_end=page),
    )


def test_build_chunk_payloads_returns_empty_for_no_elements() -> None:
    builder = SectionChunkBuilder()
    section = make_section(title="Notes", section_path=["Notes"])

    payloads = builder.build_chunk_payloads(
        document_title="Manual",
        section=section,
        elements=[],
    )

    assert payloads == []


def test_build_chunk_payloads_returns_empty_when_section_is_skipped() -> None:
    # A top-level (no parent), page-1 section whose only content is
    # boilerplate is exactly what SectionChunkSkipper's front-matter gate
    # exists to filter out.
    builder = SectionChunkBuilder()
    section = make_section(
        title="Legal notice",
        section_path=["Legal notice"],
        page=1,
        parent_section_id=None,
    )
    elements = [
        make_element(element_id="t1", text="Copyright 2024 Acme Corp.", page=1),
        make_element(element_id="t2", text="All rights reserved.", page=1),
    ]

    payloads = builder.build_chunk_payloads(
        document_title="Manual",
        section=section,
        elements=elements,
    )

    assert payloads == []


def test_build_chunk_payloads_returns_content_payload_for_normal_section() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        title="Installation",
        section_path=["Chapter 1", "Installation"],
    )
    elements = [
        make_element(
            element_id="t1",
            text="Mount the bracket to the wall using the four supplied screws.",
        ),
    ]

    payloads = builder.build_chunk_payloads(
        document_title="Manual",
        section=section,
        elements=elements,
    )

    assert len(payloads) == 1
    assert "Mount the bracket" in payloads[0].content
    assert payloads[0].section_path == ["Chapter 1", "Installation"]


def test_build_chunk_payloads_deduplicates_exact_duplicate_content_split_by_token_budget() -> (
    None
):
    # A tiny max_chunk_tokens forces the packer to split two identical
    # fragments into two separate payloads (same section -> the merge
    # policy alone would never flush between them, but the packer's hard
    # token cap does). Both payloads share section_id and normalized
    # content, so the deduplicator should still collapse them back to one.
    builder = SectionChunkBuilder(max_chunk_tokens=5, chunk_overlap=0)
    section = make_section(title="Notes", section_path=["Notes"])
    elements = [
        make_element(element_id="t1", text="Duplicate content here.", reading_order=1),
        make_element(element_id="t2", text="Duplicate content here.", reading_order=2),
    ]

    payloads = builder.build_chunk_payloads(
        document_title="Manual",
        section=section,
        elements=elements,
    )

    assert len(payloads) == 1


def test_build_document_chunk_payloads_returns_empty_for_no_sections() -> None:
    builder = SectionChunkBuilder()

    payloads = builder.build_document_chunk_payloads(
        document_title="Manual",
        sections=[],
        section_elements_by_id={},
    )

    assert payloads == []


def test_build_document_chunk_payloads_produces_overview_and_content_payloads_for_parent_with_child() -> (
    None
):
    builder = SectionChunkBuilder()
    parent = make_section(
        section_id="chapter_1",
        title="Chapter 1",
        section_path=["Chapter 1"],
        parent_section_id=None,
        sequence_number=1,
    )
    child = make_section(
        section_id="installation",
        title="Installation",
        section_path=["Chapter 1", "Installation"],
        parent_section_id="chapter_1",
        sequence_number=2,
    )
    section_elements_by_id = {
        "installation": [
            make_element(
                element_id="t1",
                text="Mount the bracket to the wall using the four supplied screws.",
            ),
        ],
    }

    payloads = builder.build_document_chunk_payloads(
        document_title="Manual",
        sections=[parent, child],
        section_elements_by_id=section_elements_by_id,
    )

    overview_payloads = [
        payload for payload in payloads if payload.chunk_type.value == "overview"
    ]
    content_payloads = [
        payload for payload in payloads if payload.chunk_type.value != "overview"
    ]

    assert len(overview_payloads) == 1
    assert overview_payloads[0].section_path == ["Chapter 1"]
    assert "Installation" in overview_payloads[0].content

    assert len(content_payloads) == 1
    assert "Mount the bracket" in content_payloads[0].content
    assert content_payloads[0].section_path == ["Chapter 1", "Installation"]


def test_build_document_chunk_payloads_skips_front_matter_section_but_keeps_normal_section() -> (
    None
):
    builder = SectionChunkBuilder()
    front_matter_section = make_section(
        section_id="legal",
        title="Legal notice",
        section_path=["Legal notice"],
        page=1,
        parent_section_id=None,
        sequence_number=1,
    )
    normal_section = make_section(
        section_id="installation",
        title="Installation",
        section_path=["Installation"],
        page=5,
        parent_section_id=None,
        sequence_number=2,
    )
    section_elements_by_id = {
        "legal": [
            make_element(
                element_id="t1", text="Copyright 2024 Acme Corp.", page=1
            ),
            make_element(
                element_id="t2", text="All rights reserved.", page=1
            ),
        ],
        "installation": [
            make_element(
                element_id="t3",
                text="Mount the bracket to the wall using the four supplied screws.",
                page=5,
            ),
        ],
    }

    payloads = builder.build_document_chunk_payloads(
        document_title="Manual",
        sections=[front_matter_section, normal_section],
        section_elements_by_id=section_elements_by_id,
    )

    assert len(payloads) == 1
    assert payloads[0].section_path == ["Installation"]
    assert "Mount the bracket" in payloads[0].content


def test_build_document_chunk_payloads_merges_related_sibling_sections_via_merge_policy() -> (
    None
):
    # Full orchestration contract: two sibling sections sharing a title
    # topic under the same parent should come out as one packed payload,
    # proving fragment building, packing, and SectionMergePolicy all wire
    # together correctly through this entry point (not just in isolation).
    builder = SectionChunkBuilder(max_chunk_tokens=200, chunk_overlap=0)
    parent = make_section(
        section_id="lab_prep",
        title="Lab preparation",
        section_path=["Chapter 1", "Lab preparation"],
        parent_section_id="chapter_1",
        sequence_number=1,
    )
    sibling_a = make_section(
        section_id="sec_a",
        title="1.2.1 Interrupt handler and bit manipulation",
        section_path=[
            "Chapter 1",
            "Lab preparation",
            "1.2.1 Interrupt handler and bit manipulation",
        ],
        parent_section_id="lab_prep",
        sequence_number=2,
    )
    sibling_b = make_section(
        section_id="sec_b",
        title="Prep task 1: Interrupt handler and bit manipulation",
        section_path=[
            "Chapter 1",
            "Lab preparation",
            "Prep task 1: Interrupt handler and bit manipulation",
        ],
        parent_section_id="lab_prep",
        sequence_number=3,
    )
    section_elements_by_id = {
        "sec_a": [
            make_element(element_id="t1", text="Bit manipulation explanation."),
        ],
        "sec_b": [
            make_element(element_id="t2", text="Prep task question follows."),
        ],
    }

    payloads = builder.build_document_chunk_payloads(
        document_title="Lab Manual",
        sections=[parent, sibling_a, sibling_b],
        section_elements_by_id=section_elements_by_id,
    )

    # One merged content payload for the two siblings, plus the "Lab
    # preparation" parent's own overview payload (it now has two
    # recognized children) -- the point under test is that the siblings'
    # own content collapsed into a single payload rather than two.
    content_payloads = [
        payload for payload in payloads if payload.chunk_type.value != "overview"
    ]

    assert len(content_payloads) == 1
    assert "Bit manipulation explanation." in content_payloads[0].content
    assert "Prep task question follows." in content_payloads[0].content

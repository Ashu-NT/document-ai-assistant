from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.overview.section_overview_chunk_builder import (
    SectionOverviewChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def _make_text_element(*, element_id: str, text: str) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        source=SourceLocation(page_start=1, page_end=1),
    )


def _make_section(
    section_id: str,
    *,
    title: str,
    parent_section_id: str | None = None,
) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        parent_section_id=parent_section_id,
        section_path=[title],
    )


def test_build_overview_chunk_token_count_matches_truncated_text() -> None:
    text_splitter = ChunkTextSplitter(max_chunk_tokens=200)
    builder = SectionOverviewChunkBuilder(
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
    )
    parent = _make_section("sec_parent", title="Maintenance")
    child_one = _make_section(
        "sec_child_1", title="Filter replacement", parent_section_id="sec_parent"
    )
    child_two = _make_section(
        "sec_child_2", title="Oil change", parent_section_id="sec_parent"
    )

    payloads = builder.build(
        document_title="Manual",
        sections=[parent, child_one, child_two],
        section_elements_by_id={},
    )

    assert len(payloads) == 1
    overview_text, overview_token_count = builder._build_overview_text(
        section=parent,
        child_sections=[child_one, child_two],
    )
    assert overview_token_count == text_splitter.count_tokens(overview_text)
    assert parent.overview_text == overview_text


def test_build_overview_chunk_token_count_matches_when_truncated() -> None:
    text_splitter = ChunkTextSplitter(max_chunk_tokens=20)
    builder = SectionOverviewChunkBuilder(
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
    )
    parent = _make_section("sec_parent", title="Maintenance")
    children = [
        _make_section(
            f"sec_child_{i}",
            title=f"Long subsection title number {i} about maintenance tasks",
            parent_section_id="sec_parent",
        )
        for i in range(10)
    ]

    payloads = builder.build(
        document_title="Manual",
        sections=[parent, *children],
        section_elements_by_id={},
    )

    assert len(payloads) == 1
    overview_text, overview_token_count = builder._build_overview_text(
        section=parent,
        child_sections=children,
    )
    assert overview_token_count == text_splitter.count_tokens(overview_text)
    assert overview_token_count <= builder.max_overview_tokens
    assert "Direct subsections (10):" in overview_text
    assert "omitted due to token limit" in overview_text


def test_build_overview_reports_complete_direct_child_count() -> None:
    builder = SectionOverviewChunkBuilder(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=400),
        payload_factory=ChunkPayloadFactory(),
    )
    parent = _make_section("sec_parent", title="Safety")
    children = [
        _make_section(
            f"sec_child_{index}",
            title=f"Safety topic {index}",
            parent_section_id=parent.section_id,
        )
        for index in range(12)
    ]

    overview_text, _ = builder._build_overview_text(
        section=parent,
        child_sections=children,
    )

    assert "Direct subsections (12):" in overview_text
    assert "Safety topic 11" in overview_text


def test_build_overview_never_includes_the_sections_own_direct_text() -> None:
    # Regression: overview chunks used to also pull in the section's own
    # TEXT/LIST_ITEM/KEY_VALUE/CODE elements (_direct_section_text), which
    # duplicated the exact same content that independently flows into the
    # section's real content chunk(s) -- confirmed on a real document to
    # produce 54-77% word overlap that dedup's containment check (tuned
    # for near-total duplicates) didn't reliably catch. Fixed at the
    # source: this element text must never appear in the overview.
    text_splitter = ChunkTextSplitter(max_chunk_tokens=200)
    builder = SectionOverviewChunkBuilder(
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
    )
    parent = _make_section("sec_parent", title="Electrical Installation")
    child = _make_section(
        "sec_child", title="Commissioning & Shutdown", parent_section_id="sec_parent"
    )
    direct_text_element = _make_text_element(
        element_id="el_1",
        text="If all mechanical connections are examined and satisfactory, the drive can be connected.",
    )

    payloads = builder.build(
        document_title="Manual",
        sections=[parent, child],
        section_elements_by_id={"sec_parent": [direct_text_element]},
    )

    assert len(payloads) == 1
    overview_content = payloads[0].content
    assert "Direct subsections (1): Commissioning & Shutdown" in overview_content
    assert "mechanical connections" not in overview_content
    assert "drive can be connected" not in overview_content


def test_build_returns_no_payload_when_no_child_sections() -> None:
    text_splitter = ChunkTextSplitter(max_chunk_tokens=200)
    builder = SectionOverviewChunkBuilder(
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
    )
    lone_section = _make_section("sec_1", title="Introduction")

    payloads = builder.build(
        document_title="Manual",
        sections=[lone_section],
        section_elements_by_id={},
    )

    assert payloads == []

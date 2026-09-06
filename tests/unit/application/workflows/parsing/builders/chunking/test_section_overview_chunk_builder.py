from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.section_overview_chunk_builder import (
    SectionOverviewChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.document import DocumentSection


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
        elements=[],
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
        elements=[],
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
        elements=[],
    )

    assert "Direct subsections (12):" in overview_text
    assert "Safety topic 11" in overview_text


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

from src.application.workflows.question_answering.answer_context.structured_source_builder import (
    StructuredSourceBuilder,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    *,
    chunk_id: str = "chunk_001",
    content: str = "content",
    chunk_type: ChunkType = ChunkType.TECHNICAL_SPECIFICATION,
    section_path: list[str] | None = None,
    retrieval_source: str = "dense",
    section_id: str | None = None,
    statistics: ChunkStatistics | None = None,
    identifier_values: list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source=retrieval_source,
        chunk_type=chunk_type,
        section_id=section_id,
        section_path=(
            ["Certificate", "Particulars"] if section_path is None else section_path
        ),
        source=SourceLocation(page_start=2, page_end=2),
        statistics=statistics,
        identifier_values=identifier_values or [],
        metadata=metadata or {},
    )


def test_build_sources_numbers_sequentially_from_one() -> None:
    builder = StructuredSourceBuilder()

    sources = builder.build_sources(
        [_make_chunk(chunk_id="chunk_a"), _make_chunk(chunk_id="chunk_b")]
    )

    assert [source.source_number for source in sources] == [1, 2]
    assert [source.chunk_id for source in sources] == ["chunk_a", "chunk_b"]


def test_build_sources_maps_retrieval_and_chunk_metadata() -> None:
    builder = StructuredSourceBuilder()
    statistics = ChunkStatistics(char_count=42, token_count_estimate=8)

    sources = builder.build_sources(
        [
            _make_chunk(
                content="Test pressure: 700 bar",
                retrieval_source="sql_keyword",
                section_id="sec_042",
                statistics=statistics,
                identifier_values=["HP-001"],
                metadata={
                    "dedup_collapsed_chunk_ids": "chunk_a,chunk_b",
                    "sql_keyword_source_score": "12.0",
                },
            )
        ]
    )

    source = sources[0]
    assert source.retrieval_source == "sql_keyword"
    assert source.section_id == "sec_042"
    assert source.statistics is statistics
    assert source.identifier_values == ["HP-001"]
    assert source.metadata["sql_keyword_source_score"] == "12.0"
    assert source.collapsed_chunk_ids == ["chunk_a", "chunk_b"]
    assert source.page_start == 2
    assert source.section_path == "Certificate > Particulars"
    assert source.content == "Test pressure: 700 bar"


def test_build_sources_defaults_collapsed_chunk_ids_when_absent() -> None:
    builder = StructuredSourceBuilder()

    sources = builder.build_sources([_make_chunk()])

    assert sources[0].collapsed_chunk_ids == []


def test_build_sources_decodes_table_rows_json() -> None:
    builder = StructuredSourceBuilder()

    sources = builder.build_sources(
        [_make_chunk(metadata={"table_rows_json": '[["a", "b"], ["1", "2"]]'})]
    )

    assert sources[0].table_rows == [["a", "b"], ["1", "2"]]


def test_build_sources_returns_none_for_malformed_table_rows_json() -> None:
    builder = StructuredSourceBuilder()

    sources = builder.build_sources([_make_chunk(metadata={"table_rows_json": "{not json"})])

    assert sources[0].table_rows is None


def test_build_sources_falls_back_to_chunk_type_for_name_without_section_or_citation() -> None:
    builder = StructuredSourceBuilder()

    sources = builder.build_sources(
        [_make_chunk(chunk_type=ChunkType.GENERAL, section_path=[])]
    )

    assert sources[0].chunk_name == "general"
    assert sources[0].section_path is None

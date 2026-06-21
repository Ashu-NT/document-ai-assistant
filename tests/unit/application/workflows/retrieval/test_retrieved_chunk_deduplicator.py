from src.application.workflows.retrieval.deduplication import (
    RetrievedChunkDeduplicator,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


def make_query(
    *,
    query_text: str = "When should the hydraulic filter be replaced?",
    detected_identifiers: list[str] | None = None,
) -> RetrievalQuery:
    return RetrievalQuery(
        query_id="query_001",
        query_text=query_text,
        detected_identifiers=detected_identifiers or [],
        top_k=5,
    )


def make_chunk(
    *,
    chunk_id: str,
    content: str,
    score: float = 0.9,
    document_id: str = "doc_001",
    retrieval_source: str = "dense",
    chunk_type: ChunkType = ChunkType.GENERAL,
    section_id: str | None = "sec_001",
    section_path: list[str] | None = None,
    page: int = 1,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=score,
        retrieval_source=retrieval_source,
        chunk_type=chunk_type,
        section_id=section_id,
        section_path=section_path or ["Section"],
        source=SourceLocation(page_start=page, page_end=page),
        metadata=metadata or {},
    )


def test_exact_same_retrieved_content_collapses() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    first_chunk = make_chunk(
        chunk_id="chunk_001",
        content="Replace hydraulic filter every 1000 hours.",
        score=0.91,
    )
    second_chunk = make_chunk(
        chunk_id="chunk_002",
        content="Replace hydraulic filter every 1000 hours.",
        score=0.89,
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[first_chunk, second_chunk],
    )

    assert len(result.chunks) == 1
    assert result.groups[0].reason == "exact_normalized_content"


def test_atomic_and_context_duplicate_keeps_atomic() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    atomic_chunk = make_chunk(
        chunk_id="chunk_atomic",
        content="Replace hydraulic filter every 1000 hours.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
    )
    context_chunk = make_chunk(
        chunk_id="chunk_context",
        content="Context: Replace hydraulic filter every 1000 hours.",
        score=0.95,
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[context_chunk, atomic_chunk],
    )

    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == "chunk_atomic"


def test_atomic_and_section_overview_duplicate_keeps_atomic() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    atomic_chunk = make_chunk(
        chunk_id="chunk_atomic",
        content="Replace hydraulic filter every 1000 hours.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
    )
    overview_chunk = make_chunk(
        chunk_id="chunk_overview",
        content="Section overview: Replace hydraulic filter every 1000 hours.",
        chunk_type=ChunkType.OVERVIEW,
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[overview_chunk, atomic_chunk],
    )

    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == "chunk_atomic"


def test_two_table_rows_with_shared_headers_do_not_collapse() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    first_row = make_chunk(
        chunk_id="chunk_row_001",
        content="| Part | Description |\n| HP-001 | Filter |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
    )
    second_row = make_chunk(
        chunk_id="chunk_row_002",
        content="| Part | Description |\n| HP-002 | Seal |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[first_row, second_row],
    )

    assert len(result.chunks) == 2


def test_chunks_from_different_documents_do_not_collapse() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    first_chunk = make_chunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content="Replace hydraulic filter every 1000 hours.",
    )
    second_chunk = make_chunk(
        chunk_id="chunk_002",
        document_id="doc_002",
        content="Replace hydraulic filter every 1000 hours.",
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[first_chunk, second_chunk],
    )

    assert len(result.chunks) == 2


def test_different_structured_item_labels_do_not_collapse() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    broader_chunk = make_chunk(
        chunk_id="chunk_broader",
        content=(
            "15 - COMBINED\n"
            "ANCHOR / MASTHEAD LANTERN WHITE / WHITE\n"
            "3540.6000\n"
            "16 - COMBINED\n"
            "ANCHOR/ TOWING LANTERN WHITE / YELLOW\n"
            "3540.7000"
        ),
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Lamp labels"],
    )
    narrower_chunk = make_chunk(
        chunk_id="chunk_narrower",
        content=(
            "ANCHOR / MASTHEAD LANTERN WHITE / WHITE\n"
            "3540.6000\n"
            "16 - COMBINED\n"
            "ANCHOR/ TOWING LANTERN WHITE / YELLOW\n"
            "3540.7000"
        ),
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Lamp labels"],
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[broader_chunk, narrower_chunk],
    )

    assert len(result.chunks) == 2


def test_exact_identifier_match_wins_representative_selection() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query(
        query_text="Where is HP-001 used?",
        detected_identifiers=["HP-001"],
    )
    generic_chunk = make_chunk(
        chunk_id="chunk_generic",
        content="Replace hydraulic filter every 1000 hours.",
        score=0.9,
        metadata={"dense_source_score": "0.9"},
    )
    identifier_chunk = make_chunk(
        chunk_id="chunk_identifier",
        content="Replace hydraulic filter HP-001 every 1000 hours.",
        score=0.9,
        metadata={"dense_source_score": "0.9"},
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[generic_chunk, identifier_chunk],
    )

    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == "chunk_identifier"
    assert (
        result.groups[0].representative_selection_reason
        == "exact_query_identifier_match"
    )


def test_final_candidate_list_is_diverse_after_deduplication() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    chunks = [
        make_chunk(
            chunk_id="chunk_atomic",
            content="Replace hydraulic filter every 1000 hours.",
            score=0.95,
        ),
        make_chunk(
            chunk_id="chunk_context",
            content="Context: Replace hydraulic filter every 1000 hours.",
            score=0.96,
        ),
        make_chunk(
            chunk_id="chunk_overview",
            content="Section overview: Replace hydraulic filter every 1000 hours.",
            score=0.94,
            chunk_type=ChunkType.OVERVIEW,
        ),
        make_chunk(
            chunk_id="chunk_unique",
            content="Inspect the filter housing for leaks before restart.",
            score=0.93,
            chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
            section_id="sec_002",
            section_path=["Procedure"],
            page=2,
        ),
    ]

    result = deduplicator.deduplicate(
        query=query,
        chunks=chunks,
    )

    assert [chunk.chunk_id for chunk in result.chunks[:2]] == [
        "chunk_atomic",
        "chunk_unique",
    ]


def test_diagnostics_include_collapsed_chunk_ids_and_reason() -> None:
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    atomic_chunk = make_chunk(
        chunk_id="chunk_atomic",
        content="Replace hydraulic filter every 1000 hours.",
    )
    context_chunk = make_chunk(
        chunk_id="chunk_context",
        content="Context: Replace hydraulic filter every 1000 hours.",
    )

    result = deduplicator.deduplicate(
        query=query,
        chunks=[context_chunk, atomic_chunk],
    )

    representative = result.chunks[0]

    assert representative.metadata["dedup_collapsed_chunk_ids"] == "chunk_context"
    assert representative.metadata["dedup_reason"] == "context_companion_duplicate"
    assert representative.metadata["dedup_group_size"] == "2"

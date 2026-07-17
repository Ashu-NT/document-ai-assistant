from types import SimpleNamespace

from src.application.workflows.question_answering.evidence.final_evidence_preparer import (
    FinalEvidencePreparer,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class _IdentityHydrator:
    def hydrate(self, *, chunks, graphs_by_document_id):
        return list(chunks)


class _IdentityDeduplicator:
    def deduplicate(self, *, query, chunks):
        return SimpleNamespace(chunks=list(chunks))


def _make_query(
    *,
    query_text: str,
    detected_intent: str,
    chunk_types: list[ChunkType],
) -> RetrievalQuery:
    return RetrievalQuery(
        query_id="rq_001",
        query_text=query_text,
        detected_intent=detected_intent,
        chunk_types=chunk_types,
        analyzed=True,
    )


def _make_chunk(
    *,
    chunk_id: str,
    chunk_type: ChunkType,
    content: str,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="hybrid",
        chunk_type=chunk_type,
        source=SourceLocation(page_start=1, page_end=1),
        metadata=metadata or {},
    )


def _make_preparer() -> FinalEvidencePreparer:
    return FinalEvidencePreparer(
        table_evidence_hydrator=_IdentityHydrator(),
        deduplicator=_IdentityDeduplicator(),
    )


def test_prepare_prunes_low_value_overview_and_context_companions_for_table_queries() -> None:
    query = _make_query(
        query_text="Show the spare parts table.",
        detected_intent="table",
        chunk_types=[ChunkType.SPARE_PARTS_TABLE],
    )
    chunks = [
        _make_chunk(
            chunk_id="chunk_table",
            chunk_type=ChunkType.SPARE_PARTS_TABLE,
            content="| Pos | Description |\n| 10 | Filter |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_001",
                "hydrated_table_ids": "table_001",
            },
        ),
        _make_chunk(
            chunk_id="chunk_overview",
            chunk_type=ChunkType.OVERVIEW,
            content="Section overview: spare parts are listed below.",
        ),
        _make_chunk(
            chunk_id="chunk_context",
            chunk_type=ChunkType.GENERAL,
            content="Context: original parts should be used.",
        ),
    ]

    prepared = _make_preparer().prepare(query=query, chunks=chunks)

    assert [chunk.chunk_id for chunk in prepared] == ["chunk_table"]


def test_prepare_keeps_specific_non_companion_chunks_with_table_evidence() -> None:
    query = _make_query(
        query_text="What are the maintenance intervals schedule table?",
        detected_intent="maintenance",
        chunk_types=[ChunkType.MAINTENANCE_INTERVAL],
    )
    chunks = [
        _make_chunk(
            chunk_id="chunk_table",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            content="| Task | Monthly |\n| Inspect filter | x |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_maintenance",
                "hydrated_table_ids": "table_maintenance",
            },
        ),
        _make_chunk(
            chunk_id="chunk_procedure",
            chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
            content="Isolate pressure before servicing the unit.",
        ),
        _make_chunk(
            chunk_id="chunk_overview",
            chunk_type=ChunkType.OVERVIEW,
            content="Section overview: maintenance intervals and procedures.",
        ),
    ]

    prepared = _make_preparer().prepare(query=query, chunks=chunks)

    assert [chunk.chunk_id for chunk in prepared] == [
        "chunk_table",
        "chunk_procedure",
    ]


def test_prepare_keeps_general_chunk_without_scaffolding_prefix_for_table_queries() -> None:
    # Regression guard for a real bug: GENERAL/OVERVIEW chunk_type alone used
    # to be treated as low-value and pruned unconditionally, even for organic
    # content that simply didn't hit a specific category's keyword threshold
    # (a caveat, a safety note) -- as opposed to auto-generated scaffolding
    # companions, which are only ever recognizable by their literal "Context:"/
    # "Section overview:" prefix (picture_fragment_builder.py/
    # section_overview_chunk_builder.py). Only the latter should be pruned.
    query = _make_query(
        query_text="Show the spare parts table.",
        detected_intent="table",
        chunk_types=[ChunkType.SPARE_PARTS_TABLE],
    )
    chunks = [
        _make_chunk(
            chunk_id="chunk_table",
            chunk_type=ChunkType.SPARE_PARTS_TABLE,
            content="| Pos | Description |\n| 10 | Filter |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_001",
                "hydrated_table_ids": "table_001",
            },
        ),
        _make_chunk(
            chunk_id="chunk_caveat",
            chunk_type=ChunkType.GENERAL,
            content="Use only genuine replacement parts to preserve the warranty.",
        ),
        _make_chunk(
            chunk_id="chunk_context_companion",
            chunk_type=ChunkType.GENERAL,
            content="Context: original parts should be used.",
        ),
    ]

    prepared = _make_preparer().prepare(query=query, chunks=chunks)

    assert [chunk.chunk_id for chunk in prepared] == [
        "chunk_table",
        "chunk_caveat",
    ]


def test_prepare_rejects_mismatched_table_family_for_maintenance_focused_query() -> None:
    # Regression guard for the other half of weakness #5: a maintenance-
    # interval-focused query should not carry an unrelated spare-parts table
    # into answer generation just because it also counts as "direct table
    # evidence" -- it's a real table, just not the one this query is about.
    query = _make_query(
        query_text="What are the maintenance intervals for this pump?",
        detected_intent="maintenance",
        chunk_types=[ChunkType.MAINTENANCE_INTERVAL],
    )
    chunks = [
        _make_chunk(
            chunk_id="chunk_maintenance_table",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            content="| Task | Interval |\n| Inspect filter | Monthly |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_maintenance",
            },
        ),
        _make_chunk(
            chunk_id="chunk_spare_parts_table",
            chunk_type=ChunkType.SPARE_PARTS_TABLE,
            content="| Pos | Description |\n| 10 | Filter |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_spares",
            },
        ),
    ]

    prepared = _make_preparer().prepare(query=query, chunks=chunks)

    assert [chunk.chunk_id for chunk in prepared] == ["chunk_maintenance_table"]


def test_prepare_keeps_mismatched_table_family_when_it_is_the_only_table_evidence() -> None:
    # The safety net: never discard the ONLY table evidence available just
    # because it isn't the exact expected family for the detected intent.
    query = _make_query(
        query_text="What are the maintenance intervals for this pump?",
        detected_intent="maintenance",
        chunk_types=[ChunkType.MAINTENANCE_INTERVAL],
    )
    chunks = [
        _make_chunk(
            chunk_id="chunk_spare_parts_table",
            chunk_type=ChunkType.SPARE_PARTS_TABLE,
            content="| Pos | Description |\n| 10 | Filter |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_spares",
            },
        ),
        _make_chunk(
            chunk_id="chunk_overview",
            chunk_type=ChunkType.OVERVIEW,
            content="Section overview: pump maintenance.",
        ),
    ]

    prepared = _make_preparer().prepare(query=query, chunks=chunks)

    assert [chunk.chunk_id for chunk in prepared] == ["chunk_spare_parts_table"]


def test_prepare_does_not_prune_non_table_focused_queries() -> None:
    query = _make_query(
        query_text="What is the purpose of the pump?",
        detected_intent="overview",
        chunk_types=[ChunkType.OVERVIEW],
    )
    chunks = [
        _make_chunk(
            chunk_id="chunk_table",
            chunk_type=ChunkType.SPARE_PARTS_TABLE,
            content="| Pos | Description |\n| 10 | Filter |",
            metadata={
                "table_evidence_hydrated": "true",
                "logical_table_family_id": "table_family_001",
            },
        ),
        _make_chunk(
            chunk_id="chunk_overview",
            chunk_type=ChunkType.OVERVIEW,
            content="Section overview: this pump transfers slurry.",
        ),
    ]

    prepared = _make_preparer().prepare(query=query, chunks=chunks)

    assert [chunk.chunk_id for chunk in prepared] == [
        "chunk_table",
        "chunk_overview",
    ]

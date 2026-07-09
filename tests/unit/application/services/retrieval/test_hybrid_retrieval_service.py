import pytest

from src.application.services.retrieval import HybridRetrievalService
from src.application.validation.retrieval import RetrievalQueryValidator
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval import RetrievalResult
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator


def make_service(
    *,
    keyword_index,
    vector_store=None,
    reranker=None,
) -> HybridRetrievalService:
    return HybridRetrievalService(
        keyword_index=keyword_index,
        vector_store=vector_store,
        reranker=reranker,
        id_generator=IdGenerator(),
        retrieval_query_validator=RetrievalQueryValidator(),
    )


class FakeKeywordIndex:
    def __init__(self, chunks) -> None:
        self.chunks = chunks
        self.search_calls = 0
        self.queries = []

    def index_chunks(self, chunks) -> None:
        pass

    def search(self, query):
        self.search_calls += 1
        self.queries.append(query)
        return self.chunks


class FakeVectorStore:
    def __init__(self, chunks) -> None:
        self.chunks = chunks
        self.search_calls = 0
        self.queries = []

    def save_chunk_vectors(self, chunks) -> None:
        pass

    def search(self, query):
        self.search_calls += 1
        self.queries.append(query)
        return self.chunks

    def delete_document_vectors(self, document_id: str) -> None:
        pass


class FakeReranker:
    def rerank(self, query, chunks):
        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)


def clone_chunk(sample_retrieved_chunk, *, chunk_id: str, score: float):
    return sample_retrieved_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_retrieved_chunk.document_id,
        content=sample_retrieved_chunk.content,
        score=score,
        retrieval_source=sample_retrieved_chunk.retrieval_source,
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )


def test_hybrid_retrieval_uses_keyword_only(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    service = make_service(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert isinstance(result, RetrievalResult)
    assert result.result_id.startswith("retrieval_")
    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == sample_retrieved_chunk.chunk_id
    assert result.total_candidates == 1


def test_hybrid_retrieval_deduplicates_by_chunk_id(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    duplicate_chunk = clone_chunk(
        sample_retrieved_chunk,
        chunk_id=sample_retrieved_chunk.chunk_id,
        score=0.95,
    )

    service = make_service(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
        vector_store=FakeVectorStore([duplicate_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert len(result.chunks) == 1
    assert result.total_candidates == 1


def test_hybrid_retrieval_uses_reranker(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    low_score_chunk = clone_chunk(
        sample_retrieved_chunk,
        chunk_id="chunk_low",
        score=0.2,
    )

    high_score_chunk = clone_chunk(
        sample_retrieved_chunk,
        chunk_id="chunk_high",
        score=0.99,
    )

    service = make_service(
        keyword_index=FakeKeywordIndex([low_score_chunk]),
        vector_store=FakeVectorStore([high_score_chunk]),
        reranker=FakeReranker(),
    )

    result = service.retrieve(sample_retrieval_query)

    assert result.chunks[0].chunk_id == "chunk_high"


def test_hybrid_retrieval_respects_top_k(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    sample_retrieval_query.top_k = 1

    second_chunk = clone_chunk(
        sample_retrieved_chunk,
        chunk_id="chunk_002",
        score=0.8,
    )

    service = make_service(
        keyword_index=FakeKeywordIndex(
            [sample_retrieved_chunk, second_chunk]
        ),
    )

    result = service.retrieve(sample_retrieval_query)

    assert len(result.chunks) == 1
    assert result.total_candidates == 2


def test_hybrid_retrieval_rejects_invalid_query(
    sample_retrieval_query,
) -> None:
    keyword_index = FakeKeywordIndex([])
    service = make_service(keyword_index=keyword_index)
    sample_retrieval_query.query_text = "   "

    with pytest.raises(SchemaValidationError):
        service.retrieve(sample_retrieval_query)

    assert keyword_index.search_calls == 0


def test_hybrid_retrieval_skips_dense_search_when_query_disables_it(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    sample_retrieval_query.use_dense = False
    keyword_index = FakeKeywordIndex([sample_retrieved_chunk])
    vector_store = FakeVectorStore([sample_retrieved_chunk])
    service = make_service(
        keyword_index=keyword_index,
        vector_store=vector_store,
    )

    result = service.retrieve(sample_retrieval_query)

    assert len(result.chunks) == 1
    assert keyword_index.search_calls == 1
    assert vector_store.search_calls == 0
    assert result.used_dense is False


def test_hybrid_retrieval_tracks_combined_sources_for_duplicate_hits(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    duplicate_chunk = clone_chunk(
        sample_retrieved_chunk,
        chunk_id=sample_retrieved_chunk.chunk_id,
        score=0.88,
    )
    service = make_service(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
        vector_store=FakeVectorStore([duplicate_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert result.chunks[0].retrieval_source == "hybrid"
    assert result.chunks[0].metadata["retrieval_sources"] == "dense,sql_keyword"


def test_hybrid_retrieval_preserves_chunk_statistics_during_fusion(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    sample_retrieved_chunk.statistics = ChunkStatistics(
        char_count=91,
        token_count_estimate=13,
    )
    service = make_service(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert result.chunks[0].statistics is not None
    assert result.chunks[0].statistics.char_count == 91
    assert result.chunks[0].statistics.token_count_estimate == 13


def test_hybrid_retrieval_passes_document_scope_to_sources_and_discards_leaks(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    sample_retrieval_query.document_id = sample_retrieved_chunk.document_id
    leaked_keyword_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_keyword_other_doc",
        document_id="doc_other",
        content=sample_retrieved_chunk.content,
        score=0.95,
        retrieval_source="sql_keyword",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
        statistics=sample_retrieved_chunk.statistics,
        identifier_values=list(sample_retrieved_chunk.identifier_values),
    )
    leaked_dense_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_dense_other_doc",
        document_id="doc_other",
        content=sample_retrieved_chunk.content,
        score=0.94,
        retrieval_source="dense",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    keyword_index = FakeKeywordIndex([sample_retrieved_chunk, leaked_keyword_chunk])
    vector_store = FakeVectorStore([sample_retrieved_chunk, leaked_dense_chunk])
    service = make_service(
        keyword_index=keyword_index,
        vector_store=vector_store,
    )

    result = service.retrieve(sample_retrieval_query)

    assert keyword_index.queries[0].document_id == sample_retrieval_query.document_id
    assert vector_store.queries[0].document_id == sample_retrieval_query.document_id
    assert all(
        chunk.document_id == sample_retrieval_query.document_id
        for chunk in result.chunks
    )


def test_retrieve_with_additional_candidates_adds_a_structured_source(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    structured_chunk = clone_chunk(
        sample_retrieved_chunk,
        chunk_id="chunk_structured_only",
        score=1.0,
    )
    structured_chunk.metadata["structured_match_count"] = "1"
    service = make_service(keyword_index=FakeKeywordIndex([]))

    result = service.retrieve_with_additional_candidates(
        sample_retrieval_query,
        additional_candidates=[structured_chunk],
    )

    assert len(result.chunks) == 1
    assert result.chunks[0].retrieval_source == "structured"
    assert result.chunks[0].metadata["structured_match_count"] == "1"


def test_structured_match_metadata_survives_fusion_when_also_found_by_keyword(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    """Structured is always collected last (see _collect_source_results), so
    a chunk also found by sql_keyword/dense gets cloned from THAT source
    first -- without explicit propagation in the merge branch, the
    structured resolver's match metadata would be silently dropped for any
    chunk that isn't structured-only."""
    structured_duplicate = clone_chunk(
        sample_retrieved_chunk,
        chunk_id=sample_retrieved_chunk.chunk_id,
        score=1.95,
    )
    structured_duplicate.metadata["structured_match_count"] = "2"
    structured_duplicate.metadata["structured_match_reasons"] = "identifier:part_number"
    service = make_service(keyword_index=FakeKeywordIndex([sample_retrieved_chunk]))

    result = service.retrieve_with_additional_candidates(
        sample_retrieval_query,
        additional_candidates=[structured_duplicate],
    )

    assert result.chunks[0].retrieval_source == "hybrid"
    assert result.chunks[0].metadata["structured_match_count"] == "2"
    assert (
        result.chunks[0].metadata["structured_match_reasons"]
        == "identifier:part_number"
    )

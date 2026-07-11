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

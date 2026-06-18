from src.application.services.retrieval import HybridRetrievalService
from src.domain.retrieval import RetrievalResult


class FakeKeywordIndex:
    def __init__(self, chunks) -> None:
        self.chunks = chunks

    def index_chunks(self, chunks) -> None:
        pass

    def search(self, query):
        return self.chunks


class FakeVectorStore:
    def __init__(self, chunks) -> None:
        self.chunks = chunks

    def save_chunk_vectors(self, chunks) -> None:
        pass

    def search(self, query):
        return self.chunks

    def delete_document_vectors(self, document_id: str) -> None:
        pass


class FakeReranker:
    def rerank(self, query, chunks):
        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)


def test_hybrid_retrieval_uses_keyword_only(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    service = HybridRetrievalService(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert isinstance(result, RetrievalResult)
    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == sample_retrieved_chunk.chunk_id


def test_hybrid_retrieval_combines_keyword_and_vector_results(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    vector_chunk = sample_retrieved_chunk
    vector_chunk.chunk_id = "chunk_vector_001"
    vector_chunk.score = 0.95

    service = HybridRetrievalService(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
        vector_store=FakeVectorStore([vector_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert len(result.chunks) == 2


def test_hybrid_retrieval_deduplicates_by_chunk_id(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    service = HybridRetrievalService(
        keyword_index=FakeKeywordIndex([sample_retrieved_chunk]),
        vector_store=FakeVectorStore([sample_retrieved_chunk]),
    )

    result = service.retrieve(sample_retrieval_query)

    assert len(result.chunks) == 1


def test_hybrid_retrieval_uses_reranker(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    low_score_chunk = sample_retrieved_chunk
    low_score_chunk.score = 0.2

    high_score_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_high",
        document_id=sample_retrieved_chunk.document_id,
        content="high relevance chunk",
        score=0.99,
        retrieval_source="vector",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )

    service = HybridRetrievalService(
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

    second_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_002",
        document_id=sample_retrieved_chunk.document_id,
        content="second chunk",
        score=0.8,
        retrieval_source="keyword",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )

    service = HybridRetrievalService(
        keyword_index=FakeKeywordIndex(
            [sample_retrieved_chunk, second_chunk]
        ),
    )

    result = service.retrieve(sample_retrieval_query)

    assert len(result.chunks) == 1
    assert result.total_candidates == 1
from src.application.services.retrieval import HybridRetrievalService
from src.domain.retrieval import RetrievalResult
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
    )

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
import pytest

from src.domain.common import ChunkType, DocumentType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval import Citation, RetrievalQuery, RetrievalResult, RetrievedChunk
from src.domain.workflow import IngestionRun


@pytest.fixture
def sample_retrieval_query() -> RetrievalQuery:
    return RetrievalQuery(
        query_id="query_001",
        query_text="When should the hydraulic filter be replaced?",
        document_types=[DocumentType.MANUAL],
        chunk_types=[ChunkType.MAINTENANCE_INTERVAL],
        top_k=5,
    )


@pytest.fixture
def sample_citation(
    document_id: str,
    section_id: str,
    chunk_id: str,
    sample_source_location: SourceLocation,
) -> Citation:
    return Citation(
        citation_id="citation_001",
        document_id=document_id,
        chunk_id=chunk_id,
        section_id=section_id,
        document_name="pump_manual.pdf",
        section_title="Maintenance Schedule",
        source=sample_source_location,
    )


@pytest.fixture
def sample_retrieved_chunk(
    document_id: str,
    section_id: str,
    chunk_id: str,
    sample_citation: Citation,
    sample_source_location: SourceLocation,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content="Replace hydraulic filter every 1000 operating hours.",
        score=0.91,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_id=section_id,
        section_path=["Maintenance Schedule"],
        source=sample_source_location,
        citation=sample_citation,
    )


@pytest.fixture
def sample_retrieval_result(
    sample_retrieval_query: RetrievalQuery,
    sample_retrieved_chunk: RetrievedChunk,
    sample_citation: Citation,
) -> RetrievalResult:
    return RetrievalResult(
        result_id="retrieval_result_001",
        query=sample_retrieval_query,
        chunks=[sample_retrieved_chunk],
        citations=[sample_citation],
        used_dense=True,
        total_candidates=1,
    )


@pytest.fixture
def sample_ingestion_run() -> IngestionRun:
    return IngestionRun(
        run_id="run_001",
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
    )

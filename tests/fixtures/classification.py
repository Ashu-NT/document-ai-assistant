import pytest

from src.domain.classification import (
    ChunkClassification,
    ClassificationResult,
    DocumentClassification,
)
from src.domain.common import ChunkType, DocumentType, ModelProcessingMetadata


@pytest.fixture
def sample_document_classification(document_id: str) -> DocumentClassification:
    result = ClassificationResult(
        classification_id="classification_doc_001",
        document_id=document_id,
        predicted_label=DocumentType.MANUAL.value,
        confidence_score=0.9,
        rationale="Document contains maintenance procedures.",
        evidence=["maintenance", "procedure", "safety"],
        processing_metadata=ModelProcessingMetadata(
            model_name="qwen3:8b",
            model_type="classification",
            prompt_version="v1",
            confidence=0.9,
        ),
    )
    return DocumentClassification(
        document_id=document_id,
        document_type=DocumentType.MANUAL,
        result=result,
    )


@pytest.fixture
def sample_chunk_classification(
    document_id: str,
    chunk_id: str,
) -> ChunkClassification:
    result = ClassificationResult(
        classification_id="classification_chunk_001",
        document_id=document_id,
        predicted_label=ChunkType.MAINTENANCE_INTERVAL.value,
        confidence_score=0.85,
        rationale="Chunk describes a recurring maintenance interval.",
        evidence=["every 1000 operating hours"],
        processing_metadata=ModelProcessingMetadata(
            model_name="qwen3:8b",
            model_type="chunk_classification",
            prompt_version="v1",
            confidence=0.85,
        ),
    )
    return ChunkClassification(
        chunk_id=chunk_id,
        document_id=document_id,
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        result=result,
    )

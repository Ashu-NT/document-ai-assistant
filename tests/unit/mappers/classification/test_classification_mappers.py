from src.domain.classification import (
    ChunkClassification,
    ClassificationResult,
    DocumentClassification,
)
from src.domain.common import ChunkType, DocumentType, ModelProcessingMetadata
from src.infrastructure.db.mappers import (
    ChunkClassificationMapper,
    ClassificationResultMapper,
    DocumentClassificationMapper,
)


def test_classification_result_common_fields() -> None:
    result = ClassificationResult(
        classification_id="class_001",
        document_id="doc_001",
        predicted_label="manual",
        confidence_score=0.91,
        rationale="Contains maintenance procedures.",
        evidence=["maintenance", "safety"],
        processing_metadata=ModelProcessingMetadata(
            model_name="qwen3:8b",
            model_type="classification",
            prompt_version="v1",
            confidence=0.91,
        ),
    )

    fields = ClassificationResultMapper.extract_common_fields(result)

    assert fields["predicted_label"] == "manual"
    assert fields["confidence_score"] == 0.91
    assert fields["model_name"] == "qwen3:8b"


def test_document_classification_mapper_round_trip() -> None:
    result = ClassificationResult(
        classification_id="class_doc_001",
        document_id="doc_001",
        predicted_label="manual",
        confidence_score=0.9,
        evidence=["procedure"],
    )

    classification = DocumentClassification(
        document_id="doc_001",
        document_type=DocumentType.MANUAL,
        result=result,
    )

    orm = DocumentClassificationMapper.to_orm(classification)
    domain = DocumentClassificationMapper.to_domain(orm)

    assert domain.document_id == classification.document_id
    assert domain.document_type == DocumentType.MANUAL
    assert domain.result is not None
    assert domain.result.predicted_label == "manual"


def test_chunk_classification_mapper_round_trip() -> None:
    result = ClassificationResult(
        classification_id="class_chunk_001",
        document_id="doc_001",
        predicted_label="maintenance_interval",
        confidence_score=0.82,
    )

    classification = ChunkClassification(
        chunk_id="chunk_001",
        document_id="doc_001",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        result=result,
    )

    orm = ChunkClassificationMapper.to_orm(classification)
    domain = ChunkClassificationMapper.to_domain(orm)

    assert domain.chunk_id == "chunk_001"
    assert domain.document_id == "doc_001"
    assert domain.chunk_type == ChunkType.MAINTENANCE_INTERVAL
    assert domain.result is not None
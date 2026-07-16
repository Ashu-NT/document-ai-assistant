import pytest

from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType, ModelProcessingMetadata


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

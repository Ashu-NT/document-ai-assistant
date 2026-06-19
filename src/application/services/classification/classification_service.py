from src.application.contracts.classification import ClassificationRepository
from src.application.validation.classification import (
    ChunkClassificationValidator,
    DocumentClassificationValidator,
)
from src.domain.classification import ChunkClassification, DocumentClassification
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


class ClassificationService:
    def __init__(
        self,
        classification_repository: ClassificationRepository,
        document_classification_validator: DocumentClassificationValidator,
        chunk_classification_validator: ChunkClassificationValidator,
    ) -> None:
        self.classification_repository = classification_repository
        self.document_classification_validator = document_classification_validator
        self.chunk_classification_validator = chunk_classification_validator

    @tracked_action(
        action="classification.document_saved",
        entity_type="document",
        activity=True,
        audit=True,
        event=True,
    )
    def save_document_classification(
        self,
        classification: DocumentClassification,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        validation = self.document_classification_validator.validate(classification)
        validation.raise_if_invalid()

        self.classification_repository.save_document_classification(classification)

        return ActionResult(
            entity_type="document",
            entity_id=classification.document_id,
            message="Document classification saved.",
            payload={
                "document_id": classification.document_id,
                "document_type": classification.document_type.value,
                "classification_id": classification.result.classification_id
                if classification.result
                else None,
                "confidence_score": classification.result.confidence_score
                if classification.result
                else None,
            },
        )

    @tracked_action(
        action="classification.chunk_saved",
        entity_type="chunk",
        activity=True,
        audit=False,
        event=True,
    )
    def save_chunk_classification(
        self,
        classification: ChunkClassification,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        validation = self.chunk_classification_validator.validate(classification)
        validation.raise_if_invalid()

        self.classification_repository.save_chunk_classification(classification)

        return ActionResult(
            entity_type="chunk",
            entity_id=classification.chunk_id,
            message="Chunk classification saved.",
            payload={
                "chunk_id": classification.chunk_id,
                "document_id": classification.document_id,
                "chunk_type": classification.chunk_type.value,
                "classification_id": classification.result.classification_id
                if classification.result
                else None,
                "confidence_score": classification.result.confidence_score
                if classification.result
                else None,
            },
        )

    def get_document_classification(
        self,
        document_id: str,
    ) -> DocumentClassification | None:
        return self.classification_repository.get_document_classification(document_id)

    def get_chunk_classification(
        self,
        chunk_id: str,
    ) -> ChunkClassification | None:
        return self.classification_repository.get_chunk_classification(chunk_id)

    def list_chunk_classifications(
        self,
        document_id: str,
    ) -> list[ChunkClassification]:
        return self.classification_repository.list_chunk_classifications(document_id)

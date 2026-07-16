from src.application.contracts.classification import ClassificationRepository
from src.application.validation.classification import DocumentClassificationValidator
from src.domain.classification import DocumentClassification
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


class ClassificationService:
    def __init__(
        self,
        classification_repository: ClassificationRepository,
        document_classification_validator: DocumentClassificationValidator,
    ) -> None:
        self.classification_repository = classification_repository
        self.document_classification_validator = document_classification_validator

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

    def get_document_classification(
        self,
        document_id: str,
    ) -> DocumentClassification | None:
        return self.classification_repository.get_document_classification(document_id)

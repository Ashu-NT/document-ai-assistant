# document_classification_validator.py
from src.application.validation.common import ValidationResult, Validator
from src.domain.classification import DocumentClassification


class DocumentClassificationValidator(Validator[DocumentClassification]):
    def validate(self, value: DocumentClassification) -> ValidationResult:
        result = ValidationResult()

        if not value.document_id:
            result.add_issue("document_id", "Document id is required.", "classification.document_id.required")

        if value.result is None:
            result.add_issue("result", "Classification result is required.", "classification.result.required")
            return result

        if not value.result.classification_id:
            result.add_issue("classification_id", "Classification id is required.", "classification.id.required")

        if value.result.confidence_score < 0 or value.result.confidence_score > 1:
            result.add_issue("confidence_score", "Confidence must be between 0 and 1.", "classification.confidence.invalid")

        return result
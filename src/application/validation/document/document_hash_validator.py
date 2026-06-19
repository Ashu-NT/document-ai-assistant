from src.application.validation.common import ValidationResult, Validator
from src.domain.document import Document


class DocumentHashValidator(Validator[Document]):
    def validate(self, value: Document) -> ValidationResult:
        result = ValidationResult()

        if not value.hashes.file_hash:
            result.add_issue(
                field="file_hash",
                message="Document file hash is required.",
                code="document.file_hash.required",
            )

        if not value.hashes.content_hash:
            result.add_issue(
                field="content_hash",
                message="Document content hash is required.",
                code="document.content_hash.required",
            )

        return result
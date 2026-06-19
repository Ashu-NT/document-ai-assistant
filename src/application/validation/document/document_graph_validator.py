from src.application.validation.common import ValidationResult, Validator
from src.domain.document import DocumentGraph


class DocumentGraphValidator(Validator[DocumentGraph]):
    def validate(self, value: DocumentGraph) -> ValidationResult:
        result = ValidationResult()

        document_id = value.document.document_id

        for section in value.sections.values():
            if section.document_id != document_id:
                result.add_issue(
                    field="sections",
                    message="Section document_id does not match graph document_id.",
                    code="document_graph.section.document_mismatch",
                )

        for chunk in value.chunks.values():
            if chunk.document_id != document_id:
                result.add_issue(
                    field="chunks",
                    message="Chunk document_id does not match graph document_id.",
                    code="document_graph.chunk.document_mismatch",
                )

        return result
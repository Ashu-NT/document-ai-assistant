from src.application.validation.common import ValidationResult, Validator
from src.domain.extraction import ExtractionResult


class ExtractionResultValidator(Validator[ExtractionResult]):
    def validate(self, value: ExtractionResult) -> ValidationResult:
        result = ValidationResult()

        if not value.extraction_id:
            result.add_issue("extraction_id", "Extraction id is required.", "extraction.id.required")

        if not value.document_id:
            result.add_issue("document_id", "Document id is required.", "extraction.document_id.required")

        if value.confidence_score < 0 or value.confidence_score > 1:
            result.add_issue("confidence_score", "Confidence must be between 0 and 1.", "extraction.confidence.invalid")

        for task in value.maintenance_tasks:
            if task.document_id != value.document_id:
                result.add_issue("maintenance_tasks", "Task document_id does not match extraction document_id.", "extraction.task.document_mismatch")

        for part in value.spare_parts:
            if part.document_id != value.document_id:
                result.add_issue("spare_parts", "Spare part document_id does not match extraction document_id.", "extraction.spare_part.document_mismatch")

        for equipment in value.equipment:
            if equipment.document_id != value.document_id:
                result.add_issue("equipment", "Equipment document_id does not match extraction document_id.", "extraction.equipment.document_mismatch")

        for manufacturer in value.manufacturers:
            if manufacturer.document_id != value.document_id:
                result.add_issue("manufacturers", "Manufacturer document_id does not match extraction document_id.", "extraction.manufacturer.document_mismatch")

        return result
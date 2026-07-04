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

        for supplier in value.suppliers:
            if supplier.document_id != value.document_id:
                result.add_issue("suppliers", "Supplier document_id does not match extraction document_id.", "extraction.supplier.document_mismatch")

        for procedure in value.procedures:
            if procedure.document_id != value.document_id:
                result.add_issue("procedures", "Procedure document_id does not match extraction document_id.", "extraction.procedure.document_mismatch")

        for specification in value.specifications:
            if specification.document_id != value.document_id:
                result.add_issue("specifications", "Specification document_id does not match extraction document_id.", "extraction.specification.document_mismatch")

        for safety_warning in value.safety_warnings:
            if safety_warning.document_id != value.document_id:
                result.add_issue("safety_warnings", "Safety warning document_id does not match extraction document_id.", "extraction.safety_warning.document_mismatch")

        for maintenance_interval in value.maintenance_intervals:
            if maintenance_interval.document_id != value.document_id:
                result.add_issue("maintenance_intervals", "Maintenance interval document_id does not match extraction document_id.", "extraction.maintenance_interval.document_mismatch")

        for troubleshooting_entry in value.troubleshooting_entries:
            if troubleshooting_entry.document_id != value.document_id:
                result.add_issue("troubleshooting_entries", "Troubleshooting entry document_id does not match extraction document_id.", "extraction.troubleshooting_entry.document_mismatch")

        return result
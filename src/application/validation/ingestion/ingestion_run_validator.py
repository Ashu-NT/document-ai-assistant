from src.application.validation.common import ValidationResult, Validator
from src.domain.workflow import IngestionRun


class IngestionRunValidator(Validator[IngestionRun]):
    def validate(self, value: IngestionRun) -> ValidationResult:
        result = ValidationResult()

        if not value.run_id:
            result.add_issue(
                "run_id",
                "Ingestion run id is required.",
                "ingestion.run_id.required",
            )

        if not value.file_path:
            result.add_issue(
                "file_path",
                "Ingestion file path is required.",
                "ingestion.file_path.required",
            )

        if not value.file_hash:
            result.add_issue(
                "file_hash",
                "Ingestion file hash is required.",
                "ingestion.file_hash.required",
            )

        return result
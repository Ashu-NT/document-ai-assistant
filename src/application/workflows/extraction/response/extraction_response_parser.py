import re
from typing import Any

from pydantic import ValidationError

from src.application.validation.common import ValidationResult
from src.application.workflows.extraction.response.extraction_response_sanitizer import (
    ExtractionResponseSanitizer,
)
from src.application.workflows.extraction.response.extraction_response_repairer import (
    ExtractionResponseRepairer,
)
from src.application.workflows.extraction.response.schemas.extraction_response_payload import (
    ExtractionResponsePayload,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)

THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class ExtractionResponseParser:
    def __init__(
        self,
        sanitizer: ExtractionResponseSanitizer | None = None,
        repairer: ExtractionResponseRepairer | None = None,
    ) -> None:
        self.sanitizer = sanitizer or ExtractionResponseSanitizer()
        self.repairer = repairer or ExtractionResponseRepairer()

    def parse(self, response: str) -> dict[str, Any]:
        normalized = strip_code_fences_if_wrapped(
            THINK_BLOCK_PATTERN.sub("", response or "").strip()
        )

        try:
            validated = self._validate_json_payload(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed extraction response.",
                    details={"response": response},
                ) from exc
            raise SchemaValidationError(
                f"Extraction response failed schema validation: {self._format_validation_error(exc)}",
                details={"response": response, "errors": exc.errors()},
            ) from exc

        item_groups = (
            validated.maintenance_tasks,
            validated.spare_parts,
            validated.equipment,
            validated.manufacturers,
            validated.suppliers,
            validated.contact_points,
            validated.procedures,
            validated.specifications,
            validated.safety_warnings,
            validated.maintenance_intervals,
            validated.troubleshooting_entries,
            validated.identifiers,
        )
        confidence_score = self._resolve_overall_confidence(validated, item_groups)

        validation = ValidationResult()
        if confidence_score < 0 or confidence_score > 1:
            validation.add_issue(
                "confidence_score",
                "Confidence score must be a number between 0 and 1.",
                "extraction.response.confidence.invalid",
            )
        try:
            validation.raise_if_invalid()
        except SchemaValidationError as exc:
            issues = exc.details.get("issues", [])
            raise SchemaValidationError(
                (
                    "Extraction response failed validation: "
                    f"{self._format_issue_details(issues)}"
                ),
                details={"response": response, "issues": issues},
            ) from exc

        payload = {
            "confidence_score": confidence_score,
            "requires_human_review": validated.requires_human_review,
            "maintenance_tasks": [
                item.model_dump() for item in validated.maintenance_tasks
            ],
            "spare_parts": [item.model_dump() for item in validated.spare_parts],
            "equipment": [item.model_dump() for item in validated.equipment],
            "manufacturers": [
                item.model_dump() for item in validated.manufacturers
            ],
            "suppliers": [item.model_dump() for item in validated.suppliers],
            "contact_points": [item.model_dump() for item in validated.contact_points],
            "procedures": [item.model_dump() for item in validated.procedures],
            "specifications": [
                item.model_dump() for item in validated.specifications
            ],
            "safety_warnings": [
                item.model_dump() for item in validated.safety_warnings
            ],
            "maintenance_intervals": [
                item.model_dump() for item in validated.maintenance_intervals
            ],
            "troubleshooting_entries": [
                item.model_dump() for item in validated.troubleshooting_entries
            ],
            "identifiers": [item.model_dump() for item in validated.identifiers],
        }
        return self.sanitizer.sanitize(payload)

    def _validate_json_payload(self, normalized: str) -> ExtractionResponsePayload:
        try:
            return ExtractionResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if not is_json_validation_error(exc):
                raise

            repaired = self.repairer.repair(normalized)
            if repaired is None or repaired == normalized:
                raise

            return ExtractionResponsePayload.model_validate_json(repaired)

    @staticmethod
    def _format_validation_error(exc: ValidationError) -> str:
        messages = [
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        return "; ".join(messages)

    @staticmethod
    def _format_issue_details(issues: Any) -> str:
        if not isinstance(issues, list) or not issues:
            return "Validation failed."

        messages: list[str] = []
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            field = issue.get("field")
            message = issue.get("message")
            if isinstance(field, str) and isinstance(message, str):
                messages.append(f"{field}: {message}")
            elif isinstance(message, str):
                messages.append(message)
        return "; ".join(messages) or "Validation failed."

    @staticmethod
    def _resolve_overall_confidence(
        validated: ExtractionResponsePayload,
        item_groups: tuple[list[Any], ...],
    ) -> float:
        if validated.confidence_score is not None:
            return validated.confidence_score

        derived_confidence = ExtractionResponseParser._derive_confidence_from_items(
            item_groups
        )
        if derived_confidence is not None:
            return derived_confidence

        return 0.0

    @staticmethod
    def _derive_confidence_from_items(item_groups: tuple[list[Any], ...]) -> float | None:
        confidences = [
            item.confidence_score
            for items in item_groups
            for item in items
            if item.confidence_score is not None
        ]
        if not confidences:
            return None
        return sum(confidences) / len(confidences)


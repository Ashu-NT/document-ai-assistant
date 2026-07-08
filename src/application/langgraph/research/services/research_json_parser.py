from __future__ import annotations

from pydantic import ValidationError

from src.application.langgraph.research.services.research_planning_response_schema import (
    ResearchPlanningResponsePayload,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_opened,
)


class ResearchJsonParser:
    def parse_planning_response(self, payload: str) -> ResearchPlanningResponsePayload:
        normalized = strip_code_fences_if_opened(payload)
        try:
            return ResearchPlanningResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed research planning response JSON.",
                    details={"payload": payload},
                ) from exc
            raise SchemaValidationError(
                "Research planning response failed schema validation.",
                details={"payload": payload, "errors": exc.errors()},
            ) from exc

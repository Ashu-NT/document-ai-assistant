from __future__ import annotations

from pydantic import ValidationError

from src.application.langgraph.research.services.research_planning_response_schema import (
    ResearchPlanningResponsePayload,
)
from src.shared.exceptions import SchemaValidationError


class ResearchJsonParser:
    def parse_planning_response(self, payload: str) -> ResearchPlanningResponsePayload:
        normalized = self._strip_code_fences(payload)
        try:
            return ResearchPlanningResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if self._is_json_error(exc):
                raise SchemaValidationError(
                    "Malformed research planning response JSON.",
                    details={"payload": payload},
                ) from exc
            raise SchemaValidationError(
                "Research planning response failed schema validation.",
                details={"payload": payload, "errors": exc.errors()},
            ) from exc

    @staticmethod
    def _strip_code_fences(payload: str) -> str:
        stripped = (payload or "").strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                stripped = "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _is_json_error(exc: ValidationError) -> bool:
        return any(error.get("type") == "json_invalid" for error in exc.errors())

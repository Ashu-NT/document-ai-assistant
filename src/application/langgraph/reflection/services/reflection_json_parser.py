from __future__ import annotations

from src.application.langgraph.reflection.models import (
    ReflectionDecision,
)
from src.application.langgraph.reflection.services.reflection_response_schema import (
    ReflectionResponsePayload,
)
from pydantic import ValidationError
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_opened,
)


class ReflectionJsonParser:
    def parse(self, payload: str) -> ReflectionDecision:
        normalized = strip_code_fences_if_opened(payload)
        try:
            data = ReflectionResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed reflection response JSON.",
                    details={"payload": payload},
                ) from exc
            raise SchemaValidationError(
                "Reflection response failed schema validation.",
                details={"payload": payload, "errors": exc.errors()},
            ) from exc
        return ReflectionDecision(
            decision=data.decision,
            confidence=data.confidence,
            reason=data.reason,
            retry_query=data.retry_query,
            clarification_question=data.clarification_question,
            missing_information=list(data.missing_information),
            # Matches the deterministic decider's own convention (a truthy
            # string reason code, falsy/absent when there's no violation) so
            # ReflectionValidator's `not hard_grounding_violation` checks
            # work identically regardless of which decider produced the
            # decision.
            diagnostics=(
                {"hard_grounding_violation": "llm_reported_grounding_violation"}
                if data.grounding_violation
                else {}
            ),
        )

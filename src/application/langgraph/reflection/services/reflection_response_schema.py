from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.application.langgraph.reflection.models import ReflectionDecisionType


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


class ReflectionResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: ReflectionDecisionType
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str
    retry_query: str | None = None
    clarification_question: str | None = None
    missing_information: list[str] = Field(default_factory=list)

    @field_validator("decision", mode="before")
    @classmethod
    def _validate_decision(cls, value: Any) -> Any:
        text = _optional_text(value)
        return text.upper() if text else text

    @field_validator("reason", "retry_query", "clarification_question", mode="before")
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("reason")
    @classmethod
    def _require_reason(cls, value: str | None) -> str:
        if not value:
            raise ValueError("reason is required")
        return value

    @field_validator("missing_information", mode="before")
    @classmethod
    def _validate_missing_information(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("missing_information must be an array")
        return [
            item
            for item in (_optional_text(entry) for entry in value)
            if item is not None
        ]


_REFLECTION_RESPONSE_JSON_SCHEMA = ReflectionResponsePayload.model_json_schema()


def build_reflection_response_json_schema() -> dict[str, Any]:
    return _REFLECTION_RESPONSE_JSON_SCHEMA

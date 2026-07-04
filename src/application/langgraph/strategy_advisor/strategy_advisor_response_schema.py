from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorIntent,
)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


class StrategyAdvisorResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: StrategyAdvisorIntent
    route: str
    confidence: float = Field(ge=0.0, le=1.0)
    concepts: list[str]
    recommended_strategies: list[str]
    comparison: bool = False
    requires_table: bool = False
    reason: str

    @field_validator("intent", mode="before")
    @classmethod
    def _validate_intent(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("route", "reason", mode="before")
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("route", "reason")
    @classmethod
    def _require_text_fields(cls, value: str | None) -> str:
        if not value:
            raise ValueError("required text field is missing")
        return value

    @field_validator("concepts", mode="before")
    @classmethod
    def _validate_concepts(cls, value: Any) -> Any:
        if not isinstance(value, list):
            raise TypeError("concepts must be an array")
        return [
            item for item in (_optional_text(entry) for entry in value) if item is not None
        ]

    @field_validator("recommended_strategies", mode="before")
    @classmethod
    def _validate_recommended_strategies(cls, value: Any) -> Any:
        if not isinstance(value, list):
            raise TypeError("recommended_strategies must be an array")
        return [
            item.upper()
            for item in (_optional_text(entry) for entry in value)
            if item is not None
        ]


_STRATEGY_ADVISOR_RESPONSE_JSON_SCHEMA = (
    StrategyAdvisorResponsePayload.model_json_schema()
)


def build_strategy_advisor_response_json_schema() -> dict[str, Any]:
    return _STRATEGY_ADVISOR_RESPONSE_JSON_SCHEMA

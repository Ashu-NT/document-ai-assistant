from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


class RetrievalStrategyResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_strategy: str
    secondary_strategies: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str
    rewritten_query: str | None = None
    top_k: int | None = Field(default=None, ge=1)

    @field_validator("primary_strategy", mode="before")
    @classmethod
    def _validate_primary_strategy(cls, value: Any) -> Any:
        text = _optional_text(value)
        return text.upper() if text else text

    @field_validator("secondary_strategies", mode="before")
    @classmethod
    def _validate_secondary_strategies(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("secondary_strategies must be an array")
        return [
            item.upper()
            for item in (_optional_text(entry) for entry in value)
            if item is not None
        ]

    @field_validator("reason", "rewritten_query", mode="before")
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("reason")
    @classmethod
    def _require_reason(cls, value: str | None) -> str:
        if not value:
            raise ValueError("reason is required")
        return value


_RETRIEVAL_STRATEGY_RESPONSE_JSON_SCHEMA = (
    RetrievalStrategyResponsePayload.model_json_schema()
)


def build_retrieval_strategy_response_json_schema() -> dict[str, Any]:
    return _RETRIEVAL_STRATEGY_RESPONSE_JSON_SCHEMA

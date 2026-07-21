from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


class PlanStepPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str | None = None
    tool_name: str
    description: str
    input_key: str | None = None
    output_key: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    required: bool = True

    @field_validator(
        "step_id",
        "tool_name",
        "description",
        "input_key",
        "output_key",
        mode="before",
    )
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("depends_on", mode="before")
    @classmethod
    def _validate_depends_on(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("depends_on must be an array")
        return [
            item
            for item in (_optional_text(entry) for entry in value)
            if item is not None
        ]

    @field_validator("tool_name", "description")
    @classmethod
    def _require_text_fields(cls, value: str | None) -> str:
        if not value:
            raise ValueError("required text field is missing")
        return value


class PlanResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str
    requires_document: bool = False
    reason: str | None = None
    steps: list[PlanStepPayload]
    plan_id: str | None = None
    document_id: str | None = None
    document_title: str | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "goal",
        "reason",
        "plan_id",
        "document_id",
        "document_title",
        mode="before",
    )
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("goal")
    @classmethod
    def _require_goal(cls, value: str | None) -> str:
        if not value:
            raise ValueError("goal is required")
        return value

    @field_validator("steps")
    @classmethod
    def _require_steps(cls, value: list[PlanStepPayload]) -> list[PlanStepPayload]:
        if not value:
            raise ValueError("at least one step is required")
        return value


_PLAN_RESPONSE_JSON_SCHEMA = PlanResponsePayload.model_json_schema()


def build_plan_response_json_schema() -> dict[str, Any]:
    return _PLAN_RESPONSE_JSON_SCHEMA

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


class ResearchPlanningTaskPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str | None = None
    title: str
    question: str
    strategy_hint: str | None = None
    answer_intent_hint: str | None = None
    document_id: str | None = None
    required: bool = True
    depends_on: list[str] = Field(default_factory=list)
    expected_evidence_type: str | None = None
    max_results: int | None = None

    @field_validator(
        "task_id",
        "title",
        "question",
        "strategy_hint",
        "answer_intent_hint",
        "document_id",
        "expected_evidence_type",
        mode="before",
    )
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("title", "question")
    @classmethod
    def _require_text_fields(cls, value: str | None) -> str:
        if not value:
            raise ValueError("required text field is missing")
        return value

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


class ResearchPlanningResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal_type: str | None = None
    reason: str
    tasks: list[ResearchPlanningTaskPayload]

    @field_validator("goal_type", "reason", mode="before")
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("reason")
    @classmethod
    def _require_reason(cls, value: str | None) -> str:
        if not value:
            raise ValueError("reason is required")
        return value

    @field_validator("tasks")
    @classmethod
    def _require_tasks(
        cls,
        value: list[ResearchPlanningTaskPayload],
    ) -> list[ResearchPlanningTaskPayload]:
        if not value:
            raise ValueError("at least one task is required")
        return value


_RESEARCH_PLANNING_RESPONSE_JSON_SCHEMA = (
    ResearchPlanningResponsePayload.model_json_schema()
)


def build_research_planning_response_json_schema() -> dict[str, Any]:
    return _RESEARCH_PLANNING_RESPONSE_JSON_SCHEMA

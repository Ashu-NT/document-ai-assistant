from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_QUESTION_PREFIX_PATTERN = re.compile(r"^\s*(?:[-*]+|\d+[\.\)]|[A-Za-z]\))\s*")


def _normalize_question(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().strip('"').strip("'").split())
    text = _QUESTION_PREFIX_PATTERN.sub("", text).strip()
    return text or None


class QuestionGenerationResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[str] = Field(default_factory=list)

    @field_validator("questions", mode="before")
    @classmethod
    def _validate_questions(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("questions must be an array")
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            question = _normalize_question(item)
            if not question or question in seen:
                continue
            seen.add(question)
            normalized.append(question)
        return normalized


_QUESTION_GENERATION_RESPONSE_JSON_SCHEMA = (
    QuestionGenerationResponsePayload.model_json_schema()
)


def build_question_generation_response_json_schema() -> dict[str, Any]:
    return _QUESTION_GENERATION_RESPONSE_JSON_SCHEMA

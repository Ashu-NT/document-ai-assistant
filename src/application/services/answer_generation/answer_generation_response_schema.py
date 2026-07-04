from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnswerGenerationResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    answer_text: str = Field(min_length=1)


def build_answer_generation_response_json_schema() -> dict[str, Any]:
    return AnswerGenerationResponsePayload.model_json_schema()

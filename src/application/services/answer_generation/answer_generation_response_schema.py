from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnswerGenerationResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    answer_text: str = Field(min_length=1)
    # Optional, enforced-structure alternative to folding a caveat into
    # answer_text's prose (plan section 4.6/9.6) -- e.g. "Only partial
    # specifications were found in the retrieved sources." Surfaced via
    # GeneratedAnswer.diagnostics rather than appended to answer_text, so a
    # caller can distinguish "the model flagged a limitation" from "the
    # model wrote a limitation into the answer text" instead of having to
    # string-parse the answer for a caveat.
    limitation_note: str | None = Field(default=None, min_length=1)


def build_answer_generation_response_json_schema() -> dict[str, Any]:
    return AnswerGenerationResponsePayload.model_json_schema()

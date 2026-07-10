from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReferenceNotePayload(BaseModel):
    """A single claim-to-source attribution the model can optionally supply
    alongside a section (plan section 9.6 sections/reference_notes
    redesign). `source_number` matches the same 1-based "SOURCE {n}" label
    already shown to the model in the prompt's raw-source blocks -- the
    model never sees a citation_id/chunk_id, so asking for one would just
    invite hallucination. Resolution to a real chunk_id happens downstream
    in AnswerGenerationService, once, against the sources actually used for
    this generation."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    note_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    source_number: int = Field(ge=1)


class AnswerSectionPayload(BaseModel):
    """An optional structured breakdown of answer_text into headed blocks,
    each pointing at the reference_notes that support it. Not a
    replacement for answer_text -- both may be present; sections/
    reference_notes are the additive, enforced-structure sibling
    (plan section 9.6), consumed by the answering-guardrail layer rather
    than the flat prose."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    heading: str = Field(min_length=1)
    body: str = Field(min_length=1)
    reference_note_ids: list[str] = Field(default_factory=list)


class AnswerGenerationResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    answer_text: str = Field(min_length=1)
    # Optional, enforced-structure alternative to folding a caveat into
    # answer_text's prose (plan section 4.6/9.6) -- e.g. "Only partial
    # specifications were found in the retrieved sources." Surfaced via
    # GeneratedAnswer.limitation_note rather than appended to answer_text,
    # so a caller can distinguish "the model flagged a limitation" from
    # "the model wrote a limitation into the answer text" instead of
    # having to string-parse the answer for a caveat.
    limitation_note: str | None = Field(default=None, min_length=1)
    # Both optional/default-empty -- omitting them is always valid, so
    # every existing answer_text-only response stays valid (plan section
    # 9.6 sections/reference_notes redesign).
    sections: list[AnswerSectionPayload] = Field(default_factory=list)
    reference_notes: list[ReferenceNotePayload] = Field(default_factory=list)


def build_answer_generation_response_json_schema() -> dict[str, Any]:
    return AnswerGenerationResponsePayload.model_json_schema()

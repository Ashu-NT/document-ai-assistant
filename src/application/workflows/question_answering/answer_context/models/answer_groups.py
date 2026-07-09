from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.question_answering.answer_context.models.answer_source import (
    AnswerSource,
)


@dataclass(slots=True)
class AnswerSourceGroup:
    group_name: str
    chunk_type: str | None = None
    sources: list[AnswerSource] = field(default_factory=list)


@dataclass(slots=True)
class AnswerSectionGroup:
    group_name: str
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    source_numbers: list[int] = field(default_factory=list)

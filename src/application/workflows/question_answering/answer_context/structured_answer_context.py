from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


@dataclass(slots=True)
class AnswerSource:
    source_number: int
    chunk_id: str
    chunk_name: str | None = None
    chunk_type: str | None = None
    document_id: str | None = None
    document_title: str | None = None
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    score: float | None = None
    content: str = ""


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


@dataclass(slots=True)
class AnswerKeyValue:
    key: str
    value: str
    unit: str | None
    source_number: int
    confidence: float | None = None


@dataclass(slots=True)
class StructuredAnswerContext:
    answer_intent: AnswerIntent
    sources: list[AnswerSource] = field(default_factory=list)
    source_groups: list[AnswerSourceGroup] = field(default_factory=list)
    section_groups: list[AnswerSectionGroup] = field(default_factory=list)
    key_values: list[AnswerKeyValue] = field(default_factory=list)
    source_count: int = 0
    diagnostics: dict[str, Any] = field(default_factory=dict)

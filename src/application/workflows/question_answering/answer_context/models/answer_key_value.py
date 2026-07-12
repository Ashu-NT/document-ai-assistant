from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AnswerKeyValue:
    key: str
    value: str
    unit: str | None
    source_number: int
    confidence: float | None = None
    field_kind: str | None = None

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClassificationStageResult:
    classification: object | None
    classification_model: str | None

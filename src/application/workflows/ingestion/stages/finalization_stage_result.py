from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FinalizationStageResult:
    final_graph: object
    question_generation_model: str | None

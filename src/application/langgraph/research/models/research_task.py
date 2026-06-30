from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ResearchTask:
    task_id: str
    title: str
    question: str
    strategy_hint: str | None
    answer_intent_hint: str | None
    document_id: str | None
    required: bool = True
    depends_on: list[str] = field(default_factory=list)
    expected_evidence_type: str | None = None
    max_results: int = 5
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

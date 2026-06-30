from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DocumentGroundingPolicy:
    require_evidence_for_answers: bool = True
    require_page_metadata: bool = False
    require_section_or_source_metadata: bool = True
    grounded_routes: tuple[str, ...] = field(
        default_factory=lambda: ("answer_question", "deep_research", "planned_task")
    )

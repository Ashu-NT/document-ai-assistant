from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CitationPolicy:
    require_citations: bool = True
    citation_required_routes: tuple[str, ...] = field(
        default_factory=lambda: ("answer_question", "deep_research")
    )

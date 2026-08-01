from __future__ import annotations

from dataclasses import dataclass, field


def _default_require_citations() -> bool:
    try:
        from src.config.settings import guardrail_settings
        return guardrail_settings.require_citations
    except Exception:
        return True


@dataclass(slots=True, frozen=True)
class CitationPolicy:
    require_citations: bool = field(default_factory=_default_require_citations)
    citation_required_routes: tuple[str, ...] = field(
        default_factory=lambda: ("answer_question", "deep_research")
    )

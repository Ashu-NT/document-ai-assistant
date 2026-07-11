from __future__ import annotations

_DEEP_RESEARCH_ROUTE_MARKERS = (
    "compare",
    "analyze",
    "research",
    "report",
    "checklist",
    "summarize all",
    "find every",
    "identify missing",
    "cross-check",
    "across the document",
    "all maintenance",
    "all inspection",
    "all warnings",
    "all specifications",
    "preventive maintenance",
    "evidence supports",
)
_DEEP_RESEARCH_COMPLEX_MARKERS = (
    "compare",
    "summarize all",
    "find every",
    "all maintenance",
    "all inspection",
    "all warnings",
    "all specifications",
    "preventive maintenance",
)


def looks_like_deep_research(
    value: str,
    *,
    deep_research_enabled: bool,
) -> bool:
    padded = f" {value} "
    if any(marker in value for marker in _DEEP_RESEARCH_ROUTE_MARKERS if marker != "compare"):
        return True
    if "compare" in value and (" and " in padded or " with " in padded):
        return True
    if deep_research_enabled and any(marker in value for marker in _DEEP_RESEARCH_COMPLEX_MARKERS):
        return True
    return False

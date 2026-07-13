from __future__ import annotations

from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    strip_heading_number,
)

_WEAK_BRIDGE_MARKERS = (
    "overview",
    "general warnings",
    "warning",
    "warnings",
    "caution",
    "danger",
    "hazard",
    "biohazard",
    "safety precautions",
    "electrical system precautions",
    "owner / user responsibility",
    "modification",
    "modifications",
    "remarks",
    "notes",
)
_STRONG_BRANCH_MARKERS = (
    "description",
    "technical data",
    "technical specification",
    "main parts",
    "maintenance",
    "preventive maintenance",
    "troubleshooting",
    "trouble shooting",
    "operation",
    "startup",
    "shutdown",
    "commissioning",
    "installation",
    "assembly",
    "spare parts",
    "parts list",
    "device information",
    "ordering example",
    "operating limits",
    "sensor list",
    "valve list",
)


def prune_semantic_bridge_segments(section_path: list[str]) -> list[str]:
    if len(section_path) < 3:
        return list(section_path)

    pruned: list[str] = []
    pending_weak_segments: list[str] = []

    for part in section_path:
        normalized = _normalize_segment(part)
        if not normalized:
            continue

        if _contains_any(normalized, _WEAK_BRIDGE_MARKERS):
            pending_weak_segments.append(part)
            continue

        if pending_weak_segments and _contains_any(normalized, _STRONG_BRANCH_MARKERS):
            pending_weak_segments = []
        elif pending_weak_segments:
            pruned.extend(pending_weak_segments)
            pending_weak_segments = []

        pruned.append(part)

    pruned.extend(pending_weak_segments)
    return pruned


def _normalize_segment(value: str | None) -> str:
    stripped = strip_heading_number(str(value or "")).strip().casefold()
    return " ".join(stripped.split())


def _contains_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)

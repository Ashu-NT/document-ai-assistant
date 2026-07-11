from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchSynthesis
from src.application.langgraph.research.services.mappers.research_gap_state_mapper import (
    gaps_from_list,
)


def synthesis_from_dict(value: Any) -> ResearchSynthesis | None:
    if not isinstance(value, dict):
        return None
    return ResearchSynthesis(
        summary=str(value.get("summary") or ""),
        sections=[
            dict(section)
            for section in list(value.get("sections") or [])
            if isinstance(section, dict)
        ],
        comparisons=[
            dict(comparison)
            for comparison in list(value.get("comparisons") or [])
            if isinstance(comparison, dict)
        ],
        checklist_items=[
            dict(item)
            for item in list(value.get("checklist_items") or [])
            if isinstance(item, dict)
        ],
        gaps=gaps_from_list(value.get("gaps")),
        references=[
            dict(reference)
            for reference in list(value.get("references") or [])
            if isinstance(reference, dict)
        ],
        diagnostics=dict(value.get("diagnostics") or {}),
    )

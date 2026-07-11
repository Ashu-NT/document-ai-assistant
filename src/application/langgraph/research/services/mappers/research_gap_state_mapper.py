from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchGap, ResearchGapSeverity
from src.application.langgraph.research.services.mappers.state_mapping_primitives import (
    enum_or_none,
    str_or_none,
)


def gaps_from_list(value: Any) -> list[ResearchGap]:
    if not isinstance(value, list):
        return []
    gaps: list[ResearchGap] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        severity = enum_or_none(ResearchGapSeverity, item.get("severity"))
        if severity is None:
            continue
        gaps.append(
            ResearchGap(
                gap_id=str(item.get("gap_id") or ""),
                description=str(item.get("description") or ""),
                severity=severity,
                related_task_id=str_or_none(item.get("related_task_id")),
                suggested_followup_query=str_or_none(
                    item.get("suggested_followup_query")
                ),
                suggested_strategy=str_or_none(
                    item.get("suggested_strategy")
                ),
                can_retry=bool(item.get("can_retry", False)),
                diagnostics=dict(item.get("diagnostics") or {}),
            )
        )
    return gaps

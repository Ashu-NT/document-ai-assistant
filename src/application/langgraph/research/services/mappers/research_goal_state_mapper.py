from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchGoal, ResearchGoalType, ResearchOutputType
from src.application.langgraph.research.services.mappers.state_mapping_primitives import (
    enum_or_none,
    str_or_none,
)


def goal_from_dict(value: Any) -> ResearchGoal | None:
    if not isinstance(value, dict):
        return None
    goal_type = enum_or_none(ResearchGoalType, value.get("goal_type"))
    output_type = enum_or_none(
        ResearchOutputType,
        value.get("expected_output_type"),
    )
    if goal_type is None or output_type is None:
        return None
    return ResearchGoal(
        goal_id=str(value.get("goal_id") or ""),
        user_input=str(value.get("user_input") or ""),
        goal_type=goal_type,
        document_id=str_or_none(value.get("document_id")),
        document_title=str_or_none(value.get("document_title")),
        requires_document=bool(value.get("requires_document", False)),
        requires_cross_section_reasoning=bool(
            value.get("requires_cross_section_reasoning", False)
        ),
        requires_multi_strategy_retrieval=bool(
            value.get("requires_multi_strategy_retrieval", False)
        ),
        expected_output_type=output_type,
        diagnostics=dict(value.get("diagnostics") or {}),
    )

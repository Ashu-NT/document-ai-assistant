from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchTask
from src.application.langgraph.research.services.mappers.state_mapping_primitives import (
    str_or_none,
)


def tasks_from_list(value: Any) -> list[ResearchTask]:
    if not isinstance(value, list):
        return []
    tasks: list[ResearchTask] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        tasks.append(
            ResearchTask(
                task_id=str(item.get("task_id") or ""),
                title=str(item.get("title") or ""),
                question=str(item.get("question") or ""),
                strategy_hint=str_or_none(item.get("strategy_hint")),
                answer_intent_hint=str_or_none(
                    item.get("answer_intent_hint")
                ),
                document_id=str_or_none(item.get("document_id")),
                required=bool(item.get("required", True)),
                depends_on=[
                    str(dependency)
                    for dependency in list(item.get("depends_on") or [])
                    if str(dependency).strip()
                ],
                expected_evidence_type=str_or_none(
                    item.get("expected_evidence_type")
                ),
                max_results=int(item.get("max_results") or 0),
                diagnostics=dict(item.get("diagnostics") or {}),
            )
        )
    return tasks

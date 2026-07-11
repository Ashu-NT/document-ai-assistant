from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchTaskResult
from src.application.langgraph.research.services.mappers.research_evidence_state_mapper import (
    evidence_from_list,
)
from src.application.langgraph.research.services.mappers.state_mapping_primitives import (
    str_or_none,
)


def task_results_from_list(value: Any) -> list[ResearchTaskResult]:
    if not isinstance(value, list):
        return []
    results: list[ResearchTaskResult] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        results.append(
            ResearchTaskResult(
                task_id=str(item.get("task_id") or ""),
                success=bool(item.get("success", False)),
                tool_names=[
                    str(tool_name)
                    for tool_name in list(item.get("tool_names") or [])
                    if str(tool_name).strip()
                ],
                retrieval_strategy=str_or_none(
                    item.get("retrieval_strategy")
                ),
                evidence=evidence_from_list(item.get("evidence")),
                answer_text=str_or_none(item.get("answer_text")),
                errors=[
                    str(error)
                    for error in list(item.get("errors") or [])
                    if str(error).strip()
                ],
                diagnostics=dict(item.get("diagnostics") or {}),
            )
        )
    return results

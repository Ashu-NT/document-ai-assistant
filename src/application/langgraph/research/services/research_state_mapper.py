from __future__ import annotations

from typing import Any

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.research.models import (
    ResearchPlan,
    ResearchResult,
)
from src.application.langgraph.research.services.mappers.research_evidence_state_mapper import (
    evidence_from_list,
)
from src.application.langgraph.research.services.mappers.research_gap_state_mapper import (
    gaps_from_list,
)
from src.application.langgraph.research.services.mappers.research_goal_state_mapper import (
    goal_from_dict,
)
from src.application.langgraph.research.services.mappers.research_report_state_mapper import (
    report_from_dict,
)
from src.application.langgraph.research.services.mappers.research_synthesis_state_mapper import (
    synthesis_from_dict,
)
from src.application.langgraph.research.services.mappers.research_task_result_state_mapper import (
    task_results_from_list,
)
from src.application.langgraph.research.services.mappers.research_task_state_mapper import (
    tasks_from_list,
)


class ResearchStateMapper:
    @classmethod
    def plan_from_dict(cls, value: dict[str, Any] | None) -> ResearchPlan | None:
        if not isinstance(value, dict):
            return None
        goal = goal_from_dict(value.get("goal"))
        if goal is None:
            return None
        tasks = tasks_from_list(value.get("tasks"))
        return ResearchPlan(
            plan_id=str(value.get("plan_id") or ""),
            goal=goal,
            tasks=tasks,
            reason=str(value.get("reason") or ""),
            source=str(value.get("source") or ""),
            requires_document=bool(value.get("requires_document", False)),
            max_iterations=int(value.get("max_iterations") or 0),
            diagnostics=dict(value.get("diagnostics") or {}),
        )

    @classmethod
    def result_from_state(cls, state: dict[str, Any]) -> ResearchResult | None:
        plan = cls.plan_from_dict(state.get("research_plan"))
        goal = goal_from_dict(state.get("research_goal"))
        if plan is None or goal is None:
            return None
        return ResearchResult(
            success=bool(state.get("research_result", {}).get("success", True))
            if isinstance(state.get("research_result"), dict)
            else True,
            goal=goal,
            plan=plan,
            task_results=task_results_from_list(state.get("research_task_results")),
            evidence=evidence_from_list(state.get("research_evidence")),
            synthesis=synthesis_from_dict(state.get("research_synthesis")),
            report=report_from_dict(state.get("research_report")),
            gaps=gaps_from_list(state.get("research_gaps")),
            iterations=int(state.get("research_iterations") or 0),
            errors=[str(item) for item in list(state.get("research_errors") or [])],
            diagnostics=dict(state.get("research_result", {}).get("diagnostics") or {})
            if isinstance(state.get("research_result"), dict)
            else {},
        )

    @staticmethod
    def plan_to_state(plan: ResearchPlan) -> dict[str, Any]:
        return {
            "research_goal": serialize_graph_value(plan.goal.to_dict()),
            "research_plan": serialize_graph_value(plan.to_dict()),
        }

    @staticmethod
    def result_to_state(result: ResearchResult) -> dict[str, Any]:
        return {
            "research_goal": serialize_graph_value(result.goal.to_dict()),
            "research_plan": serialize_graph_value(result.plan.to_dict()),
            "research_task_results": serialize_graph_value(
                [task_result.to_dict() for task_result in result.task_results]
            ),
            "research_evidence": serialize_graph_value(
                [evidence.to_dict() for evidence in result.evidence]
            ),
            "research_gaps": serialize_graph_value(
                [gap.to_dict() for gap in result.gaps]
            ),
            "research_iterations": result.iterations,
            "research_synthesis": serialize_graph_value(result.synthesis.to_dict())
            if result.synthesis is not None
            else None,
            "research_report": serialize_graph_value(result.report.to_dict())
            if result.report is not None
            else None,
            "research_errors": list(result.errors),
            "research_result": serialize_graph_value(result.to_dict()),
        }

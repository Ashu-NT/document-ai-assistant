from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import build_error, extend_trace
from src.application.langgraph.research import ResearchService
from src.application.langgraph.research.services import ResearchStateMapper
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class EvaluateResearchNode:
    def __init__(
        self,
        research_service: ResearchService,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.research_service = research_service
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict[str, Any]:
        token = self.recorder.start_node(
            "evaluate_research",
            route=state.get("route"),
        )
        result = ResearchStateMapper.result_from_state(state)
        plan = ResearchStateMapper.plan_from_dict(state.get("research_plan"))
        if result is None or plan is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="research_result_missing",
            )
            return {
                "error": build_error(
                    message="Research evaluation could not run because the intermediate research result was missing.",
                    error_code="research_result_missing",
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        result, followup_tasks = self.research_service.evaluate_research(result)
        research_trace = dict(state.get("research_trace") or {})
        coverage = dict(result.diagnostics.get("coverage") or {})
        research_trace["gaps"] = [gap.to_dict() for gap in result.gaps]
        research_trace["followup_iteration"] = bool(followup_tasks)
        research_trace["strategy_coverage"] = {
            "ratio": coverage.get("concept_coverage_ratio"),
            "covered_concepts": list(coverage.get("covered_concepts", [])),
            "uncovered_concepts": list(coverage.get("uncovered_concepts", [])),
            "passed": not bool(coverage.get("uncovered_concepts", [])),
        }
        next_iterations = int(state.get("research_iterations") or 0)
        next_plan = plan
        if followup_tasks:
            next_plan = self.research_service.append_followup_tasks(
                plan,
                followup_tasks,
            )
            next_iterations += 1

        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "gap_count": len(result.gaps),
                "followup_task_count": len(followup_tasks),
                "concept_coverage_ratio": coverage.get("concept_coverage_ratio"),
            },
        )
        return {
            **ResearchStateMapper.result_to_state(result),
            **ResearchStateMapper.plan_to_state(next_plan),
            "research_trace": research_trace,
            "research_followup_pending": bool(followup_tasks),
            "research_iterations": next_iterations,
            "trace": extend_trace(state["trace"], trace_entry),
        }

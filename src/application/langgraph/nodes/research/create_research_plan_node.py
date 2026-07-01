from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import build_error, extend_trace, resolve_selected_document
from src.application.langgraph.research import ResearchService, ResearchTrace
from src.application.langgraph.research.services import ResearchStateMapper
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorProposal,
)
from src.application.langgraph.tracing import GraphRunRecorder
from src.shared.exceptions import SchemaValidationError


class CreateResearchPlanNode:
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
            "create_research_plan",
            route=state.get("route"),
            selected_document_id=state.get("selected_document_id"),
        )
        document_id, document_title = resolve_selected_document(state)
        if self.research_service.policy.require_document_scope and not document_id:
            message = (
                "Deep research needs a selected document. "
                "Please select one first or pass --document."
            )
            trace_entry = self.recorder.finish_node(
                token,
                success=True,
                diagnostics={"needs_document": True},
            )
            return {
                "needs_clarification": True,
                "clarification_message": message,
                "clarification_question": "Which document should I research?",
                "response_text": message,
                "trace": extend_trace(state["trace"], trace_entry),
            }

        try:
            plan, diagnostics = self.research_service.plan_research(
                user_input=state.get("question") or state["user_input"],
                document_id=document_id,
                document_title=document_title,
                advisor_proposal=_advisor_proposal_from_state(state),
                use_llm_planner=bool(
                    state.get("llm_research_planning_enabled", False)
                ),
            )
        except SchemaValidationError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=exc.error_code,
                diagnostics=exc.details or {},
            )
            if self.research_service.policy.fallback_to_standard_qa:
                return {
                    "route": RouteType.ANSWER_QUESTION.value,
                    "research_planning_errors": [exc.message],
                    "trace": extend_trace(state["trace"], trace_entry),
                }
            return {
                "error": build_error(
                    message=exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        trace = ResearchTrace(
            research_goal=plan.goal.to_dict(),
            plan_source=diagnostics.get("planning_source"),
            tasks=[task.to_dict() for task in plan.tasks],
            diagnostics={
                "planning_warnings": diagnostics.get("planning_warnings", []),
                "planning_errors": diagnostics.get("planning_errors", []),
            },
        )
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "plan_id": plan.plan_id,
                "planning_source": diagnostics.get("planning_source"),
                "task_count": plan.task_count,
            },
        )
        return {
            **ResearchStateMapper.plan_to_state(plan),
            "document_id": document_id,
            "document_title": document_title,
            "research_trace": trace.to_dict(),
            "research_plan_source": diagnostics.get("planning_source"),
            "research_planning_errors": list(
                diagnostics.get("planning_errors", [])
            ),
            "research_planning_warnings": list(
                diagnostics.get("planning_warnings", [])
            ),
            "raw_llm_research_plan": (
                diagnostics.get("raw_llm_plan")
                if state.get("show_research_trace")
                else None
            ),
            "research_followup_pending": False,
            "research_errors": [],
            "trace": extend_trace(state["trace"], trace_entry),
        }


def _advisor_proposal_from_state(state: AgentState) -> StrategyAdvisorProposal | None:
    payload = state.get("strategy_advisor_result")
    if not isinstance(payload, dict):
        return None
    proposal = payload.get("proposal")
    if not isinstance(proposal, dict):
        return None
    return StrategyAdvisorProposal.from_dict(proposal)

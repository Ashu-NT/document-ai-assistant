from __future__ import annotations

from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.planning import DeterministicPlanner
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class CreatePlanNode:
    def __init__(
        self,
        planner: DeterministicPlanner,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.planner = planner
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "create_plan",
            route=state.get("route"),
            selected_document_id=state.get("selected_document_id"),
        )
        plan = self.planner.create_plan(state)
        if plan is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=True,
                fallback_reason="planner_returned_none",
                diagnostics={"reason": "No deterministic multi-step plan matched."},
            )
            return {
                "route": RouteType.ANSWER_QUESTION.value,
                "execution_plan": None,
                "plan_steps": [],
                "plan_results": {
                    "plan_success": None,
                    "fallback_reason": "planner_returned_none",
                },
                "trace": extend_trace(state["trace"], trace_entry),
            }

        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "plan_id": plan.plan_id,
                "plan_goal": plan.goal,
                "step_count": plan.step_count,
                "requires_document": plan.requires_document,
                "plan_kind": plan.diagnostics.get("plan_kind"),
            },
        )
        patch: dict[str, object] = {
            "execution_plan": plan.to_dict(),
            "plan_steps": [step.to_dict() for step in plan.steps],
            "plan_results": {
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "plan_success": None,
                "step_outputs": {},
                "plan_kind": plan.diagnostics.get("plan_kind"),
            },
            "trace": extend_trace(state["trace"], trace_entry),
        }
        if plan.requires_document and not (
            state.get("document_id")
            or state.get("selected_document_id")
            or state.get("document_query")
            or plan.document_id
        ):
            patch.update(
                {
                    "needs_clarification": True,
                    "clarification_message": (
                        "This multi-step request needs a document. "
                        "Please select one first or pass --document."
                    ),
                    "clarification_question": "Which document should I use?",
                    "response_text": (
                        "This multi-step request needs a document. "
                        "Please select one first or pass --document."
                    ),
                }
            )
        return patch

from __future__ import annotations

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.nodes.planning.create_plan.llm_plan_acceptance import (
    attempt_llm_plan,
)
from src.application.langgraph.nodes.planning.create_plan.plan_patch_builder import (
    build_accepted_plan_patch,
)
from src.application.langgraph.planning import (
    DeterministicPlanner,
    LLMPlanProposer,
    PlanParser,
    PlanPolicy,
    PlanRepair,
    PlanValidator,
)
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class CreatePlanNode:
    def __init__(
        self,
        planner: DeterministicPlanner,
        *,
        tool_registry: ToolRegistry | None = None,
        llm_plan_proposer: LLMPlanProposer | None = None,
        plan_parser: PlanParser | None = None,
        plan_validator: PlanValidator | None = None,
        plan_policy: PlanPolicy | None = None,
        plan_repair: PlanRepair | None = None,
        deterministic_confidence_threshold: float = 0.8,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.planner = planner
        self.tool_registry = tool_registry
        self.llm_plan_proposer = llm_plan_proposer
        self.plan_parser = plan_parser or PlanParser()
        self.plan_validator = plan_validator or PlanValidator()
        self.plan_policy = plan_policy or PlanPolicy.default()
        self.plan_repair = plan_repair or PlanRepair()
        self.deterministic_confidence_threshold = deterministic_confidence_threshold
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "create_plan",
            route=state.get("route"),
            selected_document_id=state.get("selected_document_id"),
        )
        plan = self.planner.create_plan(state)
        deterministic_confidence = self._plan_confidence(plan)
        llm_enabled = bool(
            state.get("llm_planning_enabled")
            and self.llm_plan_proposer is not None
            and self.tool_registry is not None
        )

        if plan is not None and (
            not llm_enabled or deterministic_confidence >= self.deterministic_confidence_threshold
        ):
            return build_accepted_plan_patch(
                state=state,
                recorder=self.recorder,
                token=token,
                plan=plan,
                planning_source="deterministic",
                planning_warnings=[],
                raw_llm_plan=None,
                diagnostics={
                    "deterministic_attempted": True,
                    "deterministic_confidence": deterministic_confidence,
                    "llm_planning_enabled": llm_enabled,
                    "llm_attempted": False,
                },
            )

        if llm_enabled:
            assert self.llm_plan_proposer is not None
            assert self.tool_registry is not None
            llm_patch = attempt_llm_plan(
                state=state,
                token=token,
                deterministic_confidence=deterministic_confidence,
                llm_plan_proposer=self.llm_plan_proposer,
                tool_registry=self.tool_registry,
                plan_parser=self.plan_parser,
                plan_validator=self.plan_validator,
                plan_repair=self.plan_repair,
                plan_policy=self.plan_policy,
                recorder=self.recorder,
            )
            if llm_patch is not None:
                return llm_patch

        if plan is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=True,
                fallback_reason="planner_returned_none",
                diagnostics={
                    "reason": "No deterministic multi-step plan matched.",
                    "deterministic_attempted": True,
                    "deterministic_confidence": deterministic_confidence,
                    "llm_planning_enabled": llm_enabled,
                    "llm_attempted": llm_enabled,
                },
            )
            return {
                "route": RouteType.ANSWER_QUESTION.value,
                "execution_plan": None,
                "validated_plan": None,
                "plan_steps": [],
                "plan_results": {
                    "plan_success": None,
                    "fallback_reason": "planner_returned_none",
                },
                "planning_source": "failed",
                "planning_errors": [],
                "planning_warnings": [],
                "raw_llm_plan": None,
                "trace": extend_trace(state["trace"], trace_entry),
            }

        return build_accepted_plan_patch(
            state=state,
            recorder=self.recorder,
            token=token,
            plan=plan,
            planning_source="deterministic",
            planning_warnings=[
                (
                    "Deterministic plan confidence was below the LLM threshold, "
                    "but LLM planning was unavailable so the deterministic plan was retained."
                )
            ],
            raw_llm_plan=None,
            diagnostics={
                "deterministic_attempted": True,
                "deterministic_confidence": deterministic_confidence,
                "llm_planning_enabled": llm_enabled,
                "llm_attempted": False,
            },
        )

    @staticmethod
    def _plan_confidence(plan) -> float:
        if plan is None:
            return 0.0
        raw_confidence = plan.diagnostics.get("planner_confidence", 1.0)
        try:
            return float(raw_confidence)
        except (TypeError, ValueError):
            return 1.0

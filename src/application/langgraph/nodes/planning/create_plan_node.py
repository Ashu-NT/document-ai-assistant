from __future__ import annotations

from typing import Any

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.planning import (
    DeterministicPlanner,
    LLMPlanProposer,
    PlanParser,
    PlanPolicy,
    PlanRepair,
    PlanValidator,
)
from src.application.langgraph.routing import RouteDecision, RouteType
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
            return self._accepted_plan_patch(
                state=state,
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
            llm_patch = self._attempt_llm_plan(
                state=state,
                token=token,
                deterministic_confidence=deterministic_confidence,
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

        return self._accepted_plan_patch(
            state=state,
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

    def _attempt_llm_plan(
        self,
        *,
        state: AgentState,
        token,
        deterministic_confidence: float,
    ) -> dict[str, Any] | None:
        assert self.llm_plan_proposer is not None
        assert self.tool_registry is not None

        raw_llm_plan = self.llm_plan_proposer.propose(
            state,
            self._reconstruct_route_decision(state),
            self.tool_registry,
            self.plan_policy,
        )
        parse_result = self.plan_parser.parse(raw_llm_plan)
        if not parse_result.success or parse_result.plan is None:
            return self._failed_plan_patch(
                state=state,
                token=token,
                raw_llm_plan=raw_llm_plan,
                deterministic_confidence=deterministic_confidence,
                errors=[parse_result.message or "Failed to parse LLM planning output."],
                warnings=[],
                diagnostics={
                    "deterministic_attempted": True,
                    "deterministic_confidence": deterministic_confidence,
                    "llm_planning_enabled": True,
                    "llm_attempted": True,
                    "parse_success": False,
                    "parse_error_code": parse_result.error_code,
                    "llm_diagnostics": self.llm_plan_proposer.last_diagnostics,
                    "parse_diagnostics": parse_result.diagnostics,
                },
            )

        validation_result = self.plan_validator.validate(
            parse_result.plan,
            policy=self.plan_policy,
            tool_registry=self.tool_registry,
            state=state,
        )
        if validation_result.success and validation_result.validated_plan is not None:
            return self._accepted_plan_patch(
                state=state,
                token=token,
                plan=validation_result.validated_plan,
                planning_source=validation_result.validated_plan.source,
                planning_warnings=list(validation_result.warnings),
                raw_llm_plan=raw_llm_plan,
                diagnostics={
                    "deterministic_attempted": True,
                    "deterministic_confidence": deterministic_confidence,
                    "llm_planning_enabled": True,
                    "llm_attempted": True,
                    "parse_success": True,
                    "validation_success": True,
                    "llm_diagnostics": self.llm_plan_proposer.last_diagnostics,
                    "parse_diagnostics": parse_result.diagnostics,
                    "validation_diagnostics": validation_result.diagnostics,
                },
            )

        repair_result = self.plan_repair.repair(
            parse_result.plan,
            policy=self.plan_policy,
            tool_registry=self.tool_registry,
            state=state,
        )
        if repair_result.plan is not None and repair_result.repaired:
            repaired_validation = self.plan_validator.validate(
                repair_result.plan,
                policy=self.plan_policy,
                tool_registry=self.tool_registry,
                state=state,
            )
            if repaired_validation.success and repaired_validation.validated_plan is not None:
                return self._accepted_plan_patch(
                    state=state,
                    token=token,
                    plan=repaired_validation.validated_plan,
                    planning_source=repaired_validation.validated_plan.source,
                    planning_warnings=[
                        *validation_result.errors,
                        *validation_result.warnings,
                        *repair_result.changes,
                        *repaired_validation.warnings,
                    ],
                    raw_llm_plan=raw_llm_plan,
                    diagnostics={
                        "deterministic_attempted": True,
                        "deterministic_confidence": deterministic_confidence,
                        "llm_planning_enabled": True,
                        "llm_attempted": True,
                        "parse_success": True,
                        "validation_success": False,
                        "repair_attempted": True,
                        "repair_success": True,
                        "llm_diagnostics": self.llm_plan_proposer.last_diagnostics,
                        "parse_diagnostics": parse_result.diagnostics,
                        "validation_diagnostics": validation_result.diagnostics,
                        "repair_changes": repair_result.changes,
                        "repaired_validation_diagnostics": repaired_validation.diagnostics,
                    },
                )

        return self._failed_plan_patch(
            state=state,
            token=token,
            raw_llm_plan=raw_llm_plan,
            deterministic_confidence=deterministic_confidence,
            errors=[
                *validation_result.errors,
                *repair_result.errors,
            ],
            warnings=[
                *validation_result.warnings,
                *repair_result.changes,
            ],
            diagnostics={
                "deterministic_attempted": True,
                "deterministic_confidence": deterministic_confidence,
                "llm_planning_enabled": True,
                "llm_attempted": True,
                "parse_success": True,
                "validation_success": False,
                "repair_attempted": True,
                "repair_success": False,
                "llm_diagnostics": self.llm_plan_proposer.last_diagnostics,
                "parse_diagnostics": parse_result.diagnostics,
                "validation_diagnostics": validation_result.diagnostics,
                "repair_changes": repair_result.changes,
            },
        )

    def _accepted_plan_patch(
        self,
        *,
        state: AgentState,
        token,
        plan,
        planning_source: str,
        planning_warnings: list[str],
        raw_llm_plan: str | None,
        diagnostics: dict[str, Any],
    ) -> dict[str, Any]:
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "plan_id": plan.plan_id,
                "plan_goal": plan.goal,
                "step_count": plan.step_count,
                "requires_document": plan.requires_document,
                "plan_kind": plan.diagnostics.get("plan_kind"),
                "planning_source": planning_source,
                **diagnostics,
            },
        )
        patch: dict[str, object] = {
            "execution_plan": plan.to_dict(),
            "validated_plan": plan.to_dict(),
            "plan_steps": [step.to_dict() for step in plan.steps],
            "plan_results": {
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "plan_success": None,
                "step_outputs": {},
                "plan_kind": plan.diagnostics.get("plan_kind"),
            },
            "planning_source": planning_source,
            "planning_errors": [],
            "planning_warnings": planning_warnings,
            "raw_llm_plan": raw_llm_plan if state.get("show_raw_plan") else None,
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

    def _failed_plan_patch(
        self,
        *,
        state: AgentState,
        token,
        raw_llm_plan: str,
        deterministic_confidence: float,
        errors: list[str],
        warnings: list[str],
        diagnostics: dict[str, Any],
    ) -> dict[str, Any]:
        response_text = (
            "I could not build a safe multi-step plan for that request. "
            "Please narrow the request or specify the document to use."
        )
        if self._needs_document_clarification(state):
            response_text = (
                "I could not safely build a multi-step plan without a document. "
                "Please select a document first or pass --document."
            )
        trace_entry = self.recorder.finish_node(
            token,
            success=False,
            error_code="plan_validation_failed",
            diagnostics={
                "planning_source": "failed",
                "deterministic_attempted": True,
                "deterministic_confidence": deterministic_confidence,
                "error_count": len(errors),
                "warning_count": len(warnings),
                **diagnostics,
            },
        )
        patch: dict[str, Any] = {
            "execution_plan": None,
            "validated_plan": None,
            "plan_steps": [],
            "planning_source": "failed",
            "planning_errors": [error for error in errors if error],
            "planning_warnings": [warning for warning in warnings if warning],
            "raw_llm_plan": raw_llm_plan if state.get("show_raw_plan") else None,
            "trace": extend_trace(state["trace"], trace_entry),
        }
        if self._needs_document_clarification(state):
            patch.update(
                {
                    "needs_clarification": True,
                    "clarification_message": response_text,
                    "clarification_question": "Which document should I use?",
                    "response_text": response_text,
                }
            )
            return patch

        patch["error"] = {
            "message": response_text,
            "error_code": "plan_validation_failed",
            "diagnostics": {
                "planning_errors": [error for error in errors if error],
                "planning_warnings": [warning for warning in warnings if warning],
            },
        }
        patch["response_text"] = response_text
        return patch

    @staticmethod
    def _plan_confidence(plan) -> float:
        if plan is None:
            return 0.0
        raw_confidence = plan.diagnostics.get("planner_confidence", 1.0)
        try:
            return float(raw_confidence)
        except (TypeError, ValueError):
            return 1.0

    @staticmethod
    def _needs_document_clarification(state: AgentState) -> bool:
        return not (
            state.get("document_id")
            or state.get("selected_document_id")
            or state.get("document_query")
        )

    @staticmethod
    def _reconstruct_route_decision(state: AgentState) -> RouteDecision:
        diagnostics = CreatePlanNode._route_diagnostics(state)
        route_value = state.get("route") or RouteType.UNKNOWN.value
        try:
            route_type = RouteType(route_value)
        except ValueError:
            route_type = RouteType.UNKNOWN
        return RouteDecision(
            route_type=route_type,
            confidence=_float_value(diagnostics.get("confidence"), default=0.0),
            reason=_string_value(diagnostics.get("reason"))
            or "Reconstructed from routed graph state.",
            extracted_document_query=state.get("document_query"),
            extracted_question=state.get("question"),
            requires_document=bool(diagnostics.get("requires_document", False)),
            uses_current_document=bool(diagnostics.get("uses_current_document", False)),
            is_compound=bool(diagnostics.get("is_compound", False)),
            requires_plan=bool(
                diagnostics.get("requires_plan", route_type == RouteType.PLANNED_TASK)
            ),
            plan_hint=_string_value(diagnostics.get("plan_hint")),
        )

    @staticmethod
    def _route_diagnostics(state: AgentState) -> dict[str, Any]:
        for entry in reversed(list(state.get("trace", []))):
            if not isinstance(entry, dict):
                continue
            if entry.get("node_name") != "route_request":
                continue
            diagnostics = entry.get("diagnostics")
            if isinstance(diagnostics, dict):
                return diagnostics
        return {}


def _float_value(value: object, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None

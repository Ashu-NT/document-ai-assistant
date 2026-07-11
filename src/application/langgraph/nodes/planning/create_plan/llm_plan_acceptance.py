from __future__ import annotations

from typing import Any

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.planning.create_plan.plan_patch_builder import (
    build_accepted_plan_patch,
    build_failed_plan_patch,
)
from src.application.langgraph.nodes.planning.create_plan.route_decision_reconstructor import (
    reconstruct_route_decision,
)
from src.application.langgraph.planning import (
    LLMPlanProposer,
    PlanParser,
    PlanPolicy,
    PlanRepair,
    PlanValidator,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


def attempt_llm_plan(
    *,
    state: AgentState,
    token,
    deterministic_confidence: float,
    llm_plan_proposer: LLMPlanProposer,
    tool_registry: ToolRegistry,
    plan_parser: PlanParser,
    plan_validator: PlanValidator,
    plan_repair: PlanRepair,
    plan_policy: PlanPolicy,
    recorder: GraphRunRecorder,
) -> dict[str, Any] | None:
    raw_llm_plan = llm_plan_proposer.propose(
        state,
        reconstruct_route_decision(state),
        tool_registry,
        plan_policy,
    )
    parse_result = plan_parser.parse(raw_llm_plan)
    if not parse_result.success or parse_result.plan is None:
        return build_failed_plan_patch(
            state=state,
            recorder=recorder,
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
                "llm_diagnostics": llm_plan_proposer.last_diagnostics,
                "parse_diagnostics": parse_result.diagnostics,
            },
        )

    validation_result = plan_validator.validate(
        parse_result.plan,
        policy=plan_policy,
        tool_registry=tool_registry,
        state=state,
    )
    if validation_result.success and validation_result.validated_plan is not None:
        return build_accepted_plan_patch(
            state=state,
            recorder=recorder,
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
                "llm_diagnostics": llm_plan_proposer.last_diagnostics,
                "parse_diagnostics": parse_result.diagnostics,
                "validation_diagnostics": validation_result.diagnostics,
            },
        )

    repair_result = plan_repair.repair(
        parse_result.plan,
        policy=plan_policy,
        tool_registry=tool_registry,
        state=state,
    )
    if repair_result.plan is not None and repair_result.repaired:
        repaired_validation = plan_validator.validate(
            repair_result.plan,
            policy=plan_policy,
            tool_registry=tool_registry,
            state=state,
        )
        if repaired_validation.success and repaired_validation.validated_plan is not None:
            return build_accepted_plan_patch(
                state=state,
                recorder=recorder,
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
                    "llm_diagnostics": llm_plan_proposer.last_diagnostics,
                    "parse_diagnostics": parse_result.diagnostics,
                    "validation_diagnostics": validation_result.diagnostics,
                    "repair_changes": repair_result.changes,
                    "repaired_validation_diagnostics": repaired_validation.diagnostics,
                },
            )

    return build_failed_plan_patch(
        state=state,
        recorder=recorder,
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
            "llm_diagnostics": llm_plan_proposer.last_diagnostics,
            "parse_diagnostics": parse_result.diagnostics,
            "validation_diagnostics": validation_result.diagnostics,
            "repair_changes": repair_result.changes,
        },
    )

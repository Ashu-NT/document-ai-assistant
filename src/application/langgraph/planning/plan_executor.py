from __future__ import annotations

from typing import Any

from src.application.guardrails import GuardrailContext
from src.application.guardrails.services import PreToolGuardrailService
from src.application.langgraph.common import GraphError
from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import build_error, serialize_tool_result
from src.application.langgraph.planning.combined_answer_formatter import format_combined_answer
from src.application.langgraph.planning.execution.plan_step_request_builder import (
    build_plan_step_request,
    resolved_document_id,
)
from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_step_state_updater import (
    apply_failure_state,
    apply_success_state,
    store_canonical_tool_result,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.common import ToolResult


class PlanExecutor:
    def __init__(
        self,
        *,
        pre_tool_guardrail_service: PreToolGuardrailService | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.pre_tool_guardrail_service = (
            pre_tool_guardrail_service or PreToolGuardrailService()
        )
        self.recorder = recorder or GraphRunRecorder()

    def execute(
        self,
        plan: ExecutionPlan,
        state: AgentState,
        tool_registry: ToolRegistry,
    ) -> AgentState:
        next_state: AgentState = dict(state)  # type: ignore[assignment]
        tool_results = dict(next_state.get("tool_results", {}))
        trace = list(next_state.get("trace", []))
        step_outputs: dict[str, dict[str, Any]] = {}
        completed_dependencies: set[str] = set()
        executed_steps: list[str] = []
        failed_step: str | None = None
        plan_success = True

        for step in plan.steps:
            if not self._dependencies_satisfied(step.depends_on, completed_dependencies):
                failed_step = step.step_id
                plan_success = False
                next_state["error"] = build_error(
                    message="Plan step dependencies were not satisfied.",
                    error_code="plan_dependency_failed",
                    diagnostics={
                        "plan_id": plan.plan_id,
                        "step_id": step.step_id,
                        "depends_on": step.depends_on,
                    },
                )
                break

            token = self.recorder.start_node(
                "plan_step",
                route=next_state.get("route"),
                tool_name=step.tool_name,
                plan_id=plan.plan_id,
                plan_goal=plan.goal,
                step_id=step.step_id,
                selected_document_id=resolved_document_id(next_state),
            )
            try:
                result = self._execute_step(
                    step=step,
                    state=next_state,
                    tool_registry=tool_registry,
                    step_outputs=step_outputs,
                )
            except GraphError as exc:
                result = ToolResult.fail(
                    exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                )
            serialized = serialize_tool_result(result)
            serialized["tool_name"] = step.tool_name
            serialized["step_id"] = step.step_id
            tool_results[step.output_key] = serialized
            store_canonical_tool_result(
                tool_results=tool_results,
                tool_name=step.tool_name,
                serialized=serialized,
            )
            step_outputs[step.output_key] = {
                "tool_name": step.tool_name,
                "success": serialized["success"],
                "data": serialized.get("data"),
                "message": serialized.get("message"),
                "error_code": serialized.get("error_code"),
            }
            if step.step_id != step.output_key:
                step_outputs[step.step_id] = step_outputs[step.output_key]
            executed_steps.append(step.step_id)
            trace.append(
                self.recorder.finish_node(
                    token,
                    success=result.success,
                    error_code=result.error_code,
                    diagnostics=result.diagnostics,
                )
            )

            next_state["tool_results"] = tool_results
            next_state["trace"] = trace
            apply_success_state(
                next_state=next_state,
                step=step,
                result=result,
                step_outputs=step_outputs,
            )

            if result.success:
                completed_dependencies.add(step.output_key)
                completed_dependencies.add(step.step_id)
                continue

            failed_step = step.step_id
            plan_success = False
            if apply_failure_state(
                next_state=next_state,
                step=step,
                result=result,
            ):
                break
            if step.required:
                break

        next_state["execution_plan"] = plan.to_dict()
        next_state["plan_steps"] = [step.to_dict() for step in plan.steps]
        next_state["plan_success"] = plan_success
        next_state["failed_plan_step"] = failed_step
        next_state["plan_results"] = serialize_graph_value(
            {
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "executed_steps": executed_steps,
                "failed_step": failed_step,
                "plan_success": plan_success,
                "step_outputs": step_outputs,
                "plan_kind": plan.diagnostics.get("plan_kind"),
                "final_response_text": next_state.get("response_text"),
            }
        )
        return next_state

    @staticmethod
    def _dependencies_satisfied(
        depends_on: list[str],
        completed_dependencies: set[str],
    ) -> bool:
        return all(dependency in completed_dependencies for dependency in depends_on)

    def _execute_step(
        self,
        *,
        step: Any,
        state: AgentState,
        tool_registry: ToolRegistry,
        step_outputs: dict[str, dict[str, Any]],
    ) -> ToolResult:
        if step.tool_name == "format_combined_answer":
            return format_combined_answer(step=step, step_outputs=step_outputs)

        guardrail_result = self.pre_tool_guardrail_service.check(
            GuardrailContext(
                user_input=state.get("user_input") or "",
                query_text=state.get("user_input") or "",
                route=state.get("route"),
                document_id=resolved_document_id(state),
                selected_document_id=state.get("selected_document_id"),
                requested_tool=step.tool_name,
                requested_action=f"execute:{step.tool_name}",
                tool_arguments=dict(step.args or {}),
                runtime_mode="graph_plan",
            ),
            available_tool_names=tool_registry.names(),
        )
        if not guardrail_result.allowed:
            return ToolResult.fail(
                guardrail_result.user_message or guardrail_result.reason,
                error_code="guardrail_blocked",
                diagnostics={"guardrail_result": guardrail_result.to_dict()},
            )

        tool = tool_registry.require(step.tool_name)
        request = build_plan_step_request(
            step=step,
            state=state,
            step_outputs=step_outputs,
        )
        return tool.run(request)

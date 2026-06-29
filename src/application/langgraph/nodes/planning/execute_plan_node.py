from __future__ import annotations

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import build_error
from src.application.langgraph.planning import ExecutionPlan, PlanExecutor
from src.application.langgraph.state import AgentState


class ExecutePlanNode:
    def __init__(
        self,
        plan_executor: PlanExecutor,
        tool_registry: ToolRegistry,
    ) -> None:
        self.plan_executor = plan_executor
        self.tool_registry = tool_registry

    def __call__(self, state: AgentState) -> dict:
        raw_plan = state.get("execution_plan")
        if not isinstance(raw_plan, dict):
            return {
                "error": build_error(
                    message="Execution plan was missing from state.",
                    error_code="plan_missing",
                    diagnostics={},
                )
            }

        plan = ExecutionPlan.from_dict(raw_plan)
        return self.plan_executor.execute(plan, state, self.tool_registry)

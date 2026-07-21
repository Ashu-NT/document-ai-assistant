from __future__ import annotations

from collections.abc import Sequence

from src.application.langgraph.planning.models.execution_plan import ExecutionPlan
from src.application.langgraph.planning.models.plan_step import PlanStep
from src.shared.ids import IdGenerator


def build_plan_step(
    id_generator: IdGenerator,
    *,
    tool_name: str,
    description: str,
    output_key: str,
    input_key: str | None = None,
    args: dict[str, object] | None = None,
    depends_on: list[str] | None = None,
    required: bool = True,
) -> PlanStep:
    return PlanStep(
        step_id=id_generator.new_id("step"),
        tool_name=tool_name,
        description=description,
        input_key=input_key,
        output_key=output_key,
        args=dict(args or {}),
        depends_on=list(depends_on or []),
        required=required,
    )


def build_document_resolution_steps(
    id_generator: IdGenerator,
    *,
    document_query: str | None,
    document_id: str | None,
) -> list[PlanStep]:
    if document_id or not document_query:
        return []
    return [
        build_plan_step(
            id_generator,
            tool_name="find_document",
            description="Resolve the requested document before executing the remaining steps.",
            output_key="resolved_document",
            args={"query_text": document_query},
        )
    ]


def build_execution_plan(
    id_generator: IdGenerator,
    *,
    goal: str,
    steps: Sequence[PlanStep],
    reason: str,
    requires_document: bool,
    document_id: str | None,
    document_title: str | None,
    diagnostics: dict[str, object],
) -> ExecutionPlan:
    resolved_diagnostics = {
        "planner_confidence": 0.95,
        **diagnostics,
    }
    return ExecutionPlan(
        plan_id=id_generator.new_id("plan"),
        goal=goal,
        steps=list(steps),
        reason=reason,
        requires_document=requires_document,
        document_id=document_id,
        document_title=document_title,
        diagnostics=resolved_diagnostics,
    )

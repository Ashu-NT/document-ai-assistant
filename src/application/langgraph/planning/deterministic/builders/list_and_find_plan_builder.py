from __future__ import annotations

from src.application.langgraph.planning.models.execution_plan import ExecutionPlan
from src.application.langgraph.planning.models.plan_step_factory import (
    build_execution_plan,
    build_plan_step,
)
from src.shared.ids import IdGenerator


def _extract_open_target(normalized_input: str) -> str | None:
    for marker in ("open ", "open document ", "find document "):
        if marker in normalized_input:
            tail = normalized_input.split(marker, 1)[1].strip()
            if tail:
                return tail
    return None


def build_list_and_find_plan(
    id_generator: IdGenerator,
    *,
    normalized_input: str,
    document_query: str | None,
    document_id: str | None,
    document_title: str | None,
) -> ExecutionPlan:
    target_query = document_query or _extract_open_target(normalized_input)
    steps = [
        build_plan_step(
            id_generator,
            tool_name="list_documents",
            description="List available documents.",
            output_key="listed_documents",
        ),
        build_plan_step(
            id_generator,
            tool_name="find_document",
            description="Find the requested document from the available list.",
            output_key="resolved_document",
            args={"query_text": target_query},
            depends_on=["listed_documents"],
        ),
    ]
    return build_execution_plan(
        id_generator,
        goal=normalized_input,
        steps=steps,
        reason="Detected a compound request that first lists the corpus and then resolves a target document.",
        requires_document=False,
        document_id=document_id,
        document_title=document_title or target_query,
        diagnostics={"plan_kind": "list_and_find"},
    )

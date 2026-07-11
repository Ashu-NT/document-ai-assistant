from __future__ import annotations

from src.application.langgraph.common.structured_entity_query_detector import (
    detect_structured_entity_type,
)
from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_step_factory import (
    build_document_resolution_steps,
    build_execution_plan,
    build_plan_step,
)
from src.shared.ids import IdGenerator


def extract_structured_entity_type(normalized_input: str) -> str | None:
    return detect_structured_entity_type(normalized_input)


def build_structured_entity_plan(
    id_generator: IdGenerator,
    *,
    normalized_input: str,
    entity_type: str,
    document_query: str | None,
    document_id: str | None,
    document_title: str | None,
) -> ExecutionPlan:
    retrieve_args: dict[str, object] = {
        "entity_type": entity_type,
        "query_text": normalized_input,
    }
    if document_id:
        retrieve_args["document_id"] = document_id

    plan_steps = build_document_resolution_steps(
        id_generator, document_query=document_query, document_id=document_id
    )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="retrieve_structured_entities",
            description=f"Look up extracted {entity_type} rows matching the request.",
            output_key="structured_entity_hits",
            args=retrieve_args,
        )
    )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="answer_question",
            description="Answer the question using the retrieved structured entity data.",
            output_key="answer",
            input_key="structured_entity_hits",
            args={"question": normalized_input},
            depends_on=["structured_entity_hits"],
        )
    )

    return build_execution_plan(
        id_generator,
        goal=normalized_input,
        steps=plan_steps,
        reason="Detected a structured-entity lookup request requiring extracted row retrieval.",
        requires_document=bool(document_id or document_query),
        document_id=document_id,
        document_title=document_title or document_query,
        diagnostics={
            "plan_kind": "structured_entity_lookup",
            "entity_type": entity_type,
        },
    )

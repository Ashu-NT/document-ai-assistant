from __future__ import annotations

from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_step_factory import (
    build_document_resolution_steps,
    build_execution_plan,
    build_plan_step,
)
from src.shared.ids import IdGenerator


def _build_follow_up_question(normalized_input: str) -> str:
    if "maintenance" in normalized_input:
        return "What maintenance tasks are described in this document?"
    if "specification" in normalized_input:
        return "What specifications are available in this document?"
    if "safety" in normalized_input:
        return "What safety warnings are described in this document?"
    return normalized_input


def _extract_retrieval_subject(normalized_input: str) -> str:
    for marker in ("retrieve evidence for ", "show context for ", "summarize evidence for "):
        if marker in normalized_input:
            tail = normalized_input.split(marker, 1)[1]
            tail = tail.split(" and ", 1)[0].strip()
            if tail:
                return tail
    return normalized_input


def _build_summary_question(subject: str) -> str:
    return f"Summarize the evidence for {subject}."


def build_explore_and_answer_plan(
    id_generator: IdGenerator,
    *,
    normalized_input: str,
    document_query: str | None,
    document_id: str | None,
    document_title: str | None,
) -> ExecutionPlan:
    plan_steps = build_document_resolution_steps(
        id_generator, document_query=document_query, document_id=document_id
    )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="explore_document",
            description="Explore the selected document.",
            output_key="exploration",
        )
    )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="answer_question",
            description="Answer the requested follow-up question against the same document.",
            output_key="answer",
            args={"question": _build_follow_up_question(normalized_input)},
        )
    )
    return build_execution_plan(
        id_generator,
        goal=normalized_input,
        steps=plan_steps,
        reason="Detected a compound request that needs document exploration plus grounded answering.",
        requires_document=True,
        document_id=document_id,
        document_title=document_title or document_query,
        diagnostics={"plan_kind": "explore_answer"},
    )


def build_retrieve_and_answer_plan(
    id_generator: IdGenerator,
    *,
    normalized_input: str,
    document_query: str | None,
    document_id: str | None,
    document_title: str | None,
) -> ExecutionPlan:
    plan_steps = build_document_resolution_steps(
        id_generator, document_query=document_query, document_id=document_id
    )
    retrieval_question = _extract_retrieval_subject(normalized_input)
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="retrieve_chunks",
            description="Retrieve evidence chunks for the requested topic.",
            output_key="retrieved_evidence",
            args={"query_text": retrieval_question},
        )
    )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="answer_question",
            description="Summarize the retrieved evidence as an answer.",
            input_key="retrieved_evidence",
            output_key="answer",
            args={"question": _build_summary_question(retrieval_question)},
            depends_on=["retrieved_evidence"],
        )
    )
    return build_execution_plan(
        id_generator,
        goal=normalized_input,
        steps=plan_steps,
        reason="Detected a compound request that needs retrieval followed by deterministic answer generation.",
        requires_document=True,
        document_id=document_id,
        document_title=document_title or document_query,
        diagnostics={"plan_kind": "retrieve_answer"},
    )

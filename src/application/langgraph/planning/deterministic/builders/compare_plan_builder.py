from __future__ import annotations

from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_step_factory import (
    build_document_resolution_steps,
    build_execution_plan,
    build_plan_step,
)
from src.shared.ids import IdGenerator

_COMPARISON_TOPICS: tuple[tuple[str, str, str], ...] = (
    ("specification", "Specifications", "What specifications are available in this document?"),
    ("maintenance", "Maintenance tasks", "What maintenance tasks are described in this document?"),
    ("safety", "Safety warnings", "What safety warnings are described in this document?"),
    ("procedure", "Procedures", "What procedures are described in this document?"),
    ("troubleshooting", "Troubleshooting", "What troubleshooting information is described in this document?"),
)


def _comparison_topics(normalized_input: str) -> list[tuple[str, str, str]]:
    topics: list[tuple[int, tuple[str, str, str]]] = []
    for topic in _COMPARISON_TOPICS:
        marker = topic[0]
        index = normalized_input.find(marker)
        if index >= 0:
            topics.append((index, topic))
    topics.sort(key=lambda item: item[0])
    resolved = [topic for _, topic in topics]
    if len(resolved) >= 2:
        return resolved
    return [
        _COMPARISON_TOPICS[0],
        _COMPARISON_TOPICS[1],
    ]


def build_compare_plan(
    id_generator: IdGenerator,
    *,
    normalized_input: str,
    document_query: str | None,
    document_id: str | None,
    document_title: str | None,
) -> ExecutionPlan:
    comparison_topics = _comparison_topics(normalized_input)
    plan_steps = build_document_resolution_steps(
        id_generator, document_query=document_query, document_id=document_id
    )
    for index, (_, label, question) in enumerate(comparison_topics[:2], start=1):
        output_key = f"answer_{index}"
        plan_steps.append(
            build_plan_step(
                id_generator,
                tool_name="answer_question",
                description=f"Answer the {label.lower()} part of the comparison.",
                output_key=output_key,
                args={"question": question, "section_label": label},
            )
        )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="format_combined_answer",
            description="Combine both grounded answers into a deterministic comparison response.",
            output_key="combined_answer",
            depends_on=["answer_1", "answer_2"],
            args={
                "section_labels": [topic[1] for topic in comparison_topics[:2]],
                "comparison_title": "Comparison",
            },
        )
    )
    return build_execution_plan(
        id_generator,
        goal=normalized_input,
        steps=plan_steps,
        reason="Detected a comparison request that needs multiple grounded answer steps.",
        requires_document=True,
        document_id=document_id,
        document_title=document_title or document_query,
        diagnostics={
            "plan_kind": "compare_answers",
            "comparison_labels": [topic[1] for topic in comparison_topics[:2]],
        },
    )

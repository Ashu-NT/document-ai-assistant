from __future__ import annotations

from collections.abc import Iterable

from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.formatting.renderers.support import (
    StructuredContextSourceIndex,
    simplify_section_path,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerStructuredEntity,
    StructuredAnswerContext,
)


class ProcedureStepsRenderer:
    def render(
        self,
        *,
        answer_intent: AnswerIntent | None,
        structured_context: StructuredAnswerContext | None,
    ) -> str | None:
        if answer_intent != AnswerIntent.PROCEDURE_STEPS:
            return None
        if structured_context is None:
            return None

        source_index = StructuredContextSourceIndex.from_context(structured_context)
        procedures = _collect_procedures(structured_context, source_index)
        if not procedures:
            return None

        lines: list[str] = []
        for index, procedure in enumerate(procedures, start=1):
            lines.append(f"{index}. {procedure['title']}")
            if procedure["component"]:
                lines.append(f"   Component: {procedure['component']}")
            if procedure["section"]:
                lines.append(f"   Section: {procedure['section']}")
            if procedure["pages"]:
                lines.append(f"   Pages: {procedure['pages']}")
            lines.append("")
            for step_number, step in enumerate(procedure["steps"], start=1):
                lines.append(f"   {step_number}. {step}")
            if index < len(procedures):
                lines.append("")
        return "\n".join(lines).strip()


def _collect_procedures(
    structured_context: StructuredAnswerContext,
    source_index: StructuredContextSourceIndex,
) -> list[dict[str, object]]:
    procedures: list[dict[str, object]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()

    for entity in structured_context.entities_of_type("procedure"):
        candidate = _build_procedure_candidate(
            title=str(entity.fields.get("title") or "").strip(),
            steps=_coerce_steps(entity.fields.get("steps")),
            component=_string_or_none(entity.fields.get("component_name")),
            pages=source_index.page_label_for_chunk_id(entity.source_chunk_id),
            section=source_index.section_label_for_chunk_id(entity.source_chunk_id),
        )
        _append_candidate(procedures, seen, candidate)

    for task in structured_context.entities_of_type("maintenance_task"):
        for relationship in task.relationships:
            if relationship.target_entity_type != "procedure":
                continue
            fields = relationship.target_entity_fields
            candidate = _build_procedure_candidate(
                title=str(fields.get("title") or "").strip(),
                steps=_coerce_steps(fields.get("steps")),
                component=_string_or_none(fields.get("component_name")),
                pages=source_index.page_label_for_chunk_id(
                    _string_or_none(fields.get("source_chunk_id"))
                ),
                section=source_index.section_label_for_chunk_id(
                    _string_or_none(fields.get("source_chunk_id"))
                ),
            )
            _append_candidate(procedures, seen, candidate)

    return procedures


def _build_procedure_candidate(
    *,
    title: str,
    steps: list[str],
    component: str | None,
    pages: str | None,
    section: str | None,
) -> dict[str, object] | None:
    if not title or not steps:
        return None
    return {
        "title": title,
        "steps": steps,
        "component": component,
        "pages": pages,
        "section": simplify_section_path(section),
    }


def _append_candidate(
    procedures: list[dict[str, object]],
    seen: set[tuple[str, tuple[str, ...]]],
    candidate: dict[str, object] | None,
) -> None:
    if candidate is None:
        return
    key = (
        str(candidate["title"]).lower(),
        tuple(str(step).lower() for step in candidate["steps"]),
    )
    if key in seen:
        return
    seen.add(key)
    procedures.append(candidate)


def _coerce_steps(value: object) -> list[str]:
    if not isinstance(value, Iterable) or isinstance(value, str):
        return []
    steps = []
    for item in value:
        text = str(item or "").strip()
        if text:
            steps.append(text)
    return steps


def _string_or_none(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None

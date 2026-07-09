from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.question_answering.answer_context.models.answer_relationship import (
    AnswerRelationship,
)


@dataclass(slots=True)
class AnswerStructuredEntity:
    """A resolved structured entity (manufacturer, procedure, spare part,
    etc.), typed generically by `entity_type` rather than one dedicated
    dataclass per entity type -- see plan section 9.2. A consumer wanting
    "procedure_entries" or "specification_entries" filters
    `StructuredAnswerContext.entities_of_type("procedure")` instead of
    reading a separately-populated list that could drift out of sync with
    this one, and a type with no current entities (e.g. "certification",
    which has no structured-extraction path in this codebase) never needs
    a permanently-empty dedicated field."""

    entity_type: str
    entity_id: str
    fields: dict[str, object] = field(default_factory=dict)
    source_chunk_id: str | None = None
    relationships: list[AnswerRelationship] = field(default_factory=list)

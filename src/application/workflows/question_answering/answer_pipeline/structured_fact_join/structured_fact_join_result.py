from __future__ import annotations

from dataclasses import dataclass, field

from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentDecision,
)
from src.application.workflows.question_answering.answer_context import (
    StructuredAnswerContext,
)
from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class StructuredFactJoinResult:
    chunks: list[RetrievedChunk]
    structured_context: StructuredAnswerContext | None
    intent_decision: AnswerIntentDecision | None
    resolved_identifiers: list[Identifier] = field(default_factory=list)
    resolved_structured_entities: list[dict] = field(default_factory=list)

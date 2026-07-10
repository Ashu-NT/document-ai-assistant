from dataclasses import dataclass, field
from typing import Any

from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


@dataclass(slots=True)
class ReferenceNote:
    """A model-supplied claim-to-source attribution (plan section 9.6
    sections/reference_notes redesign). `source_number` is the model's raw,
    1-based "SOURCE {n}" reference; `chunk_id` is resolved once, by
    AnswerGenerationService against the sources actually used for this
    generation, and is None when source_number didn't match a real one --
    that None is the signal CitationGuardrail checks for."""

    note_id: str
    claim_text: str
    source_number: int
    chunk_id: str | None = None


@dataclass(slots=True)
class AnswerSection:
    """An optional structured breakdown of answer_text into a headed block,
    pointing at the reference_notes that support it. Not a replacement for
    answer_text -- both may be present."""

    heading: str
    body: str
    reference_note_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GeneratedAnswer:
    answer_text: str
    citations: list[Citation]
    cited_chunk_ids: list[str]
    prompt_version: str

    model_name: str | None = None
    confidence: float | None = None
    raw_model_output: str | None = None
    metadata: ModelProcessingMetadata | None = None
    answer_intent: AnswerIntent | None = None
    limitation_note: str | None = None
    sections: list[AnswerSection] = field(default_factory=list)
    reference_notes: list[ReferenceNote] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

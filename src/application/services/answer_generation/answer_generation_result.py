from dataclasses import dataclass, field
from typing import Any

from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


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
    diagnostics: dict[str, Any] = field(default_factory=dict)

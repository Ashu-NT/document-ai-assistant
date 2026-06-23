from dataclasses import dataclass, field

from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation


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

from dataclasses import dataclass, field

from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class AnswerGenerationRequest:
    question: str
    context_chunks: list[RetrievedChunk]
    query_intent: str | None = None
    document_id: str | None = None
    require_citations: bool = True
    max_context_chunks: int | None = None

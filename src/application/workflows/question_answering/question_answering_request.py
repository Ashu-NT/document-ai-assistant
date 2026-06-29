from dataclasses import dataclass

from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class QuestionAnsweringRequest:
    question: str
    document_id: str | None = None
    document_alias: str | None = None
    top_k: int | None = None
    include_context: bool = False
    allow_answer_generation: bool = False
    require_citations: bool = True
    context_override_chunks: list[RetrievedChunk] | None = None
    retry_query: str | None = None

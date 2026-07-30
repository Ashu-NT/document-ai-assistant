from dataclasses import dataclass, field

from src.domain.common import ChunkType, DocumentType


@dataclass(slots=True)
class RetrievalQuery:
    query_id: str
    query_text: str

    document_types: list[DocumentType] = field(default_factory=list)
    chunk_types: list[ChunkType] = field(default_factory=list)

    detected_identifiers: list[str] = field(default_factory=list)

    document_id: str | None = None

    top_k: int = 5
    use_dense: bool = True
    use_keyword: bool = True
    use_sql: bool = True

    rewritten_query: str | None = None

    analyzed: bool = False

    detected_intent: str | None = None

    intent_best_score: int | None = None
    intent_runner_up_score: int | None = None
    intent_score_gap: int | None = None
    intent_confidence: float | None = None
    intent_runner_up: str | None = None

    def effective_query(self) -> str:
        return self.rewritten_query or self.query_text

    def has_identifiers(self) -> bool:
        return bool(self.detected_identifiers)

    def is_intent_contested(self) -> bool:
        return self.intent_runner_up is not None and self.intent_score_gap == 0
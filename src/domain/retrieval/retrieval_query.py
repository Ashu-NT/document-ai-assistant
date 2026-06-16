from dataclasses import dataclass, field

from src.domain.common import ChunkType, DocumentType


@dataclass(slots=True)
class RetrievalQuery:
    query_id: str
    query_text: str

    document_types: list[DocumentType] = field(default_factory=list)
    chunk_types: list[ChunkType] = field(default_factory=list)

    detected_identifiers: list[str] = field(default_factory=list)

    top_k: int = 5
    use_dense: bool = True
    use_keyword: bool = True
    use_sql: bool = True

    rewritten_query: str | None = None

    def effective_query(self) -> str:
        return self.rewritten_query or self.query_text

    def has_identifiers(self) -> bool:
        return bool(self.detected_identifiers)
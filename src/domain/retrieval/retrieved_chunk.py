from dataclasses import dataclass, field

from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval.citation import Citation


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str

    content: str

    score: float
    retrieval_source: str

    chunk_type: ChunkType = ChunkType.UNKNOWN
    section_id: str | None = None
    section_path: list[str] = field(default_factory=list)

    source: SourceLocation = field(default_factory=SourceLocation)
    citation: Citation | None = None

    metadata: dict[str, str] = field(default_factory=dict)

    def is_relevant(self, threshold: float) -> bool:
        return self.score >= threshold

    def section_path_text(self) -> str:
        return " > ".join(self.section_path)
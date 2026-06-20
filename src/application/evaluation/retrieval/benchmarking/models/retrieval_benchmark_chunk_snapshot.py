from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievalBenchmarkChunkSnapshot:
    chunk_id: str
    document_id: str
    retrieval_source: str
    score: float
    chunk_type: str
    section_id: str | None = None
    section_path: list[str] = field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None
    content_preview: str = ""

    @property
    def section_path_text(self) -> str:
        return " > ".join(self.section_path)

    def covers_page(self, page_number: int | None) -> bool:
        if page_number is None:
            return False
        if self.page_start is None and self.page_end is None:
            return False
        page_start = self.page_start if self.page_start is not None else self.page_end
        page_end = self.page_end if self.page_end is not None else self.page_start
        if page_start is None or page_end is None:
            return False
        return page_start <= page_number <= page_end

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "retrieval_source": self.retrieval_source,
            "score": round(self.score, 4),
            "chunk_type": self.chunk_type,
            "section_id": self.section_id,
            "section_path": list(self.section_path),
            "section_path_text": self.section_path_text,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "content_preview": self.content_preview,
        }

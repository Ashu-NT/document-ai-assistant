from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievalBenchmarkResolutionCandidate:
    chunk_id: str
    section_id: str | None
    section_path: list[str] = field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None
    sequence_number: int = 0
    score: float = 0.0
    passage_overlap: float = 0.0
    exact_passage_match: bool = False
    exact_section_path_match: bool = False
    page_match: bool = False
    viable: bool = False
    content_preview: str = ""

    @property
    def section_path_text(self) -> str:
        return " > ".join(self.section_path)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "section_id": self.section_id,
            "section_path": list(self.section_path),
            "section_path_text": self.section_path_text,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "sequence_number": self.sequence_number,
            "score": round(self.score, 4),
            "passage_overlap": round(self.passage_overlap, 4),
            "exact_passage_match": self.exact_passage_match,
            "exact_section_path_match": self.exact_section_path_match,
            "page_match": self.page_match,
            "viable": self.viable,
            "content_preview": self.content_preview,
        }

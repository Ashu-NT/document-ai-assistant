from dataclasses import dataclass, field

from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.domain.retrieval.retrieval_query import RetrievalQuery


@dataclass(slots=True)
class RetrievalResult:
    result_id: str
    query: RetrievalQuery

    chunks: list[RetrievedChunk] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)

    used_dense: bool = False
    used_keyword: bool = False
    used_sql: bool = False

    total_candidates: int = 0

    def has_results(self) -> bool:
        return bool(self.chunks)

    def top_chunks(self, limit: int) -> list[RetrievedChunk]:
        return sorted(
            self.chunks,
            key=lambda chunk: chunk.score,
            reverse=True,
        )[:limit]

    def has_enough_evidence(self, min_chunks: int) -> bool:
        return len(self.chunks) >= min_chunks

    def best_score(self) -> float | None:
        if not self.chunks:
            return None
        return max(chunk.score for chunk in self.chunks)
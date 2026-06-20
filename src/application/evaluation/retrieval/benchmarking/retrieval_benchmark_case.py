from dataclasses import dataclass, field

from src.domain.retrieval import RetrievalQuery


@dataclass(slots=True)
class RetrievalBenchmarkCase:
    query: RetrievalQuery
    expected_chunk_ids: list[str] = field(default_factory=list)
    expected_section_paths: list[list[str]] = field(default_factory=list)
    description: str | None = None

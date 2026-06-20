from dataclasses import dataclass, field

from src.application.evaluation.retrieval_benchmark_case import (
    RetrievalBenchmarkCase,
)


@dataclass(slots=True)
class RetrievalBenchmarkCaseResult:
    case: RetrievalBenchmarkCase
    returned_chunk_ids: list[str] = field(default_factory=list)
    returned_section_paths: list[list[str]] = field(default_factory=list)
    hit: bool = False
    reciprocal_rank: float = 0.0
    relevant_hits: int = 0

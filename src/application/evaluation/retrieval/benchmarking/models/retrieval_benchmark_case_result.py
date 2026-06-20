from dataclasses import dataclass, field

from src.application.evaluation.retrieval.benchmarking.models.retrieval_benchmark_case import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.models.retrieval_benchmark_chunk_snapshot import (
    RetrievalBenchmarkChunkSnapshot,
)


@dataclass(slots=True)
class RetrievalBenchmarkCaseResult:
    case: RetrievalBenchmarkCase
    returned_chunk_ids: list[str] = field(default_factory=list)
    returned_section_paths: list[list[str]] = field(default_factory=list)
    returned_chunks: list[RetrievalBenchmarkChunkSnapshot] = field(
        default_factory=list
    )
    context_chunk_ids: list[str] = field(default_factory=list)
    context_section_paths: list[list[str]] = field(default_factory=list)
    context_chunks: list[RetrievalBenchmarkChunkSnapshot] = field(
        default_factory=list
    )
    hit: bool = False
    reciprocal_rank: float = 0.0
    relevant_hits: int = 0
    matched_rank: int | None = None
    context_hit: bool = False
    context_reciprocal_rank: float = 0.0
    context_relevant_hits: int = 0
    context_matched_rank: int | None = None
    exact_section_path_hit: bool = False
    context_exact_section_path_hit: bool = False
    evidence_completeness: float = 0.0
    used_context_expansion: bool = False

    def recall_at(self, limit: int) -> bool:
        return self.matched_rank is not None and self.matched_rank <= limit

    def context_recall_at(self, limit: int) -> bool:
        return (
            self.context_matched_rank is not None
            and self.context_matched_rank <= limit
        )

    @property
    def meets_expected_rank_target(self) -> bool:
        if self.case.expected_rank_target is None:
            return self.hit
        if self.matched_rank is None:
            return False
        return self.matched_rank <= self.case.expected_rank_target.max_rank

    @property
    def identifier_top_1_hit(self) -> bool:
        query_type = self.case.query_type
        if query_type is None or not query_type.is_identifier_focused():
            return False
        return self.matched_rank == 1

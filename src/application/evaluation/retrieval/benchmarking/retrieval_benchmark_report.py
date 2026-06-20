from dataclasses import dataclass, field

from src.application.evaluation.retrieval.benchmarking.retrieval_benchmark_case_result import (
    RetrievalBenchmarkCaseResult,
)


@dataclass(slots=True)
class RetrievalBenchmarkReport:
    case_results: list[RetrievalBenchmarkCaseResult] = field(default_factory=list)

    @property
    def case_count(self) -> int:
        return len(self.case_results)

    @property
    def hit_rate(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(1 for result in self.case_results if result.hit) / len(
            self.case_results
        )

    @property
    def mean_reciprocal_rank(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(result.reciprocal_rank for result in self.case_results) / len(
            self.case_results
        )

    @property
    def average_relevant_hits(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(result.relevant_hits for result in self.case_results) / len(
            self.case_results
        )

from dataclasses import dataclass, field

from src.application.evaluation.retrieval.benchmarking.models.retrieval_benchmark_case_result import (
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

    @property
    def context_hit_rate(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(1 for result in self.case_results if result.context_hit) / len(
            self.case_results
        )

    @property
    def context_mean_reciprocal_rank(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(
            result.context_reciprocal_rank for result in self.case_results
        ) / len(self.case_results)

    @property
    def recall_at_1(self) -> float:
        return self._recall_at(1)

    @property
    def recall_at_3(self) -> float:
        return self._recall_at(3)

    @property
    def recall_at_5(self) -> float:
        return self._recall_at(5)

    @property
    def recall_at_10(self) -> float:
        return self._recall_at(10)

    @property
    def context_recall_at_1(self) -> float:
        return self._context_recall_at(1)

    @property
    def context_recall_at_3(self) -> float:
        return self._context_recall_at(3)

    @property
    def context_recall_at_5(self) -> float:
        return self._context_recall_at(5)

    @property
    def context_recall_at_10(self) -> float:
        return self._context_recall_at(10)

    @property
    def identifier_top_1_accuracy(self) -> float:
        identifier_results = [
            result
            for result in self.case_results
            if result.case.query_type is not None
            and result.case.query_type.is_identifier_focused()
        ]
        if not identifier_results:
            return 0.0
        return sum(
            1 for result in identifier_results if result.identifier_top_1_hit
        ) / len(identifier_results)

    @property
    def section_path_accuracy(self) -> float:
        section_results = [
            result
            for result in self.case_results
            if result.case.expected_section_paths
        ]
        if not section_results:
            return 0.0
        return sum(
            1 for result in section_results if result.exact_section_path_hit
        ) / len(section_results)

    @property
    def evidence_completeness_rate(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(
            result.evidence_completeness for result in self.case_results
        ) / len(self.case_results)

    @property
    def rank_target_satisfaction_rate(self) -> float:
        if not self.case_results:
            return 0.0
        return sum(
            1
            for result in self.case_results
            if result.meets_expected_rank_target
        ) / len(self.case_results)

    def _recall_at(self, limit: int) -> float:
        if not self.case_results:
            return 0.0
        return sum(
            1 for result in self.case_results if result.recall_at(limit)
        ) / len(self.case_results)

    def _context_recall_at(self, limit: int) -> float:
        if not self.case_results:
            return 0.0
        return sum(
            1 for result in self.case_results if result.context_recall_at(limit)
        ) / len(self.case_results)

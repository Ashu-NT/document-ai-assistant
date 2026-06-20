from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkReport,
)


class RetrievalBenchmarkReportSummaryBuilder:
    def build_overview(
        self,
        report: RetrievalBenchmarkReport,
    ) -> dict[str, float | int]:
        return {
            "case_count": report.case_count,
            "hit_rate": report.hit_rate,
            "context_hit_rate": report.context_hit_rate,
            "mean_reciprocal_rank": report.mean_reciprocal_rank,
            "context_mean_reciprocal_rank": report.context_mean_reciprocal_rank,
            "average_relevant_hits": report.average_relevant_hits,
            "recall_at_1": report.recall_at_1,
            "recall_at_3": report.recall_at_3,
            "recall_at_5": report.recall_at_5,
            "recall_at_10": report.recall_at_10,
            "context_recall_at_1": report.context_recall_at_1,
            "context_recall_at_3": report.context_recall_at_3,
            "context_recall_at_5": report.context_recall_at_5,
            "context_recall_at_10": report.context_recall_at_10,
            "identifier_top_1_accuracy": report.identifier_top_1_accuracy,
            "section_path_accuracy": report.section_path_accuracy,
            "evidence_completeness_rate": report.evidence_completeness_rate,
            "rank_target_satisfaction_rate": (
                report.rank_target_satisfaction_rate
            ),
        }

    def build_document_family_breakdown(
        self,
        report: RetrievalBenchmarkReport,
    ) -> list[dict[str, float | int | str]]:
        grouped_results: dict[str, list[RetrievalBenchmarkCaseResult]] = {}

        for case_result in report.case_results:
            label = case_result.case.expected_document_family or "unknown"
            grouped_results.setdefault(label, []).append(case_result)

        return self._build_breakdown_rows(grouped_results)

    def build_query_type_breakdown(
        self,
        report: RetrievalBenchmarkReport,
    ) -> list[dict[str, float | int | str]]:
        grouped_results: dict[str, list[RetrievalBenchmarkCaseResult]] = {}

        for case_result in report.case_results:
            label = (
                case_result.case.query_type.value
                if case_result.case.query_type is not None
                else "unknown"
            )
            grouped_results.setdefault(label, []).append(case_result)

        return self._build_breakdown_rows(grouped_results)

    def _build_breakdown_rows(
        self,
        grouped_results: dict[str, list[RetrievalBenchmarkCaseResult]],
    ) -> list[dict[str, float | int | str]]:
        return [
            self._build_breakdown_row(label, grouped_results[label])
            for label in sorted(grouped_results)
        ]

    def _build_breakdown_row(
        self,
        label: str,
        case_results: list[RetrievalBenchmarkCaseResult],
    ) -> dict[str, float | int | str]:
        subset_report = RetrievalBenchmarkReport(case_results=list(case_results))
        return {
            "label": label,
            "case_count": subset_report.case_count,
            "hit_rate": subset_report.hit_rate,
            "context_hit_rate": subset_report.context_hit_rate,
            "mean_reciprocal_rank": subset_report.mean_reciprocal_rank,
            "recall_at_3": subset_report.recall_at_3,
            "rank_target_satisfaction_rate": (
                subset_report.rank_target_satisfaction_rate
            ),
        }

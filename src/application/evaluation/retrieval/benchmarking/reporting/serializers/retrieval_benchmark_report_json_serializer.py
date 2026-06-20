from typing import Any

from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkReport,
)
from src.application.evaluation.retrieval.benchmarking.reporting.diagnostics import (
    RetrievalBenchmarkFailureDiagnosticBuilder,
)
from src.application.evaluation.retrieval.benchmarking.reporting.summaries import (
    RetrievalBenchmarkReportSummaryBuilder,
)


class RetrievalBenchmarkReportJsonSerializer:
    def __init__(
        self,
        *,
        summary_builder: RetrievalBenchmarkReportSummaryBuilder | None = None,
        failure_diagnostic_builder: (
            RetrievalBenchmarkFailureDiagnosticBuilder | None
        ) = None,
    ) -> None:
        self.summary_builder = (
            summary_builder or RetrievalBenchmarkReportSummaryBuilder()
        )
        self.failure_diagnostic_builder = (
            failure_diagnostic_builder
            or RetrievalBenchmarkFailureDiagnosticBuilder()
        )

    def serialize(
        self,
        report: RetrievalBenchmarkReport,
    ) -> dict[str, Any]:
        return {
            "summary": self.summary_builder.build_overview(report),
            "document_family_breakdown": (
                self.summary_builder.build_document_family_breakdown(report)
            ),
            "query_type_breakdown": (
                self.summary_builder.build_query_type_breakdown(report)
            ),
            "case_results": [
                self._serialize_case_result(case_result)
                for case_result in report.case_results
            ],
        }

    def _serialize_case_result(
        self,
        case_result: RetrievalBenchmarkCaseResult,
    ) -> dict[str, Any]:
        case = case_result.case
        return {
            "case_id": case.case_id,
            "query_text": case.query_text,
            "query_type": (
                case.query_type.value
                if case.query_type is not None
                else None
            ),
            "priority": (
                case.priority.value
                if case.priority is not None
                else None
            ),
            "expected_rank_target": (
                case.expected_rank_target.value
                if case.expected_rank_target is not None
                else None
            ),
            "expected_document_alias": case.expected_document_alias,
            "expected_document_family": case.expected_document_family,
            "expected_file_name": case.expected_file_name,
            "expected_section_path_text": case.expected_section_path_text,
            "expected_section_paths": [
                list(section_path)
                for section_path in case.expected_section_paths
            ],
            "expected_page": case.expected_page,
            "expected_relevant_passage": case.expected_relevant_passage,
            "expected_chunk_ids": list(case.expected_chunk_ids),
            "notes": case.notes,
            "anchor": {
                "hit": case_result.hit,
                "matched_rank": case_result.matched_rank,
                "reciprocal_rank": case_result.reciprocal_rank,
                "relevant_hits": case_result.relevant_hits,
                "exact_section_path_hit": case_result.exact_section_path_hit,
                "recall_at_1": case_result.recall_at(1),
                "recall_at_3": case_result.recall_at(3),
                "recall_at_5": case_result.recall_at(5),
                "recall_at_10": case_result.recall_at(10),
                "returned_chunk_ids": list(case_result.returned_chunk_ids),
                "returned_section_paths": [
                    list(section_path)
                    for section_path in case_result.returned_section_paths
                ],
                "chunks": [
                    chunk.to_dict()
                    for chunk in case_result.returned_chunks
                ],
            },
            "context": {
                "hit": case_result.context_hit,
                "matched_rank": case_result.context_matched_rank,
                "reciprocal_rank": case_result.context_reciprocal_rank,
                "relevant_hits": case_result.context_relevant_hits,
                "exact_section_path_hit": (
                    case_result.context_exact_section_path_hit
                ),
                "recall_at_1": case_result.context_recall_at(1),
                "recall_at_3": case_result.context_recall_at(3),
                "recall_at_5": case_result.context_recall_at(5),
                "recall_at_10": case_result.context_recall_at(10),
                "used_context_expansion": case_result.used_context_expansion,
                "returned_chunk_ids": list(case_result.context_chunk_ids),
                "returned_section_paths": [
                    list(section_path)
                    for section_path in case_result.context_section_paths
                ],
                "chunks": [
                    chunk.to_dict()
                    for chunk in case_result.context_chunks
                ],
            },
            "evaluation": {
                "evidence_completeness": case_result.evidence_completeness,
                "meets_expected_rank_target": (
                    case_result.meets_expected_rank_target
                ),
                "identifier_top_1_hit": case_result.identifier_top_1_hit,
            },
            "diagnostics": {
                "failure_reasons": (
                    self.failure_diagnostic_builder.build_failure_reasons(
                        case_result
                    )
                ),
            },
        }

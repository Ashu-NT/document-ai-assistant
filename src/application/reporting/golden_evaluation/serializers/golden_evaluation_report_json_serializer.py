from dataclasses import asdict
from typing import Any

from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationOutcome,
)
from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (
    IngestionExpectationCaseResult,
)
from src.application.evaluation.ingestion.models.cross_reference_evaluation_result import (
    CrossReferenceEvaluationResult,
)
from src.application.evaluation.ingestion.models.chunk_token_budget_result import (
    ChunkTokenBudgetEvaluationResult,
)


class GoldenEvaluationReportJsonSerializer:
    def serialize(self, report: GoldenEvaluationReport) -> dict[str, Any]:
        return {
            "run_metadata": asdict(report.run_metadata),
            "corpus_coverage": asdict(report.corpus_coverage),
            "summary": {
                "structural_passed_count": report.structural_passed_count,
                "structural_failed_count": report.structural_failed_count,
                "structural_assertion_failure_count": report.structural_assertion_failure_count,
                "chunk_invariant_failure_count": report.chunk_invariant_failure_count,
                "chunk_token_budget_hard_violation_count": (
                    report.chunk_token_budget_hard_violation_count
                ),
                "chunk_token_budget_oversized_indivisible_count": (
                    report.chunk_token_budget_oversized_indivisible_count
                ),
                "chunk_token_budget_unresolved_aliases": list(
                    report.chunk_token_budget_unresolved_aliases
                ),
                "documents_not_evaluated": [
                    outcome.alias for outcome in report.documents_not_evaluated
                ],
            },
            "cross_reference_type_metrics": [
                {
                    "reference_type": metrics.reference_type,
                    "true_positives": metrics.true_positives,
                    "false_negatives": metrics.false_negatives,
                    "false_positives": metrics.false_positives,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1": metrics.f1,
                    "exhaustive_document_count": metrics.exhaustive_document_count,
                    "non_exhaustive_document_count": metrics.non_exhaustive_document_count,
                }
                for metrics in report.cross_reference_type_metrics
            ],
            "reconciliation_outcome_counts": report.reconciliation_outcome_counts,
            "documents": [
                self._serialize_document_outcome(outcome)
                for outcome in report.document_outcomes
            ],
        }

    def _serialize_document_outcome(
        self, outcome: GoldenDocumentEvaluationOutcome
    ) -> dict[str, Any]:
        return {
            "alias": outcome.alias,
            "status": outcome.status.value,
            "detail": outcome.detail,
            "structural": (
                self._serialize_structural_result(outcome.structural_result)
                if outcome.structural_result is not None
                else None
            ),
            "cross_references": (
                self._serialize_cross_reference_result(outcome.cross_reference_result)
                if outcome.cross_reference_result is not None
                else None
            ),
            "chunk_token_budget": (
                self._serialize_chunk_token_budget_result(
                    outcome.chunk_token_budget_result
                )
                if outcome.chunk_token_budget_result is not None
                else None
            ),
        }

    @staticmethod
    def _serialize_structural_result(
        result: IngestionExpectationCaseResult,
    ) -> dict[str, Any]:
        return {
            "case_id": result.case_id,
            "passed": result.passed,
            "assertions": [
                {
                    "name": assertion.name,
                    "expected": assertion.expected,
                    "actual": assertion.actual,
                    "passed": assertion.passed,
                }
                for assertion in result.assertions
            ],
        }

    @staticmethod
    def _serialize_cross_reference_result(
        result: CrossReferenceEvaluationResult,
    ) -> dict[str, Any]:
        return {
            "case_id": result.case_id,
            "type_metrics": [
                {
                    "reference_type": metrics.reference_type,
                    "exhaustive": metrics.exhaustive,
                    "true_positives": metrics.true_positives,
                    "false_negatives": metrics.false_negatives,
                    "false_positives": metrics.false_positives,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1": metrics.f1,
                    "matched_clues": list(metrics.matched_clues),
                    "missed_clues": list(metrics.missed_clues),
                }
                for metrics in result.type_metrics
            ],
            "reconciliation_outcome_counts": result.reconciliation_outcome_counts,
            "external_reference_clues_correctly_unresolved": (
                result.external_reference_clues_correctly_unresolved
            ),
            "external_reference_clues_incorrectly_resolved": (
                result.external_reference_clues_incorrectly_resolved
            ),
        }

    @staticmethod
    def _serialize_chunk_token_budget_result(
        result: ChunkTokenBudgetEvaluationResult,
    ) -> dict[str, Any]:
        return {
            "resolved": result.resolved,
            "profile": result.profile,
            "effective_budget": result.effective_budget,
            "unresolved_reason": result.unresolved_reason,
            "max_observed_tokens": result.max_observed_tokens,
            "normal_count": result.normal_count,
            "oversized_indivisible_count": result.oversized_indivisible_count,
            "hard_budget_violation_count": result.hard_budget_violation_count,
            "passed": result.passed,
            "oversized_chunks": [
                {
                    "chunk_id": diagnostic.chunk_id,
                    "token_count": diagnostic.token_count,
                    "budget": diagnostic.budget,
                    "status": diagnostic.status.value,
                    "chunk_type": diagnostic.chunk_type,
                    "table_id": diagnostic.table_id,
                    "table_row_start": diagnostic.table_row_start,
                    "table_row_end": diagnostic.table_row_end,
                }
                for diagnostic in result.oversized_chunks
            ],
        }


__all__ = ["GoldenEvaluationReportJsonSerializer"]

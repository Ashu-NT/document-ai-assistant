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


__all__ = ["GoldenEvaluationReportJsonSerializer"]

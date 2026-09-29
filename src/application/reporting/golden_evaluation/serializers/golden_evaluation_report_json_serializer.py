from dataclasses import asdict
from typing import Any

from src.application.evaluation.classification.classification_golden_metrics import (
    ClassificationGoldenMetrics,
)
from src.application.evaluation.classification.golden_classification_document_result import (
    GoldenClassificationDocumentResult,
)
from src.application.evaluation.extraction.extraction_golden_metrics import (
    aggregate_extraction_metrics,
    build_bucket_keyed_results,
    collect_applicability_counts,
    summarize_buckets_by,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)
from src.application.evaluation.extraction.golden_extraction_document_result import (
    ExtractionScopeRunOutcome,
    GoldenExtractionDocumentResult,
)
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
            # Sibling to the structural/cross-reference sections above, never
            # merged with them into one combined "AI quality" score.
            "classification": self._serialize_classification(report),
            "extraction": self._serialize_extraction(report),
        }

    def _serialize_extraction(self, report) -> dict[str, Any]:
        results = report.extraction_results
        keyed = build_bucket_keyed_results(results)
        buckets = aggregate_extraction_metrics(keyed)
        applicability = collect_applicability_counts(results)

        def _metrics_table(review_status: ExtractionReviewStatus) -> list[dict[str, Any]]:
            rolled = summarize_buckets_by(buckets, only_review_status=review_status)
            return [
                {
                    "entity_type": entity_type,
                    "completeness": completeness.value,
                    "true_positive_count": bucket.true_positive_count,
                    "false_positive_count": bucket.false_positive_count,
                    "false_negative_count": bucket.false_negative_count,
                    "precision": bucket.precision,
                    "recall": bucket.recall,
                    "f1": bucket.f1,
                    "evidence_correct_count": bucket.evidence_correct_count,
                    "evidence_incorrect_count": bucket.evidence_incorrect_count,
                    "evidence_not_checked_count": bucket.evidence_not_checked_count,
                    "ambiguous_count": bucket.ambiguous_count,
                }
                for (entity_type, completeness), bucket in sorted(rolled.items())
            ]

        return {
            "applicability_counts": {
                "applicable": applicability.applicable,
                "not_applicable": applicability.not_applicable,
                "not_assessed": applicability.not_assessed,
            },
            "metrics_reviewed": _metrics_table(ExtractionReviewStatus.REVIEWED),
            "metrics_candidate_non_authoritative": _metrics_table(
                ExtractionReviewStatus.CANDIDATE
            ),
            "documents": [
                self._serialize_extraction_document_result(document_result)
                for document_result in results
            ],
        }

    @staticmethod
    def _serialize_extraction_document_result(
        document_result: GoldenExtractionDocumentResult,
    ) -> dict[str, Any]:
        return {
            "alias": document_result.alias,
            "was_evaluated": document_result.was_evaluated,
            "has_execution_failures": document_result.has_execution_failures,
            "scope_outcomes": [
                GoldenEvaluationReportJsonSerializer._serialize_extraction_scope_outcome(
                    outcome
                )
                for outcome in document_result.scope_outcomes
            ],
        }

    @staticmethod
    def _serialize_extraction_scope_outcome(
        outcome: ExtractionScopeRunOutcome,
    ) -> dict[str, Any]:
        scope = outcome.scope
        return {
            "scope": {
                "scope_type": scope.scope_type.value,
                "page_start": scope.page_start,
                "page_end": scope.page_end,
            },
            "stage_status": outcome.stage_status.value,
            "execution_error": outcome.execution_error,
            "batch_summary": (
                {
                    "batch_count": outcome.batch_summary.batch_count,
                    "parse_success_count": outcome.batch_summary.parse_success_count,
                    "parse_failure_count": outcome.batch_summary.parse_failure_count,
                    "dropped_empty_count": outcome.batch_summary.dropped_empty_count,
                    "invalid_source_chunk_id_event_count": (
                        outcome.batch_summary.invalid_source_chunk_id_event_count
                    ),
                }
                if outcome.batch_summary is not None
                else None
            ),
            "applicability_declarations": [
                {
                    "declaration_id": declaration.declaration_id,
                    "entity_type": declaration.entity_type.value,
                    "applicability": declaration.applicability.value,
                    "review_status": declaration.review_status.value,
                    "reason": declaration.reason,
                    "notes": declaration.notes,
                }
                for declaration in outcome.applicability_declarations
            ],
            "matches": [
                {
                    "outcome": match.outcome.value,
                    "entity_type": match.entity_type,
                    "group_completeness": match.group_completeness.value,
                    "group_review_status": match.group_review_status.value,
                    "case_id": (
                        match.expectation.case_id
                        if match.expectation is not None
                        else None
                    ),
                    "actual_entity_id": match.actual_entity_id,
                    "identity_fields_used": list(match.identity_fields_used),
                    "differing_fields": list(match.differing_fields),
                    "normalized_expected": match.normalized_expected,
                    "normalized_actual": match.normalized_actual,
                    "match_reason": match.match_reason,
                    "ambiguous_actual_entity_ids": list(
                        match.ambiguous_actual_entity_ids
                    ),
                    "evidence_correct": match.evidence_correct,
                    "evidence_detail": match.evidence_detail,
                }
                for match in outcome.match_results
            ],
        }

    def _serialize_classification(self, report) -> dict[str, Any]:
        return {
            "metrics": self._serialize_classification_metrics(
                report.classification_metrics
            ),
            "documents": [
                self._serialize_classification_document_result(result)
                for result in report.classification_results
            ],
        }

    @staticmethod
    def _serialize_classification_metrics(
        metrics: ClassificationGoldenMetrics,
    ) -> dict[str, Any]:
        return {
            "executed_count": metrics.executed_count,
            "execution_failed_count": metrics.execution_failed_count,
            "skipped_parsing_unavailable_count": metrics.skipped_parsing_unavailable_count,
            "unknown_count": metrics.unknown_count,
            "unknown_rate": metrics.unknown_rate,
            "low_confidence_rejected_count": metrics.low_confidence_rejected_count,
            "low_confidence_rejection_rate": metrics.low_confidence_rejection_rate,
            "confidence_count": metrics.confidence_count,
            "confidence_min": metrics.confidence_min,
            "confidence_max": metrics.confidence_max,
            "confidence_mean": metrics.confidence_mean,
            "confidence_median": metrics.confidence_median,
            "reviewed_eligible_document_count": metrics.reviewed_eligible_document_count,
            "raw_correct_count": metrics.raw_correct_count,
            "raw_accuracy": metrics.raw_accuracy,
            "accepted_count": metrics.accepted_count,
            "accepted_correct_count": metrics.accepted_correct_count,
            "accepted_classification_accuracy": metrics.accepted_classification_accuracy,
            "accuracy_among_accepted": metrics.accuracy_among_accepted,
            "ambiguous_document_count": metrics.ambiguous_document_count,
            "ambiguous_raw_match_count": metrics.ambiguous_raw_match_count,
            "confusion_matrix": metrics.confusion_matrix,
        }

    @staticmethod
    def _serialize_classification_document_result(
        result: GoldenClassificationDocumentResult,
    ) -> dict[str, Any]:
        expectation = result.expectation
        attempt = result.attempt
        return {
            "alias": result.alias,
            "stage_status": result.stage_status.value,
            "detail": result.detail,
            "execution_error": result.execution_error,
            "expectation": (
                {
                    "expected_document_type": expectation.expected_document_type.value,
                    "ambiguous": expectation.ambiguous,
                    "review_status": expectation.review_status.value,
                    "notes": expectation.notes,
                }
                if expectation is not None
                else None
            ),
            "attempt": (
                {
                    "predicted_document_type": attempt.predicted_document_type.value,
                    "predicted_label": attempt.predicted_label,
                    "confidence": attempt.confidence,
                    "confidence_threshold": attempt.confidence_threshold,
                    "passed_confidence_gate": attempt.passed_confidence_gate,
                    "validation_outcome": attempt.validation_outcome.value,
                    "model_name": attempt.model_name,
                    "rationale": attempt.rationale,
                    "processing_errors": list(
                        attempt.processing_metadata.errors
                        if attempt.processing_metadata
                        else []
                    ),
                    "prompt_version": (
                        attempt.processing_metadata.prompt_version
                        if attempt.processing_metadata
                        else None
                    ),
                }
                if attempt is not None
                else None
            ),
            "eligible_for_accuracy": result.eligible_for_accuracy,
            "raw_prediction_correct": result.raw_prediction_correct,
            "accepted_classification_correct": result.accepted_classification_correct,
            "ambiguous_raw_match": result.ambiguous_raw_match,
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
        provenance = result.provenance
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
            "baseline_provenance": (
                {
                    "parser_name": provenance.parser_name,
                    "parser_version": provenance.parser_version,
                    "conversion_fingerprint": provenance.conversion_fingerprint,
                }
                if provenance is not None and provenance.is_recorded
                else None
            ),
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

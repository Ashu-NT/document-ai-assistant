import statistics
from dataclasses import dataclass, field

from src.application.evaluation.classification.golden_classification_document_result import (
    ClassificationStageStatus,
    GoldenClassificationDocumentResult,
)
from src.domain.common import DocumentType


@dataclass(slots=True, frozen=True)
class ClassificationGoldenMetrics:
    """Deterministic, pure metrics computed from a list of already-executed
    `GoldenClassificationDocumentResult`s. Never collapsed into one
    combined score - every denominator is explicit and separately
    reportable, matching Phase 1's established convention for structural
    and cross-reference metrics.
    """

    executed_count: int
    execution_failed_count: int
    skipped_parsing_unavailable_count: int

    unknown_count: int
    unknown_rate: float | None

    low_confidence_rejected_count: int
    low_confidence_rejection_rate: float | None

    confidence_count: int
    confidence_min: float | None
    confidence_max: float | None
    confidence_mean: float | None
    confidence_median: float | None

    reviewed_eligible_document_count: int
    raw_correct_count: int
    raw_accuracy: float | None

    accepted_count: int
    accepted_correct_count: int
    accepted_classification_accuracy: float | None
    accuracy_among_accepted: float | None

    ambiguous_document_count: int
    ambiguous_raw_match_count: int

    # confusion_matrix[expected_label][predicted_label] = count. Only
    # populated from `eligible_for_accuracy` documents (reviewed,
    # non-ambiguous, successful attempt) - see eligibility rules in
    # GoldenClassificationDocumentResult.
    confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)


def compute_classification_golden_metrics(
    document_results: list[GoldenClassificationDocumentResult],
) -> ClassificationGoldenMetrics:
    executed = [
        r for r in document_results if r.stage_status == ClassificationStageStatus.EVALUATED
    ]
    execution_failed_count = sum(
        1
        for r in document_results
        if r.stage_status == ClassificationStageStatus.EXECUTION_FAILED
    )
    skipped_count = sum(
        1
        for r in document_results
        if r.stage_status == ClassificationStageStatus.SKIPPED_PARSING_UNAVAILABLE
    )

    executed_attempts = [r.attempt for r in executed if r.attempt is not None]

    unknown_count = sum(
        1 for a in executed_attempts if a.predicted_document_type == DocumentType.UNKNOWN
    )
    unknown_rate = (
        unknown_count / len(executed_attempts) if executed_attempts else None
    )

    low_confidence_rejected_count = sum(
        1 for a in executed_attempts if not a.passed_confidence_gate
    )
    low_confidence_rejection_rate = (
        low_confidence_rejected_count / len(executed_attempts)
        if executed_attempts
        else None
    )

    confidences = [
        a.confidence for a in executed_attempts if a.confidence is not None
    ]
    confidence_min = min(confidences) if confidences else None
    confidence_max = max(confidences) if confidences else None
    confidence_mean = statistics.fmean(confidences) if confidences else None
    confidence_median = statistics.median(confidences) if confidences else None

    eligible = [r for r in document_results if r.eligible_for_accuracy]
    raw_correct_count = sum(1 for r in eligible if r.raw_prediction_correct)
    raw_accuracy = raw_correct_count / len(eligible) if eligible else None

    accepted = [
        r
        for r in eligible
        if r.attempt is not None and r.attempt.passed_confidence_gate
    ]
    accepted_correct_count = sum(
        1 for r in accepted if r.raw_prediction_correct
    )
    accepted_classification_accuracy = (
        accepted_correct_count / len(eligible) if eligible else None
    )
    accuracy_among_accepted = (
        accepted_correct_count / len(accepted) if accepted else None
    )

    ambiguous_results = [
        r for r in document_results if r.ambiguous_raw_match is not None
    ]
    ambiguous_raw_match_count = sum(
        1 for r in ambiguous_results if r.ambiguous_raw_match
    )

    confusion_matrix: dict[str, dict[str, int]] = {}
    for r in eligible:
        assert r.attempt is not None and r.expectation is not None
        expected_label = r.expectation.expected_document_type.value
        predicted_label = r.attempt.predicted_document_type.value
        row = confusion_matrix.setdefault(expected_label, {})
        row[predicted_label] = row.get(predicted_label, 0) + 1

    return ClassificationGoldenMetrics(
        executed_count=len(executed),
        execution_failed_count=execution_failed_count,
        skipped_parsing_unavailable_count=skipped_count,
        unknown_count=unknown_count,
        unknown_rate=unknown_rate,
        low_confidence_rejected_count=low_confidence_rejected_count,
        low_confidence_rejection_rate=low_confidence_rejection_rate,
        confidence_count=len(confidences),
        confidence_min=confidence_min,
        confidence_max=confidence_max,
        confidence_mean=confidence_mean,
        confidence_median=confidence_median,
        reviewed_eligible_document_count=len(eligible),
        raw_correct_count=raw_correct_count,
        raw_accuracy=raw_accuracy,
        accepted_count=len(accepted),
        accepted_correct_count=accepted_correct_count,
        accepted_classification_accuracy=accepted_classification_accuracy,
        accuracy_among_accepted=accuracy_among_accepted,
        ambiguous_document_count=len(ambiguous_results),
        ambiguous_raw_match_count=ambiguous_raw_match_count,
        confusion_matrix=confusion_matrix,
    )


__all__ = ["ClassificationGoldenMetrics", "compute_classification_golden_metrics"]

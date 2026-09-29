from src.application.evaluation.classification.classification_attempt import (
    ClassificationAttempt,
    ClassificationValidationOutcome,
)
from src.application.evaluation.classification.classification_expectation_case import (
    ClassificationExpectationCase,
)
from src.application.evaluation.classification.classification_golden_metrics import (
    compute_classification_golden_metrics,
)
from src.application.evaluation.classification.classification_review_status import (
    ClassificationReviewStatus,
)
from src.application.evaluation.classification.golden_classification_document_result import (
    ClassificationStageStatus,
    GoldenClassificationDocumentResult,
)
from src.domain.common import DocumentType


def _attempt(
    *,
    predicted: DocumentType = DocumentType.MANUAL,
    confidence: float | None = 0.9,
    passed_gate: bool = True,
) -> ClassificationAttempt:
    return ClassificationAttempt(
        predicted_document_type=predicted,
        predicted_label=predicted.value,
        confidence=confidence,
        rationale=None,
        processing_metadata=None,
        confidence_threshold=0.6,
        passed_confidence_gate=passed_gate,
        validation_outcome=ClassificationValidationOutcome.VALID,
        model_name="qwen3:8b",
    )


def _reviewed_case(alias: str, expected: DocumentType, ambiguous: bool = False):
    return ClassificationExpectationCase(
        document_alias=alias,
        expected_document_type=expected,
        ambiguous=ambiguous,
        review_status=ClassificationReviewStatus.REVIEWED,
    )


def _candidate_case(alias: str, expected: DocumentType, ambiguous: bool = False):
    return ClassificationExpectationCase(
        document_alias=alias,
        expected_document_type=expected,
        ambiguous=ambiguous,
        review_status=ClassificationReviewStatus.CANDIDATE,
    )


class TestZeroDocuments:
    def test_empty_input_never_crashes_and_reports_explicit_none(self) -> None:
        metrics = compute_classification_golden_metrics([])

        assert metrics.executed_count == 0
        assert metrics.unknown_rate is None
        assert metrics.low_confidence_rejection_rate is None
        assert metrics.raw_accuracy is None
        assert metrics.accepted_classification_accuracy is None
        assert metrics.accuracy_among_accepted is None
        assert metrics.confusion_matrix == {}


class TestZeroReviewedLabels:
    def test_candidate_only_corpus_yields_no_authoritative_accuracy(self) -> None:
        results = [
            GoldenClassificationDocumentResult(
                alias="doc_a",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=_candidate_case("doc_a", DocumentType.MANUAL),
                attempt=_attempt(predicted=DocumentType.MANUAL),
            )
        ]

        metrics = compute_classification_golden_metrics(results)

        # Zero reviewed labels is an acceptable, honest outcome - never
        # fabricated from candidate labels.
        assert metrics.reviewed_eligible_document_count == 0
        assert metrics.raw_accuracy is None
        assert metrics.accepted_classification_accuracy is None
        assert metrics.confusion_matrix == {}
        # But execution/confidence stats are still computed - they don't
        # need golden truth at all.
        assert metrics.executed_count == 1
        assert metrics.confidence_count == 1


class TestAccuracyAndConfusionMatrix:
    def test_mixed_correct_and_incorrect_reviewed_predictions(self) -> None:
        results = [
            GoldenClassificationDocumentResult(
                alias="doc_a",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=_reviewed_case("doc_a", DocumentType.MANUAL),
                attempt=_attempt(predicted=DocumentType.MANUAL, passed_gate=True),
            ),
            GoldenClassificationDocumentResult(
                alias="doc_b",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=_reviewed_case("doc_b", DocumentType.DATASHEET),
                attempt=_attempt(predicted=DocumentType.MANUAL, passed_gate=True),
            ),
        ]

        metrics = compute_classification_golden_metrics(results)

        assert metrics.reviewed_eligible_document_count == 2
        assert metrics.raw_correct_count == 1
        assert metrics.raw_accuracy == 0.5
        assert metrics.confusion_matrix == {
            "manual": {"manual": 1},
            "datasheet": {"manual": 1},
        }

    def test_gate_rejected_reviewed_document_lowers_accepted_but_not_raw(self) -> None:
        results = [
            GoldenClassificationDocumentResult(
                alias="doc_a",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=_reviewed_case("doc_a", DocumentType.MANUAL),
                attempt=_attempt(predicted=DocumentType.MANUAL, passed_gate=False),
            ),
        ]

        metrics = compute_classification_golden_metrics(results)

        assert metrics.raw_correct_count == 1
        assert metrics.raw_accuracy == 1.0
        assert metrics.accepted_count == 0
        assert metrics.accepted_correct_count == 0
        # accepted_classification_accuracy denominator is the reviewed
        # ELIGIBLE count (1), not the accepted count (0) - so this must be
        # 0/1, never a 0/0 crash and never silently omitted.
        assert metrics.accepted_classification_accuracy == 0.0
        assert metrics.accuracy_among_accepted is None  # 0 accepted -> n/a

    def test_ambiguous_documents_excluded_from_confusion_matrix_but_counted_separately(
        self,
    ) -> None:
        results = [
            GoldenClassificationDocumentResult(
                alias="doc_ambiguous",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=_candidate_case(
                    "doc_ambiguous", DocumentType.REPORT, ambiguous=True
                ),
                attempt=_attempt(predicted=DocumentType.REPORT),
            ),
        ]

        metrics = compute_classification_golden_metrics(results)

        assert metrics.confusion_matrix == {}
        assert metrics.reviewed_eligible_document_count == 0
        assert metrics.ambiguous_document_count == 1
        assert metrics.ambiguous_raw_match_count == 1


class TestModelBehaviourStatsIgnoreReviewStatus:
    def test_unknown_and_low_confidence_counted_across_all_executed_documents(self) -> None:
        results = [
            GoldenClassificationDocumentResult(
                alias="doc_a",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=None,
                attempt=_attempt(predicted=DocumentType.UNKNOWN, confidence=0.9, passed_gate=True),
            ),
            GoldenClassificationDocumentResult(
                alias="doc_b",
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=None,
                attempt=_attempt(predicted=DocumentType.MANUAL, confidence=0.1, passed_gate=False),
            ),
            GoldenClassificationDocumentResult(
                alias="doc_c",
                stage_status=ClassificationStageStatus.EXECUTION_FAILED,
                expectation=None,
                execution_error="boom",
            ),
            GoldenClassificationDocumentResult(
                alias="doc_d",
                stage_status=ClassificationStageStatus.SKIPPED_PARSING_UNAVAILABLE,
                expectation=None,
            ),
        ]

        metrics = compute_classification_golden_metrics(results)

        assert metrics.executed_count == 2
        assert metrics.execution_failed_count == 1
        assert metrics.skipped_parsing_unavailable_count == 1
        assert metrics.unknown_count == 1
        assert metrics.unknown_rate == 0.5
        assert metrics.low_confidence_rejected_count == 1
        assert metrics.low_confidence_rejection_rate == 0.5
        assert metrics.confidence_count == 2
        assert metrics.confidence_min == 0.1
        assert metrics.confidence_max == 0.9
        assert metrics.confidence_mean == 0.5
        assert metrics.confidence_median == 0.5

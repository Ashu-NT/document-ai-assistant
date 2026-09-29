from src.application.evaluation.classification.classification_attempt import (
    ClassificationAttempt,
    ClassificationValidationOutcome,
)
from src.application.evaluation.classification.classification_expectation_case import (
    ClassificationExpectationCase,
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
    passed_gate: bool = True,
) -> ClassificationAttempt:
    return ClassificationAttempt(
        predicted_document_type=predicted,
        predicted_label=predicted.value,
        confidence=0.9,
        rationale=None,
        processing_metadata=None,
        confidence_threshold=0.6,
        passed_confidence_gate=passed_gate,
        validation_outcome=ClassificationValidationOutcome.VALID,
        model_name="qwen3:8b",
    )


def _expectation(
    *,
    expected: DocumentType = DocumentType.MANUAL,
    ambiguous: bool = False,
    review_status: ClassificationReviewStatus = ClassificationReviewStatus.REVIEWED,
) -> ClassificationExpectationCase:
    return ClassificationExpectationCase(
        document_alias="doc_a",
        expected_document_type=expected,
        ambiguous=ambiguous,
        review_status=review_status,
    )


class TestEligibility:
    def test_eligible_when_evaluated_reviewed_non_ambiguous_with_attempt(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(),
            attempt=_attempt(),
        )

        assert result.eligible_for_accuracy is True

    def test_not_eligible_when_candidate_only(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(review_status=ClassificationReviewStatus.CANDIDATE),
            attempt=_attempt(),
        )

        assert result.eligible_for_accuracy is False
        assert result.raw_prediction_correct is None
        assert result.accepted_classification_correct is None

    def test_not_eligible_when_ambiguous_even_if_reviewed(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(ambiguous=True),
            attempt=_attempt(),
        )

        assert result.eligible_for_accuracy is False

    def test_not_eligible_when_no_expectation(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=None,
            attempt=_attempt(),
        )

        assert result.eligible_for_accuracy is False

    def test_not_eligible_when_execution_failed(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EXECUTION_FAILED,
            expectation=_expectation(),
            attempt=None,
            execution_error="boom",
        )

        assert result.eligible_for_accuracy is False


class TestRawVsAcceptedCorrectness:
    def test_raw_correct_true_when_prediction_matches(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(expected=DocumentType.MANUAL),
            attempt=_attempt(predicted=DocumentType.MANUAL, passed_gate=True),
        )

        assert result.raw_prediction_correct is True
        assert result.accepted_classification_correct is True

    def test_raw_correct_false_when_prediction_mismatches(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(expected=DocumentType.MANUAL),
            attempt=_attempt(predicted=DocumentType.DATASHEET, passed_gate=True),
        )

        assert result.raw_prediction_correct is False
        assert result.accepted_classification_correct is False

    def test_accepted_is_false_when_gate_rejected_even_if_raw_correct(self) -> None:
        # This is the core distinction the spec calls out: a correct raw
        # prediction that was rejected by the confidence gate must NOT be
        # counted as an accepted correct classification.
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(expected=DocumentType.MANUAL),
            attempt=_attempt(predicted=DocumentType.MANUAL, passed_gate=False),
        )

        assert result.raw_prediction_correct is True
        assert result.accepted_classification_correct is False


class TestAmbiguousReporting:
    def test_ambiguous_raw_match_reports_informationally(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(
                expected=DocumentType.REPORT,
                ambiguous=True,
                review_status=ClassificationReviewStatus.CANDIDATE,
            ),
            attempt=_attempt(predicted=DocumentType.REPORT),
        )

        assert result.is_ambiguous is True
        assert result.ambiguous_raw_match is True
        assert result.eligible_for_accuracy is False

    def test_ambiguous_raw_match_is_none_for_non_ambiguous_documents(self) -> None:
        result = GoldenClassificationDocumentResult(
            alias="doc_a",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=_expectation(ambiguous=False),
            attempt=_attempt(),
        )

        assert result.ambiguous_raw_match is None

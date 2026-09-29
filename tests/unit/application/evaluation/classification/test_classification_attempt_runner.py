from src.application.evaluation.classification.classification_attempt import (
    ClassificationExecutionStatus,
    ClassificationValidationOutcome,
)
from src.application.evaluation.classification.classification_attempt_runner import (
    build_classification_attempt,
)
from src.application.validation.classification import DocumentClassificationValidator
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType, ModelProcessingMetadata


class FakeAttemptWorkflow:
    """Stands in for DocumentClassificationWorkflow - only implements
    classify_document_attempt(), proving build_classification_attempt()
    never needs the full workflow's cache/reclassification machinery."""

    def __init__(self, classification: DocumentClassification | None, error: Exception | None = None) -> None:
        self._classification = classification
        self._error = error
        self.calls = 0

    def classify_document_attempt(self, document_graph, activity_context=None):
        self.calls += 1
        if self._error is not None:
            raise self._error
        return self._classification


def _make_classification(
    *,
    document_type: DocumentType = DocumentType.MANUAL,
    confidence: float | None = 0.9,
    errors: list[str] | None = None,
) -> DocumentClassification:
    return DocumentClassification(
        document_id="doc_1",
        document_type=document_type,
        result=ClassificationResult(
            classification_id="classification_1",
            document_id="doc_1",
            predicted_label=document_type.value,
            confidence_score=confidence,
            rationale="because",
            evidence=["evidence"],
            processing_metadata=ModelProcessingMetadata(
                model_name="qwen3:8b",
                model_type="document_classification",
                confidence=confidence,
                errors=errors or [],
            ),
        ),
    )


class TestSuccessfulAttempt:
    def test_passes_gate_and_validates_when_confident(self) -> None:
        workflow = FakeAttemptWorkflow(_make_classification(confidence=0.95))

        outcome = build_classification_attempt(
            workflow, object(), document_alias="doc_a", confidence_threshold=0.6
        )

        assert outcome.execution_status == ClassificationExecutionStatus.SUCCEEDED
        assert outcome.succeeded
        assert outcome.attempt is not None
        assert outcome.attempt.passed_confidence_gate is True
        assert outcome.attempt.validation_outcome == ClassificationValidationOutcome.VALID
        assert outcome.attempt.predicted_document_type == DocumentType.MANUAL
        assert outcome.attempt.confidence == 0.95
        assert outcome.attempt.confidence_threshold == 0.6
        assert outcome.attempt.model_name == "qwen3:8b"

    def test_gate_rejected_attempt_has_no_validation_outcome(self) -> None:
        workflow = FakeAttemptWorkflow(_make_classification(confidence=0.1))

        outcome = build_classification_attempt(
            workflow, object(), document_alias="doc_a", confidence_threshold=0.6
        )

        assert outcome.attempt is not None
        assert outcome.attempt.passed_confidence_gate is False
        # Production never runs the validator on a gate-rejected result -
        # this must not fabricate a VALID/INVALID verdict for something
        # that was never actually validated.
        assert (
            outcome.attempt.validation_outcome
            == ClassificationValidationOutcome.NOT_APPLICABLE
        )

    def test_invalid_classification_is_reported_as_invalid_not_raised(self) -> None:
        # confidence_score > 1 fails DocumentClassificationValidator, but
        # build_classification_attempt must report this, never raise.
        classification = _make_classification(confidence=1.5)
        workflow = FakeAttemptWorkflow(classification)

        outcome = build_classification_attempt(
            workflow,
            object(),
            document_alias="doc_a",
            confidence_threshold=0.6,
            validator=DocumentClassificationValidator(),
        )

        assert outcome.succeeded
        assert outcome.attempt is not None
        assert outcome.attempt.passed_confidence_gate is True
        assert (
            outcome.attempt.validation_outcome
            == ClassificationValidationOutcome.INVALID
        )

    def test_unknown_prediction_with_processing_error_is_carried_through(self) -> None:
        classification = _make_classification(
            document_type=DocumentType.UNKNOWN,
            confidence=0.9,
            errors=["Unknown label returned by model: bogus"],
        )
        workflow = FakeAttemptWorkflow(classification)

        outcome = build_classification_attempt(
            workflow, object(), document_alias="doc_a", confidence_threshold=0.6
        )

        assert outcome.attempt is not None
        assert outcome.attempt.predicted_document_type == DocumentType.UNKNOWN
        assert outcome.attempt.has_processing_error is True


class TestExecutionFailure:
    def test_llm_failure_is_isolated_as_execution_failed_not_raised(self) -> None:
        workflow = FakeAttemptWorkflow(None, error=RuntimeError("ollama unreachable"))

        outcome = build_classification_attempt(
            workflow, object(), document_alias="doc_a", confidence_threshold=0.6
        )

        assert outcome.execution_status == ClassificationExecutionStatus.EXECUTION_FAILED
        assert outcome.succeeded is False
        assert outcome.attempt is None
        assert "ollama unreachable" in (outcome.execution_error or "")
        assert outcome.document_alias == "doc_a"

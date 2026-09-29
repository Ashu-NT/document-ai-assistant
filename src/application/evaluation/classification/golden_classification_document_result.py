from dataclasses import dataclass
from enum import StrEnum

from src.application.evaluation.classification.classification_attempt import (
    ClassificationAttempt,
)
from src.application.evaluation.classification.classification_expectation_case import (
    ClassificationExpectationCase,
)


class ClassificationStageStatus(StrEnum):
    """Explicit per-document outcome of the classification STAGE only -
    deliberately separate from `GoldenDocumentEvaluationStatus`, which is
    scoped to the parsing stage (see
    outputs/architecture/phase2_classification_extraction_evaluation_investigation.md
    section 19). A document only ever reaches classification once parsing
    already produced a `DocumentGraph`; if it did not, that is recorded here
    as SKIPPED_PARSING_UNAVAILABLE rather than silently omitted."""

    EVALUATED = "evaluated"
    EXECUTION_FAILED = "execution_failed"
    SKIPPED_PARSING_UNAVAILABLE = "skipped_parsing_unavailable"


@dataclass(slots=True, frozen=True)
class GoldenClassificationDocumentResult:
    """One golden-corpus document's classification-stage result, pairing a
    (possibly absent, possibly unreviewed) golden expectation with a
    (possibly failed) fresh classification attempt.

    `raw_prediction_correct`/`accepted_classification_correct` are `None`
    whenever there is no basis to compute them (no attempt, or no reviewed
    golden label) - never coerced to `False`, which would silently count as
    a wrong answer rather than "not applicable".
    """

    alias: str
    stage_status: ClassificationStageStatus
    expectation: ClassificationExpectationCase | None = None
    attempt: ClassificationAttempt | None = None
    execution_error: str | None = None
    detail: str | None = None

    @property
    def has_reviewed_expectation(self) -> bool:
        return self.expectation is not None and self.expectation.is_reviewed

    @property
    def is_ambiguous(self) -> bool:
        return self.expectation is not None and self.expectation.ambiguous

    @property
    def eligible_for_accuracy(self) -> bool:
        """The primary accuracy/confusion-matrix denominator: a REVIEWED,
        non-ambiguous golden label paired with a successful attempt."""
        return (
            self.stage_status == ClassificationStageStatus.EVALUATED
            and self.attempt is not None
            and self.has_reviewed_expectation
            and not self.is_ambiguous
        )

    @property
    def raw_prediction_correct(self) -> bool | None:
        if not self.eligible_for_accuracy:
            return None
        assert self.attempt is not None and self.expectation is not None
        return (
            self.attempt.predicted_document_type
            == self.expectation.expected_document_type
        )

    @property
    def accepted_classification_correct(self) -> bool | None:
        if not self.eligible_for_accuracy:
            return None
        assert self.attempt is not None
        if not self.attempt.passed_confidence_gate:
            return False
        return self.raw_prediction_correct

    @property
    def ambiguous_raw_match(self) -> bool | None:
        """Informational only (see `ClassificationExpectationCase.ambiguous`)
        - never folded into the primary accuracy denominator."""
        if (
            self.stage_status != ClassificationStageStatus.EVALUATED
            or self.attempt is None
            or self.expectation is None
            or not self.is_ambiguous
        ):
            return None
        return self.attempt.predicted_document_type == self.expectation.expected_document_type


__all__ = ["ClassificationStageStatus", "GoldenClassificationDocumentResult"]

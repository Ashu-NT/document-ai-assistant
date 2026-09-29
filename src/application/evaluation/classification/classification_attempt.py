from dataclasses import dataclass
from enum import StrEnum

from src.domain.common import DocumentType, ModelProcessingMetadata


class ClassificationValidationOutcome(StrEnum):
    """Mirrors production exactly: `DocumentClassificationValidator` only
    ever runs on a classification that already passed the confidence gate
    (see `DocumentClassificationWorkflow.classify_document`) - so a
    gate-rejected attempt has no validation outcome to report at all,
    rather than a fabricated one."""

    VALID = "valid"
    INVALID = "invalid"
    NOT_APPLICABLE = "not_applicable"


class ClassificationExecutionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    EXECUTION_FAILED = "execution_failed"


@dataclass(slots=True, frozen=True)
class ClassificationAttempt:
    """The full pre-confidence-gate result of one fresh classification
    attempt against a single document - the exact information
    `DocumentClassificationWorkflow.classify_document()` computes and then
    discards (`return None`) when confidence is below threshold.

    `predicted_document_type`/`predicted_label` are always populated (an
    unresolved/invalid model label already resolves to
    `DocumentType.UNKNOWN` upstream, recorded via `processing_metadata.errors`
    rather than by this model inventing a second UNKNOWN pathway).
    """

    predicted_document_type: DocumentType
    predicted_label: str
    confidence: float | None
    rationale: str | None
    processing_metadata: ModelProcessingMetadata | None
    confidence_threshold: float
    passed_confidence_gate: bool
    validation_outcome: ClassificationValidationOutcome
    model_name: str | None

    @property
    def has_processing_error(self) -> bool:
        return bool(self.processing_metadata and self.processing_metadata.errors)


@dataclass(slots=True, frozen=True)
class ClassificationAttemptOutcome:
    """Wraps a `ClassificationAttempt` with the one failure mode it cannot
    itself represent: the fresh classification call raising outright (LLM
    unavailable, malformed/unparseable response, schema validation error)
    before any attempt fields could even be computed. `attempt` is `None`
    if and only if `execution_status` is `EXECUTION_FAILED`."""

    document_alias: str
    execution_status: ClassificationExecutionStatus
    attempt: ClassificationAttempt | None = None
    execution_error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.execution_status == ClassificationExecutionStatus.SUCCEEDED


__all__ = [
    "ClassificationAttempt",
    "ClassificationAttemptOutcome",
    "ClassificationExecutionStatus",
    "ClassificationValidationOutcome",
]

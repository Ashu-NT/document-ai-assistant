from src.application.evaluation.classification.classification_attempt import (
    ClassificationAttempt,
    ClassificationAttemptOutcome,
    ClassificationExecutionStatus,
    ClassificationValidationOutcome,
)
from src.application.validation.classification import DocumentClassificationValidator
from src.application.workflows.classification import DocumentClassificationWorkflow
from src.domain.document import Document, DocumentGraph


def build_classification_attempt(
    workflow: DocumentClassificationWorkflow,
    document_graph: DocumentGraph | Document,
    *,
    document_alias: str,
    confidence_threshold: float,
    validator: DocumentClassificationValidator | None = None,
) -> ClassificationAttemptOutcome:
    """Runs one FRESH classification attempt via
    `DocumentClassificationWorkflow.classify_document_attempt()` - never
    `classify_document()` - which structurally guarantees fresh execution:
    that method never consults `allow_reclassification`/`use_cache` at all,
    rather than merely being called with those flags hardcoded off.

    `confidence_threshold` is passed in explicitly (rather than re-read
    from `classification_settings` here) so the golden report can record
    exactly which threshold gated each run, per `EvaluationRunMetadata`.

    A broad `except Exception` is deliberate here, mirroring the fault
    isolation the Phase 1 fast-regression runner already uses for one
    document's real Docling failure (`PARSE_FAILED`): a single document's
    LLM/network/schema failure must not abort evaluation of the rest of the
    corpus, but must also never disappear - it becomes an explicit,
    visible `EXECUTION_FAILED` outcome.
    """
    resolved_validator = validator or DocumentClassificationValidator()

    try:
        classification = workflow.classify_document_attempt(document_graph)
    except Exception as exc:  # noqa: BLE001 - see docstring: fault isolation
        # across an independent unit of work in a multi-document batch.
        return ClassificationAttemptOutcome(
            document_alias=document_alias,
            execution_status=ClassificationExecutionStatus.EXECUTION_FAILED,
            execution_error=repr(exc),
        )

    result = classification.result
    assert result is not None

    passed_gate = result.is_confident(confidence_threshold)
    validation_outcome = ClassificationValidationOutcome.NOT_APPLICABLE
    if passed_gate:
        validation = resolved_validator.validate(classification)
        validation_outcome = (
            ClassificationValidationOutcome.VALID
            if validation.is_valid
            else ClassificationValidationOutcome.INVALID
        )

    attempt = ClassificationAttempt(
        predicted_document_type=classification.document_type,
        predicted_label=result.predicted_label,
        confidence=result.confidence_score,
        rationale=result.rationale,
        processing_metadata=result.processing_metadata,
        confidence_threshold=confidence_threshold,
        passed_confidence_gate=passed_gate,
        validation_outcome=validation_outcome,
        model_name=(
            result.processing_metadata.model_name
            if result.processing_metadata
            else None
        ),
    )
    return ClassificationAttemptOutcome(
        document_alias=document_alias,
        execution_status=ClassificationExecutionStatus.SUCCEEDED,
        attempt=attempt,
    )


__all__ = ["build_classification_attempt"]

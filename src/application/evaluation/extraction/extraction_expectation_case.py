from dataclasses import dataclass, field

from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)


@dataclass(frozen=True, slots=True)
class ExtractedEvidenceExpectation:
    """Stable, human-reviewable evidence - never an exact chunk id (see
    `ExtractionEvaluationScope`'s docstring for why)."""

    page_start: int | None = None
    page_end: int | None = None
    section_heading: str | None = None
    requires_table_association: bool | None = None  # None = not checked


@dataclass(frozen=True, slots=True)
class ExtractionExpectationCase:
    """One expected extracted entity occurrence. Never stores a production-
    generated entity id or an exact chunk id as golden truth - only
    human-reviewable field values and evidence."""

    case_id: str
    document_alias: str
    entity_type: ExtractionEntityType
    scope: ExtractionEvaluationScope
    completeness: ExtractionCompleteness = ExtractionCompleteness.PRESENCE_ONLY
    review_status: ExtractionReviewStatus = ExtractionReviewStatus.CANDIDATE
    # Key presence is semantically meaningful: a field ABSENT from this dict
    # is NOT_ASSERTED (never compared for identity, never blocks a match); a
    # field present with value `None` is an EXPECTED_NULL assertion (the
    # actual field must also normalize empty); a field present with a real
    # string is an EXPECTED_VALUE assertion (compared normally). See
    # matchers/field_assertion.py - never call `.get(name, "")`-style code
    # against this dict where the NOT_ASSERTED/EXPECTED_NULL distinction
    # matters; use `resolve_field_assertion`/`effective_identity_fields`.
    expected_fields: dict[str, str | None] = field(default_factory=dict)
    # Only set when a document-specific reason exists to deviate from the
    # entity type's default production identity fields (see
    # matchers/entity_identity_keys.py) - rare, and never guessed.
    identity_fields_override: tuple[str, ...] | None = None
    expected_evidence: ExtractedEvidenceExpectation | None = None
    notes: str | None = None

    @property
    def is_reviewed(self) -> bool:
        return self.review_status is ExtractionReviewStatus.REVIEWED


@dataclass(frozen=True, slots=True)
class ExtractionApplicabilityDeclaration:
    """An explicit applicability judgment for one (document, entity_type,
    scope). Absence of a declaration means NOT_ASSESSED - it is never
    inferred."""

    declaration_id: str
    document_alias: str
    entity_type: ExtractionEntityType
    scope: ExtractionEvaluationScope
    applicability: ExtractionApplicability
    review_status: ExtractionReviewStatus = ExtractionReviewStatus.CANDIDATE
    reason: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if (
            self.applicability is ExtractionApplicability.NOT_APPLICABLE
            and not self.reason
        ):
            raise ValueError(
                "A NOT_APPLICABLE declaration must record a traceable "
                "reason/evidence quote."
            )

    @property
    def is_reviewed(self) -> bool:
        return self.review_status is ExtractionReviewStatus.REVIEWED


__all__ = [
    "ExtractedEvidenceExpectation",
    "ExtractionExpectationCase",
    "ExtractionApplicabilityDeclaration",
]

import pytest

from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractionApplicabilityDeclaration,
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)


class TestExpectationCaseReviewStatus:
    def test_defaults_to_candidate(self) -> None:
        case = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MANUFACTURER,
            scope=ExtractionEvaluationScope.whole_document(),
        )
        assert case.review_status is ExtractionReviewStatus.CANDIDATE
        assert not case.is_reviewed

    def test_is_reviewed_true_only_when_explicitly_reviewed(self) -> None:
        case = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MANUFACTURER,
            scope=ExtractionEvaluationScope.whole_document(),
            review_status=ExtractionReviewStatus.REVIEWED,
        )
        assert case.is_reviewed


class TestApplicabilityDeclaration:
    def test_not_applicable_requires_a_reason(self) -> None:
        with pytest.raises(ValueError):
            ExtractionApplicabilityDeclaration(
                declaration_id="d1",
                document_alias="doc",
                entity_type=ExtractionEntityType.MAINTENANCE_INTERVAL,
                scope=ExtractionEvaluationScope.whole_document(),
                applicability=ExtractionApplicability.NOT_APPLICABLE,
            )

    def test_not_applicable_with_reason_is_valid(self) -> None:
        declaration = ExtractionApplicabilityDeclaration(
            declaration_id="d1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MAINTENANCE_INTERVAL,
            scope=ExtractionEvaluationScope.whole_document(),
            applicability=ExtractionApplicability.NOT_APPLICABLE,
            reason="stated in a separate publication",
        )
        assert declaration.applicability is ExtractionApplicability.NOT_APPLICABLE

    def test_applicable_does_not_require_a_reason(self) -> None:
        declaration = ExtractionApplicabilityDeclaration(
            declaration_id="d1",
            document_alias="doc",
            entity_type=ExtractionEntityType.SPARE_PART,
            scope=ExtractionEvaluationScope.whole_document(),
            applicability=ExtractionApplicability.APPLICABLE,
        )
        assert declaration.reason is None

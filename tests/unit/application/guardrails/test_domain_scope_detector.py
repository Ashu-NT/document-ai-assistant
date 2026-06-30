from src.application.guardrails.detectors.domain_scope_detector import (
    DomainScopeDetector,
)
from src.application.guardrails.models.domain_scope_category import (
    DomainScopeCategory,
)


def test_domain_scope_detector_marks_technical_query_in_scope() -> None:
    detector = DomainScopeDetector()

    result = detector.detect("When should the hydraulic filter be replaced?")

    assert result.category == DomainScopeCategory.DOCUMENT_AGENT_SCOPE
    assert "filter" in result.matched_terms


def test_domain_scope_detector_marks_weather_query_out_of_scope() -> None:
    detector = DomainScopeDetector()

    result = detector.detect("Who won the football match yesterday?")

    assert result.category == DomainScopeCategory.OUT_OF_SCOPE_GENERAL
    assert "football" in result.matched_terms


def test_domain_scope_detector_clarifies_generic_follow_up_without_document() -> None:
    detector = DomainScopeDetector()

    result = detector.detect("What is the interval?")

    assert result.category == DomainScopeCategory.UNKNOWN_AMBIGUOUS
    assert result.requires_clarification is True


def test_domain_scope_detector_allows_generic_follow_up_with_selected_document() -> None:
    detector = DomainScopeDetector()

    result = detector.detect(
        "What is the interval?",
        selected_document_id="doc-42",
    )

    assert result.category == DomainScopeCategory.DOCUMENT_AGENT_SCOPE

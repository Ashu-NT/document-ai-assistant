from src.application.guardrails.detectors.grounding_failure_detector import (
    GroundingFailureDetector,
)


def test_grounding_failure_detector_flags_foreign_document_evidence() -> None:
    detector = GroundingFailureDetector()

    result = detector.detect(
        answer_text="The answer cites a different document.",
        evidence_chunks=[{"document_id": "doc-2", "content": "Foreign chunk"}],
        selected_document_id="doc-1",
    )

    assert result.matched is True
    assert "doc-2" in result.matched_terms


def test_grounding_failure_detector_allows_same_document_evidence() -> None:
    detector = GroundingFailureDetector()

    result = detector.detect(
        answer_text="The interval is 500 hours.",
        evidence_chunks=[{"document_id": "doc-1", "content": "Grounded chunk"}],
        selected_document_id="doc-1",
    )

    assert result.matched is False

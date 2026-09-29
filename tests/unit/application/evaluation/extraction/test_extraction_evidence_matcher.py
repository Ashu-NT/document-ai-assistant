from dataclasses import dataclass

from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractedEvidenceExpectation,
)
from src.application.evaluation.extraction.extraction_evidence_matcher import (
    evaluate_evidence,
    resolve_evidence_input,
)


@dataclass
class _FakeSourceMetadata:
    page_start: int | None = None
    page_end: int | None = None
    section_path: tuple = ()
    table_id: str | None = None


@dataclass
class _FakeSource:
    page_start: int | None = None
    page_end: int | None = None


@dataclass
class _EntityWithSourceMetadata:
    source_metadata: _FakeSourceMetadata
    source_chunk_id: str | None = None


@dataclass
class _EntityWithSourceOnly:
    source: _FakeSource
    source_chunk_id: str | None = None


@dataclass
class _EntityWithNeither:
    source_chunk_id: str | None = None


class TestResolveEvidenceInput:
    def test_prefers_source_metadata_when_present(self) -> None:
        entity = _EntityWithSourceMetadata(
            source_metadata=_FakeSourceMetadata(page_start=10, page_end=11, section_path=("Safety",))
        )
        evidence = resolve_evidence_input(entity)
        assert evidence.page_start == 10
        assert evidence.page_end == 11
        assert evidence.section_path == ("Safety",)

    def test_falls_back_to_source_when_no_source_metadata(self) -> None:
        entity = _EntityWithSourceOnly(source=_FakeSource(page_start=5, page_end=5))
        evidence = resolve_evidence_input(entity)
        assert evidence.page_start == 5
        assert evidence.page_end == 5

    def test_falls_back_to_chunk_page_lookup_for_extracted_identifier_shape(self) -> None:
        entity = _EntityWithNeither(source_chunk_id="c1")
        evidence = resolve_evidence_input(entity, chunk_page_lookup={"c1": (7, 8)})
        assert evidence.page_start == 7
        assert evidence.page_end == 8

    def test_empty_when_nothing_resolvable(self) -> None:
        entity = _EntityWithNeither(source_chunk_id=None)
        evidence = resolve_evidence_input(entity)
        assert evidence.page_start is None
        assert evidence.page_end is None


class TestEvaluateEvidence:
    def test_not_checked_when_no_expectation_declared(self) -> None:
        entity = _EntityWithSourceMetadata(source_metadata=_FakeSourceMetadata(page_start=10, page_end=10))
        evidence = resolve_evidence_input(entity)
        result = evaluate_evidence(None, evidence)
        assert not result.checked
        assert result.evidence_correct is None

    def test_exact_page_match(self) -> None:
        expected = ExtractedEvidenceExpectation(page_start=10, page_end=10)
        entity = _EntityWithSourceMetadata(source_metadata=_FakeSourceMetadata(page_start=10, page_end=10))
        result = evaluate_evidence(expected, resolve_evidence_input(entity))
        assert result.page_match is True
        assert result.evidence_correct is True

    def test_overlapping_page_range_is_correct(self) -> None:
        expected = ExtractedEvidenceExpectation(page_start=162, page_end=167)
        entity = _EntityWithSourceMetadata(source_metadata=_FakeSourceMetadata(page_start=163, page_end=164))
        result = evaluate_evidence(expected, resolve_evidence_input(entity))
        assert result.page_match is True
        assert result.evidence_correct is True

    def test_wrong_page_is_incorrect(self) -> None:
        expected = ExtractedEvidenceExpectation(page_start=12, page_end=12)
        entity = _EntityWithSourceMetadata(source_metadata=_FakeSourceMetadata(page_start=200, page_end=200))
        result = evaluate_evidence(expected, resolve_evidence_input(entity))
        assert result.page_match is False
        assert result.evidence_correct is False

    def test_correct_entity_wrong_evidence_is_a_distinct_signal_from_no_match(self) -> None:
        """Evidence-correctness must be assessable independently of whether
        the entity's own content matched - this test only exercises the
        evidence dimension itself."""
        expected = ExtractedEvidenceExpectation(page_start=1, page_end=1)
        entity = _EntityWithSourceMetadata(source_metadata=_FakeSourceMetadata(page_start=99, page_end=99))
        result = evaluate_evidence(expected, resolve_evidence_input(entity))
        assert result.checked
        assert result.evidence_correct is False
        assert "expected page" in result.detail

    def test_section_heading_match(self) -> None:
        expected = ExtractedEvidenceExpectation(section_heading="Maintenance Safety")
        entity = _EntityWithSourceMetadata(
            source_metadata=_FakeSourceMetadata(section_path=("2 Safety", "2.3 Maintenance Safety"))
        )
        result = evaluate_evidence(expected, resolve_evidence_input(entity))
        assert result.section_match is True

    def test_section_heading_mismatch(self) -> None:
        expected = ExtractedEvidenceExpectation(section_heading="Fuel System")
        entity = _EntityWithSourceMetadata(
            source_metadata=_FakeSourceMetadata(section_path=("2 Safety", "2.3 Maintenance Safety"))
        )
        result = evaluate_evidence(expected, resolve_evidence_input(entity))
        assert result.section_match is False
        assert result.evidence_correct is False

import pytest
from unittest.mock import MagicMock

from src.application.validation.document_quality import (
    DocumentQualityGate,
    DocumentQualityResult,
    QualityCheckSeverity,
)
from src.application.validation.document_quality.chunking_quality_checks import (
    check_general_chunk_ratio,
    check_chunks_have_section_paths,
    check_maintenance_headings_have_chunks,
)
from src.application.validation.document_quality.parser_quality_checks import (
    check_elements_have_pages,
    check_orphan_element_ratio,
    check_section_count,
)
from src.domain.common import ElementType, SourceLocation
from src.domain.elements import CanonicalElement
from src.application.validation.document_quality.retrieval_quality_checks import (
    check_retrieved_chunk_scores,
    check_retrieved_chunks_have_content,
)


def _make_chunk(chunk_type="general", section_path=None, score=0.8, content="some text"):
    mock = MagicMock()
    mock.chunk_type = chunk_type
    mock.section_path = section_path or ["Section 1"]
    return mock


def _make_retrieved_chunk(score=0.8, content="some text"):
    mock = MagicMock()
    mock.chunk_id = "c1"
    mock.score = score
    mock.content = content
    return mock


class TestDocumentQualityGate:
    def test_check_chunking_passes_on_empty(self):
        gate = DocumentQualityGate()
        result = gate.check_chunking("doc1", chunks=[])
        assert result.passed

    def test_check_retrieval_passes_on_empty(self):
        gate = DocumentQualityGate()
        result = gate.check_retrieval("doc1", chunks=[])
        assert result.passed


class TestGeneralChunkRatioCheck:
    def test_passes_when_general_ratio_acceptable(self):
        chunks = [_make_chunk("general")] + [_make_chunk("maintenance_procedure")] * 4
        result = check_general_chunk_ratio(chunks)
        assert result.passed

    def test_warns_when_too_many_general_chunks(self):
        chunks = [_make_chunk("general")] * 7 + [_make_chunk("maintenance_procedure")] * 3
        result = check_general_chunk_ratio(chunks)
        assert not result.passed
        assert result.severity == QualityCheckSeverity.WARNING

    def test_passes_on_empty(self):
        result = check_general_chunk_ratio([])
        assert result.passed


class TestSectionPathCheck:
    def test_warns_when_most_chunks_missing_section_path(self):
        chunks = [_make_chunk(section_path=None)] * 8 + [_make_chunk(section_path=["S1"])] * 2
        # Monkeypatch: make section_path None (not default empty)
        for c in chunks[:8]:
            c.section_path = None
        result = check_chunks_have_section_paths(chunks)
        assert not result.passed

    def test_passes_when_most_chunks_have_section_path(self):
        chunks = [_make_chunk(section_path=["Section 1"])] * 9 + [_make_chunk(section_path=None)]
        chunks[-1].section_path = None
        result = check_chunks_have_section_paths(chunks)
        assert result.passed


class TestMaintenanceHeadingCheck:
    def test_warns_when_maintenance_heading_but_no_maintenance_chunks(self):
        # Chunk with maintenance in section_path but general chunk_type
        c = MagicMock()
        c.chunk_type = "general"
        c.section_path = ["Maintenance Schedule"]
        result = check_maintenance_headings_have_chunks([c])
        assert not result.passed

    def test_passes_when_maintenance_chunks_present(self):
        c1 = MagicMock()
        c1.chunk_type = "general"
        c1.section_path = ["Maintenance Schedule"]
        c2 = MagicMock()
        c2.chunk_type = "ChunkType.maintenance_procedure"
        c2.section_path = ["Maintenance Schedule", "Procedures"]
        result = check_maintenance_headings_have_chunks([c1, c2])
        assert result.passed

    def test_passes_when_no_maintenance_headings(self):
        c = MagicMock()
        c.chunk_type = "general"
        c.section_path = ["Introduction"]
        result = check_maintenance_headings_have_chunks([c])
        assert result.passed


class TestRetrievalQualityChecks:
    def test_warns_when_too_many_low_score_chunks(self):
        chunks = [_make_retrieved_chunk(score=0.05)] * 6 + [_make_retrieved_chunk(score=0.9)] * 4
        result = check_retrieved_chunk_scores(chunks)
        assert not result.passed

    def test_passes_when_scores_acceptable(self):
        chunks = [_make_retrieved_chunk(score=0.7)] * 5
        result = check_retrieved_chunk_scores(chunks)
        assert result.passed

    def test_warns_on_empty_content(self):
        chunks = [_make_retrieved_chunk(content="  ")]
        result = check_retrieved_chunks_have_content(chunks)
        assert not result.passed

    def test_passes_when_all_have_content(self):
        chunks = [_make_retrieved_chunk(content="Oil change every 500 hours.")]
        result = check_retrieved_chunks_have_content(chunks)
        assert result.passed


def _make_element(*, parent_section_id: str | None = None, page_start: int | None = None) -> CanonicalElement:
    return CanonicalElement(
        element_id="e_test",
        document_id="doc_test",
        element_type=ElementType.TEXT,
        parent_section_id=parent_section_id,
        source=SourceLocation(page_start=page_start),
    )


class TestOrphanElementRatioCheck:
    def test_passes_when_all_elements_linked_to_section(self):
        elements = [_make_element(parent_section_id="sec_1") for _ in range(5)]
        result = check_orphan_element_ratio(elements, sections=[])
        assert result.passed

    def test_warns_when_orphan_ratio_exceeds_threshold(self):
        # 3 orphans, 1 linked → 75% orphan ratio > 25% threshold
        elements = [_make_element(parent_section_id=None)] * 3 + [_make_element(parent_section_id="sec_1")]
        result = check_orphan_element_ratio(elements, sections=[])
        assert not result.passed

    def test_passes_when_orphan_ratio_below_threshold(self):
        # 1 orphan, 9 linked → 10% orphan ratio < 25% threshold
        elements = [_make_element(parent_section_id=None)] + [_make_element(parent_section_id="sec_1")] * 9
        result = check_orphan_element_ratio(elements, sections=[])
        assert result.passed

    def test_passes_on_empty_elements(self):
        result = check_orphan_element_ratio([], sections=[])
        assert result.passed


class TestElementsHavePagesCheck:
    def test_passes_when_all_elements_have_page(self):
        elements = [_make_element(page_start=i + 1) for i in range(5)]
        result = check_elements_have_pages(elements)
        assert result.passed

    def test_warns_when_majority_missing_page(self):
        # 6 without page, 4 with → 60% missing > 50% threshold
        elements = [_make_element(page_start=None)] * 6 + [_make_element(page_start=1)] * 4
        result = check_elements_have_pages(elements)
        assert not result.passed

    def test_passes_when_missing_ratio_at_or_below_threshold(self):
        # 4 without page, 6 with → 40% missing ≤ 50% threshold
        elements = [_make_element(page_start=None)] * 4 + [_make_element(page_start=1)] * 6
        result = check_elements_have_pages(elements)
        assert result.passed

    def test_passes_on_empty_elements(self):
        result = check_elements_have_pages([])
        assert result.passed


class TestDocumentQualityResult:
    def test_summary_shows_pass(self):
        result = DocumentQualityResult(document_id="doc1")
        from src.application.validation.document_quality.quality_check_result import (
            QualityCheckResult,
        )
        result.checks.append(QualityCheckResult.ok("check.one"))
        assert "PASS" in result.summary()

    def test_passed_is_false_on_error(self):
        result = DocumentQualityResult(document_id="doc1")
        from src.application.validation.document_quality.quality_check_result import (
            QualityCheckResult,
        )
        result.checks.append(
            QualityCheckResult.error("check.one", "Something went wrong")
        )
        assert not result.passed

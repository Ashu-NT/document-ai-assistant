import pytest
from unittest.mock import MagicMock, patch

from src.application.workflows.parsing.parsing_workflow import (
    _compute_parse_confidence,
    _collect_parse_warnings,
)
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)


class TestParseConfidenceComputation:
    def test_perfect_parse_returns_1(self):
        score = _compute_parse_confidence(
            element_count=100, orphan_count=0, no_page_count=0
        )
        assert score == pytest.approx(1.0)

    def test_all_orphans_half_penalty(self):
        score = _compute_parse_confidence(
            element_count=100, orphan_count=100, no_page_count=0
        )
        assert score == pytest.approx(0.5)

    def test_all_missing_pages_half_penalty(self):
        score = _compute_parse_confidence(
            element_count=100, orphan_count=0, no_page_count=100
        )
        assert score == pytest.approx(0.5)

    def test_all_bad_returns_0(self):
        score = _compute_parse_confidence(
            element_count=100, orphan_count=100, no_page_count=100
        )
        assert score == pytest.approx(0.0)

    def test_zero_elements_returns_none(self):
        score = _compute_parse_confidence(
            element_count=0, orphan_count=0, no_page_count=0
        )
        assert score is None


class TestCollectParseWarnings:
    def test_no_warnings_on_clean_document(self):
        warnings = _collect_parse_warnings(
            element_count=100,
            orphan_count=0,
            no_page_count=0,
            section_count=5,
            chunk_count=20,
        )
        assert warnings == []

    def test_warns_on_high_orphan_ratio(self):
        warnings = _collect_parse_warnings(
            element_count=100,
            orphan_count=30,
            no_page_count=0,
            section_count=5,
            chunk_count=20,
        )
        assert any("orphan" in w.lower() for w in warnings)

    def test_warns_on_no_sections(self):
        warnings = _collect_parse_warnings(
            element_count=100,
            orphan_count=0,
            no_page_count=0,
            section_count=0,
            chunk_count=5,
        )
        assert any("section" in w.lower() for w in warnings)

    def test_warns_on_no_chunks(self):
        warnings = _collect_parse_warnings(
            element_count=100,
            orphan_count=0,
            no_page_count=0,
            section_count=5,
            chunk_count=0,
        )
        assert any("chunk" in w.lower() for w in warnings)


class TestParsingWorkflowResultNewFields:
    def test_result_has_parse_confidence_field(self):
        graph = MagicMock()
        result = ParsingWorkflowResult(
            document_id="doc1",
            file_path="/f.pdf",
            page_count=10,
            element_count=50,
            section_count=5,
            chunk_count=20,
            table_count=2,
            picture_count=1,
            document_graph=graph,
            parse_confidence=0.87,
            orphan_element_count=3,
            elements_without_page_count=1,
            parse_warnings=["some warning"],
        )
        assert result.parse_confidence == pytest.approx(0.87)
        assert result.orphan_element_count == 3
        assert result.elements_without_page_count == 1
        assert result.parse_warnings == ["some warning"]

    def test_result_defaults_for_new_fields(self):
        graph = MagicMock()
        result = ParsingWorkflowResult(
            document_id="doc1",
            file_path="/f.pdf",
            page_count=None,
            element_count=0,
            section_count=0,
            chunk_count=0,
            table_count=0,
            picture_count=0,
            document_graph=graph,
        )
        assert result.parse_confidence is None
        assert result.orphan_element_count == 0
        assert result.elements_without_page_count == 0
        assert result.parse_warnings == []

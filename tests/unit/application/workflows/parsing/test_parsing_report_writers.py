import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.application.workflows.parsing.reports import (
    ChunkingReportWriter,
    ParsingReportWriter,
    QualityReportWriter,
)


def _make_result(
    document_id="doc1",
    chunk_count=5,
    orphan_count=0,
    no_page_count=0,
    parse_confidence=0.95,
    parse_warnings=None,
):
    result = MagicMock()
    result.document_id = document_id
    result.file_path = "/some/path/file.pdf"
    result.page_count = 10
    result.element_count = 50
    result.section_count = 8
    result.chunk_count = chunk_count
    result.table_count = 2
    result.picture_count = 1
    result.parse_confidence = parse_confidence
    result.orphan_element_count = orphan_count
    result.elements_without_page_count = no_page_count
    result.parse_warnings = parse_warnings or []

    # Build mock document_graph
    def _make_chunk(chunk_id, chunk_type="general", section_path=None):
        c = MagicMock()
        c.chunk_id = chunk_id
        c.chunk_type = chunk_type
        c.section_path = section_path or ["Section 1"]
        c.content = "Some chunk content here."
        return c

    chunks = {f"c{i}": _make_chunk(f"c{i}") for i in range(chunk_count)}
    result.document_graph.chunks = chunks
    result.document_graph.sections = {"s1": MagicMock()}
    result.document_graph.elements = {"e1": MagicMock()}
    return result


class TestParsingReportWriter:
    def test_writes_json_file(self, tmp_path):
        writer = ParsingReportWriter(output_dir=tmp_path)
        result = _make_result()
        path = writer.write(result)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["document_id"] == "doc1"
        assert "parse_confidence" in data
        assert "orphan_element_count" in data
        assert "elements_without_page_count" in data
        assert "parse_warnings" in data

    def test_filename_contains_document_id(self, tmp_path):
        writer = ParsingReportWriter(output_dir=tmp_path)
        result = _make_result(document_id="docXYZ")
        path = writer.write(result)
        assert "docXYZ" in path.name

    def test_creates_output_directory(self, tmp_path):
        nested = tmp_path / "a" / "b"
        writer = ParsingReportWriter(output_dir=nested)
        result = _make_result()
        writer.write(result)
        assert nested.exists()


class TestChunkingReportWriter:
    def test_writes_type_distribution(self, tmp_path):
        writer = ChunkingReportWriter(output_dir=tmp_path)
        result = _make_result(chunk_count=3)
        path = writer.write(result)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "type_distribution" in data
        assert "total_chunks" in data
        assert data["total_chunks"] == 3

    def test_reports_section_path_coverage(self, tmp_path):
        writer = ChunkingReportWriter(output_dir=tmp_path)
        result = _make_result(chunk_count=2)
        path = writer.write(result)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "chunks_with_section_path" in data
        assert "chunks_without_section_path" in data


class TestQualityReportWriter:
    def test_writes_quality_json(self, tmp_path):
        writer = QualityReportWriter(output_dir=tmp_path)
        result = _make_result()

        # Provide real-ish DocumentGraph mock for quality checks
        from unittest.mock import patch
        from src.application.validation.document_quality import DocumentQualityGate, DocumentQualityResult
        with patch.object(DocumentQualityGate, "check_parsing") as mock_parse, \
             patch.object(DocumentQualityGate, "check_chunking") as mock_chunk:
            mock_result = MagicMock(spec=DocumentQualityResult)
            mock_result.passed = True
            mock_result.summary.return_value = "PASS 3/3 checks passed (0 errors, 0 warnings)"
            mock_result.checks = []
            mock_parse.return_value = mock_result
            mock_chunk.return_value = mock_result

            path = writer.write(result)

        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "parsing" in data
        assert "chunking" in data
        assert "overall_passed" in data

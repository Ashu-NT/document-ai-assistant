import json
from unittest.mock import MagicMock

from src.application.reporting.document_parsing.parsing import ParsingReportWriter


def _make_result(document_id="doc1"):
    result = MagicMock()
    result.document_id = document_id
    result.file_path = "/some/path/file.pdf"
    result.page_count = 10
    result.element_count = 50
    result.section_count = 8
    result.chunk_count = 5
    result.table_count = 2
    result.picture_count = 1
    result.parse_confidence = 0.95
    result.orphan_element_count = 0
    result.elements_without_page_count = 0
    result.parse_warnings = []
    result.ocr_trace = None
    return result


def test_write_creates_json_file(tmp_path) -> None:
    writer = ParsingReportWriter(output_dir=tmp_path)
    path = writer.write(_make_result())

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["document_id"] == "doc1"
    assert "parse_confidence" in data


def test_write_filename_contains_document_id(tmp_path) -> None:
    writer = ParsingReportWriter(output_dir=tmp_path)
    path = writer.write(_make_result(document_id="docXYZ"))

    assert "docXYZ" in path.name


def test_write_creates_output_directory(tmp_path) -> None:
    nested = tmp_path / "a" / "b"
    writer = ParsingReportWriter(output_dir=nested)
    writer.write(_make_result())

    assert nested.exists()

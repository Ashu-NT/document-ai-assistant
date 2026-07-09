from unittest.mock import MagicMock

from src.application.reporting.document_parsing.parsing import ParsingReportBuilder


def _make_result(**overrides):
    result = MagicMock()
    result.document_id = "doc1"
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
    for key, value in overrides.items():
        setattr(result, key, value)
    return result


def test_build_includes_core_parse_fields() -> None:
    payload = ParsingReportBuilder().build(_make_result())

    assert payload["document_id"] == "doc1"
    assert payload["parse_confidence"] == 0.95
    assert payload["orphan_element_count"] == 0
    assert payload["elements_without_page_count"] == 0
    assert payload["parse_warnings"] == []


def test_build_delegates_ocr_serialization_to_injected_serializer() -> None:
    fake_serializer = MagicMock()
    fake_serializer.serialize.return_value = {"trace_path": "/tmp/x.json"}
    builder = ParsingReportBuilder(ocr_trace_serializer=fake_serializer)

    result = _make_result(ocr_trace="some-trace-object")
    payload = builder.build(result)

    fake_serializer.serialize.assert_called_once_with("some-trace-object")
    assert payload["ocr"] == {"trace_path": "/tmp/x.json"}

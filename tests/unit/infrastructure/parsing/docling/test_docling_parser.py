import pytest

from src.infrastructure.parsing.docling import DoclingParser
from src.shared.exceptions import DocumentParsingError


class FakeConverter:
    def __init__(self, result=None, exc: Exception | None = None) -> None:
        self.result = result
        self.exc = exc
        self.calls: list[tuple[tuple, dict]] = []

    def convert(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.exc is not None:
            raise self.exc
        return self.result


def test_parse_calls_converter_and_returns_raw_parsed_document() -> None:
    raw_document = type(
        "FakeRawDocument",
        (),
        {
            "title": "Hydraulic Pump Manual",
            "num_pages": 3,
        },
    )()
    conversion_result = type(
        "FakeConversionResult",
        (),
        {
            "document": raw_document,
            "pages": [object(), object(), object()],
            "status": type("FakeStatus", (), {"value": "success"})(),
            "confidence": 0.97,
        },
    )()
    converter = FakeConverter(result=conversion_result)
    parser = DoclingParser(
        converter=converter,
        max_num_pages=12,
        max_file_size_bytes=2048,
        parser_version="1.2.3",
    )

    parsed_document = parser.parse("data/input/pump_manual.pdf")

    assert converter.calls == [
        (
            ("data/input/pump_manual.pdf",),
            {
                "raises_on_error": True,
                "max_num_pages": 12,
                "max_file_size": 2048,
            },
        )
    ]
    assert parsed_document.file_path == "data/input/pump_manual.pdf"
    assert parsed_document.title == "Hydraulic Pump Manual"
    assert parsed_document.page_count == 3
    assert parsed_document.raw_document is raw_document
    assert parsed_document.parser_name == "docling"
    assert parsed_document.parser_version == "1.2.3"
    assert parsed_document.metadata["status"] == "success"
    assert parsed_document.metadata["confidence"] == 0.97


def test_parse_wraps_converter_failures_in_document_parsing_error() -> None:
    converter = FakeConverter(exc=RuntimeError("docling boom"))
    parser = DoclingParser(
        converter=converter,
        parser_version="1.2.3",
    )

    with pytest.raises(DocumentParsingError):
        parser.parse("data/input/pump_manual.pdf")


def test_parse_reuses_cached_converter_when_no_ocr_override_given() -> None:
    raw_document = type("FakeRawDocument", (), {"title": "Manual", "num_pages": 1})()
    conversion_result = type(
        "FakeConversionResult",
        (),
        {"document": raw_document, "pages": [object()]},
    )()
    converter = FakeConverter(result=conversion_result)
    parser = DoclingParser(converter=converter, parser_version="1.2.3")

    parser.parse("data/input/pump_manual.pdf")

    assert converter.calls[0][0] == ("data/input/pump_manual.pdf",)


def test_parse_builds_fresh_converter_when_ocr_override_given(monkeypatch) -> None:
    raw_document = type("FakeRawDocument", (), {"title": "Manual", "num_pages": 1})()
    conversion_result = type(
        "FakeConversionResult",
        (),
        {"document": raw_document, "pages": [object()]},
    )()
    cached_converter = FakeConverter(result=conversion_result)
    override_converter = FakeConverter(result=conversion_result)
    build_calls: list[bool | None] = []

    def _fake_build_docling_converter(*, enable_ocr_override=None):
        build_calls.append(enable_ocr_override)
        return override_converter

    monkeypatch.setattr(
        "src.infrastructure.parsing.docling.docling_parser.build_docling_converter",
        _fake_build_docling_converter,
    )
    parser = DoclingParser(converter=cached_converter, parser_version="1.2.3")

    parser.parse("data/input/pump_manual.pdf", enable_ocr_override=True)

    assert build_calls == [True]
    assert cached_converter.calls == []
    assert len(override_converter.calls) == 1


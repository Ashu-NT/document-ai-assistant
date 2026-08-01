import time

import pytest

from src.infrastructure.parsing.docling import DoclingParser
from src.shared.exceptions import DocumentParsingError, DocumentParsingTimeoutError


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


# --- Fixtures below are module-level (not defined inline in test functions)
# because the timeout-enforcing path now runs the conversion in a real
# `multiprocessing.Process` (spawned, per Windows' only supported start
# method). A spawned child re-imports its target/arguments by reference
# (module + qualname), so everything crossing that boundary - the converter
# factory function and anything it returns/raises - must be a plain,
# picklable, module-level object. Dynamically-created `type(...)` fixtures (as
# used by the in-process tests above) are NOT picklable this way.


class _FakeRawDocument:
    def __init__(self, title: str | None, num_pages: int | None) -> None:
        self.title = title
        self.num_pages = num_pages


class _FakeConversionResult:
    def __init__(self, document, pages=None) -> None:
        self.document = document
        self.pages = pages if pages is not None else []


class _SubprocessFakeConverter:
    """Picklable stand-in for a real Docling converter, for subprocess tests."""

    def __init__(self, *, enable_ocr_override: bool | None = None) -> None:
        self.enable_ocr_override = enable_ocr_override

    def convert(self, file_path, **kwargs):
        return _FakeConversionResult(
            document=_FakeRawDocument(title="Manual", num_pages=1),
        )


def _build_subprocess_fake_converter(*, enable_ocr_override: bool | None = None):
    return _SubprocessFakeConverter(enable_ocr_override=enable_ocr_override)


class _SubprocessSlowConverter:
    """Blocks convert() long enough to reliably exceed a tiny test timeout."""

    def __init__(self, *, enable_ocr_override: bool | None = None) -> None:
        self.enable_ocr_override = enable_ocr_override

    def convert(self, file_path, **kwargs):
        import time

        time.sleep(5)
        return _FakeConversionResult(document=_FakeRawDocument("x", 1))


def _build_subprocess_slow_converter(*, enable_ocr_override: bool | None = None):
    return _SubprocessSlowConverter(enable_ocr_override=enable_ocr_override)


class _SubprocessFailingConverter:
    """Picklable converter stand-in that always raises, for subprocess tests."""

    def __init__(self, *, enable_ocr_override: bool | None = None) -> None:
        self.enable_ocr_override = enable_ocr_override

    def convert(self, file_path, **kwargs):
        raise RuntimeError("docling boom")


def _build_subprocess_failing_converter(*, enable_ocr_override: bool | None = None):
    return _SubprocessFailingConverter(enable_ocr_override=enable_ocr_override)


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


def test_parse_succeeds_within_timeout_budget() -> None:
    # The timeout-enforced path always runs conversion in a real spawned
    # subprocess and ignores the injected `converter` instance (it can't be
    # pickled across the process boundary, and in production is never used
    # together with a timeout anyway) - `converter_factory` is the seam for
    # controlling what the subprocess actually converts with.
    parser = DoclingParser(
        converter=FakeConverter(),  # unused on this path; avoids a real build
        parser_version="1.2.3",
        timeout_seconds=5,
        converter_factory=_build_subprocess_fake_converter,
    )

    parsed_document = parser.parse("data/input/pump_manual.pdf")

    assert parsed_document.title == "Manual"
    assert parsed_document.page_count == 1


def test_parse_raises_timeout_error_when_conversion_hangs() -> None:
    parser = DoclingParser(
        converter=FakeConverter(),  # unused on this path; avoids a real build
        parser_version="1.2.3",
        timeout_seconds=0.2,
        converter_factory=_build_subprocess_slow_converter,
    )

    started_at = time.monotonic()
    with pytest.raises(DocumentParsingTimeoutError):
        parser.parse("data/input/pump_manual.pdf")
    elapsed_seconds = time.monotonic() - started_at

    # The fake converter sleeps for 5s and terminate->kill allows up to a
    # further 5s grace period; finishing well under both confirms the
    # subprocess was actually killed rather than the test just waiting out
    # the sleep (which is exactly the failure mode the old thread-based
    # timeout had: it could only *detect* a hang, never stop it).
    assert elapsed_seconds < 3


def test_parse_wraps_subprocess_conversion_failures_when_timeout_set() -> None:
    parser = DoclingParser(
        converter=FakeConverter(),  # unused on this path; avoids a real build
        parser_version="1.2.3",
        timeout_seconds=5,
        converter_factory=_build_subprocess_failing_converter,
    )

    with pytest.raises(DocumentParsingError):
        parser.parse("data/input/pump_manual.pdf")


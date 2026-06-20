import pytest

from src.infrastructure.parsing.docling import docling_converter_factory
from src.shared.exceptions import InfrastructureError


class FakeInputFormat:
    PDF = "pdf"


class FakePdfPipelineOptions:
    def __init__(self) -> None:
        self.do_ocr = True
        self.ocr_batch_size = 4
        self.ocr_options = None


class FakePdfFormatOption:
    def __init__(self, *, pipeline_options=None, **kwargs) -> None:
        self.pipeline_options = pipeline_options
        self.extra = kwargs


class FakeDocumentConverter:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs


class FakeOcrAutoOptions:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs


class FakeRapidOcrOptions:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs


class FakeDoclingSettings:
    def __init__(
        self,
        *,
        enable_ocr: bool,
        ocr_engine: str,
        rapidocr_backend: str,
        force_full_page_ocr: bool,
        bitmap_area_threshold: float,
        ocr_batch_size: int,
    ) -> None:
        self.enable_ocr = enable_ocr
        self.ocr_engine = ocr_engine
        self.rapidocr_backend = rapidocr_backend
        self.force_full_page_ocr = force_full_page_ocr
        self.bitmap_area_threshold = bitmap_area_threshold
        self.ocr_batch_size = ocr_batch_size


def fake_components() -> dict[str, object]:
    return {
        "DocumentConverter": FakeDocumentConverter,
        "InputFormat": FakeInputFormat,
        "PdfFormatOption": FakePdfFormatOption,
        "PdfPipelineOptions": FakePdfPipelineOptions,
        "OcrAutoOptions": FakeOcrAutoOptions,
        "RapidOcrOptions": FakeRapidOcrOptions,
    }


def test_build_docling_converter_disables_ocr_when_configured(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        docling_converter_factory,
        "_import_docling_components",
        fake_components,
    )
    monkeypatch.setattr(
        docling_converter_factory,
        "docling_settings",
        FakeDoclingSettings(
            enable_ocr=False,
            ocr_engine="auto",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=1,
        ),
    )

    converter = docling_converter_factory.build_docling_converter()
    pdf_option = converter.kwargs["format_options"][FakeInputFormat.PDF]

    assert pdf_option.pipeline_options.do_ocr is False
    assert pdf_option.pipeline_options.ocr_batch_size == 1
    assert pdf_option.pipeline_options.ocr_options is None


def test_build_docling_converter_uses_rapidocr_when_requested(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        docling_converter_factory,
        "_import_docling_components",
        fake_components,
    )
    monkeypatch.setattr(
        docling_converter_factory,
        "docling_settings",
        FakeDoclingSettings(
            enable_ocr=True,
            ocr_engine="rapidocr",
            rapidocr_backend="torch",
            force_full_page_ocr=True,
            bitmap_area_threshold=0.2,
            ocr_batch_size=2,
        ),
    )

    converter = docling_converter_factory.build_docling_converter()
    pdf_option = converter.kwargs["format_options"][FakeInputFormat.PDF]
    ocr_options = pdf_option.pipeline_options.ocr_options

    assert pdf_option.pipeline_options.do_ocr is True
    assert pdf_option.pipeline_options.ocr_batch_size == 2
    assert isinstance(ocr_options, FakeRapidOcrOptions)
    assert ocr_options.kwargs["backend"] == "torch"
    assert ocr_options.kwargs["force_full_page_ocr"] is True
    assert ocr_options.kwargs["bitmap_area_threshold"] == 0.2


def test_build_docling_converter_rejects_unsupported_ocr_engine(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        docling_converter_factory,
        "_import_docling_components",
        fake_components,
    )
    monkeypatch.setattr(
        docling_converter_factory,
        "docling_settings",
        FakeDoclingSettings(
            enable_ocr=True,
            ocr_engine="paddleocr",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=4,
        ),
    )

    with pytest.raises(InfrastructureError):
        docling_converter_factory.build_docling_converter()

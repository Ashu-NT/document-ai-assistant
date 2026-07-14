import pytest

from src.infrastructure.parsing.docling import docling_converter_factory

from src.shared.exceptions import InfrastructureError

class FakeInputFormat:
    PDF = "pdf"

class FakePyPdfiumDocumentBackend:
    pass

class FakeDoclingParseDocumentBackend:
    pass

class FakeThreadedDoclingParseDocumentBackend:
    pass

class FakeAcceleratorOptions:
    def __init__(self) -> None:
        self.num_threads = 4
        self.device = "auto"


class FakeTableStructureOptions:
    def __init__(self) -> None:
        self.mode = "accurate"
        self.do_cell_matching = True


class FakePdfPipelineOptions:
    def __init__(self) -> None:
        self.images_scale = 1.0
        self.do_table_structure = True
        self.do_ocr = True
        self.ocr_batch_size = 4
        self.layout_batch_size = 4
        self.table_batch_size = 4
        self.ocr_options = None
        self.accelerator_options = FakeAcceleratorOptions()
        self.table_structure_options = FakeTableStructureOptions()

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


class FakeTableFormerMode:
    ACCURATE = "accurate"
    FAST = "fast"


class FakeDoclingSettings:
    def __init__(
        self,
        *,
        pdf_backend: str,
        accelerator_device: str,
        images_scale: float,
        num_threads: int,
        enable_table_structure: bool,
        table_structure_mode: str,
        table_cell_matching: bool,
        enable_ocr: bool,
        ocr_engine: str,
        rapidocr_backend: str,
        force_full_page_ocr: bool,
        bitmap_area_threshold: float,
        ocr_batch_size: int,
        layout_batch_size: int,
        table_batch_size: int,
    ) -> None:
        self.pdf_backend = pdf_backend
        self.accelerator_device = accelerator_device
        self.images_scale = images_scale
        self.num_threads = num_threads
        self.enable_table_structure = enable_table_structure
        self.table_structure_mode = table_structure_mode
        self.table_cell_matching = table_cell_matching
        self.enable_ocr = enable_ocr
        self.ocr_engine = ocr_engine
        self.rapidocr_backend = rapidocr_backend
        self.force_full_page_ocr = force_full_page_ocr
        self.bitmap_area_threshold = bitmap_area_threshold
        self.ocr_batch_size = ocr_batch_size
        self.layout_batch_size = layout_batch_size
        self.table_batch_size = table_batch_size

def fake_components() -> dict[str, object]:
    return {
        "DocumentConverter": FakeDocumentConverter,
        "InputFormat": FakeInputFormat,
        "PdfFormatOption": FakePdfFormatOption,
        "PdfPipelineOptions": FakePdfPipelineOptions,
        "OcrAutoOptions": FakeOcrAutoOptions,
        "RapidOcrOptions": FakeRapidOcrOptions,
        "TableFormerMode": FakeTableFormerMode,
        "PyPdfiumDocumentBackend": FakePyPdfiumDocumentBackend,
        "DoclingParseDocumentBackend": FakeDoclingParseDocumentBackend,
        "ThreadedDoclingParseDocumentBackend": FakeThreadedDoclingParseDocumentBackend,
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
            pdf_backend="pypdfium2",
            accelerator_device="cpu",
            images_scale=0.75,
            num_threads=1,
            enable_table_structure=False,
            table_structure_mode="fast",
            table_cell_matching=False,
            enable_ocr=False,
            ocr_engine="auto",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=1,
            layout_batch_size=2,
            table_batch_size=1,
        ),
    )

    converter = docling_converter_factory.build_docling_converter()
    pdf_option = converter.kwargs["format_options"][FakeInputFormat.PDF]

    assert pdf_option.pipeline_options.images_scale == 0.75
    assert pdf_option.pipeline_options.do_table_structure is False
    assert pdf_option.pipeline_options.do_ocr is False
    assert pdf_option.pipeline_options.ocr_batch_size == 1
    assert pdf_option.pipeline_options.layout_batch_size == 2
    assert pdf_option.pipeline_options.table_batch_size == 1
    assert pdf_option.pipeline_options.accelerator_options.num_threads == 1
    assert pdf_option.pipeline_options.accelerator_options.device == "cpu"
    assert pdf_option.pipeline_options.table_structure_options.mode == "fast"
    assert pdf_option.pipeline_options.table_structure_options.do_cell_matching is False
    assert pdf_option.extra["backend"] is FakePyPdfiumDocumentBackend
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
            pdf_backend="docling_parse",
            accelerator_device="auto",
            images_scale=1.0,
            num_threads=2,
            enable_table_structure=True,
            table_structure_mode="accurate",
            table_cell_matching=True,
            enable_ocr=True,
            ocr_engine="rapidocr",
            rapidocr_backend="torch",
            force_full_page_ocr=True,
            bitmap_area_threshold=0.2,
            ocr_batch_size=2,
            layout_batch_size=3,
            table_batch_size=2,
        ),
    )

    converter = docling_converter_factory.build_docling_converter()
    pdf_option = converter.kwargs["format_options"][FakeInputFormat.PDF]
    ocr_options = pdf_option.pipeline_options.ocr_options

    assert pdf_option.pipeline_options.images_scale == 1.0
    assert pdf_option.pipeline_options.do_table_structure is True
    assert pdf_option.pipeline_options.do_ocr is True
    assert pdf_option.pipeline_options.ocr_batch_size == 2
    assert pdf_option.pipeline_options.layout_batch_size == 3
    assert pdf_option.pipeline_options.table_batch_size == 2
    assert pdf_option.pipeline_options.accelerator_options.num_threads == 2
    assert pdf_option.pipeline_options.accelerator_options.device == "auto"
    assert pdf_option.pipeline_options.table_structure_options.mode == "accurate"
    assert pdf_option.pipeline_options.table_structure_options.do_cell_matching is True
    assert pdf_option.extra["backend"] is FakeDoclingParseDocumentBackend
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
            pdf_backend="pypdfium2",
            accelerator_device="auto",
            images_scale=1.0,
            num_threads=1,
            enable_table_structure=True,
            table_structure_mode="accurate",
            table_cell_matching=True,
            enable_ocr=True,
            ocr_engine="paddleocr",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=4,
            layout_batch_size=4,
            table_batch_size=4,
        ),
    )

    with pytest.raises(InfrastructureError):
        docling_converter_factory.build_docling_converter()

def test_build_docling_converter_rejects_unsupported_accelerator_device(
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
            pdf_backend="pypdfium2",
            accelerator_device="metal",
            images_scale=1.0,
            num_threads=1,
            enable_table_structure=True,
            table_structure_mode="accurate",
            table_cell_matching=True,
            enable_ocr=False,
            ocr_engine="auto",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=1,
            layout_batch_size=2,
            table_batch_size=1,
        ),
    )

    with pytest.raises(InfrastructureError):
        docling_converter_factory.build_docling_converter()

def test_build_docling_converter_enable_ocr_override_forces_ocr_on(
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
            pdf_backend="pypdfium2",
            accelerator_device="cpu",
            images_scale=0.75,
            num_threads=1,
            enable_table_structure=False,
            table_structure_mode="accurate",
            table_cell_matching=True,
            enable_ocr=False,
            ocr_engine="auto",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=1,
            layout_batch_size=2,
            table_batch_size=1,
        ),
    )

    converter = docling_converter_factory.build_docling_converter(
        enable_ocr_override=True,
    )
    pdf_option = converter.kwargs["format_options"][FakeInputFormat.PDF]

    assert pdf_option.pipeline_options.do_ocr is True
    assert isinstance(pdf_option.pipeline_options.ocr_options, FakeOcrAutoOptions)


def test_build_docling_converter_rejects_unsupported_table_structure_mode(
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
            pdf_backend="pypdfium2",
            accelerator_device="cpu",
            images_scale=0.75,
            num_threads=1,
            enable_table_structure=True,
            table_structure_mode="balanced",
            table_cell_matching=True,
            enable_ocr=False,
            ocr_engine="auto",
            rapidocr_backend="torch",
            force_full_page_ocr=False,
            bitmap_area_threshold=0.05,
            ocr_batch_size=1,
            layout_batch_size=2,
            table_batch_size=1,
        ),
    )

    with pytest.raises(InfrastructureError):
        docling_converter_factory.build_docling_converter()

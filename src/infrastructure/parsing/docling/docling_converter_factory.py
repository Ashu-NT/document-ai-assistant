from typing import Any

from src.config.settings import docling_settings
from src.shared.exceptions import InfrastructureError


def build_docling_converter() -> Any:
    components = _import_docling_components()
    document_converter_class = components["DocumentConverter"]
    input_format = components["InputFormat"]
    pdf_format_option_class = components["PdfFormatOption"]
    pdf_pipeline_options_class = components["PdfPipelineOptions"]
    ocr_auto_options_class = components["OcrAutoOptions"]
    rapid_ocr_options_class = components["RapidOcrOptions"]

    pipeline_options = pdf_pipeline_options_class()
    pipeline_options.do_ocr = docling_settings.enable_ocr
    pipeline_options.ocr_batch_size = docling_settings.ocr_batch_size

    if docling_settings.enable_ocr:
        pipeline_options.ocr_options = _build_ocr_options(
            ocr_auto_options_class=ocr_auto_options_class,
            rapid_ocr_options_class=rapid_ocr_options_class,
        )

    return document_converter_class(
        format_options={
            input_format.PDF: pdf_format_option_class(
                pipeline_options=pipeline_options,
            )
        }
    )


def _build_ocr_options(
    *,
    ocr_auto_options_class,
    rapid_ocr_options_class,
):
    common_options = {
        "force_full_page_ocr": docling_settings.force_full_page_ocr,
        "bitmap_area_threshold": docling_settings.bitmap_area_threshold,
    }
    normalized_engine = docling_settings.ocr_engine.strip().lower()

    if normalized_engine in {"", "auto"}:
        return ocr_auto_options_class(**common_options)

    if normalized_engine == "rapidocr":
        return rapid_ocr_options_class(
            backend=_normalize_rapidocr_backend(),
            **common_options,
        )

    raise InfrastructureError(
        "Unsupported Docling OCR engine configured.",
        details={
            "ocr_engine": docling_settings.ocr_engine,
            "supported_engines": ["auto", "rapidocr"],
        },
    )


def _normalize_rapidocr_backend() -> str:
    normalized_backend = docling_settings.rapidocr_backend.strip().lower()
    supported_backends = {"onnxruntime", "openvino", "paddle", "torch"}

    if normalized_backend in supported_backends:
        return normalized_backend

    raise InfrastructureError(
        "Unsupported Docling RapidOCR backend configured.",
        details={
            "rapidocr_backend": docling_settings.rapidocr_backend,
            "supported_backends": sorted(supported_backends),
        },
    )


def _import_docling_components() -> dict[str, Any]:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (
        OcrAutoOptions,
        PdfPipelineOptions,
        RapidOcrOptions,
    )
    from docling.document_converter import DocumentConverter, PdfFormatOption

    return {
        "DocumentConverter": DocumentConverter,
        "InputFormat": InputFormat,
        "PdfFormatOption": PdfFormatOption,
        "PdfPipelineOptions": PdfPipelineOptions,
        "OcrAutoOptions": OcrAutoOptions,
        "RapidOcrOptions": RapidOcrOptions,
    }

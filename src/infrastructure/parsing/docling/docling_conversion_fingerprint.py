import hashlib
import json
from importlib.metadata import PackageNotFoundError, version

from src.config.settings import docling_settings


def compute_docling_conversion_fingerprint(
    *,
    enable_ocr_override: bool | None = None,
) -> str:
    """Opaque, deterministic fingerprint of everything that can change what
    Docling actually produces for a given input: the docling-core payload
    shape (via its installed version) and every material pipeline knob in
    `DoclingSettings`, plus the effective per-call OCR enable/disable
    (`enable_ocr_override` can differ from `docling_settings.enable_ocr` on
    any given call - see `DoclingParser._convert_with_timeout`).

    Callers (e.g. `ParsingWorkflow` via `ParsedArtifactKey`) must treat this
    as an opaque identity value, not something to decompose - that is the
    whole point of keeping Docling-specific configuration knowledge inside
    the infrastructure layer.
    """
    effective_enable_ocr = (
        enable_ocr_override if enable_ocr_override is not None else docling_settings.enable_ocr
    )
    payload = {
        "docling_core_version": _docling_core_version(),
        "pdf_backend": docling_settings.pdf_backend,
        "accelerator_device": docling_settings.accelerator_device,
        "images_scale": docling_settings.images_scale,
        "num_threads": docling_settings.num_threads,
        "enable_table_structure": docling_settings.enable_table_structure,
        "table_structure_mode": docling_settings.table_structure_mode,
        "table_cell_matching": docling_settings.table_cell_matching,
        "enable_ocr": effective_enable_ocr,
        "ocr_engine": docling_settings.ocr_engine,
        "rapidocr_backend": docling_settings.rapidocr_backend,
        "force_full_page_ocr": docling_settings.force_full_page_ocr,
        "bitmap_area_threshold": docling_settings.bitmap_area_threshold,
        "ocr_batch_size": docling_settings.ocr_batch_size,
        "layout_batch_size": docling_settings.layout_batch_size,
        "table_batch_size": docling_settings.table_batch_size,
        "max_table_grid_cells": docling_settings.max_table_grid_cells,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _docling_core_version() -> str:
    try:
        return version("docling-core")
    except PackageNotFoundError:
        return "unknown"

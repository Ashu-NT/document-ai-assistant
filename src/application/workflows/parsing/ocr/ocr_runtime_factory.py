from dataclasses import dataclass

from src.application.services.ai import OCRService
from src.application.workflows.parsing.canonical_element_ocr_enricher import (
    CanonicalElementOCREnricher,
)
from src.application.workflows.parsing.ocr.canonical_ocr_merger import (
    CanonicalOCRMerger,
)
from src.application.workflows.parsing.ocr.ocr_merge_policy import OCRMergePolicy
from src.application.workflows.parsing.ocr.ocr_selection_policy import (
    OCRSelectionPolicy,
)
from src.application.workflows.parsing.ocr.ocr_target_selector import OCRTargetSelector
from src.application.workflows.parsing.ocr.page_ocr_fallback_workflow import (
    PageOCRFallbackWorkflow,
)
from src.application.workflows.parsing.ocr.page_text_quality_analyzer import (
    PageTextQualityAnalyzer,
)
from src.config.paths import resolve_project_path
from src.config.settings import ocr_settings
from src.infrastructure.ai.ocr import build_ocr_provider
from src.infrastructure.pdf import PDFPageRenderer, PDFRegionCropper
from src.shared.ids import IdGenerator


@dataclass(slots=True)
class ParsingOCRRuntime:
    canonical_element_ocr_enricher: CanonicalElementOCREnricher | None
    page_ocr_fallback_workflow: PageOCRFallbackWorkflow | None


def build_parsing_ocr_runtime(
    *,
    id_generator: IdGenerator,
) -> ParsingOCRRuntime:
    if not ocr_settings.enabled:
        return ParsingOCRRuntime(
            canonical_element_ocr_enricher=None,
            page_ocr_fallback_workflow=None,
        )

    ocr_service = OCRService(build_ocr_provider())
    canonical_element_ocr_enricher = (
        CanonicalElementOCREnricher(ocr_service)
        if ocr_settings.asset_enabled
        else None
    )

    if not (
        ocr_settings.page_fallback_enabled
        or ocr_settings.region_fallback_enabled
    ):
        return ParsingOCRRuntime(
            canonical_element_ocr_enricher=canonical_element_ocr_enricher,
            page_ocr_fallback_workflow=None,
        )

    selection_policy = OCRSelectionPolicy(
        asset_enabled=ocr_settings.asset_enabled,
        page_fallback_enabled=ocr_settings.page_fallback_enabled,
        region_fallback_enabled=ocr_settings.region_fallback_enabled,
        max_pages_per_document=ocr_settings.max_pages_per_document,
        max_regions_per_page=ocr_settings.max_regions_per_page,
        min_text_chars_per_page=ocr_settings.min_text_chars_per_page,
        min_text_density=ocr_settings.min_text_density,
        min_image_area_ratio=ocr_settings.min_image_area_ratio,
        page_render_dpi=ocr_settings.page_render_dpi,
        timeout_seconds=ocr_settings.timeout_seconds,
    )
    merge_policy = OCRMergePolicy(
        min_confidence=ocr_settings.min_confidence,
        attach_low_confidence_text=ocr_settings.attach_low_confidence_text,
    )
    output_dir = resolve_project_path(ocr_settings.output_dir)

    return ParsingOCRRuntime(
        canonical_element_ocr_enricher=canonical_element_ocr_enricher,
        page_ocr_fallback_workflow=PageOCRFallbackWorkflow(
            ocr_service=ocr_service,
            target_selector=OCRTargetSelector(
                page_text_quality_analyzer=PageTextQualityAnalyzer(selection_policy),
                policy=selection_policy,
            ),
            canonical_ocr_merger=CanonicalOCRMerger(
                id_generator=id_generator,
                merge_policy=merge_policy,
            ),
            page_renderer=PDFPageRenderer(),
            region_cropper=PDFRegionCropper(),
            output_dir=output_dir,
            trace_enabled=ocr_settings.trace_enabled,
            fail_fast=ocr_settings.fail_fast,
        ),
    )


from dataclasses import dataclass

from src.application.services.ai import OCRService
from src.application.workflows.parsing.canonical_element_ocr_enricher import (
    CanonicalElementOCREnricher,
)
from src.application.workflows.parsing.ocr.merging.canonical_ocr_merger import (
    CanonicalOCRMerger,
)
from src.application.workflows.parsing.ocr.merging.ocr_merge_policy import OCRMergePolicy
from src.application.workflows.parsing.ocr.parsing_ocr_policy import (
    ParsingOCRPolicy,
    resolve_parsing_ocr_policy,
)
from src.application.workflows.parsing.ocr.selection.ocr_selection_policy import (
    OCRSelectionPolicy,
)
from src.application.workflows.parsing.ocr.selection.ocr_target_selector import OCRTargetSelector
from src.application.workflows.parsing.ocr.page_ocr_fallback_workflow import (
    PageOCRFallbackWorkflow,
)
from src.application.workflows.parsing.ocr.selection.page_text_quality_analyzer import (
    PageTextQualityAnalyzer,
)
from src.config.paths import resolve_project_path
from src.config.settings import ocr_settings
from src.infrastructure.ai.ocr import build_ocr_provider
from src.infrastructure.pdf import PDFPageRenderer, PDFRegionCropper
from src.shared.ids import IdGenerator


@dataclass(slots=True)
class ParsingOCRRuntime:
    policy: ParsingOCRPolicy
    canonical_element_ocr_enricher: CanonicalElementOCREnricher | None
    page_ocr_fallback_workflow: PageOCRFallbackWorkflow | None


def build_parsing_ocr_runtime(
    *,
    id_generator: IdGenerator,
    policy: ParsingOCRPolicy | None = None,
) -> ParsingOCRRuntime:
    resolved_policy = policy or resolve_parsing_ocr_policy()
    if not resolved_policy.provider_runtime_enabled:
        return ParsingOCRRuntime(
            policy=resolved_policy,
            canonical_element_ocr_enricher=None,
            page_ocr_fallback_workflow=None,
        )

    ocr_service = OCRService(
        build_ocr_provider(),
        retry_attempts=ocr_settings.retry_attempts,
        retry_backoff_seconds=ocr_settings.retry_backoff_seconds,
    )
    canonical_element_ocr_enricher = (
        CanonicalElementOCREnricher(ocr_service)
        if resolved_policy.asset_ocr_enabled
        else None
    )

    if not (
        resolved_policy.page_fallback_enabled
        or resolved_policy.region_fallback_enabled
    ):
        return ParsingOCRRuntime(
            policy=resolved_policy,
            canonical_element_ocr_enricher=canonical_element_ocr_enricher,
            page_ocr_fallback_workflow=None,
        )

    selection_policy = OCRSelectionPolicy(
        asset_enabled=resolved_policy.asset_ocr_enabled,
        page_fallback_enabled=resolved_policy.page_fallback_enabled,
        region_fallback_enabled=resolved_policy.region_fallback_enabled,
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
        policy=resolved_policy,
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

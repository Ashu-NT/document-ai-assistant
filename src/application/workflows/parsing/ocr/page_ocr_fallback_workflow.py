from __future__ import annotations

from pathlib import Path

from src.application.services.ai import OCRService
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.ocr.merging.canonical_ocr_merger import (
    CanonicalOCRMerger,
)
from src.application.workflows.parsing.ocr.merging.ocr_merge_result import OCRMergeResult
from src.application.workflows.parsing.ocr.ocr_temporary_artifact_cleaner import (
    OCRTemporaryArtifactCleaner,
)
from src.application.workflows.parsing.ocr.targets.ocr_target_execution_result import (
    OCRTargetExecutionResult,
)
from src.application.workflows.parsing.ocr.selection.ocr_target_selector import OCRTargetSelector
from src.application.workflows.parsing.ocr.targets.ocr_target_type import OCRTargetType
from src.infrastructure.pdf import PDFPageRenderer, PDFRegionCropper
from src.shared.activity import ActivityContext
from src.shared.exceptions import InfrastructureError, OCRProviderError
from src.shared.execution import tracked_action


class PageOCRFallbackWorkflow:
    def __init__(
        self,
        *,
        ocr_service: OCRService,
        target_selector: OCRTargetSelector,
        canonical_ocr_merger: CanonicalOCRMerger,
        page_renderer: PDFPageRenderer,
        region_cropper: PDFRegionCropper | None,
        output_dir: Path,
        temporary_artifact_cleaner: OCRTemporaryArtifactCleaner | None = None,
        trace_enabled: bool = False,
        fail_fast: bool = False,
    ) -> None:
        self.ocr_service = ocr_service
        self.target_selector = target_selector
        self.canonical_ocr_merger = canonical_ocr_merger
        self.page_renderer = page_renderer
        self.region_cropper = region_cropper
        self.output_dir = output_dir
        self.temporary_artifact_cleaner = (
            temporary_artifact_cleaner or OCRTemporaryArtifactCleaner(output_dir)
        )
        self.trace_enabled = trace_enabled
        self.fail_fast = fail_fast

    @tracked_action(
        action="parsing.ocr_fallback_completed",
        activity=True,
        audit=False,
        event=False,
    )
    def run(
        self,
        *,
        file_path: str,
        canonical_elements: list[ParsedCanonicalElement],
        page_count: int | None,
        activity_context: ActivityContext | None = None,
    ) -> OCRMergeResult:
        selection_result = self.target_selector.select(
            document_path=file_path,
            canonical_elements=canonical_elements,
            page_count=page_count,
        )
        execution_results: list[OCRTargetExecutionResult] = []
        temporary_artifact_paths: set[Path] = set()
        rendered_page_cache: dict[tuple[int, int], object] = {}
        needs_pdf = any(
            target.target_type != OCRTargetType.ASSET
            for target in selection_result.targets
        )
        opened_pdf = self.page_renderer.open(file_path) if needs_pdf else None

        try:
            for target in selection_result.targets:
                try:
                    source_image_path = self._resolve_target_image_path(
                        target,
                        opened_pdf,
                        rendered_page_cache,
                        temporary_artifact_paths,
                    )
                    ocr_result = self.ocr_service.extract_result_from_image(
                        source_image_path,
                        activity_context=activity_context,
                    )
                    execution_results.append(
                        OCRTargetExecutionResult(
                            target=target,
                            source_image_path=source_image_path,
                            ocr_result=ocr_result,
                        )
                    )
                except (InfrastructureError, OCRProviderError) as exc:
                    if self.fail_fast:
                        raise
                    execution_results.append(
                        OCRTargetExecutionResult(
                            target=target,
                            error=exc.message,
                        )
                    )

            return self.canonical_ocr_merger.merge(
                document_path=file_path,
                page_count=page_count or 0,
                canonical_elements=canonical_elements,
                selection_result=selection_result,
                execution_results=execution_results,
                persist_trace=self.trace_enabled,
                trace_output_dir=self.output_dir,
            )
        finally:
            if opened_pdf is not None:
                opened_pdf.close()
            if not self.trace_enabled:
                self.temporary_artifact_cleaner.cleanup(temporary_artifact_paths)

    def _resolve_target_image_path(
        self,
        target,
        opened_pdf,
        rendered_page_cache: dict[tuple[int, int], object],
        temporary_artifact_paths: set[Path],
    ) -> str:
        if target.target_type == OCRTargetType.ASSET:
            if not target.image_path:
                raise InfrastructureError(
                    "Asset OCR target is missing an image path.",
                    details={"target_id": target.target_id},
                )
            return target.image_path

        page_number = target.page_number or 1
        dpi = self.target_selector.policy.page_render_dpi
        cache_key = (page_number, dpi)
        rendered_page = rendered_page_cache.get(cache_key)
        if rendered_page is None:
            rendered_page = opened_pdf.render_page(
                page_number=page_number,
                dpi=dpi,
                output_dir=self.output_dir / "pages",
            )
            rendered_page_cache[cache_key] = rendered_page
            temporary_artifact_paths.add(Path(rendered_page.image_path))
        if target.target_type == OCRTargetType.PAGE:
            return rendered_page.image_path

        if target.target_type == OCRTargetType.REGION:
            if self.region_cropper is None or target.bbox is None:
                raise InfrastructureError(
                    "Region OCR target cannot be cropped without a cropper and bbox.",
                    details={"target_id": target.target_id},
                )
            cropped_region = self.region_cropper.crop(
                image_path=rendered_page.image_path,
                bbox=target.bbox,
                output_dir=self.output_dir / "regions",
            )
            temporary_artifact_paths.add(Path(cropped_region.image_path))
            return cropped_region.image_path

        raise InfrastructureError(
            "Unsupported OCR target type encountered.",
            details={"target_type": target.target_type.value},
        )

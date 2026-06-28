from __future__ import annotations

from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.ocr.ocr_selection_policy import OCRSelectionPolicy
from src.application.workflows.parsing.ocr.ocr_selection_result import OCRSelectionResult
from src.application.workflows.parsing.ocr.ocr_target import OCRTarget
from src.application.workflows.parsing.ocr.ocr_target_type import OCRTargetType
from src.application.workflows.parsing.ocr.page_text_quality_analyzer import (
    PageTextQualityAnalyzer,
)
from src.domain.common import ElementType


class OCRTargetSelector:
    def __init__(
        self,
        *,
        page_text_quality_analyzer: PageTextQualityAnalyzer,
        policy: OCRSelectionPolicy,
    ) -> None:
        self.page_text_quality_analyzer = page_text_quality_analyzer
        self.policy = policy

    def select(
        self,
        *,
        document_path: str,
        canonical_elements: list[CanonicalElement],
        page_count: int | None,
    ) -> OCRSelectionResult:
        page_analyses = self.page_text_quality_analyzer.analyze(
            canonical_elements,
            page_count,
        )
        warnings: list[str] = []
        targets: list[OCRTarget] = []
        seen_keys: set[str] = set()

        if self.policy.asset_enabled:
            for element in canonical_elements:
                image_path = self._clean_text(element.metadata.get("image_path"))
                if image_path is None:
                    continue
                if self._clean_text(element.metadata.get("ocr_text")) is not None:
                    continue

                target = OCRTarget(
                    target_id=f"asset:{element.element_id}",
                    target_type=OCRTargetType.ASSET,
                    document_path=document_path,
                    page_number=element.page_start,
                    image_path=image_path,
                    bbox=element.bbox,
                    source_element_id=element.element_id,
                    reason="asset_image_without_ocr",
                    priority=100,
                )
                self._add_target(targets, seen_keys, target)

        selected_asset_pages = {
            target.page_number
            for target in targets
            if target.target_type == OCRTargetType.ASSET and target.page_number is not None
        }

        if self.policy.page_fallback_enabled:
            page_candidates = [
                analysis
                for analysis in page_analyses
                if analysis.is_text_poor or analysis.is_probably_scanned
            ]
            page_candidates.sort(
                key=lambda analysis: (
                    analysis.is_probably_scanned,
                    analysis.image_area_ratio or 0.0,
                    -(analysis.text_char_count),
                ),
                reverse=True,
            )

            selected_pages = 0
            for analysis in page_candidates:
                if selected_pages >= self.policy.max_pages_per_document:
                    warnings.append(
                        "Reached OCR page fallback limit for this document."
                    )
                    break
                if analysis.page_number in selected_asset_pages:
                    continue

                target = OCRTarget(
                    target_id=f"page:{analysis.page_number}",
                    target_type=OCRTargetType.PAGE,
                    document_path=document_path,
                    page_number=analysis.page_number,
                    reason=",".join(analysis.reasons),
                    priority=90 if analysis.is_probably_scanned else 70,
                    metadata={
                        "text_char_count": analysis.text_char_count,
                        "word_count": analysis.word_count,
                    },
                )
                if self._add_target(targets, seen_keys, target):
                    selected_pages += 1

        if self.policy.region_fallback_enabled:
            for analysis in page_analyses:
                if not (analysis.is_text_poor or analysis.is_probably_scanned):
                    continue
                if any(
                    target.target_type == OCRTargetType.PAGE
                    and target.page_number == analysis.page_number
                    for target in targets
                ):
                    continue

                page_regions = 0
                for element in self._candidate_region_elements(
                    canonical_elements,
                    analysis.page_number,
                ):
                    if page_regions >= self.policy.max_regions_per_page:
                        warnings.append(
                            f"Reached OCR region limit for page {analysis.page_number}."
                        )
                        break

                    target = OCRTarget(
                        target_id=f"region:{element.element_id}",
                        target_type=OCRTargetType.REGION,
                        document_path=document_path,
                        page_number=analysis.page_number,
                        bbox=element.bbox,
                        source_element_id=element.element_id,
                        reason="large_visual_region_with_weak_text",
                        priority=60,
                    )
                    if self._add_target(targets, seen_keys, target):
                        page_regions += 1

        targets.sort(key=lambda target: (-target.priority, target.target_id))
        return OCRSelectionResult(
            page_analyses=page_analyses,
            targets=targets,
            warnings=warnings,
        )

    @staticmethod
    def _clean_text(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _candidate_region_elements(
        canonical_elements: list[CanonicalElement],
        page_number: int,
    ) -> list[CanonicalElement]:
        candidates: list[CanonicalElement] = []
        for element in canonical_elements:
            if element.page_start != page_number:
                continue
            if element.bbox is None:
                continue
            if element.element_type not in {ElementType.PICTURE, ElementType.TABLE}:
                continue
            candidates.append(element)

        candidates.sort(
            key=lambda element: (
                -abs((element.bbox.x2 - element.bbox.x1) * (element.bbox.y2 - element.bbox.y1)),
                element.order_index,
            )
        )
        return candidates

    @staticmethod
    def _add_target(
        targets: list[OCRTarget],
        seen_keys: set[str],
        target: OCRTarget,
    ) -> bool:
        key = "|".join(
            [
                target.target_type.value,
                str(target.page_number or ""),
                target.image_path or "",
                target.source_element_id or "",
                (
                    ""
                    if target.bbox is None
                    else f"{target.bbox.x1}:{target.bbox.y1}:{target.bbox.x2}:{target.bbox.y2}"
                ),
            ]
        )
        if key in seen_keys:
            return False
        seen_keys.add(key)
        targets.append(target)
        return True


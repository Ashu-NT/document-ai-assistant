from __future__ import annotations

import re

from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.ocr.ocr_selection_policy import OCRSelectionPolicy
from src.application.workflows.parsing.ocr.page_text_quality import PageTextQuality
from src.domain.common import ElementType

_TEXT_TYPES = {
    ElementType.TITLE,
    ElementType.SECTION_HEADER,
    ElementType.TEXT,
    ElementType.LIST_ITEM,
    ElementType.TABLE,
    ElementType.CAPTION,
    ElementType.KEY_VALUE,
    ElementType.CODE,
    ElementType.FORMULA,
}
_VISUAL_TYPES = {
    ElementType.PICTURE,
    ElementType.TABLE,
}


class PageTextQualityAnalyzer:
    def __init__(self, policy: OCRSelectionPolicy) -> None:
        self.policy = policy

    def analyze(
        self,
        canonical_elements: list[CanonicalElement],
        page_count: int | None,
    ) -> list[PageTextQuality]:
        resolved_page_count = self._resolve_page_count(canonical_elements, page_count)
        return [
            self._analyze_page(
                page_number=page_number,
                page_elements=self._page_elements(canonical_elements, page_number),
            )
            for page_number in range(1, resolved_page_count + 1)
        ]

    def _analyze_page(
        self,
        *,
        page_number: int,
        page_elements: list[CanonicalElement],
    ) -> PageTextQuality:
        text_char_count = 0
        word_count = 0
        table_count = 0
        image_count = 0

        for element in page_elements:
            if element.element_type == ElementType.TABLE:
                table_count += 1
            if element.element_type == ElementType.PICTURE:
                image_count += 1
            if element.element_type in _TEXT_TYPES and element.text:
                normalized_text = element.text.strip()
                text_char_count += len(normalized_text)
                word_count += len(re.findall(r"\w+", normalized_text))

        text_density = self._estimate_text_density(page_elements, text_char_count)
        image_area_ratio = self._estimate_image_area_ratio(page_elements, text_char_count)
        has_text = text_char_count > 0

        min_word_count = max(10, self.policy.min_text_chars_per_page // 12)
        reasons: list[str] = []

        low_text = (
            text_char_count < self.policy.min_text_chars_per_page
            or word_count < min_word_count
        )
        sparse_density = (
            text_density is not None
            and text_density < self.policy.min_text_density
        )
        image_heavy = (
            image_area_ratio is not None
            and image_area_ratio >= self.policy.min_image_area_ratio
        )

        is_probably_scanned = image_heavy and (not has_text or text_char_count < 40)
        if not has_text:
            reasons.append("no_extracted_text")
        if low_text:
            reasons.append("low_text_volume")
        if sparse_density:
            reasons.append("low_text_density")
        if image_heavy:
            reasons.append("image_heavy_page")
        if is_probably_scanned:
            reasons.append("probable_scanned_page")

        is_text_poor = not has_text or (
            low_text and (image_heavy or sparse_density or len(page_elements) <= 2)
        )

        return PageTextQuality(
            page_number=page_number,
            text_char_count=text_char_count,
            word_count=word_count,
            element_count=len(page_elements),
            table_count=table_count,
            image_count=image_count,
            text_density=text_density,
            image_area_ratio=image_area_ratio,
            has_text=has_text,
            is_text_poor=is_text_poor,
            is_probably_scanned=is_probably_scanned,
            reasons=reasons,
        )

    @staticmethod
    def _resolve_page_count(
        canonical_elements: list[CanonicalElement],
        page_count: int | None,
    ) -> int:
        if page_count is not None and page_count > 0:
            return page_count

        page_numbers = [
            page_number
            for element in canonical_elements
            for page_number in (element.page_start, element.page_end)
            if page_number is not None
        ]
        return max(page_numbers, default=0)

    @staticmethod
    def _page_elements(
        canonical_elements: list[CanonicalElement],
        page_number: int,
    ) -> list[CanonicalElement]:
        elements: list[CanonicalElement] = []
        for element in canonical_elements:
            start = element.page_start
            end = element.page_end or start
            if start is None or end is None:
                continue
            if start <= page_number <= end:
                elements.append(element)
        return elements

    @staticmethod
    def _estimate_text_density(
        page_elements: list[CanonicalElement],
        text_char_count: int,
    ) -> float | None:
        page_area = PageTextQualityAnalyzer._estimate_page_area(page_elements)
        if page_area is None or page_area <= 0 or text_char_count <= 0:
            return None
        return round(text_char_count / page_area, 6)

    @staticmethod
    def _estimate_image_area_ratio(
        page_elements: list[CanonicalElement],
        text_char_count: int,
    ) -> float | None:
        visual_areas = [
            PageTextQualityAnalyzer._bbox_area(element)
            for element in page_elements
            if element.element_type in _VISUAL_TYPES
        ]
        visual_areas = [area for area in visual_areas if area is not None]
        if not visual_areas:
            return 1.0 if not page_elements and text_char_count == 0 else 0.0

        page_area = PageTextQualityAnalyzer._estimate_page_area(page_elements)
        if page_area is None or page_area <= 0:
            return 1.0 if text_char_count == 0 else 0.0

        return round(min(sum(visual_areas) / page_area, 1.0), 6)

    @staticmethod
    def _estimate_page_area(page_elements: list[CanonicalElement]) -> float | None:
        boxes = [
            element.bbox
            for element in page_elements
            if element.bbox is not None
        ]
        if not boxes:
            return None

        max_x = max(max(box.x1, box.x2) for box in boxes)
        max_y = max(max(box.y1, box.y2) for box in boxes)
        if max_x <= 1.0 and max_y <= 1.0:
            return 1.0
        if max_x <= 0 or max_y <= 0:
            return None
        return max_x * max_y

    @staticmethod
    def _bbox_area(element: CanonicalElement) -> float | None:
        bbox = element.bbox
        if bbox is None:
            return None
        width = abs(bbox.x2 - bbox.x1)
        height = abs(bbox.y2 - bbox.y1)
        if width <= 0 or height <= 0:
            return None
        return width * height


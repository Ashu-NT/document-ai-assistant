from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)
from src.application.workflows.parsing.builders.chunking.policies.section_semantics import (
    is_task_like_title,
    normalize_section_title,
)
from src.domain.common import ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement

_TEXTUAL_ELEMENT_TYPES = {
    ElementType.TEXT,
    ElementType.LIST_ITEM,
    ElementType.KEY_VALUE,
    ElementType.CODE,
}

_MANUAL_MARKERS = (
    "maintenance",
    "procedure",
    "task",
    "operation",
    "installation",
    "troubleshooting",
    "service",
    "inspection",
    "repair",
)
_DATASHEET_MARKERS = (
    "datasheet",
    "technical data",
    "technical specification",
    "specification",
    "specifications",
    "electrical",
    "mechanical",
    "rating",
    "ratings",
    "dimensions",
)
_DRAWING_MARKERS = (
    "drawing",
    "schematic",
    "diagram",
    "layout",
    "wiring",
)
_REPORT_MARKERS = (
    "abstract",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "background",
    "methodology",
    "method",
)


class ChunkingProfileStatisticsBuilder:
    def build(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ChunkingProfileStatistics:
        all_titles = [
            title
            for title in [
                normalize_section_title(document_title),
                *[
                    normalize_section_title(section.title)
                    for section in sections
                ],
            ]
            if title
        ]

        element_count = 0
        table_count = 0
        picture_count = 0
        list_count = 0
        code_count = 0
        caption_count = 0
        text_element_count = 0
        text_token_total = 0
        long_text_block_count = 0
        short_text_block_count = 0

        for elements in section_elements_by_id.values():
            for element in elements:
                element_count += 1
                if element.element_type == ElementType.TABLE:
                    table_count += 1
                elif element.element_type == ElementType.PICTURE:
                    picture_count += 1
                elif element.element_type == ElementType.LIST_ITEM:
                    list_count += 1
                elif element.element_type == ElementType.CODE:
                    code_count += 1
                elif element.element_type == ElementType.CAPTION:
                    caption_count += 1

                if element.element_type not in _TEXTUAL_ELEMENT_TYPES:
                    continue
                if not element.text or not element.text.strip():
                    continue

                tokens = len(element.text.split())
                text_element_count += 1
                text_token_total += tokens
                if tokens >= 18:
                    long_text_block_count += 1
                if tokens <= 8:
                    short_text_block_count += 1

        section_count = len(sections)
        root_section_count = sum(
            1 for section in sections if section.parent_section_id is None
        )
        nested_section_count = max(0, section_count - root_section_count)
        max_section_depth = max(
            (
                max(
                    section.level,
                    len(section.section_path) if section.section_path else 0,
                    1,
                )
                for section in sections
            ),
            default=1,
        )
        procedure_like_section_count = sum(
            1
            for section in sections
            if self._is_procedure_like_title(section.title)
        )

        avg_text_tokens = (
            text_token_total / text_element_count
            if text_element_count > 0
            else 0.0
        )

        return ChunkingProfileStatistics(
            element_count=element_count,
            section_count=section_count,
            root_section_count=root_section_count,
            nested_section_count=nested_section_count,
            max_section_depth=max_section_depth,
            table_count=table_count,
            picture_count=picture_count,
            list_count=list_count,
            code_count=code_count,
            caption_count=caption_count,
            text_element_count=text_element_count,
            text_token_total=text_token_total,
            long_text_block_count=long_text_block_count,
            short_text_block_count=short_text_block_count,
            avg_text_tokens=avg_text_tokens,
            table_ratio=self._ratio(table_count, element_count),
            picture_ratio=self._ratio(picture_count, element_count),
            list_ratio=self._ratio(list_count, element_count),
            code_ratio=self._ratio(code_count, element_count),
            caption_ratio=self._ratio(caption_count, element_count),
            nested_section_ratio=self._ratio(nested_section_count, section_count),
            long_text_ratio=self._ratio(long_text_block_count, text_element_count),
            short_text_ratio=self._ratio(short_text_block_count, text_element_count),
            manual_marker_hits=self._count_marker_hits(all_titles, _MANUAL_MARKERS),
            datasheet_marker_hits=self._count_marker_hits(
                all_titles,
                _DATASHEET_MARKERS,
            ),
            drawing_marker_hits=self._count_marker_hits(all_titles, _DRAWING_MARKERS),
            report_marker_hits=self._count_marker_hits(all_titles, _REPORT_MARKERS),
            procedure_like_section_count=procedure_like_section_count,
        )

    @staticmethod
    def _count_marker_hits(
        titles: list[str],
        markers: tuple[str, ...],
    ) -> int:
        hits = 0
        for title in titles:
            hits += sum(1 for marker in markers if marker in title)
        return hits

    @staticmethod
    def _is_procedure_like_title(title: str | None) -> bool:
        normalized = normalize_section_title(title)
        if not normalized:
            return False

        return is_task_like_title(title) or any(
            marker in normalized
            for marker in (
                "maintenance",
                "procedure",
                "operation",
                "installation",
                "troubleshooting",
                "service",
            )
        )

    @staticmethod
    def _ratio(count: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return count / total

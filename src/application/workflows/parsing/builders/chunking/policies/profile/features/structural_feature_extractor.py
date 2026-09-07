from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_evidence_matcher import (
    StructuralEvidenceMatcher,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge.section_semantics import (
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


@dataclass(slots=True, frozen=True)
class _ElementCounts:
    element_count: int
    table_count: int
    picture_count: int
    list_count: int
    caption_count: int
    text_element_count: int
    text_token_total: int
    long_text_block_count: int
    short_text_block_count: int


class StructuralFeatureExtractor:
    """Builds StructuralDocumentFeatures for one document: layout,
    hierarchy, and text-shape statistics (this class's own job), plus
    per-profile title-keyword evidence (delegated to
    StructuralEvidenceMatcher)."""

    def __init__(
        self,
        *,
        evidence_matcher: StructuralEvidenceMatcher | None = None,
    ) -> None:
        self.evidence_matcher = evidence_matcher or StructuralEvidenceMatcher()

    def build(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> StructuralDocumentFeatures:
        element_counts = self._count_elements(section_elements_by_id)
        hierarchy_statistics = self._build_hierarchy_statistics(sections)
        layout_statistics = self._build_layout_statistics(element_counts)
        text_shape_statistics = self._build_text_shape_statistics(element_counts)

        titles = self._collect_titles(document_title, sections)
        evidence = self.evidence_matcher.match(titles)

        procedure_like_section_count = sum(
            1
            for section in sections
            if self._is_procedure_like_title(section.title)
        )

        return StructuralDocumentFeatures(
            **hierarchy_statistics,
            **layout_statistics,
            **text_shape_statistics,
            evidence=evidence,
            procedure_like_section_count=procedure_like_section_count,
        )

    @staticmethod
    def _count_elements(
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> _ElementCounts:
        element_count = 0
        table_count = 0
        picture_count = 0
        list_count = 0
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

        return _ElementCounts(
            element_count=element_count,
            table_count=table_count,
            picture_count=picture_count,
            list_count=list_count,
            caption_count=caption_count,
            text_element_count=text_element_count,
            text_token_total=text_token_total,
            long_text_block_count=long_text_block_count,
            short_text_block_count=short_text_block_count,
        )

    @classmethod
    def _build_hierarchy_statistics(
        cls,
        sections: list[DocumentSection],
    ) -> dict[str, int | float]:
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
        return {
            "section_count": section_count,
            "root_section_count": root_section_count,
            "nested_section_count": nested_section_count,
            "max_section_depth": max_section_depth,
            "nested_section_ratio": cls._ratio(nested_section_count, section_count),
        }

    @classmethod
    def _build_layout_statistics(
        cls,
        counts: _ElementCounts,
    ) -> dict[str, int | float]:
        return {
            "element_count": counts.element_count,
            "table_ratio": cls._ratio(counts.table_count, counts.element_count),
            "picture_ratio": cls._ratio(counts.picture_count, counts.element_count),
            "list_ratio": cls._ratio(counts.list_count, counts.element_count),
            "caption_ratio": cls._ratio(counts.caption_count, counts.element_count),
        }

    @classmethod
    def _build_text_shape_statistics(
        cls,
        counts: _ElementCounts,
    ) -> dict[str, int | float]:
        avg_text_tokens = (
            counts.text_token_total / counts.text_element_count
            if counts.text_element_count > 0
            else 0.0
        )
        return {
            "text_element_count": counts.text_element_count,
            "avg_text_tokens": avg_text_tokens,
            "long_text_ratio": cls._ratio(
                counts.long_text_block_count, counts.text_element_count
            ),
            "short_text_ratio": cls._ratio(
                counts.short_text_block_count, counts.text_element_count
            ),
        }

    @staticmethod
    def _collect_titles(
        document_title: str | None,
        sections: list[DocumentSection],
    ) -> list[str]:
        return [
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

    @staticmethod
    def _is_procedure_like_title(title: str | None) -> bool:
        normalized = normalize_section_title(title)
        if not normalized:
            return False

        return is_task_like_title(title) or any(
            keyword in normalized
            for keyword in (
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

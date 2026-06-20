from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.section_semantics import (
    normalize_section_title,
)
from src.domain.common import ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ChunkingProfileInferer:
    def infer(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ChunkingProfile:
        title_text = normalize_section_title(document_title)
        section_titles = [normalize_section_title(section.title) for section in sections]
        all_titles = [title for title in [title_text, *section_titles] if title]

        element_count = 0
        table_count = 0
        picture_count = 0
        list_count = 0
        code_count = 0
        text_token_total = 0
        text_element_count = 0

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
                elif element.text:
                    text_element_count += 1
                    text_token_total += len(element.text.split())

        avg_text_tokens = (
            text_token_total / text_element_count
            if text_element_count > 0
            else 0.0
        )
        narrative_titles = sum(
            1
            for title in all_titles
            if any(
                marker in title
                for marker in (
                    "objective",
                    "preparation",
                    "procedure",
                    "task",
                    "introduction",
                    "operation",
                    "installation",
                    "warning",
                )
            )
        )
        report_titles = sum(
            1
            for title in all_titles
            if any(
                marker in title
                for marker in (
                    "abstract",
                    "background",
                    "discussion",
                    "conclusion",
                    "results",
                )
            )
        )

        if (
            picture_count >= max(3, element_count // 6)
            and avg_text_tokens < 18
            and list_count <= picture_count
        ):
            return ChunkingProfile.DRAWING

        if (
            table_count >= max(2, element_count // 5)
            and avg_text_tokens < 24
            and code_count <= 1
        ):
            return ChunkingProfile.DATASHEET

        if report_titles >= 2 and narrative_titles < report_titles + 2:
            return ChunkingProfile.REPORT

        if narrative_titles >= 2 or list_count >= max(3, table_count):
            return ChunkingProfile.MANUAL

        return ChunkingProfile.DEFAULT

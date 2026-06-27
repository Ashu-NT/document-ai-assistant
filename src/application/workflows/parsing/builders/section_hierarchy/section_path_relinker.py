from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)
from src.domain.document import DocumentSection


class SectionPathRelinker:
    def relink(
        self,
        sections: list[DocumentSection],
    ) -> None:
        section_by_path: dict[tuple[str, ...], DocumentSection] = {}
        ordered_sections = sorted(
            sections,
            key=lambda section: (
                section.sequence_number or 0,
                section.reading_order_start or 0,
            ),
        )

        for section in ordered_sections:
            sanitized_path = sanitize_section_path(
                list(section.section_path or ([section.title] if section.title else []))
            )
            if not sanitized_path:
                sanitized_path = [section.title] if section.title else []

            section.section_path = sanitized_path
            section.level = max(1, len(sanitized_path))

            parent_section = self._find_parent_section(
                sanitized_path=sanitized_path,
                section_by_path=section_by_path,
            )
            section.parent_section_id = (
                parent_section.section_id if parent_section is not None else None
            )
            section_by_path[tuple(sanitized_path)] = section

    @staticmethod
    def _find_parent_section(
        *,
        sanitized_path: list[str],
        section_by_path: dict[tuple[str, ...], DocumentSection],
    ) -> DocumentSection | None:
        for prefix_length in range(len(sanitized_path) - 1, 0, -1):
            parent = section_by_path.get(tuple(sanitized_path[:prefix_length]))
            if parent is not None:
                return parent
        return None

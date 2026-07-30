from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
    strip_heading_number,
)


class SectionHeadingLabeler:
    def build_label(
        self,
        *,
        raw_title: str,
        resolved_numbering: str | None,
    ) -> str:
        cleaned_title = raw_title.strip()
        if not cleaned_title:
            return (resolved_numbering or "").strip()

        if not resolved_numbering:
            return cleaned_title

        existing_numbering = extract_heading_number(cleaned_title)
        if existing_numbering == resolved_numbering:
            return cleaned_title

        stripped_title = strip_heading_number(cleaned_title).strip()
        if not stripped_title:
            return resolved_numbering

        return f"{resolved_numbering} {stripped_title}"

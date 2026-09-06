from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    normalize_toc_title,
)


class TocHeadingRecognizer:
    """Recognizes conventional document-index headings across supported languages."""

    _ALIASES = frozenset(
        {
            "contents",
            "content",
            "table of contents",
            "inhaltsverzeichnis",
            "inhalt",
            "sommaire",
            "toc",
        }
    )

    @classmethod
    def matches(cls, value: str | None) -> bool:
        return normalize_toc_title(value) in cls._ALIASES

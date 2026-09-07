from typing import Any


class DoclingPageHeightResolver:
    @classmethod
    def resolve(cls, raw_document: Any, page_number: int | None) -> float | None:
        if raw_document is None or page_number is None:
            return None
        pages = cls._get_value(raw_document, "pages")
        page = cls._page_for_number(pages, page_number)
        size = cls._get_value(page, "size")
        height = cls._get_value(size, "height")
        try:
            resolved = float(height)
        except (TypeError, ValueError):
            return None
        return resolved if resolved > 0 else None

    @staticmethod
    def _page_for_number(pages: Any, page_number: int) -> Any:
        if isinstance(pages, dict):
            return pages.get(page_number) or pages.get(str(page_number))
        try:
            return pages[page_number]
        except (IndexError, KeyError, TypeError):
            return None

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)

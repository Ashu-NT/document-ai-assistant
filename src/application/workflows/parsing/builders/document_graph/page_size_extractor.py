from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument


class PageSizeExtractor:
    """Extracts per-page (width, height) size lookups from a raw parsed document."""

    @staticmethod
    def extract(
        raw_parsed_document: RawParsedDocument,
    ) -> dict[int, tuple[float, float]]:
        pages = getattr(raw_parsed_document.raw_document, "pages", None)
        if not pages:
            return {}

        page_sizes: dict[int, tuple[float, float]] = {}
        for page_no, page in pages.items():
            size = getattr(page, "size", None)
            width = getattr(size, "width", None)
            height = getattr(size, "height", None)
            if width is None or height is None:
                continue
            try:
                page_sizes[int(page_no)] = (float(width), float(height))
            except (TypeError, ValueError):
                continue
        return page_sizes

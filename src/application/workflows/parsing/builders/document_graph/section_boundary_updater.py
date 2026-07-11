from src.domain.elements import CanonicalElement


class SectionBoundaryUpdater:
    """Updates a section's reading-order and page boundaries from a newly attached element."""

    @staticmethod
    def update(section, element: CanonicalElement) -> None:
        reading_order = element.reading_order
        if reading_order is not None:
            if section.reading_order_start is None or reading_order < section.reading_order_start:
                section.reading_order_start = reading_order
            if section.reading_order_end is None or reading_order > section.reading_order_end:
                section.reading_order_end = reading_order

        source = element.source
        if source.page_start is not None:
            if section.source.page_start is None or source.page_start < section.source.page_start:
                section.source.page_start = source.page_start
        if source.page_end is not None:
            if section.source.page_end is None or source.page_end > section.source.page_end:
                section.source.page_end = source.page_end

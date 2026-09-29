from dataclasses import dataclass
from enum import StrEnum


class ExtractionScopeType(StrEnum):
    """V1 scope types. Deliberately does not use chunk IDs - chunk
    boundaries may legitimately change after chunking improvements, but a
    page range is a stable, human-reviewable annotation surface. Additional
    scope types (e.g. a section-path scope) can be added as new enum values
    plus new optional fields on `ExtractionEvaluationScope` without changing
    any caller of `contains_page`/`overlaps_pages`."""

    WHOLE_DOCUMENT = "whole_document"
    PAGE_RANGE = "page_range"


@dataclass(frozen=True, slots=True)
class ExtractionEvaluationScope:
    scope_type: ExtractionScopeType
    page_start: int | None = None
    page_end: int | None = None

    def __post_init__(self) -> None:
        if self.scope_type is ExtractionScopeType.PAGE_RANGE:
            if self.page_start is None or self.page_end is None:
                raise ValueError(
                    "PAGE_RANGE scope requires both page_start and page_end "
                    "(inclusive bounds)."
                )
            if self.page_start < 1:
                raise ValueError("page_start must be >= 1.")
            if self.page_start > self.page_end:
                raise ValueError(
                    "page_start must be <= page_end for an inclusive range."
                )
        elif self.page_start is not None or self.page_end is not None:
            raise ValueError(
                f"{self.scope_type} scope must not set page bounds."
            )

    def contains_page(self, page: int | None) -> bool:
        if self.scope_type is ExtractionScopeType.WHOLE_DOCUMENT:
            return True
        if page is None:
            return False
        assert self.page_start is not None and self.page_end is not None
        return self.page_start <= page <= self.page_end

    def overlaps_pages(
        self, page_start: int | None, page_end: int | None
    ) -> bool:
        """True if [page_start, page_end] (inclusive, either bound may be
        None to mean "same as the other bound") overlaps this scope."""
        if self.scope_type is ExtractionScopeType.WHOLE_DOCUMENT:
            return True
        if page_start is None and page_end is None:
            return False
        lo = page_start if page_start is not None else page_end
        hi = page_end if page_end is not None else page_start
        assert lo is not None and hi is not None
        assert self.page_start is not None and self.page_end is not None
        return lo <= self.page_end and hi >= self.page_start

    @staticmethod
    def whole_document() -> "ExtractionEvaluationScope":
        return ExtractionEvaluationScope(scope_type=ExtractionScopeType.WHOLE_DOCUMENT)

    @staticmethod
    def page_range(start: int, end: int) -> "ExtractionEvaluationScope":
        return ExtractionEvaluationScope(
            scope_type=ExtractionScopeType.PAGE_RANGE,
            page_start=start,
            page_end=end,
        )


__all__ = ["ExtractionScopeType", "ExtractionEvaluationScope"]
